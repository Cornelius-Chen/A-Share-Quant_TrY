# 33. Sector/Theme Context Plan

## Purpose

This phase does not start sector-specific training.

It answers a narrower question:

- do current specialist slices separate cleanly by sector/theme state
- if they do, which conditional context group should be added first

## Rules

- `sector/theme context` is a report-only audit before any new feature branch.
- do not split the strategy into per-sector models at this stage.
- only start a context feature pack if the audit changes the next decision boundary.

## First Batch

The first audit batch uses the already-closed `market_research_v1` slices:

- `2024_q2`
- `2024_q3`
- `2024_q4`

These slices are already bounded and therefore safer than reopening wide replay.

## Target Axes

The first audit focuses on:

- sector heat / breadth
- theme load
- turnover concentration
- late-quality margin

## Exit Rule

- if the audit only restates existing pocket stories, do not open a new feature branch
- if the audit shows stable separation, open one narrow conditional feature group only

## First Audit Findings

The first report is:

- [sector_theme_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/sector_theme_context_audit_v1.json)

Current conclusions:

- `market_research_v1 / 2024_q2` is `theme_loaded + concentrated_turnover`
- `market_research_v1 / 2024_q3` is `hot_sector + broad_sector + balanced_turnover`
- `market_research_v1 / 2024_q4` is `theme_light + concentrated_turnover`

So the first conditional context priority is now:

1. `theme_load_plus_turnover_concentration_context`
2. `sector_state_heat_breadth_context`

That first group has now been validated into an explicit next branch:

- [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json)
  recommends:
  - `conditioned_late_quality_on_theme_turnover_context`
  - `defer_sector_heat_branch = true`

And the current non-goal is explicit:

- do not start per-sector training yet

## Current Branch Status

The first conditional branch has now been carried through one bounded strategy
experiment.

Supporting reports:

- [context_feature_pack_a_conditioned_late_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_v1.json)
- [context_feature_pack_a_conditioned_late_quality_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_acceptance_v1.json)

Current conclusions:

- candidate rows do exist, and they cluster in `mid/high` theme-turnover interaction buckets
- that makes the branch useful as a conditioned explanation of late-quality misses
- but the retained hierarchy experiment was not material enough to keep:
  - `acceptance_posture = close_conditioned_late_quality_branch_as_non_material`
  - `do_promote_conditioned_branch = false`

So the board/theme context line remains active as analysis, but still not as
per-sector training and not yet as a kept strategy rule.

## Second Branch Audit

The deferred second branch has now also been audited directly:

- [context_feature_pack_b_sector_heat_breadth_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_b_sector_heat_breadth_v1.json)

Current result:

- `candidate_row_count = 1`
- `candidate_slice_names = ['2024_q4']`
- the only surviving candidate is:
  - `000977`
  - `2024-10-24`
  - `context_sector_heat = 0.807045`
  - `context_sector_breadth = 0.6`

So the current posture is now:

- `close_sector_heat_breadth_context_branch_as_sparse`
- do **not** continue `context_feature_pack_b`
- do **not** escalate this into per-sector training

This means both current context branches remain useful at the explanatory
layer, but neither one has earned promotion into a kept strategy rule.
