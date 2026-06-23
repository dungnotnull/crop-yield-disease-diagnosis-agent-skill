"""Data-source availability, vintage checking, and fallback logic."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from crop_yield_disease_diagnosis.types import Imagery


MAX_CLOUD_COVER = 20.0
STALE_DAYS = 30


def is_imagery_usable(imagery: Imagery, reference_date: date | None = None) -> tuple[bool, str]:
    """Check whether an imagery acquisition is usable and return (usable, reason)."""
    ref = reference_date or date.today()
    age_days = (ref - imagery.acquisition_date).days
    if imagery.cloud_cover_percent > MAX_CLOUD_COVER:
        return False, f"cloud cover {imagery.cloud_cover_percent:.0f}% exceeds {MAX_CLOUD_COVER:.0f}%"
    if age_days > STALE_DAYS:
        return False, f"image is {age_days} days old (stale >{STALE_DAYS} days)"
    return True, f"usable; {age_days} days old"


def resolve_data_sources(
    data_sources: list[str],
    imagery: list[Imagery],
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Determine what data is available and which fallback mode applies."""
    ref = reference_date or date.today()
    notes: list[str] = []

    imagery_usable = []
    imagery_unusable = []
    for img in imagery:
        ok, reason = is_imagery_usable(img, ref)
        if ok:
            imagery_usable.append(img)
            notes.append(f"{img.sensor} on {img.acquisition_date}: {reason}")
        else:
            imagery_unusable.append((img, reason))
            notes.append(f"{img.sensor} on {img.acquisition_date}: excluded ({reason})")

    has_field_data = any(
        ds in {"weather_station", "soil_test", "field_observation"} for ds in data_sources
    )

    if not imagery_usable and has_field_data:
        mode = "field_data_only"
        notes.append("No usable imagery; switching to field-data-only mode with reduced confidence.")
    elif not imagery_usable and not has_field_data:
        mode = "insufficient_data"
        notes.append("No usable imagery and no field data; analysis will be low-confidence.")
    else:
        mode = "remote_sensing"
        best = sorted(imagery_usable, key=lambda i: (i.cloud_cover_percent, i.resolution_m))[0]
        notes.append(f"Primary imagery: {best.sensor} on {best.acquisition_date} ({best.resolution_m}m, {best.cloud_cover_percent:.0f}% cloud).")

    has_recent_imagery = any(
        (ref - img.acquisition_date).days <= STALE_DAYS for img in imagery_usable
    )

    return {
        "mode": mode,
        "usable_imagery": imagery_usable,
        "unusable_imagery": imagery_unusable,
        "has_field_data": has_field_data,
        "notes": notes,
        "stale": not has_recent_imagery,
        "fallback_used": mode != "remote_sensing",
    }


def select_primary_imagery(imagery: list[Imagery]) -> Imagery | None:
    """Pick the best usable image (lowest cloud cover, then finest resolution)."""
    if not imagery:
        return None
    return sorted(imagery, key=lambda i: (i.cloud_cover_percent, i.resolution_m))[0]


def estimate_data_quality(
    resolved: dict[str, Any],
    index_nan_fraction: float | None = None,
) -> float:
    """Return a 0-1 data-quality score."""
    base = 0.7 if resolved["mode"] == "remote_sensing" else 0.45
    if resolved["has_field_data"]:
        base += 0.15
    if resolved.get("stale"):
        base -= 0.20
    if index_nan_fraction is not None:
        base -= index_nan_fraction * 0.5
    return max(0.1, min(0.95, base))
