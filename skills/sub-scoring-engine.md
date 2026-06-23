---
name: sub-scoring-engine
description: Produces a yield forecast with uncertainty band and a crop-health score by coupling indices to the selected crop model. Shared across science-industry cluster.
---

## Purpose
Quantify expected yield and overall crop health defensibly. Uses `scoring.py` and `crop_model.py`.

## Inputs
Index time series, crop model, weather/soil, stress zones, disease differential.

## Procedure
1. Drive the selected crop model (or index-yield regression) with available inputs via `crop_model.yield_forecast()`.
2. Produce a **yield estimate** with an uncertainty band reflecting data quality.
3. Compute a **crop-health score** (0–100) from vigor, stress-zone fraction, disease pressure via `scoring.score_health()`.
4. State key sensitivities (e.g., rainfall assumption).

## Python API

```python
from crop_yield_disease_diagnosis.scoring import score_yield, score_health

yield_fc = score_yield(profile, index_values, stress_zones, data_quality, prefer_model="aquacrop")
health = score_health(profile, index_values, stress_zones, disease_differential, data_quality)
```

## Outputs
- `YieldForecast`: estimate ± band, confidence, method, sensitivities, data-vintage note.
- `HealthScore`: score, component breakdown, confidence.

## Quality Gate
- Uncertainty band present.
- Sensitivities stated.
- Shared interface: scoring functions accept generic `profile`, `index_values`, and `stress_zones` so sibling cluster skills can reuse the engine.
