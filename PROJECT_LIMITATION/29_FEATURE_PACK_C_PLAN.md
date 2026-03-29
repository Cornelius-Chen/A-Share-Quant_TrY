# 29. Feature-Pack-C Plan

## Goal

`feature-pack-c` is the first post-`feature-pack-b` feature cycle.

It exists because both `feature-pack-b` tracks are now closed as
negative-but-informative:

- track A (`theme_q4 / 002902 / B`) proved that hierarchy/approval edges are
  explainable, but not cheaply fixable through local threshold relief
- track B (`theme_q2 / 002466 / C`) proved that concept-to-late variants can
  repair one bridge row, but at an unacceptable alpha cost

So `feature-pack-c` must **not** be a wider threshold search.

Its job is to add a small number of more causal local features that explain
*why* pockets drop into `junk` or fail late-mover admission.

## Entry Condition

`feature-pack-c` starts only when all of the following are true:

1. the replay queue is already paused
2. `feature-pack-b` track A is closed
3. `feature-pack-b` track B is closed
4. the next likely gain comes from local causal features, not more replay

The current readiness report is:
[feature_pack_c_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_readiness_v1.json)

## Scope

The pack is intentionally small. Start with four feature groups only:

1. `fallback_reason_decomposition`
   - break the current fallback state into more useful local causes
   - target pockets:
     - `theme_q4 / 002902 / B`
     - `theme_q2 / 002466 / C`

2. `late_quality_residual_components`
   - keep the scalar late-quality margin, but also expose the parts that create
     the deficit
   - target pockets:
     - `theme_q4 / 002902 / B`
     - `theme_q2 / 002466 / C`

3. `approval_threshold_history`
   - capture short approval-edge state, not just same-day threshold distance
   - target pocket:
     - `theme_q4 / 002902 / B`

4. `concept_support_excess_to_late_threshold`
   - express concept support relative to late-mover deficit, not as raw support
   - target pocket:
     - `theme_q2 / 002466 / C`

## First Read

The first pack-C read is now available:
[feature_pack_c_fallback_reason_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_fallback_reason_analysis_v1.json)

Current conclusion:

- `row_count = 8`
- `dominant_component_counts = {late_quality: 6, score_margin: 2}`
- `approval_edge_active_count = 2`
- `concept_supported_count = 4`
- `recommended_first_feature_group = fallback_reason_decomposition_plus_late_quality_residuals`

This means the correct pack-C opening sequence is no longer generic:

1. decompose fallback rows
2. immediately expose `late_quality` residual structure
3. only after that, add approval-threshold history and concept-support excess

So the pack has now started, and its first practical direction is:

- `late_quality`-led local causal features first
- approval and concept support as secondary context, not as the lead fix

## Second Read

The first residual-component read is now available:
[feature_pack_c_late_quality_residuals_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_late_quality_residuals_v1.json)

Current conclusion:

- `row_count = 8`
- `dominant_residual_component_counts = {stability: 3, liquidity: 3, sector_strength: 2}`
- `concept_boost_active_count = 1`
- `raw_below_threshold_count = 8`
- `recommended_second_feature_group = late_quality_stability_liquidity_context`

This means pack-C should still stay inside the raw late-quality stack:

1. keep concept support as secondary context only
2. do not reopen approval-threshold tuning as the lead lane
3. treat the next useful pack-C move as a component-context read around
   `stability/liquidity`, while keeping `sector_strength` as the secondary
   raw contributor

In other words, the suspect pockets are not asking for a wider concept bridge.
They are asking for a better explanation of why the raw late-quality stack is
weak on those rows.

## Third Read

The first `stability/liquidity` context read is now available:
[feature_pack_c_stability_liquidity_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_stability_liquidity_context_v1.json)

Current conclusion:

- `row_count = 6`
- `local_context_counts = {turnover_share_led: 3, mixed_stability_liquidity: 3}`
- `volatility_led = 0`
- `recommended_third_feature_group = late_quality_turnover_share_context`

This means the next pack-C move should be even narrower:

1. do not start with a volatility pack
2. keep `stability` in view, but treat it as part of a mixed residual bucket
3. promote `turnover_share` into the next explicit local-causal feature lane

## Fourth Read

The first turnover-share context read is now available:
[feature_pack_c_turnover_share_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_turnover_share_context_v1.json)

Current conclusion:

- `row_count = 3`
- `local_turnover_context_counts = {sector_peer_dominance: 1, balanced_share_weakness: 2}`
- `broad_attention_deficit = 0`
- `recommended_fourth_feature_group = late_quality_balanced_turnover_context`

This means the turnover-share lane does **not** collapse to a single cheap fix:

1. one suspect row (`002466 / 2024-05-09`) is clearly a sector-peer dominance case
2. two suspect rows (`002902`) remain balanced-share weakness cases
3. there is no clean broad-attention branch right now

So the next pack-C move should stay descriptive and local:
- treat sector-peer dominance as a real subfamily
- treat `002902` as a balanced turnover weakness pocket, not a simple
  attention-deficit case

## Fifth Read

The balanced-turnover weakness read is now also available:
[feature_pack_c_balanced_turnover_weakness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_balanced_turnover_weakness_v1.json)

Current conclusion:

- `row_count = 2`
- `balanced_weakness_counts = {singleton_sector_masking: 2, true_balanced_share_weakness: 0}`
- `recommended_fifth_feature_group = stop_turnover_lane_as_sector_masked`

This means the turnover-share lane is now effectively closed:

1. `002466 / 2024-05-09` remains the only clean `sector_peer_dominance` row
2. both `002902` rows are now better explained as singleton-sector masking
3. there is still no reusable broad-attention or balanced-turnover feature

So the correct next move is **not** another turnover-lane refinement. It is to
accept that pack-C has produced an explanatory closure on this branch.

## Acceptance Read

The pack-C acceptance report is now available:
[feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json)

Current conclusion:

- `acceptance_posture = close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar`
- `do_continue_pack_c_turnover_branch = false`
- `do_restart_replay_queue = false`
- `ready_for_u1_lightweight_geometry = true`

So `feature-pack-c` should now be treated as an explanatory success rather than
an open-ended refinement loop. The next stage should be a bounded `U1
lightweight geometry` sidecar, not another replay restart and not another local
turnover feature branch.

## What Feature-Pack-C Is Not

`feature-pack-c` is **not**:

- a replay-queue restart
- a broader concept-to-hierarchy rewrite
- another approval-threshold grid search
- a new attempt to promote the broad challenger directly

## Success Signals

`feature-pack-c` succeeds only if at least one suspect pocket moves to one of
these states:

1. a cleaner existing-family interpretation
2. a more credible feature-limited explanation that clearly closes the old loop
3. a new reusable family with evidence stronger than the current mixed pockets

If it only produces more local parameter options, it has failed.

## Stop Rule

If the first `feature-pack-c` recheck still leaves both pockets as:

- explanatory but non-promotable
- and no clearer than `feature-pack-b`

then the correct next move is to freeze specialist refinement again and accept
that the current feature set has already extracted most of the available
mechanism value from these pockets.
