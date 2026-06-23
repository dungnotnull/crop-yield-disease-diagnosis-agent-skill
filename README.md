# Crop Yield Forecast & Plant Disease Diagnosis

Production-grade, open-source Python engine for precision agriculture: compute vegetation indices from satellite/drone imagery, interpret them relative to crop phenology, diagnose plant disease from spectral + symptom cues, forecast yield with uncertainty bands, and generate IPM-first input recommendations.

## Install

```bash
pip install -r requirements.txt          # runtime
pip install -r requirements-dev.txt        # development
```

Or install the package in editable mode:

```bash
pip install -e ".[dev]"
```

## Quickstart

```python
from datetime import date
from crop_yield_disease_diagnosis.harness import run_analysis
from crop_yield_disease_diagnosis.types import FieldProfile

report = run_analysis(FieldProfile(
    crop="maize",
    variety="test",
    stage="tasseling",
    location=(10.5, 106.2),
    area_ha=2.0,
    planting_date=date(2026, 1, 1),
    data_sources=["field_data"],
    goal="yield_forecast",
))
print(report.model_dump_json(indent=2))
```

## Module Map

| Module | Responsibility |
|--------|----------------|
| `indices.py` | Vegetation-index formulas (NDVI, EVI, NDRE, etc.) |
| `phenology.py` | Crop-growth-stage curves and GDD mapping |
| `crop_model.py` | Backend interface, empirical regression, DSSAT/AquaCrop wiring |
| `disease_library.py` | Pathogen signatures and abiotic-stress patterns |
| `diagnoser.py` | Ranked differential diagnosis engine |
| `scoring.py` | Yield forecast with uncertainty band + health score |
| `recommendation.py` | Zone-specific, IPM-first action roadmap |
| `data_sources.py` | Imagery/weather availability and fallback logic |
| `harness.py` | End-to-end orchestration and quality gates |
| `types.py` | Pydantic domain models |

## Run Tests

```bash
python -m pytest tests -v
```

## Update Knowledge Base

```bash
python tools/knowledge_updater.py --dry-run --limit 10
```

## License

MIT
