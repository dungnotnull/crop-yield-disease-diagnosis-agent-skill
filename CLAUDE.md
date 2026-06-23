# CLAUDE.md — Crop Yield Forecast & Plant Disease Diagnosis (Idea 213)

**Skill name:** `crop-yield-disease-diagnosis`
**Tagline:** Forecasts crop yield and diagnoses plant disease from satellite/drone imagery and field data, recommending precision fertilization and irrigation.
**Cluster:** `science-industry`
**Source idea:** 213
**Current phase:** Phase 5 complete — production-ready

## Problem This Skill Solves
Farmers and agronomists need early, spatially-explicit warnings of yield shortfalls and disease outbreaks. This skill interprets vegetation indices (NDVI/EVI/NDRE) from satellite/drone imagery plus weather and soil data, estimates yield against crop models (DSSAT/AquaCrop/FAO), flags disease symptoms by spectral and visual signatures, and outputs precision fertilization/irrigation recommendations with a confidence-rated roadmap.

## Harness Flow Summary
1. **Intake** → `sub-requirements-gatherer` — crop, growth stage, field geometry, imagery/data available.
2. **Framework selection** → `sub-evaluation-framework-selector` — pick indices & crop model for the crop/region.
3. **Remote-sensing analysis** → `sub-remote-sensing-analyzer` — compute NDVI/EVI, stress zones, time series.
4. **Disease diagnosis** → `sub-disease-diagnoser` — symptom + spectral signature → candidate pathogens.
5. **Scoring** → `sub-scoring-engine` — yield estimate + crop-health score.
6. **Roadmap** → `sub-improvement-roadmap` — fertilization/irrigation/IPM actions.

## Python Engine
All analytical logic is implemented under `src/crop_yield_disease_diagnosis/`:

| Module | Purpose |
|--------|---------|
| `types.py` | Pydantic domain models |
| `indices.py` | Vegetation-index formulas |
| `phenology.py` | Crop-phenology reference curves |
| `crop_model.py` | Backend interface + empirical regression fallback |
| `disease_library.py` | Pathogen/abiotic signature catalog |
| `diagnoser.py` | Differential diagnosis engine |
| `scoring.py` | Yield forecast + health score |
| `recommendation.py` | IPM-first action roadmap |
| `data_sources.py` | Imagery/field-data availability + fallback |
| `harness.py` | End-to-end orchestration + quality gates |

Entry point:

```python
from crop_yield_disease_diagnosis.harness import run_analysis
from crop_yield_disease_diagnosis.types import FieldProfile

report = run_analysis(FieldProfile(...))
```

## Sub-skills
- `sub-requirements-gatherer.md`
- `sub-evaluation-framework-selector.md`
- `sub-remote-sensing-analyzer.md`
- `sub-disease-diagnoser.md`
- `sub-scoring-engine.md`
- `sub-improvement-roadmap.md`

## Tools Required
WebSearch, WebFetch (Sentinel/Landsat, FAO), Read, Write, Bash.

## Knowledge Sources
ESA Copernicus/Sentinel-2; USGS Landsat; FAO crop calendars & AquaCrop; DSSAT/APSIM; plant-pathology databases (CABI, IPM); NDVI/EVI literature; agronomy journals.

## Supporting Tools
- `tools/knowledge_updater.py` — production-grade crawler for RS/agronomy/pathology sources (async, retries, dedup, relevance scoring, dry-run CLI).

## Quality Gates (enforced by engine)
- Index, sensor, and acquisition date stated for any remote-sensing claim.
- Yield forecast carries a confidence/uncertainty band.
- Disease output is a differential list with confidence.
- Recommendations reference IPM (chemical use minimized, thresholds applied).
- Data vintage/staleness flagged.
- Field-data-only fallback used when imagery unavailable, with reduced confidence.

## Cluster Integration
This skill shares three sub-skills with the `science-industry` cluster:
- `sub-evaluation-framework-selector` — reusable by `microclimate-weather-forecast-analyzer` (133), `livestock-farm-management-plan` (134), and `micro-urban-agriculture-design` (232).
- `sub-scoring-engine` — shared scoring rubric across cluster skills.
- `sub-improvement-roadmap` — shared roadmap generator.

Cluster paths:
- `D:\skills\microclimate-weather-forecast-analyzer`
- `D:\skills\livestock-farm-management-plan`
- `D:\skills\micro-urban-agriculture-design`

## Active Development Tasks
- [x] Scaffold deliverables
- [x] Add per-crop NDVI phenology curves
- [x] Expand pathogen signature library
- [x] Implement Python analytics engine
- [x] Implement pytest suite (≥5 scenarios)
- [x] Integrate with cluster skills 133/134/232
- [x] Mark all phases 100% complete

## Reference Docs
`PROJECT-detail.md`, `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`, `SECOND-KNOWLEDGE-BRAIN.md`.
