"""Tests for vegetation-index formulas."""
from __future__ import annotations

import numpy as np
import pytest

from crop_yield_disease_diagnosis import indices


def test_ndvi_scalar() -> None:
    assert indices.ndvi(0.1, 0.5) == pytest.approx((0.5 - 0.1) / (0.5 + 0.1))


def test_ndvi_zero_denominator() -> None:
    assert np.isnan(indices.ndvi(0.0, 0.0))


def test_evi() -> None:
    assert indices.evi(0.1, 0.6, 0.08) == pytest.approx(
        1.0 * (0.6 - 0.1) / (0.6 + 6.0 * 0.1 - 7.5 * 0.08 + 1.0)
    )


def test_ndre() -> None:
    assert indices.ndre(0.4, 0.6) == pytest.approx((0.6 - 0.4) / (0.6 + 0.4))


def test_gndvi() -> None:
    assert indices.gndvi(0.2, 0.6) == pytest.approx((0.6 - 0.2) / (0.6 + 0.2))


def test_savi() -> None:
    assert indices.savi(0.1, 0.5, soil_factor=0.5) == pytest.approx(
        1.5 * (0.5 - 0.1) / (0.5 + 0.1 + 0.5)
    )


def test_msavi2() -> None:
    result = indices.msavi2(0.1, 0.5)
    expected = 0.5 * (2.0 * 0.5 + 1.0 - np.sqrt((2.0 * 0.5 + 1.0) ** 2 - 8.0 * (0.5 - 0.1)))
    assert result == pytest.approx(expected)


def test_compute_indices() -> None:
    bands = {
        "red": 0.1,
        "green": 0.25,
        "blue": 0.08,
        "nir": 0.6,
        "red_edge": 0.45,
    }
    result = indices.compute_indices(bands)
    assert set(result.keys()) >= {"ndvi", "evi", "ndre", "gndvi", "gci", "savi", "msavi2", "rvsi"}
    assert result["ndvi"] == pytest.approx((0.6 - 0.1) / (0.6 + 0.1))


def test_ndvi_array() -> None:
    red = np.array([0.1, 0.2, 0.0])
    nir = np.array([0.5, 0.6, 0.0])
    result = indices.ndvi(red, nir)
    np.testing.assert_array_almost_equal(
        result, [(0.5 - 0.1) / 0.6, (0.6 - 0.2) / 0.8, np.nan], decimal=6
    )
