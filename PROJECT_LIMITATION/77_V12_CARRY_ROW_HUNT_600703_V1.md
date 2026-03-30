# V1.2 Carry Row Hunt 600703 V1

## Purpose
- Check the second `basis_spread_diversity` target inside `market_research_v4_carry_row_diversity_refresh`.
- Confirm whether `600703` adds an active carry-hunt lane after `000725` closed inactive.

## Inputs
- `reports/analysis/v12_carry_row_hunting_strategy_v1.json`
- `reports/analysis/market_v4_q2_trade_divergence_capture_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_timeline_600703_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_600703_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_600703_a_v1.json`

## Result
- `600703` closes as `no_active_structural_lane`
- `pnl_delta = 0.0`
- `opening_present = false`
- `persistence_present = false`
- `identical_trade_count_signature = true`
- `lane_changes_carry_reading = false`

## Interpretation
- The second `basis_spread_diversity` target does not currently express a specialist-owned edge in `v4 / q2 / A`.
- This is now two consecutive inactive basis-spread hunts inside the current `v4` substrate.
- The next bounded hunt should move to the first `carry_duration_diversity` target: `600150`.
