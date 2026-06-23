---
name: sub-remote-sensing-analyzer
description: Computes and interprets vegetation indices from satellite/drone imagery, mapping stress zones and phenology deviations.
---

## Purpose
Translate imagery into actionable spatial crop-health information. Uses `indices.py` and `phenology.py`.

## Inputs
Imagery (Sentinel/drone), selected indices, phenology reference, `FieldProfile`.

## Procedure
1. Compute selected index(es) with `indices.compute_indices()`; note sensor, bands, acquisition date, cloud cover.
2. Build a **time series** vs. expected phenology curve; flag deviations with `phenology.index_deviation()` (early senescence, slow greenup).
3. Segment field into **stress zones** (high/medium/low vigor); quantify area per zone.
4. Hypothesize causes per zone (water, nutrient, disease, compaction) — to be confirmed by diagnosis.
5. State spatial resolution limits.

## Python API

```python
from crop_yield_disease_diagnosis.indices import compute_indices
from crop_yield_disease_diagnosis.phenology import index_deviation

index_maps = compute_indices(imagery_bands)
deviation = index_deviation(observed_ndvi, profile.crop, profile.stage, "ndvi")
```

## Outputs
- `IndexMap[]` with `name`, `sensor`, `acquisition_date`, `mean`, `std`, `valid_fraction`, `histogram`.
- `StressZone[]` with `zone_id`, `label`, `area_fraction`, `mean_index`, `cause_hypotheses`, `priority`.
- Phenology deviation note.

## Quality Gate
- Sensor + index + date stated for every `IndexMap`.
- Zones quantified (area fraction).
- Resolution limits noted.
- `valid_fraction` reported.
