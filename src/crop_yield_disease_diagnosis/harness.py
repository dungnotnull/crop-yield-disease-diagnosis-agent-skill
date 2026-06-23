"""End-to-end crop analytics harness and quality-gate enforcement."""
from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np

from crop_yield_disease_diagnosis.data_sources import (
    estimate_data_quality,
    resolve_data_sources,
    select_primary_imagery,
)
from crop_yield_disease_diagnosis.diagnoser import differential_diagnosis
from crop_yield_disease_diagnosis.indices import compute_indices
from crop_yield_disease_diagnosis.phenology import estimate_stage_from_gdd, expected_index_range
from crop_yield_disease_diagnosis.recommendation import build_roadmap
from crop_yield_disease_diagnosis.scoring import score_health, score_yield
from crop_yield_disease_diagnosis.types import (
    ActionItem,
    AnalysisReport,
    DiagnosisCandidate,
    FieldProfile,
    FrameworkSelection,
    HealthScore,
    Imagery,
    IndexMap,
    StressZone,
    YieldForecast,
    numpy_to_python,
)


def _sanitize_imagery_bands(imagery: Imagery) -> dict[str, Any]:
    """Build a band dictionary from an Imagery object."""
    bands: dict[str, Any] = {}
    for key in ("red", "green", "blue", "nir", "red_edge", "swir1", "swir2"):
        val = getattr(imagery, key)
        if val is not None:
            bands[key] = np.asarray(val, dtype=float)
    return bands


def _segment_stress_zones(
    index_values: np.ndarray,
    index_name: str,
    n_zones: int = 3,
) -> list[StressZone]:
    """Segment an index array into vigor zones by percentile thresholds."""
    arr = np.asarray(index_values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return [
            StressZone(
                zone_id="Z1",
                label="unknown",
                area_fraction=1.0,
                mean_index=float("nan"),
                index_name=index_name,
                cause_hypotheses=["No valid index pixels"],
                priority=3,
            )
        ]

    p33, p67 = np.percentile(finite, [33, 67])
    total = finite.size
    labels = ["low", "medium", "high"]
    zones: list[StressZone] = []
    for idx, (lo, hi, label) in enumerate(
        [(-np.inf, p33, "low"), (p33, p67, "medium"), (p67, np.inf, "high")]
    ):
        mask = (arr >= lo) & (arr < hi) & np.isfinite(arr)
        count = int(np.sum(mask))
        if count == 0:
            continue
        zone_arr = arr[mask]
        hypotheses: list[str] = []
        if label == "low":
            hypotheses = ["water stress", "nutrient deficiency", "disease/pest", "compaction"]
        elif label == "medium":
            hypotheses = ["moderate stress or normal variation"]
        else:
            hypotheses = ["vigorous canopy"]
        zones.append(
            StressZone(
                zone_id=f"Z{idx + 1}",
                label=label,  # type: ignore[arg-type]
                area_fraction=round(count / total, 4),
                mean_index=round(float(np.mean(zone_arr)), 3),
                index_name=index_name,
                cause_hypotheses=hypotheses,
                priority=1 if label == "low" else (5 if label == "high" else 3),
            )
        )
    return zones


def select_framework(profile: FieldProfile) -> FrameworkSelection:
    """Choose indices and crop model for the field profile."""
    crop = profile.crop.lower()
    stage = (profile.stage or "").lower()

    if crop in {"maize", "rice", "wheat", "soybean"}:
        indices = ["ndvi", "evi", "ndre"]
        if stage in {"emergence", "early vegetative"}:
            indices = ["ndvi", "savi"]
        elif stage in {"grain_fill", "senescence"}:
            indices = ["ndvi", "evi"]
    else:
        indices = ["ndvi", "evi"]

    # Prefer AquaCrop when water-driven; DSSAT for process; empirical fallback.
    if stage in {"tasseling", "silking", "heading", "flowering", "grain_fill"} and crop in {"maize", "rice", "wheat"}:
        crop_model = "aquacrop"
        reason = "water-limited yield critical at reproductive stage"
    elif crop in {"maize", "wheat", "soybean"}:
        crop_model = "dssat"
        reason = "process-based growth model available"
    else:
        crop_model = "empirical_regression"
        reason = "default fallback when external model unavailable"

    phenology_ref = f"{crop}_gdd_phenology"
    justification = (
        f"Indices {indices} selected for {crop} at {stage or 'unknown stage'}; "
        f"model {crop_model} selected because {reason}."
    )
    return FrameworkSelection(
        indices=indices,
        crop_model=crop_model,
        phenology_reference=phenology_ref,
        justification=justification,
    )


def _infer_stage_if_missing(profile: FieldProfile, reference_date: date | None = None) -> FieldProfile:
    """Fill in missing growth stage from GDD if weather data is present."""
    if profile.stage:
        return profile
    tmin = profile.weather.get("daily_tmin")
    tmax = profile.weather.get("daily_tmax")
    if profile.planting_date and tmin is not None and tmax is not None:
        inferred = estimate_stage_from_gdd(
            profile.crop,
            profile.planting_date,
            tmin,
            tmax,
            reference_date,
        )
        return profile.model_copy(update={"stage": inferred})
    return profile.model_copy(update={"stage": "unknown"})


def run_analysis(
    profile: FieldProfile,
    reference_date: date | None = None,
) -> AnalysisReport:
    """Run the full crop analytics pipeline and return a report."""
    ref = reference_date or date.today()
    profile = _infer_stage_if_missing(profile, ref)

    framework = select_framework(profile)
    resolved = resolve_data_sources(profile.data_sources, profile.imagery, ref)

    index_maps: list[IndexMap] = []
    stress_zones: list[StressZone] = []
    disease_differential: list[DiagnosisCandidate] = []
    yield_forecast_obj: YieldForecast | None = None
    health_score: HealthScore | None = None
    roadmap: list[ActionItem] = []

    primary_img = select_primary_imagery(resolved["usable_imagery"])
    if primary_img:
        bands = _sanitize_imagery_bands(primary_img)
        computed = compute_indices(bands)
        for name, values in computed.items():
            if name not in framework.indices:
                continue
            arr = np.asarray(values, dtype=float)
            index_maps.append(
                IndexMap(
                    name=name,
                    sensor=primary_img.sensor,
                    acquisition_date=primary_img.acquisition_date,
                    values=numpy_to_python(values),
                    mean=round(float(np.nanmean(arr)), 3),
                    std=round(float(np.nanstd(arr)), 3),
                    valid_fraction=round(float(np.sum(np.isfinite(arr)) / arr.size), 3) if arr.size else 0.0,
                )
            )
            if name == "ndvi":
                stress_zones = _segment_stress_zones(arr, name)

    # Derive spectral clues from index maps.
    spectral_clues: list[str] = []
    for im in index_maps:
        if im.mean is not None:
            expected = expected_index_range(profile.crop, profile.stage, im.name)
            if expected and im.mean < expected[0]:
                spectral_clues.append(f"{im.name} below expected")
            elif expected and im.mean > expected[1]:
                spectral_clues.append(f"{im.name} above expected")

    disease_differential = differential_diagnosis(
        symptoms=profile.symptoms,
        spectral_clues=spectral_clues,
        crop=profile.crop,
        weather=profile.weather,
        top_k=5,
    )

    nan_fraction = 0.0
    if index_maps:
        arr = np.asarray(index_maps[0].values, dtype=float)
        nan_fraction = float(np.sum(~np.isfinite(arr)) / arr.size) if arr.size else 0.0
    data_quality = estimate_data_quality(resolved, nan_fraction)

    index_values = {im.name: im.values for im in index_maps}
    yield_forecast_obj = score_yield(
        profile, index_values, stress_zones, data_quality, prefer_model=framework.crop_model
    )
    health_score = score_health(
        profile, index_values, stress_zones, disease_differential, data_quality
    )

    top_diagnosis = disease_differential[0] if disease_differential else None
    roadmap = build_roadmap(stress_zones, top_diagnosis, crop=profile.crop)

    # Confidence gates
    gates: dict[str, bool] = {
        "data_vintage_ok": not resolved.get("stale", True),
        "index_reliability_ok": nan_fraction <= 0.10,
        "phenology_match_ok": profile.stage is not None and profile.stage != "unknown",
        "diagnosis_confidence_ok": (not disease_differential) or disease_differential[0].confidence <= 0.85,
        "yield_uncertainty_ok": (
            yield_forecast_obj.uncertainty_band_t_ha is not None
            and yield_forecast_obj.uncertainty_band_t_ha[1] - yield_forecast_obj.uncertainty_band_t_ha[0]
            <= 2 * (yield_forecast_obj.estimated_yield_t_ha or 0.0) * 0.25
        ),
        "ipm_ordering_ok": all(a.ipm_tier != "chemical" or a.economic_threshold_note for a in roadmap),
    }

    return AnalysisReport(
        field_profile=profile,
        framework=framework,
        index_maps=index_maps,
        stress_zones=stress_zones,
        disease_differential=disease_differential,
        yield_forecast=yield_forecast_obj,
        health_score=health_score,
        roadmap=roadmap,
        data_vintage_notes=resolved["notes"],
        confidence_gates=gates,
        fallback_used=resolved["fallback_used"],
    )
