# Cluster Integration — science-industry

## Shared Sub-skills

The `crop-yield-disease-diagnosis` skill (Idea 213) contributes the following sub-skills for reuse across the `science-industry` cluster:

| Sub-skill | File | Reusable by |
|-----------|------|-------------|
| Evaluation Framework Selector | `skills/sub-evaluation-framework-selector.md` | 133, 134, 232 |
| Scoring Engine | `skills/sub-scoring-engine.md` | 133, 134, 232 |
| Improvement Roadmap | `skills/sub-improvement-roadmap.md` | 133, 134, 232 |

## Sibling Skills

| Idea | Slug | Path | How it reuses 213 |
|------|------|------|-------------------|
| 133 | microclimate-weather-forecast-analyzer | `D:\skills\microclimate-weather-forecast-analyzer` | Uses `sub-scoring-engine` for forecast-skill scoring and `sub-improvement-roadmap` for action prioritization; weather inputs feed 213's data_sources resolver |
| 134 | livestock-farm-management-plan | `D:\skills\livestock-farm-management-plan` | Uses `sub-evaluation-framework-selector` to pick NRC/woah frameworks; uses `sub-scoring-engine` for herd-health KPIs; uses `sub-improvement-roadmap` for biosecurity action plans |
| 232 | micro-urban-agriculture-design | `D:\skills\micro-urban-agriculture-design` | Uses `sub-evaluation-framework-selector` to choose DLI/VPD/EC-pH frameworks; uses `sub-scoring-engine` for design compliance; uses `sub-improvement-roadmap` for system upgrades |

## Python Reuse Conventions

The shared logic is implemented as generic engine functions:

- `harness.select_framework(profile)` — accepts any profile with `crop`/`stage`.
- `scoring.score_yield(profile, index_values, stress_zones, data_quality)` — accepts generic index/stress inputs.
- `recommendation.build_roadmap(stress_zones, diagnosis, crop)` — accepts generic stress-zone-like objects.

When a sibling skill invokes these, it can map its own intake schema to `FieldProfile` or pass equivalent typed dictionaries.

## Cross-References Added

- `CLAUDE.md` — cluster integration section.
- `PROJECT-detail.md` — cluster integration section.
- `skills/sub-evaluation-framework-selector.md` — cluster-neutral interface note.
- `skills/sub-scoring-engine.md` — cluster-neutral interface note.
- `skills/sub-improvement-roadmap.md` — cluster-neutral interface note.
