# 42. Phase Guard Runbook

## Purpose

This runbook defines the single command that both:

1. refreshes the current phase-status stack
2. prints the operator-facing console result

It is the shortest safe way to ask:

**"Can the repo do anything new right now?"**

## Command

```powershell
python scripts/run_phase_guard.py
```

## What It Does

In order, the guard command:

1. refreshes `next_batch_refresh_readiness_v1.json`
2. refreshes `refresh_trigger_monitor_v1.json`
3. refreshes `refresh_trigger_action_plan_v1.json`
4. refreshes `phase_status_snapshot_v1.json`
5. prints the console status view
6. exits with the console exit code

## Current Use Rule

Use this command when you want the fastest correct answer to:

1. whether the repo is still in explicit no-trigger wait
2. whether any refresh trigger has become active
3. what the next allowed action is

This command still does **not** authorize a new replay lane or a new refresh
cycle by itself.
