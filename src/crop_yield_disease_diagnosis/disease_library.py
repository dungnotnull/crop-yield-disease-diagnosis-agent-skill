"""Structured pathogen and abiotic-stress signatures for differential diagnosis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Signature:
    """A disease or stress signature."""

    name: str
    crop: str
    kind: Literal["biotic", "abiotic"]
    symptom_keywords: list[str] = field(default_factory=list)
    spectral_clues: list[str] = field(default_factory=list)
    conducive_weather: list[str] = field(default_factory=list)
    confirm_step: str = ""
    ipm_actions: list[str] = field(default_factory=list)


SIGNATURES: list[Signature] = [
    # Rice biotic
    Signature(
        name="Rice blast (Magnaporthe oryzae)",
        crop="rice",
        kind="biotic",
        symptom_keywords=["brown", "lozenge", "diamond", "lesion", "neck", "node", "gray center"],
        spectral_clues=["ndre drop", "patchy ndvi decline"],
        conducive_weather=["humid", "wet", "warm", "dew"],
        confirm_step="Inspect lesions for gray centers; lab PCR if mixed symptoms.",
        ipm_actions=[
            "Use resistant variety",
            "Balance K fertilizer; avoid excess N",
            "Apply fungicide only if >5% tillers infected and wet forecast persists",
        ],
    ),
    Signature(
        name="Brown spot (Cochliobolus miyabeanus)",
        crop="rice",
        kind="biotic",
        symptom_keywords=["brown", "spot", "oval", "lesion", "leaf tip", "dark margin"],
        spectral_clues=["moderate ndvi decline", "ndre drop"],
        conducive_weather=["humid", "warm", "nutrient deficient"],
        confirm_step="Look for dark brown lesions with lighter centers; culture if needed.",
        ipm_actions=[
            "Correct nutrient deficiency (N/P/K balance)",
            "Remove infected crop residue",
            "Fungicide if disease exceeds 10% leaf area",
        ],
    ),
    Signature(
        name="Sheath blight (Rhizoctonia solani)",
        crop="rice",
        kind="biotic",
        symptom_keywords=["sheath", "lower leaf", "oval", "lesion", "white mycelium"],
        spectral_clues=["lower canopy ndvi decline"],
        conducive_weather=["humid", "high temperature", "dense canopy"],
        confirm_step="Check sheaths for irregular lesions with white fungal growth.",
        ipm_actions=[
            "Wider plant spacing",
            "Avoid excess N",
            "Fungicide if lesions reach flag leaf",
        ],
    ),
    # Maize biotic
    Signature(
        name="Gray leaf spot (Cercospora zeae-maydis)",
        crop="maize",
        kind="biotic",
        symptom_keywords=["rectangular", "gray", "tan", "lesion", "leaf", "parallel veins"],
        spectral_clues=["canopy ndvi decline", "ndre collapse"],
        conducive_weather=["humid", "wet", "moderate temperature"],
        confirm_step="Lesions bound by leaf veins; confirm with microscope/PCR.",
        ipm_actions=[
            "Rotate crops",
            "Tillage to reduce residue",
            "Fungicide at silking if weather stays wet",
        ],
    ),
    Signature(
        name="Goss's wilt (Clavibacter michiganensis)",
        crop="maize",
        kind="biotic",
        symptom_keywords=["v-shaped", "tan", "lesion", "bacterial exudate", "wilting"],
        spectral_clues=["ndre collapse in lesion zone"],
        conducive_weather=["warm", "wet", "wind-driven rain"],
        confirm_step="Look for shiny bacterial exudate; lab isolation.",
        ipm_actions=[
            "Use resistant hybrids",
            "Avoid mechanical injury when wet",
            "Copper-based bactericide only if severe",
        ],
    ),
    # Wheat biotic
    Signature(
        name="Wheat rust (Puccinia spp.)",
        crop="wheat",
        kind="biotic",
        symptom_keywords=["rust", "pustule", "orange", "yellow", "stripe", "leaf"],
        spectral_clues=["ndvi decline", "hotspot of low reflectance"],
        conducive_weather=["cool", "humid", "dew"],
        confirm_step="Rub pustules to release colored spores; send to lab for race ID.",
        ipm_actions=[
            "Plant resistant varieties",
            "Early fungicide if pustules appear before flag leaf",
            "Monitor volunteer wheat",
        ],
    ),
    # Soybean biotic
    Signature(
        name="Frogeye leaf spot (Cercospora sojina)",
        crop="soybean",
        kind="biotic",
        symptom_keywords=["circular", "tan", "purple ring", "leaf spot"],
        spectral_clues=["patchy ndre decline"],
        conducive_weather=["warm", "humid", "rainy"],
        confirm_step="Look for tan lesions with purple borders.",
        ipm_actions=[
            "Resistant variety",
            "Crop rotation",
            "Fungicide if R3 and disease increasing",
        ],
    ),
    # Abiotic
    Signature(
        name="Nitrogen deficiency",
        crop="*",
        kind="abiotic",
        symptom_keywords=["uniform yellowing", "older leaves yellow", "chlorosis", "stunted"],
        spectral_clues=["ndre low", "gndvi low", "general ndvi decline"],
        conducive_weather=["cool", "wet leaching", "sandy soil"],
        confirm_step="Soil nitrate test + tissue N analysis.",
        ipm_actions=[
            "Variable-rate sidedress N in deficient zones",
            "Split N applications",
        ],
    ),
    Signature(
        name="Cold/chilling injury",
        crop="*",
        kind="abiotic",
        symptom_keywords=["uniform yellowing", "wilting", "browning", "whole field"],
        spectral_clues=["uniform ndvi/evi drop", "no patchiness"],
        conducive_weather=["cold snap", "frost", "low temperature"],
        confirm_step="Review weather record; inspect growing point; rule out pathogen.",
        ipm_actions=[
            "Avoid spraying chemicals until cause confirmed",
            "Monitor recovery; rescue irrigation if needed",
        ],
    ),
    Signature(
        name="Water stress",
        crop="*",
        kind="abiotic",
        symptom_keywords=["wilting", "rolled leaves", "leaf firing", "stunted"],
        spectral_clues=["ndvi drop midday", "swir1/swir2 high", "evi decline"],
        conducive_weather=["drought", "high temperature", "low humidity"],
        confirm_step="Soil moisture probe; ET vs rainfall balance.",
        ipm_actions=[
            "Irrigate high-priority zones first",
            "Mulch/residue cover to reduce evaporation",
        ],
    ),
    Signature(
        name="Compaction",
        crop="*",
        kind="abiotic",
        symptom_keywords=["stunted", "patchy", "wheel track", "poor root"],
        spectral_clues=["patchy low ndvi following traffic patterns"],
        conducive_weather=["wet field traffic"],
        confirm_step="Penetrometer reading >300 psi; root inspection.",
        ipm_actions=[
            "Controlled traffic in future seasons",
            "Deep ripping if severe and soil dry",
        ],
    ),
]


def get_signatures(crop: str, kind: str | None = None) -> list[Signature]:
    """Return signatures matching the crop and optional kind."""
    out: list[Signature] = []
    for sig in SIGNATURES:
        if sig.crop != "*" and sig.crop.lower() != crop.lower():
            continue
        if kind and sig.kind != kind:
            continue
        out.append(sig)
    return out
