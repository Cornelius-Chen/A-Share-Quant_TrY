# 50. Carry Factor Design v1

## Purpose

This file defines the first bounded factor-design posture for:

- `carry_in_basis_advantage`

The design problem here is narrower than factor admission.

The repo already knows carry is worth a bounded factor lane.

What it must decide next is:

1. how wide that lane is allowed to be
2. whether the current evidence supports whole-pocket scoring
3. or whether the design must isolate carry rows inside mixed pockets

## Inputs

The current design read uses:

1. [carry_in_basis_first_pass_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_in_basis_first_pass_v1.json)
2. [theme_q4_cycle_mechanism_300750_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_b_v1.json)
3. [theme_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_c_v1.json)
4. [theme_q4_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cross_strategy_cycle_consistency_v1.json)

## Current Artifact

The first bounded design artifact is:

- [carry_factor_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_design_v1.json)

## Current Read

The current design posture is:

1. open the carry factor lane
2. keep it bounded
3. require row isolation

The reason is that carry repeats cleanly across `B/C`, but it currently sits
inside a mixed pocket together with `earlier_exit_loss_reduction`.

So the repo should **not** treat the whole mixed pocket as one factor.

## What This Changes

The next factor step is now more specific:

1. isolate carry rows
2. define the carry-specific observable schema
3. keep broad scoring and retained-feature promotion turned off

## Non-Goals

This design does not:

1. reopen replay
2. widen factor work to penalty-track or thin candidates
3. upgrade carry into a retained feature
4. justify whole-pocket factor scoring

## Next Step

Define the first carry-specific observable schema as a row-isolated negative
cycle basis factor.
