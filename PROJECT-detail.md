# PROJECT-detail.md — Crop Yield Forecast & Plant Disease Diagnosis

## Executive Summary
A precision-agriculture harness that turns remote-sensing imagery and field data into a yield forecast, a spatial crop-health map, a disease diagnosis shortlist, and precision input recommendations. Grounded in established vegetation indices (NDVI, EVI, NDRE), crop-simulation models (DSSAT, FAO AquaCrop), and IPM principles. Every estimate carries a confidence rating and data-vintage note.

## Problem Statement
Yield losses from drought, nutrient deficiency, and disease are often detected too late. Satellite/drone imagery enables early detection, but raw indices are meaningless without crop-, stage-, and region-specific interpretation. Small and mid-size growers lack the analytics capacity to do this.

## Target Users & Use Cases
- **Agronomist** — "Interpret this NDVI map for my maize field." → stress zones + cause hypotheses.
- **Farmer** — "Will my rice hit target yield?" → model-based forecast + confidence.
- **Crop scout** — "These leaves show yellowing — what disease?" → ranked pathogen candidates + IPM.
- **Cooperative** — "Which fields need fertilizer first?" → prioritized variable-rate plan.
- **Insurer/lender** — "Yield risk for this parcel?" → forecast with uncertainty band.

## Repository Layout
```
/crop-yield-disease-diagnosis
  pyproject.toml
  README.md
  requirements.txt
  CLAUDE.md
  PROJECT-detail.md
  PROJECT-DEVELOPMENT-PHASE-TRACKING.md
  SECOND-KNOWLEDGE-BRAIN.md
  src/crop_yield_disease_diagnosis/
    __init__.py
    types.py              → Pydantic domain models
    indices.py            → NDVI/EVI/NDRE/etc.
    phenology.py          → Crop-stage curves
    crop_model.py         → Backend interface + empirical fallback
    disease_library.py    → Pathogen/abiotic catalog
    diagnoser.py          → Differential engine
    scoring.py            → Yield/health scoring
    recommendation.py     → IPM roadmap
    data_sources.py       → Availability + fallback
    harness.py            → End-to-end orchestration
  skills/
    main.md
    sub-requirements-gatherer.md
    sub-evaluation-framework-selector.md
    sub-remote-sensing-analyzer.md
    sub-disease-diagnoser.md
    sub-scoring-engine.md
    sub-improvement-roadmap.md
  tests/
    test_indices.py
    test_phenology.py
    test_diagnoser.py
    test_scoring.py
    test_recommendation.py
    test_harness.py
    test_knowledge_updater.py
  tools/
    knowledge_updater.py  → Production knowledge pipeline
```

## Module Responsibility Table
| Module | Responsibility | Quality gate enforced |
|--------|----------------|----------------------|
| `indices.py` | Compute vegetation indices, handle edge values | Index + bands documented |
| `phenology.py` | Expected index per crop/stage | Stage-relative interpretation |
| `crop_model.py` | Yield forecast with backend selection | Uncertainty band present |
| `disease_library.py` | Structured signatures | ≥2 candidates where applicable |
| `diagnoser.py` | Ranked differential diagnosis | Biotic/abiotic distinguished |
| `scoring.py` | Yield + health score | Band + sensitivity |
| `recommendation.py` | Zone-specific input plan | IPM ordering; timing given |
| `data_sources.py` | Source availability, fallback | Staleness flagged |
| `harness.py` | Orchestration + confidence gates | All gates verified before output |

## Harness Architecture
```
Stage 1 Intake        → sub-requirements-gatherer        → crop/field/data profile
Stage 2 Framework     → sub-evaluation-framework-selector→ indices + crop model
Stage 3 Remote sense  → sub-remote-sensing-analyzer      → index maps + stress zones
Stage 4 Diagnosis     → sub-disease-diagnoser            → pathogen shortlist
Stage 5 Scoring       → sub-scoring-engine               → yield + health score
Stage 6 Roadmap       → sub-improvement-roadmap          → input recommendations
```

## Confidence Gates
| Gate | Threshold | Fallback if not met |
|------|-----------|---------------------|
| Data vintage | Imagery ≤30 days old for near-real-time | Use field-data-only mode |
| Index reliability | Cloud cover ≤20%; no NaN fraction >10% | Lower confidence, flag issue |
| Phenology match | Growth stage declared or inferred from GDD | Wider uncertainty band |
| Diagnosis confidence | Top candidate ≤0.85; ≥2 candidates listed | Advise lab confirmation |
| Yield uncertainty | Band width ≤±25% of mean at "good" data quality | Widen band and flag |

## Data-Source Matrix
| Source | Provides | Fallback when unavailable |
|--------|----------|-----------------------------|
| Sentinel-2 | 10–60 m multispectral + red-edge | Landsat, drone, field data |
| Landsat 8/9 | 30 m multispectral | Sentinel, drone, field data |
| Drone multispectral | High-res red-edge/RGB | Sentinel/Landsat |
| Weather station | Temp/rain/humidity | Global reanalysis (ERA5) |
| Soil test | N/P/K/pH | Regional soil maps |
| Field observation | Symptoms, growth stage | Imagery-only lower confidence |

## E2E Execution Flow
Intake → framework → index computation → diagnosis → yield/health score → roadmap. If imagery APIs are down, switch to field-data-only mode, flag staleness, and lower confidence.

## SECOND-KNOWLEDGE-BRAIN Integration
`knowledge_updater.py` crawls Copernicus/Landsat docs, FAO, agronomy + plant-pathology literature; dedup by URL hash; dated append. See `SECOND-KNOWLEDGE-BRAIN.md` for the seed knowledge base.

## Cluster Integration
This skill contributes three shared sub-skills to the `science-industry` cluster:
- `sub-evaluation-framework-selector.md`
- `sub-scoring-engine.md`
- `sub-improvement-roadmap.md`

These are designed to be invoked by sibling skills:
- `microclimate-weather-forecast-analyzer` (133)
- `livestock-farm-management-plan` (134)
- `micro-urban-agriculture-design` (232)

Each shared sub-skill documents its generic interface and crop/livestock/urban neutral parameters.

## Test Scenarios
Six scenarios are implemented as pytest tests in `tests/`:
1. Maize NDVI interpretation
2. Disease differential
3. Imagery unavailable fallback
4. Variable-rate roadmap
5. Yield forecast with band
6. Abiotic vs. biotic

## Key Design Decisions
1. Indices interpreted relative to crop phenology, never absolute thresholds alone.
2. Disease output always a ranked differential with confidence — never definitive.
3. IPM-first: cultural/biological controls before chemicals; economic thresholds.
4. Field-data-only fallback when imagery unavailable.
5. Forecasts include uncertainty; never single-point without band.
6. External crop-model executables (DSSAT/AquaCrop) are wired but not bundled; the engine uses an empirical regression fallback when they are absent.
