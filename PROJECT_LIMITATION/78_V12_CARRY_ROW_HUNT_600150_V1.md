# V1.2 Carry Row Hunt 600150 V1

## Purpose
- Check the first `carry_duration_diversity` target inside `market_research_v4_carry_row_diversity_refresh`.
- Decide whether `600150` adds an active structural lane after the inactive `basis_spread_diversity` checks.

## Inputs
- `reports/analysis/v12_carry_row_hunting_strategy_v1.json`
- `reports/analysis/market_v4_q2_trade_divergence_capture_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_timeline_600150_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_600150_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_600150_a_v1.json`

## Result
- `600150` closes as `no_active_structural_lane`
- `pnl_delta = 0.0`
- `opening_present = false`
- `persistence_present = false`
- `identical_trade_count_signature = true`
- `lane_changes_carry_reading = false`

## Interpretation
- The first `carry_duration_diversity` target still does not express a specialist-owned edge in `v4 / q2 / A`.
- This means the current v4 hunt has now eliminated both checked `basis_spread_diversity` symbols and the first checked `carry_duration_diversity` symbol.
- The next bounded hunt should move to the second duration target: `601127`.
