# V1.2 V5 Refresh Criteria V1

## Purpose
- Freeze symbol-selection criteria for `market_research_v5_carry_row_diversity_refresh` before any v5 manifest is written.

## Inputs
- `v12_next_refresh_entry_v2.json`
- `v12_training_sample_manifest_v1.json`
- `carry_observable_schema_v1.json`

## Current Read
- `v5` should target:
  - `true carry rows` first
  - `clean persistence rows` second
- `opening_led` stays frozen
- `v4 / q2 / A` locally exhausted replay must not be reopened

## What This Means
- `v5` is not a generic carry refresh.
- It is a **training-gap-aware** refresh.
- Any future manifest must satisfy:
  - acceptance-grade carry or persistence observability
  - no opening-clone chasing
  - no relabeling into carry/persistence
  - novelty versus the combined reference base
