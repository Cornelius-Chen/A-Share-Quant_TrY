# 28. Feature-Pack-B Plan

## Goal

`feature-pack-b` is the first post-triage refinement cycle after
`feature-pack-a` confirmed that the current replay loop is feature-limited.

Its job is **not** to reopen broad replay work.
Its job is to run two narrow tracks in sequence and test whether either one
changes the current specialist-family boundary.

## Triage Result

The authoritative split now comes from:
[feature_pack_a_triage_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_triage_v1.json)
and
[feature_pack_b_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_readiness_v1.json).

Current case split:

1. `theme_q4 / 002902 / B`
   - class: `hierarchy_approval_edge`
   - dominant bottleneck: `late_quality_and_permission_edge`
   - next track: `feature_pack_b_hierarchy_approval`

2. `theme_q2 / 002466 / C`
   - class: `concept_supported_hierarchy_edge`
   - dominant bottleneck: `concept_to_hierarchy_bridge`
   - next track: `feature_pack_b_concept_supported_hierarchy`

## Execution Order

Run the tracks sequentially, not in parallel:

1. `feature_pack_b_hierarchy_approval`
2. `feature_pack_b_concept_supported_hierarchy`

Reason:

- `002902` is the cleaner edge because concept coverage is zero across all
  trigger rows
- if the hierarchy/approval track already changes the family boundary, it may
  alter whether the concept-supported track is still worth running immediately

## Track A: Hierarchy / Approval

Primary target:

- `theme_q4 / 002902 / B`

Priority features:

- `fallback_reason_score`
- `approval_hysteresis_state`
- `switch_buffer_pressure`
- `late_mover_quality_margin`
- `non_junk_composite_margin`

Success signal:

- the pocket becomes a cleaner existing-family interpretation
- or yields a stronger negative conclusion that it is just a local hierarchy /
  approval artifact

## Track B: Concept-Supported Hierarchy

Primary target:

- `theme_q2 / 002466 / C`

Priority features:

- `primary_concept_support_margin`
- `secondary_concept_support_margin`
- `concept_rotation_pressure`
- `concept_concentration_ratio`
- `late_mover_quality_margin`

Success signal:

- concept support starts explaining hierarchy admission more cleanly than the
  current stacked-family label
- or the pocket is downgraded from "feature-limited" to "stacked but already
  explained"

## Exit Rule

After each track, the next step must be exactly one of:

1. promote the improved interpretation into the family inventory
2. record a negative result and stop that track
3. continue to the next track in this file

No replay-queue restart should happen before both tracks are either completed
or explicitly rejected.

## Current Status

Track A is now complete and closed as a negative-but-informative result:

- `theme_q4 / 002902 / B` is explainable as a coupled
  `late_mover_quality + score-margin threshold` edge
- but local repairs worsened symbol-level PnL, so this track is not a cheap
  promotion candidate

Track B is now also effectively in acceptance mode rather than open-ended
refinement:

- `theme_q2 / 002466 / C` was correctly narrowed to `concept_to_late_mover`
- but the first two bridge variants (`v6` / `v7`) only repaired one of the two
  bridge rows and materially degraded the challenger alpha

So `feature-pack-b` should now be treated as a bounded refinement cycle with
two negative-but-informative exits, not as a prompt to reopen broad concept or
hierarchy experimentation.
