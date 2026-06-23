# SECOND-KNOWLEDGE-BRAIN — Crop Yield Forecast & Plant Disease Diagnosis

## Core Concepts & Frameworks
- **Vegetation indices** — NDVI = (NIR−Red)/(NIR+Red); EVI (soil/atmosphere-corrected); NDRE (red-edge, better at high biomass/N status); GNDVI.
- **Phenology** — interpret indices relative to crop growth stage; NDVI follows a season curve (emergence→peak→senescence).
- **Crop simulation models** — DSSAT, APSIM, FAO AquaCrop (water-driven yield); GDD (growing degree days) for stage timing.
- **Plant pathology** — symptom recognition, differential diagnosis, Koch's postulates; biotic vs. abiotic stress distinction.
- **IPM (Integrated Pest Management)** — monitoring, economic thresholds, cultural/biological/chemical controls in that priority.
- **Precision agriculture** — variable-rate fertilization/irrigation by management zone.

## Key Reference Frameworks (citable)
| Framework | Source | Use |
|-----------|--------|-----|
| NDVI/EVI | Rouse 1974; Huete 2002 | Vegetation vigor |
| FAO AquaCrop | FAO | Water-limited yield |
| DSSAT/APSIM | DSSAT Foundation/CSIRO | Yield simulation |
| IPM | FAO/EPA | Disease/pest management |

## Key Research Papers
| Title | Authors | Year | Venue | Link | Relevance |
|-------|---------|------|-------|------|-----------|
| Monitoring Vegetation Systems (NDVI) | Rouse et al. | 1974 | NASA | ntrs.nasa.gov | Index origin |
| Overview of EVI | Huete et al. | 2002 | RSE | sciencedirect | Improved index |

## State-of-the-Art Methods & Tools
Sentinel-2 (10m, red-edge); Landsat 8/9; PlanetScope; drone multispectral (RedEdge); deep-learning disease classifiers (PlantVillage); Google Earth Engine.

## Sentinel-2 Band Reference
| Band | Name | Resolution (m) | Use |
|------|------|----------------|-----|
| B2 | Blue | 10 | Atmospheric correction |
| B3 | Green | 10 | GNDVI, EVI |
| B4 | Red | 10 | NDVI, EVI, NDRE denominator |
| B5 | Vegetation red edge 1 | 20 | NDRE numerator |
| B6 | Vegetation red edge 2 | 20 | Red-edge indices |
| B8 | NIR | 10 | NDVI, EVI, GNDVI |
| B8A | Narrow NIR | 20 | Red-edge indices |
| B11 | SWIR 1 | 20 | Moisture/stress |
| B12 | SWIR 2 | 20 | Moisture/stress |

## Common Crop Phenology Reference (NDVI expected ranges)
| Crop | Emergence | Vegetative | Flowering/Heading | Grain-fill | Senescence |
|------|-----------|------------|-------------------|------------|------------|
| Maize | 0.15–0.25 | 0.40–0.65 | 0.70–0.85 (tasseling/silking) | 0.60–0.75 | 0.25–0.40 |
| Rice | 0.20–0.30 | 0.45–0.65 | 0.70–0.85 (heading) | 0.55–0.70 | 0.20–0.35 |
| Wheat | 0.15–0.25 | 0.40–0.60 | 0.65–0.80 (heading) | 0.50–0.65 | 0.20–0.35 |
| Soybean | 0.15–0.25 | 0.40–0.65 | 0.70–0.85 (R1–R2) | 0.55–0.75 | 0.25–0.40 |

## Disease/Stress Signature Quick Reference
| Symptom pattern | Spectral clue | Most likely cause class | Confirm step |
|-----------------|---------------|------------------------|--------------|
| Brown lozenge lesions, humid | NDRE drop, NDVI moderate | Biotic (fungal) | Lesion mount / lab PCR |
| Uniform yellowing after cold snap | NDVI/EVI uniformly low, NDRE low | Abiotic (cold/nutrient) | Soil N test, weather log |
| Patchy low vigor, field edges | NDVI low patches | Biotic/abiotic mixed | Scout patches, soil sample |
| V-shaped tan lesions on maize | NDRE collapse in lesion zone | Biotic (Goss's wilt / gray leaf spot) | Lab isolate |
| Rolled leaves, wilting midday | NDVI high in morning, drops noon | Abiotic (water stress) | Soil moisture probe |

## IPM Threshold Examples
| Pest/disease | Action threshold | First response |
|--------------|------------------|----------------|
| Rice blast | >5% tillers infected | Resistant variety + K balance |
| Maize gray leaf spot | >5% leaf area at silking | Fungicide only if weather stays wet |
| N deficiency | NDRE <25th percentile of field | Variable-rate sidedress N |

## Authoritative Data Sources
Copernicus Open Access Hub; USGS EarthExplorer; FAO; CABI Crop Protection Compendium; PlantVillage; national ag extension services.

## Analytical Frameworks
NDVI-phenology deviation; index-to-yield regression/model coupling; spectral+visual differential diagnosis; IPM economic-threshold decision.

## Self-Update Protocol
`knowledge_updater.py` weekly: crawl RS/agronomy/pathology sources; dedup by URL hash; append below.

## Knowledge Update Log
- 2026-06-18 — Seed: indices, crop models, IPM, pathology basics captured.
