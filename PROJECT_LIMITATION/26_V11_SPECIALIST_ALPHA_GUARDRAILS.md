# 26. V1.1 Specialist Alpha Guardrails

## Purpose

This file defines how `V1.1 research refinement` stops being an open-ended
replay loop and becomes a bounded research phase.

The immediate target of `V1.1` is:

- turn specialist-alpha pockets into reusable mechanism assets
- separate clean families from mixed pockets and toxic patterns
- decide when replay should stop and feature expansion should begin

`V1.1` is **not** responsible for:

- upgrading `shared_default`
- endlessly expanding the pocket catalogue
- forcing every replayed pocket into a new family
- treating taxonomy completeness as a goal by itself

## Completion Modes

### Positive Completion

`V1.1` can be treated as positively complete when at least one of the
following is true:

- a new non-baseline family is confirmed on at least `2` symbols and across at
  least `2` pockets or pack/slice combinations
- the family inventory is rich enough to support the next research stage
  without relying on ad hoc replay selection

### Negative Completion

`V1.1` can also complete by negative conclusion. This is still a valid
research result.

Negative completion is reached when:

- the replay queue's leading candidates mostly collapse into
  `single_row_baseline_reuse`, `baseline_family_reuse`, or
  `mixed_existing_families`
- newly replayed candidates no longer change the family inventory boundary
- the most plausible residual pockets are better explained as feature-limited
  or stacked-family cases than as new reusable assets

### Resource / Marginal-Return Completion

The phase must also stop when:

- the replay loop keeps adding commentary but not new assets
- repeated queue rotations mostly strengthen already-known baseline-style
  families
- the next-best action is clearly "add features" rather than "replay another
  pocket"

## Operational Stop Rules

Treat the specialist replay loop as entering a controlled stop state when all
three conditions hold:

1. `thinning_signal = true` in the feature-gap audit
2. at least one `feature_gap_suspect` exists
3. the latest replayed pockets do not add a clean new family asset

When those conditions hold, the default next action is:

- stop extending the replay queue
- run a `feature gap -> feature pack -> replay recheck` cycle

## Current Status

As of `2026-03-29`, the latest audit
[specialist_feature_gap_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_feature_gap_audit_v1.json)
shows:

- `pocket_count = 9`
- `feature_gap_suspect_count = 2`
- `classification_counts = {mixed_existing_families: 4, single_row_baseline_reuse: 4, stacked_family_pocket: 1}`
- `thinning_signal = true`

So the current `V1.1` state is:

- `specialist replay loop`: feature-limited thinning phase
- `next recommended step`: start `feature-pack-a`
- `default behavior`: pause replay-queue expansion unless a queued candidate
  is needed as a post-feature recheck

## Feature-Pack-A Scope

The first feature-expansion cycle should stay narrow.

Priority candidates:

- theme/concept time-varying support strength
- hierarchy intermediate margins
- approval-edge / threshold proximity features
- cycle-context features around entry and exit days

The test of success is not "more features exist".
The test is whether at least one current `feature_gap_suspect` moves from:

- `mixed_existing_families`
- `stacked_family_pocket`

to either:

- a cleaner existing family interpretation
- or a genuinely new reusable family
