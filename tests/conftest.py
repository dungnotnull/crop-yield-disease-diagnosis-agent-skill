"""Shared fixtures for the crop analytics test suite."""
from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from crop_yield_disease_diagnosis.types import FieldProfile, Imagery


@pytest.fixture
def base_maize_profile() -> FieldProfile:
    return FieldProfile(
        crop="maize",
        variety="Pioneer P1197",
        stage="tasseling",
        location=(41.66, -93.47),
        area_ha=45.0,
        planting_date=date(2026, 5, 1),
        data_sources=["sentinel_2", "weather_station"],
        goal="yield_forecast",
    )


@pytest.fixture
def base_rice_profile() -> FieldProfile:
    return FieldProfile(
        crop="rice",
        variety="IR64",
        stage="heading",
        location=(13.0, 123.0),
        area_ha=10.0,
        planting_date=date(2026, 2, 1),
        data_sources=["field_observation"],
        goal="disease_diagnosis",
    )


@pytest.fixture
def sentinel_imagery() -> Imagery:
    rng = np.random.default_rng(42)
    rows, cols = 120, 120
    red = np.clip(rng.normal(0.12, 0.03, (rows, cols)), 0.01, 0.5)
    green = np.clip(rng.normal(0.25, 0.04, (rows, cols)), 0.05, 0.6)
    blue = np.clip(rng.normal(0.08, 0.02, (rows, cols)), 0.01, 0.4)
    nir = np.clip(rng.normal(0.55, 0.08, (rows, cols)), 0.05, 0.9)
    red_edge = np.clip(rng.normal(0.45, 0.07, (rows, cols)), 0.05, 0.8)
    # Create a low-vigor patch.
    nir[40:60, 40:60] *= 0.5
    red[40:60, 40:60] *= 1.3
    return Imagery(
        sensor="Sentinel-2",
        acquisition_date=date(2026, 7, 15),
        resolution_m=10.0,
        cloud_cover_percent=5.0,
        red=red,
        green=green,
        blue=blue,
        nir=nir,
        red_edge=red_edge,
    )


@pytest.fixture
def wheat_profile() -> FieldProfile:
    return FieldProfile(
        crop="wheat",
        variety="Hard Red Winter",
        stage="heading",
        location=(38.0, -97.0),
        area_ha=100.0,
        planting_date=date(2025, 10, 15),
        data_sources=["sentinel_2", "soil_test", "weather_station"],
        goal="yield_forecast",
        weather={"rainfall_mm": 120, "temperature_c": 22},
    )
