"""Integration tests for the end-to-end harness."""
from __future__ import annotations

from datetime import date

import numpy as np

from crop_yield_disease_diagnosis.harness import run_analysis
from crop_yield_disease_diagnosis.types import FieldProfile, Imagery


def test_maize_ndvi_interpretation(base_maize_profile: FieldProfile, sentinel_imagery: Imagery) -> None:
    profile = base_maize_profile.model_copy(update={"imagery": [sentinel_imagery]})
    report = run_analysis(profile, reference_date=date(2026, 7, 20))
    assert report.framework.crop_model == "aquacrop"
    assert len(report.index_maps) >= 1
    ndvi_map = next(m for m in report.index_maps if m.name == "ndvi")
    assert ndvi_map.sensor == "Sentinel-2"
    assert ndvi_map.acquisition_date == date(2026, 7, 15)
    assert len(report.stress_zones) >= 2
    low_zone = next((z for z in report.stress_zones if z.label == "low"), None)
    assert low_zone is not None
    assert low_zone.area_fraction > 0
    assert report.yield_forecast is not None
    assert report.yield_forecast.uncertainty_band_t_ha is not None


def test_imagery_unavailable_fallback(base_maize_profile: FieldProfile) -> None:
    profile = base_maize_profile.model_copy(
        update={"data_sources": ["soil_test", "weather_station"], "imagery": []}
    )
    report = run_analysis(profile, reference_date=date(2026, 7, 20))
    assert report.fallback_used is True
    assert any("field-data-only" in note.lower() for note in report.data_vintage_notes)
    assert report.yield_forecast is not None
    assert report.yield_forecast.confidence <= 0.65


def test_yield_forecast_with_band(wheat_profile: FieldProfile) -> None:
    report = run_analysis(wheat_profile, reference_date=date(2026, 5, 1))
    assert report.yield_forecast is not None
    assert report.yield_forecast.uncertainty_band_t_ha is not None
    assert len(report.yield_forecast.sensitivities) >= 1
    assert report.health_score is not None
    assert 0 <= report.health_score.score <= 100


def test_abiotic_vs_biotic_call() -> None:
    profile = FieldProfile(
        crop="maize",
        stage="vegetative",
        location=(0.0, 0.0),
        area_ha=5.0,
        planting_date=date(2026, 5, 1),
        data_sources=["field_observation"],
        symptoms=["uniform yellowing across whole field after cold snap"],
    )
    report = run_analysis(profile)
    assert report.disease_differential
    top = report.disease_differential[0]
    assert top.kind == "abiotic"
    # Ensure no chemical action appears at top priority.
    if report.roadmap:
        assert report.roadmap[0].ipm_tier != "chemical"
