# 38. Next Batch Refresh Policy

## Purpose

This file defines **when** the repo is allowed to open another suspect-batch
refresh after `market_research_v2_seed`.

It is not a new batch design yet.

It is the trigger policy for the *next* batch after the current bounded
`v2_seed` state.

## Current Trigger Gate

The current gate is:

- [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json)

The current operational monitor is:

- [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json)

The current operator checklist is:

- [refresh_trigger_action_plan_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_action_plan_v1.json)

The current intake runbook is:

- [43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md)

## Current Reading

The repo should now read the current refresh state as:

1. the primary `V1.1` specialist loop is paused
2. `market_research_v2_seed` is also locally paused
3. `market_research_v2_seed` is still useful, but bounded
4. so the correct default is **wait**, not immediate next-batch expansion

## What Can Reopen Refresh

The next batch refresh should open only if at least one of these happens:

1. a new archetype-gap signal appears that is not already represented by
   `market_research_v1 + market_research_v2_seed`
2. a later suspect review shows materially different specialist geography
3. a refreshed substrate produces a lane that is no longer explained as a
   mixed slice read
4. the current bounded-secondary reading for `v2_seed` stops being true

## What Cannot Reopen Refresh

The repo should **not** open another suspect-batch refresh only because:

1. `v2_seed` is baseline-ready
2. `v2_seed` contributes specialist pockets
3. the current mixed lanes are interpretable
4. there is momentum to keep expanding

## Current Posture

Until a new trigger appears, the repo should:

1. hold `market_research_v1` as the primary specialist substrate
2. hold `market_research_v2_seed` as a bounded secondary substrate
3. avoid designing `market_research_v2_refresh` by inertia
4. wait for a new archetype-gap or materially different suspect batch

Before rerunning the guard on a genuinely new signal, the repo should first
persist that signal through the intake runbook.

That intake now accepts only canonical trigger types:

1. `archetype_gap`
2. `new_suspect`
3. `specialist_geography_shift`
4. `clean_frontier_break`
5. `secondary_status_break`
6. `policy_override`

## Current Monitor Reading

The first trigger monitor currently reads:

- `active_trigger_count = 0`
- `archetype_gap_trigger = false`
- `specialist_geography_trigger = false`
- `clean_frontier_trigger = false`
- `secondary_status_break_trigger = false`
- `recommended_posture = maintain_waiting_state_until_new_trigger`

So the operational state is now stronger than a plain pause:

1. the repo is not merely paused
2. it also has no active trigger that justifies a new refresh design cycle

## Current Action Plan

The current action plan reads:

- `action_mode = idle_wait_state`
- `action_count = 3`

Current operational checklist:

1. keep `market_research_v1` and `market_research_v2_seed` frozen
2. rerun the trigger monitor only when a genuinely new signal appears
3. rerun refresh-readiness only if a trigger actually flips

So the waiting state is now both:

1. machine-checkable
2. operationally explicit
