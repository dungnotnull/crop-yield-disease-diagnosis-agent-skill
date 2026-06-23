"""Tests for precision action recommendation engine."""
from __future__ import annotations

from crop_yield_disease_diagnosis.recommendation import build_roadmap
from crop_yield_disease_diagnosis.types import DiagnosisCandidate, StressZone


def test_variable_rate_n_zones() -> None:
    zones = [
        StressZone(zone_id="Z1", label="low", area_fraction=0.2, mean_index=0.25, index_name="ndvi", cause_hypotheses=["N deficiency"], priority=1),
        StressZone(zone_id="Z2", label="medium", area_fraction=0.5, mean_index=0.45, index_name="ndvi", priority=3),
        StressZone(zone_id="Z3", label="high", area_fraction=0.3, mean_index=0.75, index_name="ndvi", priority=5),
    ]
    diagnosis = DiagnosisCandidate(name="Nitrogen deficiency", kind="abiotic", confidence=0.8, ipm_actions=["Soil nitrate test", "Sidedress variable-rate N"])
    roadmap = build_roadmap(zones, diagnosis, crop="maize")
    assert len(roadmap) >= 3
    z1_action = next((a for a in roadmap if a.zone_id == "Z1"), None)
    assert z1_action is not None
    assert z1_action.input_rate_kg_ha is not None
    assert z1_action.ipm_tier == "cultural"
    assert z1_action.priority <= 2


def test_ipm_ordering_biological_before_chemical() -> None:
    zones = [
        StressZone(zone_id="Z1", label="low", area_fraction=0.3, mean_index=0.25, index_name="ndvi", cause_hypotheses=["disease"], priority=1),
    ]
    diagnosis = DiagnosisCandidate(
        name="Gray leaf spot",
        kind="biotic",
        confidence=0.8,
        ipm_actions=["Rotate crops", "Tillage", "Fungicide if wet"],
    )
    roadmap = build_roadmap(zones, diagnosis, crop="maize")
    tiers = [a.ipm_tier for a in roadmap]
    # Chemical should not be the first or only tier.
    assert tiers[0] in {"cultural", "biological", "monitoring"}
