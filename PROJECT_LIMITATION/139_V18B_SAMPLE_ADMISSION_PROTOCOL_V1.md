# 139 V18B Sample Admission Protocol V1

## Scope
- freeze the first bounded protocol for deciding which candidate breadth samples may enter future bounded collection for the two frozen `sample_breadth_gap` target features

## Current Targets
- `single_pulse_support`
- `policy_followthrough_support`

## Core Rules
- admission remains below actual sample collection
- candidates must stay inside the frozen breadth-entry source pools
- candidates must preserve point-in-time and source-aware constraints
- candidates must not weaken target feature readings or mix shortfall types

## Expected Outputs
- per-feature admission axes
- mandatory exclusions
- global bounded gate rules
- a lawful next step for per-feature admission gate review
