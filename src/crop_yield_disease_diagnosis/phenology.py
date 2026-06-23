"""Crop phenology reference curves and growth-stage helpers."""
from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np

# Expected NDVI ranges per crop and generic stage.
PHENOLOGY_TABLE: dict[str, dict[str, tuple[float, float]]] = {
    "maize": {
        "emergence": (0.15, 0.25),
        "vegetative": (0.40, 0.65),
        "tasseling": (0.70, 0.85),
        "silking": (0.70, 0.85),
        "grain_fill": (0.60, 0.75),
        "senescence": (0.25, 0.40),
    },
    "rice": {
        "emergence": (0.20, 0.30),
        "vegetative": (0.45, 0.65),
        "heading": (0.70, 0.85),
        "flowering": (0.70, 0.85),
        "grain_fill": (0.55, 0.70),
        "senescence": (0.20, 0.35),
    },
    "wheat": {
        "emergence": (0.15, 0.25),
        "vegetative": (0.40, 0.60),
        "heading": (0.65, 0.80),
        "flowering": (0.65, 0.80),
        "grain_fill": (0.50, 0.65),
        "senescence": (0.20, 0.35),
    },
    "soybean": {
        "emergence": (0.15, 0.25),
        "vegetative": (0.40, 0.65),
        "r1": (0.70, 0.85),
        "r2": (0.70, 0.85),
        "grain_fill": (0.55, 0.75),
        "senescence": (0.25, 0.40),
    },
}

# Base temperatures and GDD-to-stage thresholds.
CROP_GDD: dict[str, dict[str, Any]] = {
    "maize": {"tbase": 10.0, "topt": 30.0, "stages": {"emergence": 150, "vegetative": 400, "tasseling": 1100, "silking": 1300, "grain_fill": 1800, "senescence": 2400}},
    "rice": {"tbase": 10.0, "topt": 30.0, "stages": {"emergence": 150, "vegetative": 350, "heading": 900, "flowering": 1100, "grain_fill": 1600, "senescence": 2200}},
    "wheat": {"tbase": 5.0, "topt": 25.0, "stages": {"emergence": 200, "vegetative": 450, "heading": 1100, "flowering": 1400, "grain_fill": 1900, "senescence": 2400}},
    "soybean": {"tbase": 10.0, "topt": 30.0, "stages": {"emergence": 150, "vegetative": 350, "r1": 800, "r2": 1100, "grain_fill": 1800, "senescence": 2400}},
}


def growing_degree_days(daily_tmin: np.ndarray, daily_tmax: np.ndarray, tbase: float, top: float | None = None) -> np.ndarray:
    """Compute daily GDD using capped average temperature.

    GDD = max(0, ((Tmin + Tmax)/2 - Tbase)), with Tmax capped at Topt if provided.
    """
    tmax = np.asarray(daily_tmax, dtype=float)
    if top is not None:
        tmax = np.minimum(tmax, top)
    tmin = np.asarray(daily_tmin, dtype=float)
    avg = (tmin + tmax) / 2.0
    gdd = np.maximum(avg - tbase, 0.0)
    return gdd


def cumulative_gdd(daily_gdd: np.ndarray) -> np.ndarray:
    """Return cumulative GDD array."""
    return np.cumsum(np.asarray(daily_gdd, dtype=float))


def gdd_to_stage(crop: str, gdd_value: float) -> str:
    """Return the latest passed growth stage for a cumulative GDD value."""
    info = CROP_GDD.get(crop.lower())
    if info is None:
        return "unknown"
    last_stage = "emergence"
    for stage, threshold in sorted(info["stages"].items(), key=lambda kv: kv[1]):
        if gdd_value >= threshold:
            last_stage = stage
    return last_stage


def days_after_planting(planting_date: date, reference_date: date | None = None) -> int:
    """Days elapsed since planting."""
    if reference_date is None:
        reference_date = date.today()
    return (reference_date - planting_date).days


def estimate_stage_from_gdd(
    crop: str,
    planting_date: date,
    daily_tmin: list[float] | np.ndarray,
    daily_tmax: list[float] | np.ndarray,
    reference_date: date | None = None,
) -> str:
    """Infer growth stage from GDD accumulation since planting."""
    info = CROP_GDD.get(crop.lower())
    if info is None or reference_date is None:
        return "unknown"
    n_days = days_after_planting(planting_date, reference_date)
    n_days = min(n_days, len(daily_tmin))
    if n_days <= 0:
        return "emergence"
    gdd = growing_degree_days(daily_tmin[:n_days], daily_tmax[:n_days], info["tbase"], info["topt"])
    return gdd_to_stage(crop, float(np.sum(gdd)))


def expected_index_range(crop: str, stage: str | None, index_name: str = "ndvi") -> tuple[float, float] | None:
    """Return expected index range for a crop/stage, or None if unknown."""
    if stage is None:
        return None
    key = stage.lower().replace(" ", "_").replace("/", "_")
    table = PHENOLOGY_TABLE.get(crop.lower())
    if table is None:
        return None
    return table.get(key)


def index_deviation(
    observed: float, crop: str, stage: str | None, index_name: str = "ndvi"
) -> dict[str, Any]:
    """Compare observed index to expected phenology range."""
    expected = expected_index_range(crop, stage, index_name)
    if expected is None:
        return {"expected_range": None, "deviation": None, "status": "unknown"}
    lo, hi = expected
    mid = (lo + hi) / 2.0
    if observed < lo:
        status = "below_expected"
    elif observed > hi:
        status = "above_expected"
    else:
        status = "normal"
    return {
        "expected_range": expected,
        "deviation": float(observed - mid),
        "status": status,
    }

