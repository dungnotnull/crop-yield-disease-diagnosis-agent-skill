"""Tests for the knowledge updater pipeline (no live network)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tools.knowledge_updater import Appender, Entry, Fetcher, Parser, Scorer, Updater


def test_url_hash_consistency() -> None:
    e1 = Entry(title="A", url="https://example.com/1", source="test")
    e2 = Entry(title="B", url="https://example.com/1", source="test")
    assert e1.url_hash() == e2.url_hash()


def test_scorer_keywords_and_recency() -> None:
    scorer = Scorer(["ndvi", "remote sensing"])
    old = Entry(title="Old NDVI paper", url="https://example.com/old", source="test", published=date(2000, 1, 1), authority=1.0)
    new = Entry(title="New NDVI remote sensing", url="https://example.com/new", source="test", published=date(2026, 6, 1), authority=1.0)
    assert scorer.score(new) > scorer.score(old)


def test_parser_rss() -> None:
    rss = """<?xml version="1.0"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
  <channel>
    <title>Test</title>
    <link>https://example.com</link>
    <item>
      <title>NDVI and crop yield</title>
      <link>https://example.com/article1</link>
      <dc:date>2026-06-20T00:00:00Z</dc:date>
    </item>
  </channel>
</rss>
"""
    parser = Parser()
    entries = parser.parse_rss("test", rss, authority=1.0)
    assert len(entries) == 1
    assert entries[0].title == "NDVI and crop yield"
    assert entries[0].year() == 2026


def test_appender_dedup(tmp_path: Path) -> None:
    brain = tmp_path / "SECOND-KNOWLEDGE-BRAIN.md"
    brain.write_text("# Brain\n\n", encoding="utf-8")
    appender = Appender(brain)
    entries = [
        Entry(title="A", url="https://example.com/a", source="test"),
        Entry(title="B", url="https://example.com/a", source="test"),
    ]
    assert appender.append(entries) == 1
    assert appender.append(entries) == 0


def test_updater_dry_run(monkeypatch: pytest.MonkeyPatch) -> None:
    updater = Updater()
    # Replace the configured sources with a single mocked RSS source so that
    # the fetch_all result maps back to the sources dictionary.
    monkeypatch.setattr(updater, "sources", {
        "test_rss": {"url": "https://example.com/rss", "type": "rss", "authority": 1.0}
    })

    def fake_fetch_all(sources):
        return {"test_rss": """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Precision agriculture NDVI</title>
      <link>https://example.com/pa</link>
      <pubDate>Mon, 20 Jun 2026 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""}

    monkeypatch.setattr(updater.fetcher, "fetch_all", fake_fetch_all)
    entries = updater.run(dry_run=True, limit=5, source_filter=["test_rss"])
    assert len(entries) >= 1
    assert entries[0].title == "Precision agriculture NDVI"
