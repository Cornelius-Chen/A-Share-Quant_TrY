# 48. Factor Evaluation Protocol v1

## Purpose

This file defines the first formal evaluation protocol for the current
candidate-factor bucket created by:

- [feature_factor_registry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_factor_registry_v1.json)

The protocol is intentionally narrow.

It does not try to train models, compute IC series, or reopen replay slices.

Its job is to answer one bounded question:

1. which current candidate factors are ready for first-pass evaluation now
2. which should only be evaluated with an explicit penalty
3. which should stay preserved in the registry until more sample arrives

## Inputs

The current protocol reads:

1. [feature_factor_registry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_factor_registry_v1.json)
2. [cycle_family_inventory_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v3.json)

## Current Artifact

The first protocol artifact is:

- [factor_evaluation_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/factor_evaluation_protocol_v1.json)

## Current Reading

The protocol currently splits the candidate bucket into three tracks:

1. `evaluate_now`
2. `evaluate_with_penalty`
3. `hold_for_more_sample`

This means the repo can stop treating all candidate factors as equally ready.

## Current First-Pass Decision

The current expected read is:

1. `carry_in_basis_advantage`
   - `evaluate_now`
2. `preemptive_loss_avoidance_shift`
   - `evaluate_with_penalty`
3. `delayed_entry_basis_advantage`
   - `hold_for_more_sample`

## Why This Matters

This is the first point where `V1.2` stops being only a registry exercise.

The repo now has:

1. a retained feature layer
2. an explanatory-only layer
3. a candidate-factor layer
4. and a protocol that decides how those candidates should move next

## Non-Goals

This protocol does not:

1. prove that any candidate factor is already production-ready
2. reopen closed specialist slices
3. replace later factor metrics such as ranking or out-of-sample factor testing

## Next Step

Use the protocol result to open the first bounded factor-evaluation workstream,
starting with the `evaluate_now` bucket before touching penalty-track or thin
factors.
