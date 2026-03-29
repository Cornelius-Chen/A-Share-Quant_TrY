# Validation-Ready Definition

## Purpose

This file turns `Validation-Ready` from a vague label into a stricter gate.
It is meant to complement:

- [11_PROMOTION_GATES.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/11_PROMOTION_GATES.md)
- [12_VALIDATION_STANDARD.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/12_VALIDATION_STANDARD.md)
- [13_STRATEGY_LIFECYCLE.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/13_STRATEGY_LIFECYCLE.md)

## Definition

A strategy or shared-default challenger is `validation-ready` only if:

1. It has already cleared a first promotion-style gate against the current incumbent.
2. Its improvement is not concentrated in only one local environment.
3. Its drawdown and return improvements survive pack-level breakdown.
4. Any loss in `mainline_capture_ratio` is explicit, measured, and still inside tolerance.
5. The result remains explainable in trade, segment, and window-level artifacts.

## Required Evidence

At minimum, a `validation-ready` claim must include:

1. A finalists-only comparison report.
2. A first-stage promotion gate report.
3. A second-stage validation gate report with stricter thresholds.
4. The exact config paths for incumbent and challenger.
5. Decision and journal entries that explain why the challenger is not just a local-branch winner.

## Second-Stage Gate Focus

The second-stage gate should try to falsify the challenger, not support it.
Compared with the first gate, it should be stricter on:

1. Pack-level consistency.
2. Capture regression tolerance.
3. Row-level win concentration.
4. Small positive improvements that may disappear after sample expansion.

## Pack-Level Consistency Requirements

A challenger should not be called `validation-ready` if:

1. It only improves one research pack while clearly regressing the other.
2. It improves return globally but loses too much capture inside a key pack.
3. It improves drawdown only because it becomes too passive in the stronger opportunity pack.

## Shared Default Standard

For a shared default replacement, the bar is stricter than for a branch-local winner.

The challenger should usually satisfy all of the following:

1. Better composite stability than the incumbent.
2. Better mean total return than the incumbent.
3. Better mean max drawdown than the incumbent.
4. No large per-pack capture collapse.
5. At least some row-level ownership of total-return wins.

If those conditions are only partially true, the candidate may remain:

- `candidate but experimental`
- `shared-default challenger`
- not yet `validation-ready`

## Current Practical Meaning

At the current project stage, `validation-ready` means:

- strong enough to deserve serious default-replacement discussion
- not yet the same as `approved for shadow` or `approved for live`

It is still a research-stage status, but a much stricter one than `baseline`.

## One-Line Rule

`Validation-ready` means the project has actively tried to break the candidate and failed to do so with the currently available evidence.
