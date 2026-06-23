"""Vegetation-index formulas.

All functions accept scalars or numpy arrays and return the same shape with NaN-safe
division. Formulas are cited in each docstring.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def _safe_divide(numerator: Any, denominator: Any, default: float = np.nan) -> Any:
    """Divide arrays/scalars with NaN where denominator is zero or invalid."""
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = numerator / denominator
    invalid = (denominator == 0) | np.isnan(denominator) | np.isnan(numerator)
    if np.any(invalid):
        result = np.where(invalid, default, result)
    return result


def ndvi(red: Any, nir: Any) -> Any:
    """Normalized Difference Vegetation Index.

    Rouse et al. (1974): (NIR - Red) / (NIR + Red).
    """
    return _safe_divide(nir - red, nir + red)


def evi(red: Any, nir: Any, blue: Any, canopy_bg_adjustment: float = 1.0, c1: float = 6.0, c2: float = 7.5, l: float = 1.0) -> Any:
    """Enhanced Vegetation Index (Huete et al. 2002).

    EVI = G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L).
    """
    numerator = canopy_bg_adjustment * (nir - red)
    denominator = nir + c1 * red - c2 * blue + l
    return _safe_divide(numerator, denominator)


def ndre(red_edge: Any, nir: Any) -> Any:
    """Normalized Difference Red Edge.

    (NIR - RedEdge) / (NIR + RedEdge). Sensitive to chlorophyll/N at high biomass.
    """
    return _safe_divide(nir - red_edge, nir + red_edge)


def gndvi(green: Any, nir: Any) -> Any:
    """Green Normalized Difference Vegetation Index.

    (NIR - Green) / (NIR + Green).
    """
    return _safe_divide(nir - green, nir + green)


def gci(green: Any, nir: Any) -> Any:
    """Green Chlorophyll Index.

    (NIR / Green) - 1.
    """
    return _safe_divide(nir, green, default=np.nan) - 1.0


def savi(red: Any, nir: Any, soil_factor: float = 0.5) -> Any:
    """Soil-Adjusted Vegetation Index.

    (1 + L) * (NIR - Red) / (NIR + Red + L), with L typically 0.5.
    """
    numerator = (1.0 + soil_factor) * (nir - red)
    denominator = nir + red + soil_factor
    return _safe_divide(numerator, denominator)


def msavi2(red: Any, nir: Any) -> Any:
    """Modified Soil-Adjusted Vegetation Index 2.

    0.5 * (2 * NIR + 1 - sqrt((2*NIR+1)^2 - 8*(NIR-Red))).
    """
    red = np.asarray(red, dtype=float)
    nir = np.asarray(nir, dtype=float)
    inner = (2.0 * nir + 1.0) ** 2.0 - 8.0 * (nir - red)
    inner = np.maximum(inner, 0.0)  # guard tiny negatives from floating noise
    return 0.5 * (2.0 * nir + 1.0 - np.sqrt(inner))


def rvsi(red: Any, green: Any, nir: Any) -> Any:
    """Red-Edge Vegetation Stress Index (simplified).

    ((NIR - Red) - (NIR - Green)) / (NIR - Red + NIR - Green).
    """
    return _safe_divide((nir - red) - (nir - green), (nir - red) + (nir - green))


def compute_indices(imagery: dict[str, Any]) -> dict[str, Any]:
    """Compute a standard set of indices from a band dictionary.

    Expected keys: red, green, blue, nir, red_edge (optional), swir1, swir2.
    Returns dict keyed by index name.
    """
    bands = {k: np.asarray(v, dtype=float) for k, v in imagery.items()}
    red = bands.get("red")
    green = bands.get("green")
    blue = bands.get("blue")
    nir = bands.get("nir")
    red_edge = bands.get("red_edge")

    out: dict[str, Any] = {}
    if red is not None and nir is not None:
        out["ndvi"] = ndvi(red, nir)
    if red is not None and green is not None and nir is not None:
        out["evi"] = evi(red, nir, green)
    if red_edge is not None and nir is not None:
        out["ndre"] = ndre(red_edge, nir)
    if green is not None and nir is not None:
        out["gndvi"] = gndvi(green, nir)
    if green is not None and nir is not None:
        out["gci"] = gci(green, nir)
    if red is not None and nir is not None:
        out["savi"] = savi(red, nir)
    if red is not None and nir is not None:
        out["msavi2"] = msavi2(red, nir)
    if red is not None and green is not None and nir is not None:
        out["rvsi"] = rvsi(red, green, nir)
    return out
