# 43. Refresh Trigger Intake Runbook

## Purpose

This runbook defines the canonical intake step when a human or a future process
observes a potentially new refresh-trigger signal.

It does **not** open refresh by itself.

It only records the signal in a standard form before rerunning the current
guard stack.

## Command

```powershell
python scripts/run_refresh_trigger_intake.py `
  --trigger-name new_archetype_gap `
  --trigger-type archetype_gap `
  --source manual_review `
  --rationale "Found a materially different suspect geography." `
  --dataset market_research_v1 `
  --dataset market_research_v2_seed `
  --symbol 603986 `
  --slice 2024_q4
```

## Allowed Trigger Types

Current canonical trigger types are:

1. `archetype_gap`
2. `new_suspect`
3. `specialist_geography_shift`
4. `clean_frontier_break`
5. `secondary_status_break`
6. `policy_override`

The intake command now validates this field and should not be fed free-form
trigger-type labels.

## Output

The command writes a normalized report under `reports/analysis/`.

Default output:

- `reports/analysis/refresh_trigger_intake_v1.json`

## Use Rule

Use this runbook only when at least one of these is true:

1. new data arrived and you suspect the waiting-state reading may change
2. a new suspect symbol or slice appears
3. a new archetype gap is observed
4. a human operator wants to preserve a trigger candidate before rerunning the guard

## Required Next Step

After persisting the intake record, the next safe command is still:

```powershell
python scripts/run_phase_guard.py
```

The intake artifact records the new signal.
The phase guard still decides whether the repo may do anything new.
