# 37. Market Research v2 Seed Plan

## Purpose

This file defines the *next* suspect-batch direction after the current
`market_research_v1` specialist loop is paused.

It is not the full `market_research_v2` implementation yet.

It is the seed-design rule for that next batch.

## Current Gate

The current pause gate is:

- [v11_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v11_continuation_readiness_v1.json)

The current batch-design report is:

- [next_suspect_batch_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_design_v1.json)

## Current Reading

The repo should now read the current specialist state as:

1. the present `market_research_v1` loop is paused
2. the next step is not another local replay lane
3. the next batch should be designed by **missing context archetypes**

## Observed Closed-Slice Geography

The current closed-slice geography is still too narrow.

Observed rows in `next_suspect_batch_design_v1` collapse into:

- `theme_light`
- `balanced_turnover`
- `narrow_sector`

So the next batch should *not* just add more names from the same geometry.

## Missing Archetypes

The current missing-archetype shortlist is:

1. `theme_loaded + balanced_turnover + broad_sector`
2. `theme_loaded + balanced_turnover + narrow_sector`
3. `theme_light + concentrated_turnover + broad_sector`

These are the first seed targets for `market_research_v2`.

## Design Rule

`market_research_v2_seed` should:

1. stay liquid and interpretable
2. add symbols that stress the missing archetypes above
3. avoid random sample growth
4. remain compatible with the free bootstrap path

## Non-goal

The next batch should **not**:

1. become a blind size expansion
2. become per-sector training
3. restart wide replay before the new batch is prepared

## Immediate Next Step

Before any new replay:

1. define a seed universe for `market_research_v2`
2. map each new symbol to one intended missing archetype
3. keep the seed conservative enough to remain auditable

## Current Seed Manifest

The first seed universe and manifest now exist:

- [config/universes/market_research_v2_seed.txt](D:/Creativity/A-Share-Quant_TrY/config/universes/market_research_v2_seed.txt)
- [config/market_research_v2_seed_manifest.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_v2_seed_manifest.yaml)
- [config/market_research_v2_seed_free_data_bootstrap.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_v2_seed_free_data_bootstrap.yaml)

The corresponding audit is:

- [next_suspect_batch_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v1.json)

Current result:

- `base_universe_count = 40`
- `seed_universe_count = 9`
- `new_symbol_count = 9`
- `overlap_with_market_v1_count = 0`
- `missing_archetype_count = 0`
- `ready_to_bootstrap_market_research_v2_seed = true`

So `market_research_v2_seed` is now prepared as a conservative,
context-targeted next batch rather than a random watchlist expansion.

## Bootstrap Status

`market_research_v2_seed` is now a runnable pack, not only a manifest.

The first audit is:

- [market_research_data_audit_v2_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_seed.json)

Current summary:

- `canonical_ready_count = 6`
- `canonical_partial_count = 0`
- `derived_ready_count = 3`
- `baseline_ready = true`

## First Suite Read

The first strategy-suite replay is:

- [20260329T130402Z_0e1d8809_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130402Z_0e1d8809_comparison.json)

Current reading:

1. `mainline_trend_c` is best on return and capture
2. `mainline_trend_b` is lowest drawdown
3. the pack is interpretable enough to enter the next validation layer

## Validation Status

The first four-pack validation that includes `market_research_v2_seed` is now:

- [20260329T130537Z_f0a9da05_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130537Z_f0a9da05_comparison.json)
- [specialist_alpha_analysis_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v3.json)

Current reading:

1. broad freeze remains intact
2. `buffer_only_012` remains the broad stability leader
3. `market_research_v2_seed` now contributes narrow specialist pockets
4. but `market_research_v1` still remains the primary specialist substrate

## First Narrow Replay

The first narrow replay inside `market_research_v2_seed` is now:

- [market_v2_seed_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_trade_divergence_capture_c_v1.json)
- [market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json)
- [market_v2_seed_q4_specialist_window_opening_603986_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_specialist_window_opening_603986_v1.json)

Current reading:

1. `603986` is the dominant q4/C capture driver
2. inside the q4 slice, it contains a clean opening edge on `2024-12-12`
3. but the same symbol also carries a positive trade into q4 from `2024-09-27`
4. so the current q4/C read should be treated as a mixed opening-plus-carry pocket, not yet a clean new family boundary

The first q4/C acceptance gate is now also in:

- [market_v2_seed_q4_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_capture_slice_acceptance_v1.json)

Current verdict:

- `acceptance_posture = close_market_v2_seed_q4_capture_slice_as_opening_plus_carry`
- `do_continue_q4_capture_replay = false`

So the current `v2_seed / q4 / C` lane should now be treated as closed at the
slice level.

## First Q3 Drawdown Replay

The first narrow drawdown replay inside `market_research_v2_seed / 2024_q3 /
mainline_trend_c` is now also in:

- [market_v2_seed_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_trade_divergence_quality_c_v1.json)
- [market_v2_seed_q3_symbol_timeline_603986_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_symbol_timeline_603986_quality_c_v1.json)
- [market_v2_seed_q3_cycle_mechanism_603986_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_cycle_mechanism_603986_c_v1.json)

Current reading:

1. `603986` is the dominant q3/C drawdown symbol
2. its negative side is a clean `entry_suppression_avoidance`
3. but the same symbol also carries a positive
   `entry_suppression_opportunity_cost`
4. so the q3/C read is also mixed rather than a clean new drawdown-family
   frontier

The first q3/C acceptance gate is now also in:

- [market_v2_seed_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_drawdown_slice_acceptance_v1.json)

Current verdict:

- `acceptance_posture = close_market_v2_seed_q3_drawdown_slice_as_avoidance_plus_opportunity_cost`
- `do_continue_q3_drawdown_replay = false`

So the current `v2_seed / q3 / C` lane should also now be treated as closed
at the slice level.

## Continuation Gate

The current continuation gate is now also explicit:

- [market_v2_seed_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_continuation_readiness_v1.json)

Current verdict:

- `all_open_v2_seed_lanes_closed = true`
- `v2_seed_baseline_ready = true`
- `v2_seed_contributes_specialist_pockets = true`
- `recommended_next_phase = hold_market_v2_seed_as_secondary_substrate_and_wait_for_next_batch_refresh`
- `do_continue_current_v2_seed_replay = false`

So `market_research_v2_seed` should now be treated as a real, useful, and
bounded secondary substrate rather than a batch that automatically deserves a
third local replay lane.
