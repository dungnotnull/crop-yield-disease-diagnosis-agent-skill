# Test Scenarios — Crop Yield Forecast & Plant Disease Diagnosis (Idea 213)

## Scenario 1 — Maize NDVI interpretation
**Input:** Sentinel-2 NDVI map of maize at tasseling, one low-vigor patch.
**Expected:** Index+sensor+date stated, stress zone quantified, cause hypotheses, yield band.
**Pass:** Phenology-relative interpretation; uncertainty band present.

## Scenario 2 — Disease differential
**Input:** Rice leaves with brown lozenge lesions, humid weather.
**Expected:** Ranked differential (e.g., blast vs. brown spot), confidence, confirm-step; IPM-first plan.
**Pass:** ≥2 candidates; biotic/abiotic distinguished.

## Scenario 3 — Imagery unavailable
**Input:** Only soil + weather data, no cloud-free imagery.
**Expected:** Field-data-only mode, lower confidence, staleness flagged.
**Pass:** Fallback used; confidence reduced.

## Scenario 4 — Variable-rate roadmap
**Input:** Field with 3 N-deficiency zones.
**Expected:** Zone-specific variable-rate N recommendations prioritized by yield impact.
**Pass:** Actions tied to zones with timing.

## Scenario 5 — Yield forecast with band
**Input:** Wheat field, AquaCrop inputs available.
**Expected:** Yield estimate ± uncertainty, sensitivity to rainfall stated.
**Pass:** Band + sensitivity present.

## Scenario 6 — Abiotic vs. biotic
**Input:** Uniform yellowing across whole field after cold snap.
**Expected:** Diagnoser leans abiotic (cold/nutrient), not pathogen; advises against spraying.
**Pass:** Correct biotic/abiotic call; no unnecessary chemicals.
