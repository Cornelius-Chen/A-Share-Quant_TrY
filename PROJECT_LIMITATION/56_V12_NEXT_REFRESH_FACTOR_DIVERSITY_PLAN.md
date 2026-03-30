# 56. V1.2 Next Refresh Factor Diversity Plan

## Purpose

This file defines the next refresh posture after the first bounded factorization
cycle has closed successfully but still lacks enough factor-row diversity.

The key change is:

1. the next refresh is no longer justified by generic sample growth
2. it is justified by a very specific factor-row diversity gap

## Inputs

The design reads:

1. [v12_phase_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_phase_readiness_v1.json)
2. [carry_factor_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_pilot_v1.json)
3. [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)

## Current Artifact

The design artifact is:

- [v12_next_refresh_factor_diversity_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_factor_diversity_design_v1.json)

## Current Read

The next refresh should now target:

1. basis-spread diversity
2. carry-duration diversity
3. exit-alignment diversity
4. carry reuse outside the current `theme_q4 / 300750` evidence island

That means the next batch should be designed for:

1. new factor rows
2. not just new symbols
3. not just new archetypes in the old sense

## Why This Matters

The first `V1.2` factorization cycle succeeded.

But it succeeded in a bounded way.

The next bottleneck is not:

1. more replay
2. a second factor lane
3. broad strategy integration

The next bottleneck is:

1. getting more diverse carry rows into the system

## Next Step

Prepare the next refresh manifest around this factor-row diversity gap before
opening any second factor lane.
