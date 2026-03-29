# V1 Freeze Candidates

## Purpose

This file defines what is currently:

- frozen enough to count as V1 default
- strong enough to remain as V1 candidate
- still too early to freeze

The goal is to stop V1 from drifting forever.

## Current Classification

### V1 Default

`shared_default`

Reason:

1. It is still the official default config.
2. It remains the fairest common comparison baseline.
3. It has not yet been formally replaced.

Representative configs:

- [baseline_research_strategy_suite.yaml](D:/Creativity/A-Share-Quant_TrY/config/baseline_research_strategy_suite.yaml)
- [theme_research_strategy_suite.yaml](D:/Creativity/A-Share-Quant_TrY/config/theme_research_strategy_suite.yaml)

### V1 Shared-Default Challenger

`balanced_compromise`

Reason:

1. It is the current promotion frontrunner in the finalists screen.
2. It has passed the first-stage promotion gate.
3. It is not yet promoted because the second-stage validation-ready gate is intentionally stricter.
4. The current second-stage gate fails on pack-level capture regression, so it remains below `validation-ready`.

Representative configs:

- [baseline_research_strategy_suite_balanced_compromise.yaml](D:/Creativity/A-Share-Quant_TrY/config/baseline_research_strategy_suite_balanced_compromise.yaml)
- [theme_research_strategy_suite_balanced_compromise.yaml](D:/Creativity/A-Share-Quant_TrY/config/theme_research_strategy_suite_balanced_compromise.yaml)

### V1 Branch Baselines

`baseline_expansion_branch`

Reason:

1. Best current local baseline-branch reference.
2. Keeps the strongest capture profile on the baseline research pack.
3. Not suitable as direct shared default replacement by itself.

Config:

- [baseline_research_strategy_suite_expansion.yaml](D:/Creativity/A-Share-Quant_TrY/config/baseline_research_strategy_suite_expansion.yaml)

`theme_strict_quality_branch`

Reason:

1. Best current local theme-branch reference.
2. Keeps the strongest local drawdown discipline on the theme research pack.
3. Not suitable as direct shared default replacement by itself.

Config:

- [theme_research_strategy_suite_strict_quality.yaml](D:/Creativity/A-Share-Quant_TrY/config/theme_research_strategy_suite_strict_quality.yaml)

### Candidate But Experimental

These remain useful research candidates, but are not freeze targets right now:

- `theme_capture_relief_branch`
- `expansion_regime_guard`
- `quality_floor_with_faster_entry`
- `expansion_with_quality_floor`
- earlier sweep candidates such as `strict_quality`, `expansion_capture`, `selective_entry`, `broad_late_mover`

Reason:

1. They contributed to directional discovery.
2. They are not the current best freeze targets.
3. Promoting them now would widen the surface without improving clarity.

### Not Ready

Anything that still depends on:

1. stale-output-sensitive evidence
2. one-pack-only superiority
3. unclear theme-label quality
4. unverified validation behavior

## Freeze Rule

V1 should not freeze a new shared default unless all three are true:

1. finalists comparison still favors it
2. first-stage promotion gate passes
3. second-stage validation-ready gate passes

If any one of those is missing, the candidate stays below `V1 default`.

## One-Line Rule

V1 freeze is about stopping drift, not rewarding novelty.
