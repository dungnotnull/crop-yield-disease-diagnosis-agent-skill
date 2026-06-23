"""Precision fertilization, irrigation, and IPM recommendation engine."""
from __future__ import annotations

from crop_yield_disease_diagnosis.types import ActionItem, DiagnosisCandidate, StressZone


def _zone_issue(zone: StressZone, diagnosis: DiagnosisCandidate | None) -> tuple[str, str, list[str]]:
    """Map a stress zone to an issue label and IPM actions."""
    if zone.label in {"low", "stressed"}:
        if diagnosis and "nitrogen" in diagnosis.name.lower():
            return "N deficiency", "cultural", ["Soil/tissue N test", "Sidedress variable-rate N"]
        if diagnosis and "water" in diagnosis.name.lower():
            return "Water stress", "cultural", ["Soil moisture check", "Irrigate priority zones"]
        if diagnosis and diagnosis.kind == "biotic":
            return diagnosis.name, "biological", diagnosis.ipm_actions[:2]
        return "Low vigor (unspecified)", "monitoring", ["Scout to confirm cause", "Resample zone in 3-5 days"]
    return "Vigorous zone", "monitoring", ["Maintain current management; monitor"]


def build_roadmap(
    zones: list[StressZone],
    diagnosis: DiagnosisCandidate | None = None,
    crop: str = "",
) -> list[ActionItem]:
    """Generate prioritized, zone-specific action items.

    IPM ordering: cultural → biological → chemical (with threshold note).
    """
    actions: list[ActionItem] = []

    # Zone-specific actions
    for zone in sorted(zones, key=lambda z: z.priority, reverse=False):
        issue, tier, notes = _zone_issue(zone, diagnosis)
        if zone.label in {"high", "medium", "vigorous"}:
            actions.append(
                ActionItem(
                    zone_id=zone.zone_id,
                    issue="Vigorous zone",
                    action="Maintain current practice; use as reference for variable-rate decisions",
                    ipm_tier="monitoring",
                    timing="Ongoing",
                    priority=5,
                    economic_threshold_note="No action needed while vigor remains above field average",
                )
            )
            continue

        # Low/stressed zones: derive corrective action.
        if "N deficiency" in issue:
            action = f"Sidedress N at 40–80 kg N/ha in zone {zone.zone_id}"
            input_rate = 60.0
        elif "Water stress" in issue:
            action = f"Irrigate {zone.zone_id} with 25–40 mm to refill root zone"
            input_rate = None
        elif diagnosis and diagnosis.kind == "biotic":
            action = f"Scout zone {zone.zone_id} for {diagnosis.name}; apply IPM threshold before treatment"
            input_rate = None
        else:
            action = f"Investigate cause of low vigor in zone {zone.zone_id} before input application"
            input_rate = None

        actions.append(
            ActionItem(
                zone_id=zone.zone_id,
                issue=issue,
                action=action,
                input_rate_kg_ha=input_rate,
                ipm_tier=tier,  # type: ignore[arg-type]
                timing="Within 5–7 days",
                priority=max(1, min(5, zone.priority)),
                economic_threshold_note="Confirm cause before chemical use; prefer cultural controls",
            )
        )

    # Diagnosis-specific actions (whole-field or confirmed-zone).
    if diagnosis and diagnosis.kind == "biotic":
        actions.append(
            ActionItem(
                zone_id="FIELD",
                issue=diagnosis.name,
                action="Confirm diagnosis; if threshold exceeded, apply biological control first, then targeted fungicide/bactericide only as last resort",
                ipm_tier="biological",
                timing="Within 48 hours if threshold met",
                priority=1,
                economic_threshold_note=diagnosis.ipm_actions[-1] if diagnosis.ipm_actions else "Follow label and local threshold",
            )
        )
    elif diagnosis and diagnosis.kind == "abiotic":
        actions.append(
            ActionItem(
                zone_id="FIELD",
                issue=diagnosis.name,
                action=diagnosis.ipm_actions[0] if diagnosis.ipm_actions else "Monitor and address underlying stress",
                ipm_tier="cultural",
                timing="Within 5–7 days",
                priority=2,
                economic_threshold_note="Do not apply chemicals for abiotic stress until pathogen ruled out",
            )
        )

    return sorted(actions, key=lambda a: a.priority)
