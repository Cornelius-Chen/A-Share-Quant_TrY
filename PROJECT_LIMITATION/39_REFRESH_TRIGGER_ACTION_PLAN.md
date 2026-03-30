# 39. Refresh Trigger Action Plan

## Purpose

This file turns the post-`v2_seed` waiting state into an explicit operator
checklist.

It is not a new strategy phase.

It is the execution order to follow once the refresh-trigger monitor is either:

1. still idle
2. or has just flipped active

## Current Inputs

- [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json)
- [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json)
- [refresh_trigger_action_plan_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_action_plan_v1.json)

## Current Reading

The current action plan reads:

- `action_mode = idle_wait_state`
- `active_trigger_count = 0`
- `should_open_refresh = false`

The one-command refresh chain is now also available:

- [41_PHASE_STATUS_REFRESH_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/41_PHASE_STATUS_REFRESH_RUNBOOK.md)
- `python scripts/run_phase_status_refresh.py`

So the current repo posture is:

1. keep `market_research_v1` and `market_research_v2_seed` frozen
2. rerun the trigger monitor only when a genuinely new signal appears
3. rerun refresh-readiness only if a trigger actually flips

If a genuinely new signal appears, the first persistence step is now:

- [43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md)
- `python scripts/run_refresh_trigger_intake.py ...`

## Triggered Sequence

Once a trigger does flip, the sequence should be:

1. persist the new signal through refresh-trigger intake
2. rerun `phase_guard`
3. rerun `next_batch_refresh_readiness` if the guard no longer reads as explicit wait
4. reopen `next_suspect_batch_design`
5. audit the next manifest before any new bootstrap

This preserves the repo's rule:

**refresh must be trigger-driven, not momentum-driven**
