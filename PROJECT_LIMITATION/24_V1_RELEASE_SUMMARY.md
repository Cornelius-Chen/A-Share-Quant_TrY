# V1 Release Summary

## Release Position

`A-Share Quant V1` should be treated as:

**a completed research-system foundation release**

It should not be described as:

- a finished live trading system
- a broker-connected execution system
- a final alpha answer

## What V1 Officially Includes

### Governance

1. project charter
2. research protocol
3. experiment standard
4. promotion gates
5. validation-ready definition
6. freeze status and candidate classification

### Research Infrastructure

1. canonical and derived data flow
2. data audit
3. regime / trend / strategy modules
4. standardized backtest engine
5. reporting and run registry
6. cross-pack comparison and rule sweeps
7. promotion and validation gate tooling

### Research Packs

1. `baseline_research_v1`
2. `theme_research_v2`
3. `market_research_v0`

### Current Official Default State

1. official shared default: `shared_default`
2. strongest shared-default challenger: `balanced_targeted_timing_repair`
3. branch baseline for baseline pack: `baseline_expansion_branch`
4. branch baseline for theme pack: `theme_strict_quality_branch`

## What V1 Explicitly Does Not Include

1. automatic live execution
2. broker integration
3. shadow execution service
4. account synchronization
5. live risk enforcement
6. operational kill-switch workflow

## Current Release Verdict

The repo is ready to be called:

- `V1 research foundation complete`
- `V1 freeze-ready`

The repo is not ready to be called:

- `V1 live-trading ready`

## Current Freeze Verdict

1. V1 official default remains `shared_default`
2. `balanced_targeted_timing_repair` is the current strongest broad challenger
3. `balanced_targeted_timing_repair` still fails the stricter validation-ready gate
4. therefore the repo is in `freeze-but-do-not-promote-yet` state

## What Happens After V1

Two paths are allowed:

1. `V1.1 research refinement`
   Focus on improving the strongest challenger without reopening uncontrolled exploration.

2. `V1.5 practical trading foundation`
   Build execution, shadow, broker, and operational control layers.

## One-Line Rule

V1 is complete as a research operating system, not as a live trading machine.
