# 52. Carry Scoring Design v1

## Purpose

This file defines the first bounded scoring design inside the carry factor
lane.

The lane is still row-isolated.

The goal here is only to:

1. convert the observable schema into an explicit score
2. keep the score bounded inside the carry row universe
3. avoid premature strategy integration

## Inputs

The scoring design reads:

1. [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)

## Current Artifact

The first scoring artifact is:

- [carry_scoring_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_scoring_design_v1.json)

## Current Read

The carry score remains intentionally narrow.

It combines:

1. basis advantage
2. same-exit alignment
3. positive carry duration
4. realized negative-cycle confirmation

It does **not**:

1. score whole mixed pockets
2. integrate into strategy rules
3. promote carry into retained-feature status

## Why This Matters

The carry lane now has:

1. admission
2. bounded design
3. observable schema
4. scoring design

That means the next step can become a bounded carry factor pilot rather than
another round of narrative refinement.

## Next Step

Open the first carry factor pilot evaluation on top of `carry_score_v1`, while
keeping penalty-track and thin factors frozen.
