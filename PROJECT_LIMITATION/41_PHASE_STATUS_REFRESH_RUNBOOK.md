# 41. Phase Status Refresh Runbook

## Purpose

This runbook defines the one-command refresh path for the current post-`v2_seed`
status stack.

It does not open a new research phase.

It only regenerates the existing gate chain in the correct order.

## Command

```powershell
python scripts/run_phase_status_refresh.py
```

## Fast Console Check

For a short operator-facing read, the repo also now supports:

```powershell
python scripts/run_phase_status_console.py
```

This prints the current phase mode, trigger count, and next actions without
opening any new research lane.

## Fastest Guard Check

For the shortest safe command that both refreshes the stack and prints the
final operator-facing read, the repo also now supports:

```powershell
python scripts/run_phase_guard.py
```

This is the fastest correct way to ask whether the repo may do anything new
right now.

## What It Runs

In order, the refresh chain regenerates:

1. `next_batch_refresh_readiness_v1.json`
2. `refresh_trigger_monitor_v1.json`
3. `refresh_trigger_action_plan_v1.json`
4. `phase_status_snapshot_v1.json`

## Current Use Rule

Use this runbook when:

1. new data arrives
2. a new suspect signal appears
3. you need to reconfirm whether the repo should stay in the current waiting state

If a genuinely new signal appears and you want to preserve it before rerunning
the stack, first use:

```powershell
python scripts/run_refresh_trigger_intake.py ...
```

Do **not** use this runbook as permission to reopen replay or design a new
batch by itself.

The runbook only refreshes the current status stack.
