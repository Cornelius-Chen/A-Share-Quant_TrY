# 35. Context Feature Pack B Plan

## Purpose

This phase tests the deferred second context branch:

- `sector_state_heat_breadth_context`

It remains report-only unless current evidence changes a decision boundary.

## Rule

- do not open a new hierarchy rule before a sparse-vs-repeat audit is complete
- do not restart replay queue for this branch
- do not treat one hot symbol in one slice as a reusable conditional rule

## Current Audit

The first heat/breadth audit is now in:

- [context_feature_pack_b_sector_heat_breadth_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_b_sector_heat_breadth_v1.json)

Current result:

- `candidate_row_count = 1`
- `candidate_slice_names = ['2024_q4']`
- `candidate_bucket_counts = {heat_breadth_high: 1, heat_only: 0, breadth_only: 0, heat_breadth_low: 0}`
- only one candidate survives the current filter:
  - `000977`
  - `2024-10-24`
  - `non_junk_gap_to_threshold = 0.024282`
  - `late_mover_quality = 0.550817`
  - `resonance = 0.546532`
  - `context_sector_heat = 0.807045`
  - `context_sector_breadth = 0.6`

## Decision

The current branch is too sparse to continue.

The correct posture is:

- `recommended_next_feature_branch = close_sector_heat_breadth_context_branch_as_sparse`
- `recommended_posture = close_sector_heat_breadth_context_branch_as_sparse`
- `do_continue_context_feature_pack_b = false`

## Meaning

This does **not** prove sector heat and breadth are useless.

It only means:

- under the current suspect set
- under the current thresholds
- and under the current slice-level stop rules

the second context branch does not justify a new retained rule or a per-sector
training path.

## Next Step

- keep sector/theme context at the analysis layer
- do not open `context_feature_pack_b` rule experiments
- only revisit this branch if a later suspect batch produces multi-slice
  heat/breadth-supported misses
