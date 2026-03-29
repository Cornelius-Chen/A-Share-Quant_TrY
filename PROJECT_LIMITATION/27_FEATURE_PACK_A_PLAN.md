# 27. Feature-Pack-A Plan

## Goal

`feature-pack-a` is the first bounded feature-expansion cycle after the
specialist replay loop entered a `feature-limited thinning phase`.

Its job is **not** to build a large new factor library.
Its job is to test whether a small number of more expressive features can
change the interpretation boundary of the current feature-gap suspects.

## Primary Recheck Targets

The first recheck targets are:

- `theme_research_v4 / 2024_q4 / 002902`
- `theme_research_v4 / 2024_q2 / 002466`

These were selected because the latest audit
[specialist_feature_gap_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_feature_gap_audit_v1.json)
flags them as the clearest feature-gap suspects:

- `002902`: `cross_strategy_mixed_repeat`
- `002466`: `stacked_known_families`

## Candidate Feature Set

`feature-pack-a` should stay narrow. The first-pass feature shortlist is:

### Theme / Concept Features

- `primary_concept_support_margin`
- `secondary_concept_support_margin`
- `concept_concentration_ratio`
- `concept_rotation_pressure`

### Hierarchy Intermediate Features

- `late_mover_quality_margin`
- `composite_margin`
- `resonance_margin`
- `fallback_reason_score`

### Approval-Edge Features

- `top_score_to_threshold_gap`
- `top_vs_second_score_gap`
- `approval_hysteresis_state`
- `switch_buffer_pressure`

### Cycle-Context Features

- `pre_entry_regime_delta_3d`
- `pre_exit_replacement_pressure_3d`

## Success Test

`feature-pack-a` is successful if at least one current suspect moves from:

- `mixed_existing_families`
- `stacked_family_pocket`

into one of these outcomes:

- a cleaner existing family interpretation
- a stable new reusable family
- a much stronger negative conclusion that the pocket is true noise

## Failure Test

`feature-pack-a` should be considered unsuccessful if:

- both primary recheck targets remain mixed / stacked
- no family boundary changes after the added features
- the only effect is to add more annotations without changing any decision

If that happens, the correct conclusion is not "keep adding features".
The correct conclusion is that the current pockets are not being limited by
these first-pass features.

## Exit Rule

After `feature-pack-a`, the next step must be exactly one of:

1. promote the improved interpretation into the specialist family inventory
2. record a negative result and stop this line
3. define a new, equally narrow `feature-pack-b`

No open-ended replay expansion should happen in between.
