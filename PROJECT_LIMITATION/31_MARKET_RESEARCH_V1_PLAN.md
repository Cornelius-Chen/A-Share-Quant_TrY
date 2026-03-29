# 31. Market Research v1 Plan

## Purpose

`market_research_v1` is the next controlled expansion pack after
`market_research_v0`.

Its role is not "go full market now." Its role is narrower:

1. enlarge the liquid mixed-market universe
2. create a better chance of producing a larger suspect batch
3. stress the current regime / hierarchy / theme logic beyond the current v0
   pack

## Why v1 now

Current state after `feature-pack-c` and `U1`:

1. replay queue is paused
2. `feature-pack-c` closed as explanatory
3. `U1 lightweight geometry` succeeded
4. `U2 pocket clustering` is not ready because the current suspect set is too
   small and already separable

So the next productive move is not another local feature loop. It is to create
the conditions for a **larger future suspect batch**.

## Design rule

`market_research_v1` should be:

1. strictly larger than `market_research_v0`
2. built only from already-proven or already-used symbols
3. still interpretable by bucket
4. cheap enough to bootstrap from the free-data path

## Construction rule

For this repo, `market_research_v1` is built as:

1. the full `market_research_v0` universe
2. plus the remaining symbols already proven in:
   - `baseline_research_v1`
   - `theme_research_v1`
3. without adding a fresh layer of uncertain symbols yet

This keeps the expansion conservative:

- bigger than `v0`
- broader than either `baseline` or `theme`
- but still based on symbols that are already operational in the repo

## Immediate goals

The first `market_research_v1` cycle should only aim to:

1. bootstrap raw daily bars / indices / security master / adjustment factors
2. bootstrap daily sector mapping
3. prepare the pack for later concept mapping and derived-table generation

It does **not** need to complete full specialist replay immediately.

## Success signal

`market_research_v1` is useful if it gives the repo:

1. a larger liquid mixed-market pack than `v0`
2. a plausible next source of new suspect pockets
3. a better future test bed for whether `U2` should ever become ready

## Current Status

`market_research_v1` has now completed its first full pack cycle.

Completed artifacts:

1. raw bars / indices / reference tables
2. sector mapping
3. concept mapping
4. derived tables
5. pack audit
6. first strategy suite replay

Current evidence:

- [market_research_data_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v1.json)
  shows:
  - `canonical_ready_count = 6`
  - `canonical_partial_count = 0`
  - `derived_ready_count = 3`
  - `baseline_ready = true`
- [20260329T111733Z_3e700662_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T111733Z_3e700662_comparison.json)
  shows:
  - `mainline_trend_c` best total return and capture
  - `mainline_trend_a` lowest drawdown

So `market_research_v1` is now an operational broad substrate. It still should
not be treated as a new default-validation pack, but it is ready to supply the
next future suspect batch.

## First Suspect Signal

The first downstream validation layer is now also complete:

- [20260329T112015Z_d5db1be9_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T112015Z_d5db1be9_comparison.json)
  keeps the broad freeze stable
- [specialist_alpha_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v2.json)
  shows that `market_research_v1` already produces new specialist opportunity
  geography, especially:
  - drawdown pocket:
    `market_research_v1 / 2024_q3 / mainline_trend_c`
  - capture pockets:
    `market_research_v1 / 2024_q2 / mainline_trend_a|b|c`

So the pack has already crossed the threshold from "future expansion idea" to
"actual next suspect substrate."

## First Pocket Classification

The first market-v1 drawdown pocket has now also been replayed:

- [market_v1_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_c_v1.json)
  identifies `300308` as the dominant positive symbol in
  `market_research_v1 / 2024_q3 / mainline_trend_c`
- [market_v1_q3_cycle_mechanism_300308_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_c_v1.json)
  classifies that symbol as clean reuse of the established baseline-style
  drawdown family:
  - `entry_suppression_avoidance`
  - `earlier_exit_loss_reduction`

So the first `market_research_v1` replay result is healthy:
it does not expand the family frontier, but it confirms the broader pack is
still interpretable under the current taxonomy.

## First Q2 Capture Classification

The first market-v1 q2 capture replay is now also classified:

- [market_v1_q2_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_trade_divergence_capture_c_v1.json)
  identifies `300502` as the dominant positive symbol in
  `market_research_v1 / 2024_q2 / mainline_trend_c`
- [market_v1_q2_specialist_window_persistence_300502_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_persistence_300502_v1.json)
  shows the edge is persistence-driven:
  - specialist keeps the window alive on `2024-06-17`
  - both broad anchors exit because `assignment_became_junk`
  - specialist remains `late_mover` with `structure_intact`

So the first q2 capture pocket is not another opening-only story. It is a
clean market-v1 persistence edge.

## Q2 Capture Slice Status

That q2 line is now formally closed at slice level:

- [market_v1_q2_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_capture_slice_acceptance_v1.json)
  concludes:
  - `close_market_q2_capture_slice_as_mixed_opening_plus_persistence`
  - `do_continue_q2_capture_replay = false`

So q2 should now be treated as a bounded mixed slice rather than a replay lane
that stays open by default.

## Q3 Drawdown Slice Status

The q3 drawdown line is now also formally closed:

- [market_v1_q3_cycle_mechanism_300308_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_b_v1.json)
  and
  [market_v1_q3_cycle_mechanism_300308_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_c_v1.json)
  show the same baseline-style mechanism map across `B/C`
- [market_v1_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cross_strategy_cycle_consistency_v1.json)
  confirms:
  - `identical_negative_cycle_map = true`
  - `shared_negative_mechanism_count = 3`
- [market_v1_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_drawdown_slice_acceptance_v1.json)
  concludes:
  - `close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse`
  - `shared_top_driver = 300308`
  - `do_continue_q3_drawdown_replay = false`

So q3 should now be treated as a cross-strategy-stable drawdown slice under the
current family inventory.

## First Q4 Drawdown Classification

The first q4 drawdown replay is now also in:

- [market_v1_q4_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_trade_divergence_quality_c_v1.json)
  identifies `002371` as the dominant positive symbol in
  `market_research_v1 / 2024_q4 / mainline_trend_c`
- [market_v1_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_002371_c_v1.json)
  shows the edge is only:
  - `entry_suppression_avoidance`

So the first q4 result does **not** open a new family frontier. It lowers the
novelty reading for q4, but q4 should remain open until at least one more
strong q4 symbol is checked.

## Q4 Drawdown Slice Status

That second q4 symbol is now also in:

- [market_v1_q4_cycle_mechanism_000977_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_000977_c_v1.json)
  and it widens q4 beyond pure avoidance:
  - `preemptive_loss_avoidance_shift`
  - `earlier_exit_loss_reduction`
- [market_v1_q4_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_drawdown_slice_acceptance_v1.json)
  now concludes:
  - `close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix`
  - `top_positive_symbols = [002371, 000977, 000858]`
  - `do_continue_q4_drawdown_replay = false`

So q4 should now be treated as a bounded mixed drawdown slice rather than an
open replay lane.

## Non-goal

`market_research_v1` is **not**:

1. a full-market pack
2. a new default validation pack
3. a reason to reopen replay queue immediately

It is an expansion substrate, not a decision shortcut.

## Sector/Theme Context Read

The first context audit for `market_research_v1` is now in:

- [sector_theme_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/sector_theme_context_audit_v1.json)

It says:

- q2 is `theme_loaded + concentrated_turnover`
- q3 is `hot_sector + broad_sector + balanced_turnover`
- q4 is `theme_light + concentrated_turnover`

So the correct next step is not per-sector training.

The correct next step is:

1. `theme_load_plus_turnover_concentration_context`
2. `sector_state_heat_breadth_context`

That first context group is now validated into:

- [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json)
  with:
  - `recommended_next_feature_branch = conditioned_late_quality_on_theme_turnover_context`
  - `defer_sector_heat_branch = true`
