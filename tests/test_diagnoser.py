"""Tests for differential disease diagnosis engine."""
from __future__ import annotations

from crop_yield_disease_diagnosis.diagnoser import differential_diagnosis


def test_rice_blast_vs_brown_spot() -> None:
    candidates = differential_diagnosis(
        symptoms=["brown lozenge lesions"],
        spectral_clues=["ndre drop", "patchy ndvi decline"],
        crop="rice",
        weather={"humidity": "high", "temperature": "warm"},
        top_k=5,
    )
    assert len(candidates) >= 2
    names = [c.name.lower() for c in candidates]
    assert any("blast" in n for n in names)
    assert any("brown spot" in n or "sheath blight" in n for n in names)
    assert candidates[0].kind == "biotic"
    assert candidates[0].confidence <= 0.95


def test_abiotic_cold_injury() -> None:
    candidates = differential_diagnosis(
        symptoms=["uniform yellowing across whole field after cold snap"],
        spectral_clues=["uniform ndvi drop"],
        crop="rice",
        weather={"temperature": "cold", "event": "cold snap"},
        top_k=5,
    )
    # Top candidate should be abiotic because of uniform yellowing/cold snap cues.
    assert candidates[0].kind == "abiotic"
    assert "cold" in candidates[0].name.lower() or "nitrogen" in candidates[0].name.lower()
    # No biotic candidate should dominate.
    assert all(c.confidence < 0.6 for c in candidates if c.kind == "biotic")


def test_at_least_two_candidates() -> None:
    candidates = differential_diagnosis(
        symptoms=["brown lesions"],
        spectral_clues=["ndre drop"],
        crop="rice",
        weather={},
        top_k=5,
    )
    assert len(candidates) >= 2


def test_unknown_crop_fallback() -> None:
    candidates = differential_diagnosis(
        symptoms=["yellow leaves"], spectral_clues=[], crop="quinoa", weather={}
    )
    # Generic abiotic signatures apply to any crop (crop='*'), so we get actionable
    # candidates rather than a generic Unknown label.
    assert len(candidates) >= 1
    assert candidates[0].kind == "abiotic"

