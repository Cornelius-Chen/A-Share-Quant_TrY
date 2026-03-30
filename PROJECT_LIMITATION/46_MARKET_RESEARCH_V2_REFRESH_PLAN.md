# 46. Market Research v2 Refresh Plan

## Purpose

This file defines the first refreshed market-research batch inside `V1.2`.

It follows `market_research_v2_seed`, but it is not a blind size expansion.

Its job is to:

1. add new sample geography beyond `market_research_v1 + market_research_v2_seed`
2. target new context archetypes that were not covered by the seed batch
3. remain auditable before any new replay loop is opened

## Current Posture

The repo should read the current state as:

1. `V1.1` replay refinement is paused correctly
2. `market_research_v2_seed` is now a bounded secondary substrate
3. the next active move is a refreshed data batch, not another replay lane

## Refresh Design Rule

`market_research_v2_refresh` should:

1. remain liquid and interpretable
2. avoid overlap with the current `market_research_v1 + v2_seed` base
3. target a new set of missing context archetypes
4. be runnable through the same free-data bootstrap path

## First Refresh Archetypes

The first refresh batch is designed to add:

1. `theme_loaded + concentrated_turnover + narrow_sector`
2. `theme_light + balanced_turnover + narrow_sector`
3. `theme_moderate + concentrated_turnover + broad_sector`

These archetypes are intentionally different from the first `v2_seed` set.

## Immediate Artifacts

The first refresh artifacts should include:

1. a merged reference-base universe
2. a new refresh universe
3. a refresh manifest
4. a free-data bootstrap config
5. sector/concept/derived/audit/suite configs

## Success Condition

This phase step should be treated as successful when:

1. the refresh manifest contains only new symbols vs the current base
2. all intended archetypes are covered
3. the refresh pack is runnable without new ad hoc config work

## Current Status

`market_research_v2_refresh` has now crossed the line from design to active
research substrate:

1. the pack is runnable and `baseline_ready`
2. broad freeze remains intact after the first five-pack validation
3. the first `q1 / mainline_trend_c` drawdown lane is now closed as a mixed
   slice rather than left open for momentum replay

Key evidence:

- [market_research_data_audit_v2_refresh.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_refresh.json)
  confirms:
  - `baseline_ready = true`
- [20260329T145913Z_8ec3708c_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T145913Z_8ec3708c_comparison.json)
  confirms:
  - five-pack broad comparison completed
  - `buffer_only_012` remains the most stable broad candidate
- [market_v2_refresh_q1_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_refresh_q1_trade_divergence_quality_c_v1.json)
  identifies:
  - `002415` and `603019` as the top positive q1/C symbols
- [market_v2_refresh_q1_cycle_mechanism_002415_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_refresh_q1_cycle_mechanism_002415_c_v1.json)
  confirms:
  - a clean `entry_suppression_avoidance` read
- [market_v2_refresh_q1_cycle_mechanism_603019_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_refresh_q1_cycle_mechanism_603019_c_v1.json)
  confirms:
  - positive fragmentation via `other_worse_loss_shift`
- [market_v2_refresh_q1_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_refresh_q1_drawdown_slice_acceptance_v1.json)
  concludes:
  - `close_market_v2_refresh_q1_drawdown_slice_as_avoidance_plus_positive_fragmentation`
  - `do_continue_q1_drawdown_replay = false`
