# 49. Carry-In-Basis First Pass

## Purpose

This file defines the first bounded factor workstream opened by:

- [factor_evaluation_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/factor_evaluation_protocol_v1.json)

The goal is not to promote `carry_in_basis_advantage` directly into a retained
feature.

The goal is only to answer whether it deserves a bounded first-pass factor
lane.

## Inputs

The first-pass read uses:

1. [factor_evaluation_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/factor_evaluation_protocol_v1.json)
2. [cycle_family_inventory_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v3.json)
3. [theme_q4_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cross_strategy_cycle_consistency_v1.json)
4. [theme_q4_cycle_mechanism_300750_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_b_v1.json)
5. [theme_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_c_v1.json)

## Current Artifact

The first bounded carry artifact is:

- [carry_in_basis_first_pass_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_in_basis_first_pass_v1.json)

## Current Read

The key distinction here is:

1. `carry_in_basis_advantage` is ready for bounded factor design
2. it is **not** yet promoted into retained-feature status

That means the repo should now treat it as:

1. the first `evaluate_now` factor lane
2. still narrower than the retained-feature pool

## Why This Is The Right Scope

The factor now clears three bars:

1. protocol-level `evaluate_now`
2. repeated clean family evidence with no opportunity-cost contamination
3. cross-strategy reuse across `mainline_trend_b` and `mainline_trend_c`

But it still does **not** clear the stronger bar of broad retained-feature
promotion.

## Non-Goals

This first pass does not:

1. evaluate the penalty-track factor
2. reopen replay
3. prove full cross-dataset generality
4. replace the retained-feature pool

## Next Step

Open the first bounded factor design workstream for
`carry_in_basis_advantage`, while keeping the penalty and thin buckets frozen.
