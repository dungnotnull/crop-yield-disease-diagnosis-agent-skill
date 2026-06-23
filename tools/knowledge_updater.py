#!/usr/bin/env python3
"""knowledge_updater.py — Production knowledge pipeline for Idea 213.

Fetches authoritative remote-sensing, agronomy, and plant-pathology sources,
scores entries by relevance and recency, deduplicates by URL hash, and appends
dated entries to SECOND-KNOWLEDGE-BRAIN.md.

No external model training or heavy inference is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("knowledge_updater")

DEFAULT_BRAIN = Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"

KEYWORDS = [
    "ndvi", "evi", "remote sensing", "crop yield", "plant disease",
    "precision agriculture", "sentinel", "aquacrop", "phenology", "ipm",
    "dssat", "landsat", "red edge", "vegetation index", "integrated pest management",
]

SOURCE_CONFIG: dict[str, dict[str, Any]] = {
    "copernicus": {
        "url": "https://dataspace.copernicus.eu/news/",
        "type": "html",
        "authority": 1.0,
    },
    "usgs": {
        "url": "https://earthexplorer.usgs.gov/",
        "type": "html",
        "authority": 1.0,
    },
    "fao_aquacrop": {
        "url": "https://www.fao.org/land-water/databases-and-software/aquacrop/en/",
        "type": "html",
        "authority": 1.0,
    },
    "mdpi_horticulturae": {
        "url": "https://www.mdpi.com/journal/horticulturae/rss",
        "type": "rss",
        "authority": 0.9,
    },
    "arxiv_eess_iv": {
        "url": "http://export.arxiv.org/rss/eess.IV",
        "type": "rss",
        "authority": 0.85,
    },
    "arxiv_qbio_pe": {
        "url": "http://export.arxiv.org/rss/q-bio.PE",
        "type": "rss",
        "authority": 0.8,
    },
    "cabi": {
        "url": "https://www.cabidigitallibrary.org/product/qc",
        "type": "html",
        "authority": 0.9,
    },
}


@dataclass
class Entry:
    """A knowledge-base entry candidate."""

    title: str
    url: str
    source: str
    published: date | None = None
    summary: str = ""
    authority: float = 0.5
    raw_score: float = field(init=False)

    def url_hash(self) -> str:
        return hashlib.sha256(self.url.encode("utf-8")).hexdigest()[:12]

    def year(self) -> int:
        return self.published.year if self.published else date.today().year

    def __hash__(self) -> int:
        return hash(self.url_hash())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entry):
            return NotImplemented
        return self.url_hash() == other.url_hash()


class Fetcher:
    """Fetch sources with retries, timeouts, and polite headers."""

    def __init__(self, timeout: int = 20, max_retries: int = 3, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": user_agent or (
                "Mozilla/5.0 (compatible; CropYieldKnowledgeBot/0.1; +https://example.com)"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.session = requests.Session()

    def fetch(self, url: str) -> str:
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, headers=self.headers, timeout=self.timeout)
                resp.raise_for_status()
                return resp.text
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("Fetch attempt %d/%d failed for %s: %s", attempt, self.max_retries, url, exc)
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"Failed to fetch {url}: {last_exc}")

    def fetch_all(self, sources: dict[str, str]) -> dict[str, str]:
        """Fetch many sources concurrently."""
        results: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=min(8, len(sources))) as pool:
            future_to_name = {
                pool.submit(self.fetch, url): name for name, url in sources.items()
            }
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    results[name] = future.result()
                except Exception as exc:  # noqa: BLE001
                    logger.error("Source %s failed: %s", name, exc)
                    results[name] = ""
        return results


class Parser:
    """Parse RSS/Atom and HTML pages into Entry candidates."""

    def parse_rss(self, name: str, text: str, authority: float) -> list[Entry]:
        entries: list[Entry] = []
        try:
            feed = feedparser.parse(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("RSS parse failed for %s: %s", name, exc)
            return entries

        for item in feed.get("entries", []):
            title = item.get("title", "(untitled)").strip()
            link = item.get("link", "").strip()
            if not link or not title:
                continue
            pub = self._parse_date(item.get("published_parsed") or item.get("updated_parsed"))
            summary = self._clean_text(item.get("summary", ""))
            entries.append(
                Entry(
                    title=title,
                    url=link,
                    source=name,
                    published=pub,
                    summary=summary,
                    authority=authority,
                )
            )
        return entries

    def parse_html(self, name: str, text: str, authority: float, base_url: str) -> list[Entry]:
        entries: list[Entry] = []
        try:
            soup = BeautifulSoup(text, "html.parser")
        except Exception as exc:  # noqa: BLE001
            logger.warning("HTML parse failed for %s: %s", name, exc)
            return entries

        # Extract article-like blocks: h2/a, h3/a, or any anchor with title-looking text.
        for tag in soup.find_all(["h2", "h3", "h4", "article", "li"]):
            a = tag.find("a", href=True)
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a["href"].strip()
            if not title or len(title) < 20 or href.startswith("javascript:") or href == "#":
                continue
            if href.startswith("/"):
                parsed = urlparse(base_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif not href.startswith(("http://", "https://")):
                continue
            # Try to find a nearby date snippet.
            pub = None
            for dt_tag in tag.find_all(["time", "span", "div"], limit=3):
                pub = self._guess_date(dt_tag.get_text(" ", strip=True))
                if pub:
                    break
            entries.append(
                Entry(
                    title=title,
                    url=href,
                    source=name,
                    published=pub,
                    summary="",
                    authority=authority,
                )
            )
        return entries

    def _parse_date(self, struct_time: Any) -> date | None:
        if not struct_time:
            return None
        try:
            return date(struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday)
        except (AttributeError, ValueError):
            return None

    def _guess_date(self, text: str) -> date | None:
        # Look for ISO-like or Month DD, YYYY.
        patterns = [
            r"(\d{4})-(\d{2})-(\d{2})",
            r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if not m:
                continue
            try:
                if len(m.groups()) == 3 and m.group(2).isdigit():
                    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                # Month name form
                month_names = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
                mon = month_names.index(m.group(2).lower()[:3]) + 1
                return date(int(m.group(3)), mon, int(m.group(1)))
            except (ValueError, IndexError):
                continue
        return None

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", BeautifulSoup(text, "html.parser").get_text(" ", strip=True))


class Scorer:
    """Score entries by keyword relevance, recency, and source authority."""

    def __init__(self, keywords: list[str]) -> None:
        self.keywords = [k.lower() for k in keywords]

    def score(self, entry: Entry) -> float:
        text = (entry.title + " " + entry.summary).lower()
        keyword_hits = sum(1 for k in self.keywords if k in text)
        recency = self._recency_factor(entry.published)
        return keyword_hits * recency * entry.authority

    def _recency_factor(self, published: date | None) -> float:
        if published is None:
            return 0.5
        age_days = (date.today() - published).days
        if age_days <= 30:
            return 1.0
        if age_days <= 365:
            return 0.7
        if age_days <= 730:
            return 0.4
        return 0.2


class Appender:
    """Deduplicate and append entries to SECOND-KNOWLEDGE-BRAIN.md."""

    def __init__(self, brain_path: Path) -> None:
        self.brain_path = brain_path

    def existing_hashes(self) -> set[str]:
        if not self.brain_path.exists():
            return set()
        text = self.brain_path.read_text(encoding="utf-8")
        return set(re.findall(r"<!--h:([0-9a-f]{12})-->", text))

    def append(self, entries: list[Entry]) -> int:
        if not entries:
            return 0
        if not self.brain_path.exists():
            self.brain_path.write_text("# SECOND-KNOWLEDGE-BRAIN\n\n", encoding="utf-8")
        text = self.brain_path.read_text(encoding="utf-8").rstrip()
        seen = self.existing_hashes()
        lines: list[str] = []
        added = 0
        for entry in entries:
            h = entry.url_hash()
            if h in seen:
                continue
            pub = entry.published.isoformat() if entry.published else "unknown"
            lines.append(
                f"- {date.today().isoformat()} — {entry.title} "
                f"({entry.source}, {pub}) {entry.url} <!--h:{h}-->"
            )
            seen.add(h)
            added += 1
        if lines:
            new_text = text + "\n" + "\n".join(lines) + "\n"
            self.brain_path.write_text(new_text, encoding="utf-8")
        return added


class Updater:
    """Orchestrate fetch, parse, score, dedup, append."""

    def __init__(
        self,
        brain_path: Path | None = None,
        sources: dict[str, dict[str, Any]] | None = None,
        keywords: list[str] | None = None,
        timeout: int = 20,
        max_retries: int = 3,
    ) -> None:
        self.brain_path = brain_path or DEFAULT_BRAIN
        self.sources = sources or SOURCE_CONFIG
        self.keywords = keywords or KEYWORDS
        self.fetcher = Fetcher(timeout=timeout, max_retries=max_retries)
        self.parser = Parser()
        self.scorer = Scorer(self.keywords)
        self.appender = Appender(self.brain_path)

    def run(
        self,
        limit: int | None = None,
        since: date | None = None,
        source_filter: list[str] | None = None,
        dry_run: bool = False,
    ) -> list[Entry]:
        selected = {
            name: cfg["url"]
            for name, cfg in self.sources.items()
            if not source_filter or name in source_filter
        }
        logger.info("Fetching %d sources...", len(selected))
        raw = self.fetcher.fetch_all(selected)

        all_entries: list[Entry] = []
        for name, text in raw.items():
            if not text:
                continue
            cfg = self.sources[name]
            if cfg["type"] == "rss":
                parsed = self.parser.parse_rss(name, text, cfg["authority"])
            else:
                parsed = self.parser.parse_html(name, text, cfg["authority"], cfg["url"])
            logger.info("%s parsed %d entries", name, len(parsed))
            all_entries.extend(parsed)

        # Score and filter.
        for entry in all_entries:
            entry.raw_score = self.scorer.score(entry)
        all_entries.sort(key=lambda e: e.raw_score, reverse=True)

        if since:
            all_entries = [e for e in all_entries if (e.published is None) or (e.published >= since)]

        if limit:
            all_entries = all_entries[:limit]

        if dry_run:
            logger.info("Dry run: %d candidates would be appended", len(all_entries))
            return all_entries

        added = self.appender.append(all_entries)
        logger.info("Appended %d new entries to %s", added, self.brain_path.name)
        return all_entries


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update SECOND-KNOWLEDGE-BRAIN.md")
    parser.add_argument("--brain", type=Path, default=DEFAULT_BRAIN, help="Path to brain markdown")
    parser.add_argument("--limit", type=int, default=None, help="Max entries to append")
    parser.add_argument("--since", type=str, default=None, help="YYYY-MM-DD cutoff")
    parser.add_argument("--sources", nargs="+", default=None, help="Source names to use")
    parser.add_argument("--dry-run", action="store_true", help="Show candidates without writing")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    since = date.fromisoformat(args.since) if args.since else None
    updater = Updater(brain_path=args.brain, timeout=args.timeout, max_retries=args.retries)
    try:
        entries = updater.run(
            limit=args.limit,
            since=since,
            source_filter=args.sources,
            dry_run=args.dry_run,
        )
        for e in entries[:10]:
            print(f"{e.raw_score:.2f} | {e.title[:70]} | {e.url[:80]}")
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Update failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
