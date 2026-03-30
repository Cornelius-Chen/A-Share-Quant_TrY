# 53. Carry Factor Pilot v1

## Purpose

This file defines the first pilot posture for the carry factor lane.

The lane now already has:

1. admission
2. row-isolated design
3. observable schema
4. bounded score

The remaining question is:

1. what kind of pilot is justified right now

## Inputs

The pilot read uses:

1. [carry_scoring_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_scoring_design_v1.json)
2. [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)

## Current Artifact

The first pilot artifact is:

- [carry_factor_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_pilot_v1.json)

## Current Read

The current carry pilot opens as:

1. `report_only_micro_pilot`

It does not yet open as:

1. a rankable pilot
2. a strategy-integrated pilot
3. a retained-feature promotion event

The reason is simple:

1. the current rows are still too symmetric
2. the score exists
3. but the score does not yet create cross-row dispersion

## Why This Matters

This is still real progress.

The repo now has a bounded factor pilot posture instead of stopping at scoring
design.

But the posture remains honest:

1. the pilot is open
2. the lane is still narrow
3. more row diversity is required before ranking logic should expand

## Next Step

Keep the carry lane in report-only pilot mode until a later batch adds more
diverse carry rows or score dispersion.
