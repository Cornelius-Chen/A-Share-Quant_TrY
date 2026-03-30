# V1.2 Carry Row Hunt 000725 V1

## Purpose
- Check the first `basis_spread_diversity` target inside `market_research_v4_carry_row_diversity_refresh` without widening replay.
- Decide whether `000725` adds an active structural lane or should be closed as an inactive carry-hunt symbol.

## Inputs
- `reports/analysis/v12_carry_row_hunting_strategy_v1.json`
- `reports/analysis/market_v4_q2_trade_divergence_capture_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_timeline_000725_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_000725_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_000725_a_v1.json`

## Result
- `000725` closes as `no_active_structural_lane`
- `pnl_delta = 0.0`
- `opening_present = false`
- `persistence_present = false`
- `identical_trade_count_signature = true`
- `lane_changes_carry_reading = false`

## Interpretation
- `000725` was selected for `basis_spread_diversity`, but the checked q2/A lane does not currently express a specialist-owned edge.
- The correct posture is to close this symbol-specific hunt rather than force a carry interpretation out of a zero-delta lane.
- The next single-symbol hunt should move to `600703` while keeping the no-widening discipline intact.
