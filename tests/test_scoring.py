"""Tests for yield/health scoring engine."""
from __future__ import annotations

from datetime import date

from crop_yield_disease_diagnosis.crop_model import EmpiricalRegressionBackend
from crop_yield_disease_diagnosis.scoring import score_health, score_yield
from crop_yield_disease_diagnosis.types import DiagnosisCandidate, FieldProfile, StressZone


def test_empirical_regression_yield_band() -> None:
    backend = EmpiricalRegressionBackend()
    profile = FieldProfile(crop="wheat", planting_date=date(2025, 10, 15), data_sources=[])
    forecast = backend.run(
        profile,
        {
            "ndvi_mean": 0.60,
            "evi_mean": 0.50,
            "ndre_mean": 0.45,
            "data_quality": 0.85,
            "stress_fraction": 0.10,
        },
    )
    assert forecast.estimated_yield_t_ha is not None
    assert forecast.uncertainty_band_t_ha is not None
    low, high = forecast.uncertainty_band_t_ha
    assert low <= forecast.estimated_yield_t_ha <= high
    assert 0.0 < forecast.confidence <= 0.95


def test_score_yield_includes_band() -> None:
    profile = FieldProfile(crop="wheat", planting_date=date(2025, 10, 15), data_sources=[])
    index_values = {"ndvi": 0.60, "evi": 0.50, "ndre": 0.45}
    zones = [StressZone(zone_id="Z1", label="medium", area_fraction=1.0, mean_index=0.5, index_name="ndvi")]
    forecast = score_yield(profile, index_values, zones, data_quality=0.85, prefer_model="aquacrop")
    assert forecast.uncertainty_band_t_ha is not None
    assert "Backend selection" in forecast.data_vintage_note


def test_score_health_bounds() -> None:
    profile = FieldProfile(crop="maize", planting_date=date(2026, 5, 1), data_sources=[])
    index_values = {"ndvi": 0.7, "evi": 0.6, "ndre": 0.55}
    zones = [StressZone(zone_id="Z1", label="high", area_fraction=1.0, mean_index=0.7, index_name="ndvi")]
    diagnosis = DiagnosisCandidate(name="Water stress", kind="abiotic", confidence=0.6)
    health = score_health(profile, index_values, zones, [diagnosis], data_quality=0.9)
    assert 0 <= health.score <= 100
    assert health.confidence > 0
