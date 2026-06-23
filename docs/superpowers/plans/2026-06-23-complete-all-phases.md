# Complete All Phases (0-5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the `crop-yield-disease-diagnosis` skill from scaffolded state to production-grade, open-source-ready implementation covering all six phases, with all tasks marked done in `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`.

**Architecture:** A pure-Python analytics engine (`src/crop_yield_disease_diagnosis/`) implements vegetation-index computation, crop-phenology references, empirical crop-model fallback, differential disease diagnosis, yield/health scoring, and precision-agriculture recommendation generation. Skill markdown files in `skills/` and root docs describe the harness and delegate to the Python engine. The knowledge pipeline (`tools/knowledge_updater.py`) fetches, scores, deduplicates, and appends authoritative agronomy/RS/pathology entries. A pytest suite validates the six required scenarios plus engine internals.

**Tech Stack:** Python 3.10+, Pydantic, NumPy, python-dateutil, requests, feedparser, BeautifulSoup4, pytest, pytest-cov.

---

## Task 1: Project Foundation & Configuration

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1.1: Write packaging and dependency files**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "crop-yield-disease-diagnosis"
version = "0.1.0"
description = "Forecast crop yield and diagnose plant disease from RS imagery and field data."
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "Open Source Contributors"}]
keywords = ["precision-agriculture", "ndvi", "crop-yield", "disease-diagnosis", "ipm"]
dependencies = [
    "pydantic>=2.0",
    "numpy>=1.24",
    "python-dateutil>=2.8",
    "requests>=2.31",
    "feedparser>=6.0",
    "beautifulsoup4>=4.12",
    "typing-extensions>=4.5",
]

[project.optional-dependencies]
dev = ["pytest>=7.4", "pytest-cov>=4.1", "ruff>=0.1.0", "mypy>=1.5"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "--cov=src/crop_yield_disease_diagnosis --cov-report=term-missing --cov-fail-under=80"

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4"]

[tool.mypy]
python_version = "3.10"
strict = true
```

- `requirements.txt`: list runtime deps from `pyproject.toml`.
- `requirements-dev.txt`: runtime + dev deps.
- `README.md`: project purpose, install, quickstart, module map, test command.
- `.gitignore`: Python/IDE artifacts.

- [ ] **Step 1.2: Verify files exist and are readable**

Run: `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
Expected: no exception.

---

## Task 2: Phase 0 — Architecture & Reference Docs

**Files:**
- Modify: `CLAUDE.md`
- Modify: `PROJECT-detail.md`
- Modify: `SECOND-KNOWLEDGE-BRAIN.md`
- Create: `src/crop_yield_disease_diagnosis/__init__.py`
- Create: `src/crop_yield_disease_diagnosis/types.py`

- [ ] **Step 2.1: Update `CLAUDE.md`**

Expand with:
- Python engine package path and API entry points.
- Phase 0 done status and data-vintage rules.
- Cluster integration note (shared framework-selector/scoring-engine/roadmap with skills 133, 134, 232).
- Clear quality gates as enforced by Python code.

- [ ] **Step 2.2: Update `PROJECT-detail.md`**

Add:
- Directory tree including `src/` modules.
- Module responsibility table.
- Data-source abstraction and fallback matrix.
- Confidence-gate algorithm (minimum thresholds for each stage).
- Integration with cluster skills.

- [ ] **Step 2.3: Enrich `SECOND-KNOWLEDGE-BRAIN.md`**

Add authoritative reference tables:
- Sentinel-2 band names/resolutions.
- Common crop phenology curves (maize, rice, wheat, soybean).
- Disease signature table (biotic vs abiotic).
- IPM threshold examples.
- Existing `knowledge_updater.py` protocol remains.

- [ ] **Step 2.4: Define Pydantic domain types in `src/crop_yield_disease_diagnosis/types.py`**

Models:
- `FieldProfile`, `DataSource`, `Imagery`, `IndexMap`, `StressZone`, `DiagnosisCandidate`, `YieldForecast`, `HealthScore`, `ActionItem`, `AnalysisReport`.
- All with validators, docstrings, and `model_dump` helpers.

- [ ] **Step 2.5: Verify Pydantic models import**

Run: `python -c "from crop_yield_disease_diagnosis.types import AnalysisReport; print(AnalysisReport)"`
Expected: prints class.

---

## Task 3: Phase 1 — Core Sub-Skill Algorithms (Python Engine)

**Files:**
- Create: `src/crop_yield_disease_diagnosis/indices.py`
- Create: `src/crop_yield_disease_diagnosis/phenology.py`
- Create: `src/crop_yield_disease_diagnosis/crop_model.py`
- Create: `src/crop_yield_disease_diagnosis/disease_library.py`
- Create: `src/crop_yield_disease_diagnosis/diagnoser.py`
- Create: `src/crop_yield_disease_diagnosis/scoring.py`
- Create: `src/crop_yield_disease_diagnosis/recommendation.py`
- Create: `src/crop_yield_disease_diagnosis/data_sources.py`
- Modify: `skills/sub-requirements-gatherer.md`
- Modify: `skills/sub-evaluation-framework-selector.md`
- Modify: `skills/sub-remote-sensing-analyzer.md`
- Modify: `skills/sub-disease-diagnoser.md`
- Modify: `skills/sub-scoring-engine.md`
- Modify: `skills/sub-improvement-roadmap.md`

- [ ] **Step 3.1: Implement vegetation indices (`indices.py`)**

Functions for NDVI, EVI, NDRE, GNDVI, GCI, SAVI, MSAVI2, RVSI with array/number input, nan-safe handling, and docstrings citing formulas.

- [ ] **Step 3.2: Implement phenology references (`phenology.py`)**

Phenology curves per crop (maize, rice, wheat, soybean) as functions of days after planting or GDD; growth-stage mapping; expected-index lookup.

- [ ] **Step 3.3: Implement crop-model interface + empirical fallback (`crop_model.py`)**

- Abstract `CropModelBackend`.
- `EmpiricalRegressionBackend` using index-yield regression with uncertainty band.
- `DSSATBackend` and `AquaCropBackend` stub classes with `run()` that raise `NotImplementedError` unless external executables are configured (production wiring without running models).
- `yield_forecast()` facade that selects backend by availability and returns `YieldForecast`.

- [ ] **Step 3.4: Implement disease library (`disease_library.py`)**

Structured pathogen entries: crop, pathogen, symptom keywords, spectral clues, conducive weather, confirm-step, IPM tier actions. Also abiotic stress entries.

- [ ] **Step 3.5: Implement differential diagnoser (`diagnoser.py`)**

`differential_diagnosis(symptoms, spectral_clues, crop, weather)` returns ranked list of `DiagnosisCandidate` with confidence computed from keyword match + weather match + spectral match; distinguishes biotic/abiotic.

- [ ] **Step 3.6: Implement scoring engine (`scoring.py`)**

`score_yield_and_health()` computes yield estimate ± band and health score (0-100) from stress-zone fraction, disease pressure, index deviation, and data-quality flags.

- [ ] **Step 3.7: Implement recommendation engine (`recommendation.py`)**

`build_roadmap()` maps zones/diagnoses to prioritized variable-rate fertilization/irrigation/IPM actions with timing and priority.

- [ ] **Step 3.8: Implement data-source abstraction (`data_sources.py`)**

`DataSourceResolver` detects available sources, flags staleness/cloud-cover, switches to field-data-only fallback, and records vintage notes.

- [ ] **Step 3.9: Update all sub-skill markdown files**

Each sub-skill now references the Python functions, includes concrete decision tables, thresholds, and quality-gate checklists.

- [ ] **Step 3.10: Verify engine imports and basic smoke tests**

Run: `python -c "from crop_yield_disease_diagnosis import indices, phenology, crop_model, diagnoser, scoring, recommendation, data_sources; print('OK')"`
Expected: OK.

---

## Task 4: Phase 2 — Main Harness

**Files:**
- Modify: `skills/main.md`
- Create: `src/crop_yield_disease_diagnosis/harness.py`

- [ ] **Step 4.1: Implement main harness (`harness.py`)**

`run_analysis(field_profile)` orchestrates:
1. data-source resolution,
2. framework selection,
3. index computation,
4. diagnosis,
5. scoring,
6. roadmap,
7. gate checks,
8. fallback routes.
Returns `AnalysisReport`.

- [ ] **Step 4.2: Update `skills/main.md`**

Document harness workflow, confidence-gate thresholds, fallback behavior, output schema, and how to invoke the Python API.

- [ ] **Step 4.3: Verify harness runs a synthetic end-to-end case**

Run: `python -c "from crop_yield_disease_diagnosis.harness import run_analysis; from crop_yield_disease_diagnosis.types import FieldProfile; r=run_analysis(FieldProfile(crop='maize', variety='test', stage='tasseling', location=(0,0), area_ha=1.0, planting_date='2026-01-01', data_sources=['field_data'], goal='yield_forecast')); print(r.model_dump_json(indent=2))"`
Expected: JSON report with all sections, no exception.

---

## Task 5: Phase 3 — Knowledge Pipeline

**Files:**
- Modify: `tools/knowledge_updater.py`

- [ ] **Step 5.1: Rewrite `knowledge_updater.py` as production tool**

Implement:
- Async/concurrent fetching of source feeds/pages via `requests` with retries, timeout, user-agent rotation.
- Feed parsing (RSS/Atom) for arXiv, MDPI, FAO.
- HTML scraping fallback using BeautifulSoup for FAO/CABI/USGS/Copernicus.
- Relevance scoring: keyword frequency × recency × source authority.
- Deduplication by URL SHA-256 12-hex hash and title normalization.
- Atomic append to `SECOND-KNOWLEDGE-BRAIN.md` with datestamp and hash comment.
- CLI `--dry-run`, `--sources`, `--limit`, `--since` flags.
- Logging and error resilience (continue on source failures).
- Unit-testable `Fetcher`, `Scorer`, `Appender`, `Updater` classes.

- [ ] **Step 5.2: Verify updater runs (dry-run) without network errors**

Run: `python tools/knowledge_updater.py --dry-run --limit 5`
Expected: completes, logs source attempts, no unhandled exceptions.

---

## Task 6: Phase 4 — Test Suite

**Files:**
- Modify: `tests/test-scenarios.md` → keep as human-readable scenario map.
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_indices.py`
- Create: `tests/test_phenology.py`
- Create: `tests/test_diagnoser.py`
- Create: `tests/test_scoring.py`
- Create: `tests/test_recommendation.py`
- Create: `tests/test_harness.py`
- Create: `tests/test_knowledge_updater.py`

- [ ] **Step 6.1: Implement index computation tests (`test_indices.py`)**

Tests for NDVI, EVI, NDRE, edge cases (zero denominator, nan), expected value ranges.

- [ ] **Step 6.2: Implement phenology tests (`test_phenology.py`)**

Tests expected index ranges per stage for maize/rice/wheat/soybean; GDD stage mapping.

- [ ] **Step 6.3: Implement disease differential tests (`test_diagnoser.py`)**

Scenario 2 (rice blast vs brown spot) and Scenario 6 (cold shock abiotic). Assert ≥2 candidates, biotic/abiotic labels, correct top candidate.

- [ ] **Step 6.4: Implement scoring tests (`test_scoring.py`)**

Scenario 5 (wheat AquaCrop inputs) with uncertainty band and sensitivity note; health score bounds.

- [ ] **Step 6.5: Implement recommendation tests (`test_recommendation.py`)**

Scenario 4 (3 N-deficiency zones) with zone-specific actions and priorities.

- [ ] **Step 6.6: Implement harness integration tests (`test_harness.py`)**

Scenario 1 (maize NDVI interpretation), Scenario 3 (imagery unavailable fallback). Assert fallback flags, uncertainty band, zone quantification.

- [ ] **Step 6.7: Implement knowledge updater tests (`test_knowledge_updater.py`)**

Mock network responses; test scoring, dedup, append, CLI parsing. No live network required.

- [ ] **Step 6.8: Run full pytest suite**

Run: `python -m pytest tests -v`
Expected: all tests pass, coverage ≥80%.

---

## Task 7: Phase 5 — Cluster Integration

**Files:**
- Modify: `CLAUDE.md`
- Modify: `PROJECT-detail.md`
- Modify: `skills/sub-evaluation-framework-selector.md`
- Modify: `skills/sub-scoring-engine.md`
- Modify: `skills/sub-improvement-roadmap.md`

- [ ] **Step 7.1: Document cluster sharing**

In each relevant file add a section:
- `framework-selector` and `scoring-engine` are designed to be reusable by `microclimate-weather-forecast-analyzer` (133), `livestock-farm-management-plan` (134), and `micro-urban-agriculture-design` (232).
- Provide import/invocation conventions and note which parameters are crop/livestock/urban-neutral.

- [ ] **Step 7.2: Add cluster cross-links in root docs**

Add `## Cluster Integration` section to `CLAUDE.md` and `PROJECT-detail.md` with paths and shared sub-skill matrix.

---

## Task 8: Phase Tracking & Final Verification

**Files:**
- Modify: `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`

- [ ] **Step 8.1: Rewrite tracking file with all phases and tasks marked done**

Each phase has detailed task list with `[x]`. Final line states: `All phases 100% complete.`

- [ ] **Step 8.2: Final verification pass**

Run: `python -m pytest tests -v` and `python tools/knowledge_updater.py --dry-run --limit 5`
Expected: tests pass, updater dry-run succeeds.

---

## Self-Review Checklist

1. **Spec coverage:** Every phase (0-5) maps to tasks above.
2. **Placeholder scan:** No TODO/TBD remain in code; markdown may reference external model executables (DSSAT/AquaCrop) but code must handle their absence gracefully.
3. **Type consistency:** Pydantic models and function signatures match across modules.
4. **No live model execution:** DSSAT/AquaCrop are wired but not invoked; only empirical regression runs.
