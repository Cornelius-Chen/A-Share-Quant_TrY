# 51. Carry Observable Schema v1

## Purpose

This file defines the first observable schema inside the bounded carry factor
lane.

The key shift is:

1. the lane is no longer described only in words
2. it now has explicit row-level observables

## Inputs

The first schema read uses:

1. [carry_factor_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_design_v1.json)
2. [theme_q4_cycle_mechanism_300750_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_b_v1.json)
3. [theme_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_c_v1.json)

## Current Artifact

The first schema artifact is:

- [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)

## Current Read

The carry lane is now defined as a `negative_cycle_basis_row` schema.

The required observables are:

1. `basis_advantage_abs`
2. `basis_advantage_bps`
3. `challenger_carry_days`
4. `same_exit_date`
5. `pnl_delta_vs_closest`

This means the repo can now start the next carry step using explicit row
fields instead of only pocket labels.

## Why This Matters

The current carry evidence still lives inside a mixed pocket.

So the correct move is not broad pocket scoring.

The correct move is to:

1. isolate the carry rows
2. define the row-level basis observables
3. only then design bounded scoring logic

## Non-Goals

This schema does not:

1. score the factor yet
2. reopen replay
3. promote carry into retained-feature status
4. widen the lane to penalty-track or thin factors

## Next Step

Use this schema to define the first bounded carry scoring design without
leaving the row-isolated boundary.
