"""Crop-model backend interface, empirical regression fallback, and wiring for
DSSAT/AquaCrop executables.

External model binaries are *not* executed in this package. The engine uses a
production-ready empirical index-yield regression when no external backend is
available, and provides adapters that external pipelines can call.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from crop_yield_disease_diagnosis.types import FieldProfile, YieldForecast


class CropModelBackend(ABC):
    """Abstract crop-model backend."""

    name: str = "abstract"

    @abstractmethod
    def available(self) -> bool:
        """Return True if this backend can run in the current environment."""
        raise NotImplementedError

    @abstractmethod
    def run(self, profile: FieldProfile, inputs: dict[str, Any]) -> YieldForecast:
        """Run the model and return a YieldForecast."""
        raise NotImplementedError


class DSSATBackend(CropModelBackend):
    """Adapter for DSSAT executable.

    Availability requires DSSATSM.EXE / dscsm048 on PATH or configured path.
    The adapter builds input files but does not run them unless available.
    """

    name = "dssat"

    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable or os.environ.get("DSSAT_EXECUTABLE", "dscsm048")

    def available(self) -> bool:
        for ext in ("", ".exe"):
            for path in os.environ.get("PATH", "").split(os.pathsep):
                candidate = os.path.join(path, self.executable + ext)
                if os.path.isfile(candidate):
                    return True
        return False

    def run(self, profile: FieldProfile, inputs: dict[str, Any]) -> YieldForecast:
        if not self.available():
            raise RuntimeError("DSSAT executable not available")
        # Production wiring: create input deck, run, parse output.
        raise NotImplementedError("DSSAT execution is not implemented in this resource-saving build")


class AquaCropBackend(CropModelBackend):
    """Adapter for FAO AquaCrop executable.

    Availability requires AquaCrop v7.x executable on PATH or configured path.
    """

    name = "aquacrop"

    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable or os.environ.get("AQUACROP_EXECUTABLE", "AquaCrop")

    def available(self) -> bool:
        for ext in ("", ".exe"):
            for path in os.environ.get("PATH", "").split(os.pathsep):
                candidate = os.path.join(path, self.executable + ext)
                if os.path.isfile(candidate):
                    return True
        return False

    def run(self, profile: FieldProfile, inputs: dict[str, Any]) -> YieldForecast:
        if not self.available():
            raise RuntimeError("AquaCrop executable not available")
        raise NotImplementedError("AquaCrop execution is not implemented in this resource-saving build")


class EmpiricalRegressionBackend(CropModelBackend):
    """Index-to-yield regression with uncertainty band.

    Parameters are calibrated per crop from literature/ground-truth data.
    The default parameters are conservative fallbacks; override via inputs.
    """

    name = "empirical_regression"

    # crop: (intercept, ndvi_coef, evi_coef, ndre_coef, rmse)
    DEFAULT_PARAMS: dict[str, tuple[float, float, float, float, float]] = {
        "maize": (2.0, 8.0, 6.0, 5.0, 1.2),
        "rice": (1.5, 7.5, 6.0, 4.5, 1.0),
        "wheat": (1.8, 7.0, 5.5, 4.0, 1.1),
        "soybean": (1.2, 7.5, 6.0, 4.0, 0.9),
    }

    def available(self) -> bool:
        return True

    def run(self, profile: FieldProfile, inputs: dict[str, Any]) -> YieldForecast:
        crop = profile.crop.lower()
        params = inputs.get("params") or self.DEFAULT_PARAMS.get(crop, (1.5, 7.0, 5.0, 4.0, 1.5))
        intercept, ndvi_coef, evi_coef, ndre_coef, rmse = params

        ndvi_mean = float(inputs.get("ndvi_mean", 0.5))
        evi_mean = float(inputs.get("evi_mean", 0.4))
        ndre_mean = float(inputs.get("ndre_mean", 0.35))
        data_quality = float(inputs.get("data_quality", 0.7))  # 0-1
        stress_fraction = float(inputs.get("stress_fraction", 0.0))

        yield_est = (
            intercept
            + ndvi_coef * ndvi_mean
            + evi_coef * evi_mean
            + ndre_coef * ndre_mean
        )
        yield_est = max(0.1, yield_est)

        # Widen uncertainty with data quality and stress.
        uncertainty = rmse * (1.0 + (1.0 - data_quality) * 1.5 + stress_fraction)
        confidence = max(0.1, min(0.95, data_quality * (1.0 - stress_fraction * 0.5)))

        low = max(0.0, yield_est - uncertainty)
        high = yield_est + uncertainty
        note = (
            f"Empirical regression (intercept={intercept}, ndvi_coef={ndvi_coef}). "
            f"Data quality {data_quality:.2f}; stress fraction {stress_fraction:.2f}."
        )
        return YieldForecast(
            crop=profile.crop,
            estimated_yield_t_ha=round(yield_est, 2),
            uncertainty_band_t_ha=(round(low, 2), round(high, 2)),
            confidence=round(confidence, 2),
            method="empirical_index_yield_regression",
            sensitivities=["Rainfall after {date} not yet incorporated".format(date=profile.planting_date or "planting")],
            data_vintage_note=note,
        )


def select_backend(profile: FieldProfile, prefer: str | None = None) -> tuple[CropModelBackend, str]:
    """Select the best available backend and return (backend, reason)."""
    candidates: list[CropModelBackend] = [
        AquaCropBackend(),
        DSSATBackend(),
        EmpiricalRegressionBackend(),
    ]
    if prefer:
        preferred_name = prefer.lower()
        for c in candidates:
            if c.name == preferred_name and c.available():
                return c, f"preferred_{c.name}_available"
    for c in candidates:
        if c.available():
            return c, f"auto_selected_{c.name}"
    raise RuntimeError("No crop-model backend available")


def yield_forecast(
    profile: FieldProfile,
    inputs: dict[str, Any],
    prefer: str | None = None,
) -> YieldForecast:
    """Dispatch to the best available crop-model backend."""
    backend, reason = select_backend(profile, prefer)
    forecast = backend.run(profile, inputs)
    forecast.data_vintage_note = f"{forecast.data_vintage_note} Backend selection: {reason}."
    return forecast
