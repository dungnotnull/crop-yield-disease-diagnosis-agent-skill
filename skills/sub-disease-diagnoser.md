---
name: sub-disease-diagnoser
description: Produces a ranked differential diagnosis of plant disease from spectral signatures and visual/described symptoms, distinguishing biotic vs. abiotic stress.
---

## Purpose
Provide a careful, confidence-rated disease shortlist — never a single definitive claim. Uses `diagnoser.py` and `disease_library.py`.

## Inputs
Symptom description/images, spectral stress patterns, crop, region, weather.

## Procedure
1. Characterize symptoms (lesion type, distribution, color, pattern, affected organ).
2. Distinguish **biotic** (fungal/bacterial/viral/pest) vs. **abiotic** (nutrient, water, heat, chemical).
3. Cross-reference crop + region + weather conducive conditions against `disease_library.SIGNATURES`.
4. Produce a **ranked differential** with evidence and confidence per candidate via `diagnoser.differential_diagnosis()`.
5. Recommend confirmation steps (lab test, scouting) before treatment.

## Python API

```python
from crop_yield_disease_diagnosis.diagnoser import differential_diagnosis

candidates = differential_diagnosis(
    symptoms=["brown lozenge lesions"],
    spectral_clues=["ndre drop"],
    crop="rice",
    weather={"humidity": "high", "temperature": "warm"},
    top_k=5,
)
```

## Outputs
`DiagnosisCandidate[]`: candidate | evidence | conducive conditions | confidence | confirm-step | ipm_actions.

## Quality Gate
- Ranked differential (≥2 candidates where signatures exist).
- Biotic/abiotic distinguished.
- Confirmation advised.
- Top candidate confidence ≤0.95; never definitive.
