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
