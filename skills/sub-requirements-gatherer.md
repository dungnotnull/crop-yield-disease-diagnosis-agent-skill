---
name: sub-requirements-gatherer
description: Captures crop, growth stage, field geometry, and available imagery/field data for crop analysis.
---

## Purpose
Establish the agronomic context needed for correct index and model interpretation. Produces a `FieldProfile` consumed by `src/crop_yield_disease_diagnosis/harness.py`.

## Inputs
User description; optional imagery links, weather/soil data.

## Procedure
1. Capture **crop & variety**, planting date, current **growth stage** (or estimate from GDD via `phenology.estimate_stage_from_gdd`).
2. Capture **field geometry/area**, location (coordinates), and management zones if known.
3. Inventory **data available**: satellite (Sentinel-2/Landsat), drone multispectral, weather station, soil tests.
4. Capture **goal**: yield forecast, disease ID, input optimization.
5. Note gaps (no recent cloud-free imagery, no soil data).

## Python API

```python
from crop_yield_disease_diagnosis.types import FieldProfile

profile = FieldProfile(
    crop="maize",
    variety="Pioneer P1197",
    stage="tasseling",
    location=(41.66, -93.47),
    area_ha=45.0,
    planting_date=date(2026, 5, 1),
    data_sources=["sentinel_2", "weather_station"],
    goal="yield_forecast",
)
```

## Outputs
`FieldProfile`:
- `crop`, `variety`, `stage`
- `location`, `area_ha`, `planting_date`
- `data_sources[]`, `goal`, `notes`
- Optional `imagery[]`, `weather{}`, `soil_n_pk{}`, `symptoms[]`

## Quality Gate
- Crop, stage, location, and at least one data source captured.
- Gaps listed.
- Stage validated against known phenology keys.
