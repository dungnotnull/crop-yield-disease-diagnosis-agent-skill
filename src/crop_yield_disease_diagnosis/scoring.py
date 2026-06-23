"""Yield forecast and crop-health scoring engine."""
from __future__ import annotations

from typing import Any

import numpy as np

from crop_yield_disease_diagnosis.crop_model import yield_forecast as crop_yield_forecast
from crop_yield_disease_diagnosis.phenology import index_deviation
from crop_yield_disease_diagnosis.types import DiagnosisCandidate, FieldProfile, HealthScore, StressZone, YieldForecast


def _to_scalar(values: Any) -> float:
    """Convert scalar or array to a single float."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 1:
        return float(arr.item())
    return float(np.nanmean(arr))


def _valid_fraction(values: Any) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.sum(np.isfinite(arr)) / arr.size)


def score_yield(
    profile: FieldProfile,
    index_values: dict[str, Any],
    stress_zones: list[StressZone],
    data_quality: float,
    prefer_model: str | None = None,
) -> YieldForecast:
    """Dispatch to crop model and annotate with data-vintage note."""
    inputs: dict[str, Any] = {
        "ndvi_mean": _to_scalar(index_values.get("ndvi", 0.5)),
        "evi_mean": _to_scalar(index_values.get("evi", 0.4)),
        "ndre_mean": _to_scalar(index_values.get("ndre", 0.35)),
        "data_quality": data_quality,
        "stress_fraction": sum(z.area_fraction for z in stress_zones if z.label in {"low", "stressed"}),
    }
    return crop_yield_forecast(profile, inputs, prefer=prefer_model)


def score_health(
    profile: FieldProfile,
    index_values: dict[str, Any],
    stress_zones: list[StressZone],
    disease_differential: list[DiagnosisCandidate],
    data_quality: float,
) -> HealthScore:
    """Compute an overall crop-health score (0-100)."""
    ndvi = _to_scalar(index_values.get("ndvi", 0.5))
    evi = _to_scalar(index_values.get("evi", 0.4))
    ndre = _to_scalar(index_values.get("ndre", 0.35))

    vigor_component = min(100.0, max(0.0, 100.0 * ((ndvi + evi + ndre) / 1.8)))

    stressed_fraction = sum(z.area_fraction for z in stress_zones if z.label in {"low", "stressed"})
    stress_component = max(0.0, 100.0 - 120.0 * stressed_fraction)

    disease_pressure = 0.0
    if disease_differential:
        top = disease_differential[0]
        if top.kind == "biotic":
            disease_pressure = top.confidence * 50.0
        elif top.kind == "abiotic" and top.name != "Nitrogen deficiency":
            disease_pressure = top.confidence * 25.0
    disease_component = max(0.0, 100.0 - disease_pressure)

    score = 0.35 * vigor_component + 0.35 * stress_component + 0.30 * disease_component
    confidence = max(0.1, min(0.95, data_quality * _valid_fraction(index_values.get("ndvi", []))))

    return HealthScore(
        score=int(round(score)),
        vigor_component=round(vigor_component, 2),
        stress_component=round(stress_component, 2),
        disease_component=round(disease_component, 2),
        confidence=round(confidence, 2),
    )


def evaluate_index_against_phenology(
    profile: FieldProfile, index_name: str, index_values: Any
) -> dict[str, Any]:
    """Convenience wrapper returning phenology deviation."""
    obs = _to_scalar(index_values)
    return index_deviation(obs, profile.crop, profile.stage, index_name)
