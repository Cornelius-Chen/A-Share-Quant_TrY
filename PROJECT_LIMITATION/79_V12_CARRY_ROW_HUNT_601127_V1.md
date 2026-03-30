# V1.2 Carry Row Hunt 601127 V1

## Purpose
- Check the second `carry_duration_diversity` target inside `market_research_v4_carry_row_diversity_refresh`.
- Decide whether `601127` becomes the first active carry-supporting lane after the prior inactive basis-spread and duration-track checks.

## Inputs
- `reports/analysis/v12_carry_row_hunting_strategy_v1.json`
- `reports/analysis/market_v4_q2_trade_divergence_capture_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_timeline_601127_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_601127_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_601127_a_v1.json`

## Result
- `601127` closes as `no_active_structural_lane`
- `pnl_delta = 0.0`
- `opening_present = false`
- `persistence_present = false`
- `identical_trade_count_signature = true`
- `lane_changes_carry_reading = false`

## Interpretation
- The second `carry_duration_diversity` target also does not express a specialist-owned edge in `v4 / q2 / A`.
- At this point, the checked high-priority `basis_spread_diversity` and `carry_duration_diversity` tracks inside the current v4 hunt have all closed inactive.
- The correct next step is a short phase-level check before touching lower-priority tracks such as `cross_dataset_carry_reuse` or `exit_alignment_diversity`.
