"""Pydantic domain models for the crop analytics engine."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, Field, field_validator, model_validator


class DataSource(str, Enum):
    """Recognized data sources for a field analysis."""

    SENTINEL_2 = "sentinel_2"
    LANDSAT = "landsat"
    DRONE = "drone"
    WEATHER_STATION = "weather_station"
    SOIL_TEST = "soil_test"
    FIELD_OBSERVATION = "field_observation"


class Imagery(BaseModel):
    """A satellite or drone image acquisition."""

    sensor: str = Field(..., description="Sensor name, e.g. Sentinel-2, MicaSense RedEdge.")
    acquisition_date: date
    bands: dict[str, Any] = Field(default_factory=dict)
    cloud_cover_percent: float = Field(0.0, ge=0.0, le=100.0)
    resolution_m: float = Field(..., gt=0.0)
    red: Any | None = None
    green: Any | None = None
    blue: Any | None = None
    nir: Any | None = None
    red_edge: Any | None = None
    swir1: Any | None = None
    swir2: Any | None = None

    @field_validator("cloud_cover_percent")
    @classmethod
    def _cloud_cover_range(cls, v: float) -> float:
        if not 0.0 <= v <= 100.0:
            raise ValueError("cloud_cover_percent must be between 0 and 100")
        return v


class FieldProfile(BaseModel):
    """Agronomic context captured by the requirements-gatherer stage."""

    crop: str = Field(..., min_length=1)
    variety: str = ""
    stage: str | None = None
    location: tuple[float, float] | None = None
    area_ha: float = Field(0.0, ge=0.0)
    planting_date: date | None = None
    data_sources: list[str] = Field(default_factory=list)
    goal: str = ""
    soil_n_pk: dict[str, float | None] = Field(default_factory=dict)
    weather: dict[str, Any] = Field(default_factory=dict)
    symptoms: list[str] = Field(default_factory=list)
    imagery: list[Imagery] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def _ensure_location_tuple(self) -> "FieldProfile":
        loc = self.location
        if loc is not None and len(loc) != 2:
            raise ValueError("location must be a (lat, lon) tuple")
        return self


class IndexMap(BaseModel):
    """Computed vegetation index values and metadata."""

    name: str
    sensor: str
    acquisition_date: date
    values: Any = Field(..., description="Scalar, list, or numpy array of index values.")
    mean: float | None = None
    std: float | None = None
    valid_fraction: float | None = Field(None, ge=0.0, le=1.0)
    histogram: dict[str, int | float] | None = None


class StressZone(BaseModel):
    """A spatial zone with similar crop health status."""

    zone_id: str
    label: Literal["high", "medium", "low", "stressed", "unknown"]
    area_fraction: float = Field(..., ge=0.0, le=1.0)
    mean_index: float
    index_name: str
    cause_hypotheses: list[str] = Field(default_factory=list)
    priority: int = Field(1, ge=1, le=5)


class DiagnosisCandidate(BaseModel):
    """A single item in a disease differential diagnosis."""

    name: str
    kind: Literal["biotic", "abiotic", "unknown"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    conducive_conditions: list[str] = Field(default_factory=list)
    confirm_step: str = ""
    ipm_actions: list[str] = Field(default_factory=list)


class YieldForecast(BaseModel):
    """Model-based yield forecast with uncertainty band."""

    crop: str
    estimated_yield_t_ha: float | None = None
    uncertainty_band_t_ha: tuple[float, float] | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    method: str
    sensitivities: list[str] = Field(default_factory=list)
    data_vintage_note: str = ""


class HealthScore(BaseModel):
    """Overall crop-health score and breakdown."""

    score: int = Field(..., ge=0, le=100)
    vigor_component: float = Field(..., ge=0.0, le=100.0)
    stress_component: float = Field(..., ge=0.0, le=100.0)
    disease_component: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class FrameworkSelection(BaseModel):
    """Analytical methods chosen for a given field profile."""

    indices: list[str]
    crop_model: str
    phenology_reference: str
    justification: str


class ActionItem(BaseModel):
    """One precision-agriculture recommendation."""

    zone_id: str
    issue: str
    action: str
    input_rate_kg_ha: float | None = None
    irrigation_mm: float | None = None
    ipm_tier: Literal["cultural", "biological", "chemical", "monitoring"]
    timing: str
    priority: int = Field(..., ge=1, le=5)
    economic_threshold_note: str = ""


class AnalysisReport(BaseModel):
    """Final deliverable of the crop analytics harness."""

    field_profile: FieldProfile
    framework: FrameworkSelection
    index_maps: list[IndexMap] = Field(default_factory=list)
    stress_zones: list[StressZone] = Field(default_factory=list)
    disease_differential: list[DiagnosisCandidate] = Field(default_factory=list)
    yield_forecast: YieldForecast | None = None
    health_score: HealthScore | None = None
    roadmap: list[ActionItem] = Field(default_factory=list)
    data_vintage_notes: list[str] = Field(default_factory=list)
    confidence_gates: dict[str, bool] = Field(default_factory=dict)
    fallback_used: bool = False


def numpy_to_python(obj: Any) -> Any:
    """Recursively convert numpy scalars/arrays to plain Python types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, dict):
        return {k: numpy_to_python(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [numpy_to_python(v) for v in obj]
    return obj
