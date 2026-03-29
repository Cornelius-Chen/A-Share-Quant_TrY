# 34. Context Feature Pack A Plan

## Purpose

This phase converts the first sector/theme context audit into explicit reusable
fields and a narrow conditioned-feature branch.

It is not a sector-training phase.

## First Group

The first context feature group is:

1. `theme_load_plus_turnover_concentration_context`

The second group remains deferred:

1. `sector_state_heat_breadth_context`

## Immediate Rule

- add explicit context fields to `StockSnapshot`
- validate that these fields still separate the already-closed `market_research_v1` slices
- only then open a conditioned feature branch

## Non-goal

- do not start per-sector training
- do not reopen broad replay
- do not open a second context branch before the first one is validated

## Validation Result

The first context-pack report is now in:

- [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json)

Current result:

- `bucket_counts = {interaction_high: 1, sector_heat_led: 1, turnover_led_theme_light: 1}`
- `interaction_spread = 0.179943`
- `heat_spread = 0.126929`
- `breadth_spread = 0.005463`
- `recommended_next_feature_branch = conditioned_late_quality_on_theme_turnover_context`
- `defer_sector_heat_branch = true`

So the first context branch is now validated enough to continue, and the heat /
breadth branch remains deferred.
