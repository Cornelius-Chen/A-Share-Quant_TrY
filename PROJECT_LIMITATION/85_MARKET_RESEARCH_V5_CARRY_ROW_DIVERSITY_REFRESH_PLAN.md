# V1.2 Market Research V5 Carry Row Diversity Refresh Plan

## Purpose
- Convert the frozen `v5` criteria into a first executable manifest.

## Batch Posture
- `market_research_v5_carry_row_diversity_refresh`
- `criteria_first_true_carry_plus_clean_persistence_refresh`

## Current Seed Shape
- `true_carry_row`: 2 symbols
- `clean_persistence_row`: 2 symbols

## Current Intended Effect
- Add new symbols outside the combined `v1 + v2_seed + v2_refresh + v3_seed + v4_refresh` base
- Fill the explicit training gaps:
  - `2` true carry rows
  - `2` clean persistence rows
- Keep `opening_led` frozen and keep the locally exhausted `v4 / q2 / A` replay zone out of scope
## 2026-03-30 Update: v5 refresh bootstrapped and entered active validation
- Added the full v5 data chain configs: free-data bootstrap, sector mapping, concept mapping, derived data, audit, and strategy suite.
- `reports/data/market_research_data_audit_v5_carry_row_diversity_refresh.json` now reads `baseline_ready = true`.
- Pack-level suite report is `reports/20260330T041310Z_130eb2ed_comparison.json`; inside the v5 pack, `mainline_trend_b` and `mainline_trend_c` tie as the strongest local strategies.
- Eight-pack time-slice validation report is `reports/20260330T041451Z_b6297292_comparison.json` and specialist overlay is `reports/analysis/specialist_alpha_analysis_v8.json`.
- `v5` is now a live, bounded substrate in the active specialist geography, but it has not yet changed the core `V1.2` bottleneck: we still need additional true carry rows and clean persistence rows.
## 2026-03-30 Update: v5 first lane 002273 closed as opening-led
- Added q2/B divergence, timeline, opening, persistence, and first-lane acceptance artifacts for `002273`.
- The first `v5` lane is real and positive, but it does not yet repair the core `carry_row_diversity_gap` because it closes as an opening-led lane without clean persistence.
- The next legal action is a short `v5` phase-level check before any second-lane widening.
## 2026-03-30 Update: v5 bounded manifest exhausted without repairing the gap
- Added the last true-carry probe artifacts for `000099`, including timeline, opening, persistence, and `market_v5_q2_last_carry_probe_acceptance_000099_v1.json`.
- Added `reports/analysis/v12_v5_exhaustion_phase_check_v1.json` and `PROJECT_LIMITATION/90_V12_V5_EXHAUSTION_PHASE_CHECK_V1.md`.
- `v5` is now closed as a bounded-but-non-repairing refresh: it used its legal lanes without adding acceptance-grade true carry or clean persistence rows.
- The next legal move is no longer local `v5` replay; it is the next criteria-first entry, frozen in `reports/analysis/v12_next_refresh_entry_v3.json`.