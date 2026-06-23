---
name: sub-improvement-roadmap
description: Recommends precision fertilization, irrigation, and IPM actions tied to stress zones and disease diagnosis. Shared across science-industry cluster.
---

## Purpose
Convert analysis into prioritized, zone-specific field actions. Uses `recommendation.py`.

## Inputs
Stress zones, diagnosis, yield/health score.

## Procedure
1. For each stress zone, recommend the corrective input (variable-rate N/P/K, irrigation depth, drainage).
2. For diagnosed disease, recommend **IPM** measures in priority order: cultural → biological → chemical (with threshold and label caution).
3. Prioritize by yield-impact and timing window.
4. Add monitoring/recheck cadence.

## Python API

```python
from crop_yield_disease_diagnosis.recommendation import build_roadmap

roadmap = build_roadmap(stress_zones, top_diagnosis, crop=profile.crop)
```

## Outputs
`ActionItem[]`: zone/issue | action | ipm_tier | timing | priority | economic_threshold_note.

## Quality Gate
- Actions tied to specific zones/diagnosis.
- IPM ordering respected (chemical last).
- Timing given.
- Shared interface: roadmap builder works with generic stress-zone-like inputs so cluster skills can reuse it.
