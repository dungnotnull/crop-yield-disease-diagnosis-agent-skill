"""Tests for phenology helpers."""
from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from crop_yield_disease_diagnosis import phenology


def test_growing_degree_days() -> None:
    tmin = np.array([10.0, 12.0, 14.0])
    tmax = np.array([20.0, 22.0, 24.0])
    gdd = phenology.growing_degree_days(tmin, tmax, tbase=10.0)
    expected = np.array([5.0, 7.0, 9.0])
    np.testing.assert_array_almost_equal(gdd, expected)


def test_cumulative_gdd() -> None:
    assert phenology.cumulative_gdd(np.array([5, 7, 9])).tolist() == [5, 12, 21]


def test_gdd_to_stage_maize() -> None:
    assert phenology.gdd_to_stage("maize", 200) == "emergence"
    assert phenology.gdd_to_stage("maize", 1200) == "tasseling"
    assert phenology.gdd_to_stage("maize", 2000) == "grain_fill"


def test_expected_index_range() -> None:
    assert phenology.expected_index_range("maize", "tasseling") == (0.70, 0.85)


def test_index_deviation_normal() -> None:
    dev = phenology.index_deviation(0.78, "maize", "tasseling")
    assert dev["status"] == "normal"


def test_index_deviation_below() -> None:
    dev = phenology.index_deviation(0.50, "maize", "tasseling")
    assert dev["status"] == "below_expected"


def test_estimate_stage_from_gdd() -> None:
    tmin = [10.0] * 60
    tmax = [25.0] * 60
    inferred = phenology.estimate_stage_from_gdd(
        "maize", date(2026, 5, 1), tmin, tmax, reference_date=date(2026, 6, 30)
    )
    assert inferred in {"vegetative", "tasseling"}
