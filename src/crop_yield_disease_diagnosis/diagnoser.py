"""Differential disease diagnosis engine."""
from __future__ import annotations

from typing import Any

from crop_yield_disease_diagnosis.disease_library import SIGNATURES, Signature, get_signatures
from crop_yield_disease_diagnosis.types import DiagnosisCandidate


def _normalize(text: str) -> set[str]:
    return set(text.lower().replace(",", " ").replace("/", " ").split())


def _match_score(sig: Signature, symptoms: list[str], spectral_clues: list[str], weather: dict[str, Any]) -> float:
    """Compute a 0-1 match score from symptom, spectral, and weather cues."""
    sym_text = " ".join(symptoms)
    spec_text = " ".join(spectral_clues)
    weather_text = " ".join(
        f"{k} {v}" for k, v in weather.items() if isinstance(v, str | int | float)
    )

    sym_set = _normalize(sym_text)
    spec_set = _normalize(spec_text)
    weather_set = _normalize(weather_text)

    sym_kw = set()
    for kw in sig.symptom_keywords:
        sym_kw.update(_normalize(kw))
    spec_kw = set()
    for kw in sig.spectral_clues:
        spec_kw.update(_normalize(kw))
    weather_kw = set()
    for kw in sig.conducive_weather:
        weather_kw.update(_normalize(kw))

    sym_match = len(sym_kw & sym_set) / max(1, len(sym_kw))
    spec_match = len(spec_kw & spec_set) / max(1, len(spec_kw)) if spec_set else 0.0
    weather_match = len(weather_kw & weather_set) / max(1, len(weather_kw)) if weather_set else 0.0

    # Weight symptoms highest, then weather, then spectral.
    return 0.5 * sym_match + 0.25 * weather_match + 0.25 * spec_match


def _abiotic_boost(symptoms: list[str]) -> bool:
    """Detect cues that strongly suggest abiotic stress."""
    text = " ".join(symptoms).lower()
    abiotic_cues = [
        "uniform yellowing",
        "cold snap",
        "whole field",
        "after frost",
        "heat stress",
        "drought",
        "water stress",
    ]
    return any(cue in text for cue in abiotic_cues)


def differential_diagnosis(
    symptoms: list[str],
    spectral_clues: list[str],
    crop: str,
    weather: dict[str, Any] | None = None,
    top_k: int = 5,
) -> list[DiagnosisCandidate]:
    """Return a ranked differential diagnosis.

    Always returns at least 2 candidates where signatures exist. Biotic candidates are
    down-weighted when symptoms indicate a uniform abiotic event.
    """
    weather = weather or {}
    candidates: list[Signature] = get_signatures(crop)
    if not candidates:
        # Fallback: return a generic unknown candidate.
        return [
            DiagnosisCandidate(
                name="Unknown",
                kind="unknown",
                confidence=0.0,
                evidence=["No signatures for crop"],
                confirm_step="Consult local extension agronomist/pathologist.",
            )
        ]

    abiotic_override = _abiotic_boost(symptoms)

    scored: list[tuple[float, Signature]] = []
    for sig in candidates:
        score = _match_score(sig, symptoms, spectral_clues, weather)
        if abiotic_override and sig.kind == "biotic":
            score *= 0.5
        elif abiotic_override and sig.kind == "abiotic":
            score *= 1.2
        scored.append((score, sig))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Normalize scores to pseudo-probabilities.
    raw_scores = [s for s, _ in scored]
    if sum(raw_scores) == 0:
        confidences = [1.0 / len(raw_scores)] * len(raw_scores)
    else:
        confidences = [s / sum(raw_scores) for s in raw_scores]

    results: list[DiagnosisCandidate] = []
    for (score, sig), conf in zip(scored, confidences):
        if score == 0.0 and len(results) >= 2:
            break
        evidence = []
        if any(k in " ".join(symptoms).lower() for k in sig.symptom_keywords):
            evidence.append("symptom match")
        if any(k in " ".join(spectral_clues).lower() for k in sig.spectral_clues):
            evidence.append("spectral match")
        if any(k in " ".join(f"{k} {v}" for k, v in weather.items() if isinstance(v, str | int | float)).lower() for k in sig.conducive_weather):
            evidence.append("weather match")
        results.append(
            DiagnosisCandidate(
                name=sig.name,
                kind=sig.kind,
                confidence=round(min(conf, 0.95), 3),
                evidence=evidence,
                conducive_conditions=list(sig.conducive_weather),
                confirm_step=sig.confirm_step,
                ipm_actions=list(sig.ipm_actions),
            )
        )

    # Ensure at least 2 candidates when possible.
    while len(results) < 2 and len(scored) > len(results):
        idx = len(results)
        score, sig = scored[idx]
        if score == 0.0:
            break
        conf = confidences[idx] if idx < len(confidences) else 0.01
        results.append(
            DiagnosisCandidate(
                name=sig.name,
                kind=sig.kind,
                confidence=round(conf, 3),
                evidence=["weak pattern overlap"],
                conducive_conditions=list(sig.conducive_weather),
                confirm_step=sig.confirm_step,
                ipm_actions=list(sig.ipm_actions),
            )
        )

    return results[:top_k]
