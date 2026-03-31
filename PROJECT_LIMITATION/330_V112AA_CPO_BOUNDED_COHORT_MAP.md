# V1.12AA CPO Bounded Cohort Map

Formal reports:
- `reports/analysis/v112aa_phase_charter_v1.json`
- `reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json`
- `reports/analysis/v112aa_phase_check_v1.json`
- `reports/analysis/v112aa_phase_closure_check_v1.json`

## What this phase does

This phase takes the bounded cycle reconstruction from `V1.12Z` and compresses it into a reusable cohort structure.

The purpose is not to label yet.  
The purpose is to answer:

- which objects are core truth rows,
- which are secondary or extension rows,
- which are spillover-only,
- and which must remain pending.

## Core result

The current CPO line now has:

- `20` object rows
- `3` primary core truth rows
- `4` secondary review assets
- `4` branch review assets
- `3` spillover or memory rows
- `3` pending ambiguous rows

Training and labeling remain closed.

## Layered reading

### Core truth rows
- `300308`
  - `core_anchor`
- `300502`
  - `core_beta`
- `300394`
  - `core_platform_confirmation`

These are the cleanest later candidates for bounded primary labeling.

### Secondary review assets
- `002281`
  - adjacent bridge
- `603083`
  - adjacent high-beta extension
- `688205`
  - adjacent high-beta extension
- `301205`
  - adjacent high-beta extension

These should not be treated like the core trio, but they are now clean enough to preserve in a secondary layer.

### Branch review assets
- `300570`
  - connector / MPO branch
- `688498`
  - laser-chip component
- `688313`
  - silicon-photonics component
- `300757`
  - packaging / process enabler

These are useful for route-depth and extension reading, not automatic truth assignment.

### Late-cycle extension
- `601869`
- `600487`
- `600522`

These are late-cycle breadth and maturity objects, not ignition anchors.

### Spillover and memory
- `000070`
- `603228`
  - spillover candidates
- `001267`
  - weak memory only

These remain useful, but only as A-share-style overlay information.

### Pending ambiguous
- `300620`
- `300548`
- `000988`

These are preserved explicitly and remain outside later truth layers unless role purity improves.

## Why this matters

This phase creates the bridge from:

- cycle understanding

to

- later bounded labeling review

without forcing mixed objects into clean categories too early.

## Current boundary

Still forbidden:
- auto labeling
- auto training
- signal generation

The next lawful move is owner review of the cohort map, then possibly a bounded labeling review.
