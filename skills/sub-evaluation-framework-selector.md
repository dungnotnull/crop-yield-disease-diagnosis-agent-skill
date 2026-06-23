---
name: sub-evaluation-framework-selector
description: Selects appropriate vegetation indices and crop-simulation model for the crop, growth stage, and region. Shared across science-industry cluster.
---

## Purpose
Match analytical methods to the agronomic situation rather than defaulting blindly to NDVI. The output is a `FrameworkSelection` used by the main harness.

## Inputs
`FieldProfile`.

## Procedure
1. Choose **indices**: NDVI for general vigor; NDRE for high-biomass/N status; EVI for dense canopy / atmospheric correction; GNDVI for chlorophyll; SAVI/MSAVI2 for sparse canopy.
2. Choose **crop model**: AquaCrop (water-limited), DSSAT/APSIM (full process), or empirical index-yield regression if data limited. The Python engine selects the best available backend via `crop_model.select_backend()`.
3. Select **phenology reference** (regional crop calendar / GDD curve) from `phenology.PHENOLOGY_TABLE` and `phenology.CROP_GDD`.
4. Justify each selection.

## Decision Matrix

| Crop stage | Primary index | Secondary index | Crop model priority |
|------------|---------------|-----------------|---------------------|
| Early vegetative | NDVI | SAVI/EVI | Empirical regression |
| High biomass / tasseling | NDRE | NDVI | AquaCrop > DSSAT > Empirical |
| Heading/flowering | NDRE | EVI | DSSAT > AquaCrop > Empirical |
| Grain-fill / senescence | NDVI | EVI | Empirical regression |
| Unknown stage | NDVI | EVI | Empirical regression |

## Python API

```python
from crop_yield_disease_diagnosis.harness import select_framework
framework = select_framework(profile)
# FrameworkSelection(indices, crop_model, phenology_reference, justification)
```

## Outputs
`FrameworkSelection`:
- `indices[]`
- `crop_model`
- `phenology_reference`
- `justification`

## Quality Gate
- Each method justified against crop/stage/region.
- Not a blind NDVI default.
- Shared interface: indices and model strings are cluster-neutral; sibling skills (133/134/232) can invoke this selector with their own profile schemas.
