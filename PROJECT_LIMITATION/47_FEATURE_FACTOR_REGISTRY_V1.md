# 47. Feature / Factor Registry v1

## Purpose

This file defines the first formal feature/factor registry artifact inside
`V1.2`.

It is the bridge between:

1. the repo's existing mechanism/family/context findings
2. the later factor-evaluation and ranking layer

The registry is intentionally narrow.

It does **not** claim that every current research finding is already a usable
factor.

Its job is to separate:

1. what the repo should already retain as reusable feature assets
2. what should remain explanatory-only
3. what is promising enough to evaluate next as candidate factors

## Current Artifact

The first registry artifact is:

- [feature_factor_registry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_factor_registry_v1.json)

Current summary:

1. `registry_entry_count = 10`
2. `retained_feature_count = 4`
3. `explanatory_only_feature_count = 3`
4. `candidate_factor_count = 3`
5. `ready_for_factor_evaluation_protocol = true`

## Retained Features

These are the current reusable feature assets:

1. `drawdown_entry_suppression_avoidance`
2. `drawdown_earlier_exit_loss_reduction`
3. `capture_opening_edge_late_mover_admission`
4. `capture_persistence_edge_late_mover_structure`

These are retained because they now have enough repeated structural evidence to
survive beyond one local pocket.

## Explanatory-Only Features

These remain useful inside the research stack, but should **not** be promoted
into retained strategy rules or factor inputs yet:

1. `conditioned_late_quality_theme_turnover_context`
2. `sector_heat_breadth_context`
3. `balanced_turnover_weakness_context`

These branches improved explanation, but not enough to justify retained-rule
promotion.

## Candidate Factors

These are worth formal evaluation next, but they are not yet stable enough to
call retained features:

1. `carry_in_basis_advantage`
2. `preemptive_loss_avoidance_shift`
3. `delayed_entry_basis_advantage`

Their current status is:

1. structurally promising
2. evidence-backed enough to preserve
3. still too weak or too conditional for direct retained-feature promotion

## What This Changes

The repo can now stop treating every useful finding as the same kind of asset.

It now has a first explicit split between:

1. reusable feature assets
2. explanatory context-only assets
3. factor candidates that still need protocol-level evaluation

That means the next step is no longer "find more pockets first".

The next step is:

1. define the factor evaluation protocol
2. test the current candidate-factor bucket under that protocol

## Non-Goals

This registry does **not**:

1. claim the candidate-factor bucket is already production-ready
2. reopen any closed replay slice
3. justify direct per-sector training
4. replace the existing family inventory

## Next Step

Open `factor_evaluation_protocol_v1` and evaluate the current candidate-factor
bucket before creating more registry entries.
