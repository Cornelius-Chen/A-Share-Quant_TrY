# 90. V1.2 V5 Exhaustion Phase Check V1

## Mission
Freeze the phase-level reading after `market_research_v5_carry_row_diversity_refresh` consumes its bounded lanes.

## In Scope
- Determine whether `v5` exhausted without repairing the carry-row-diversity gap.
- Decide whether the next legal move is a new refresh entry or explicit waiting.

## Out Of Scope
- Writing the next manifest.
- Reopening local `v5` replay.
- Promoting catalyst context into the mainline.

## Success Criteria
- Produce a phase-check artifact for `v5` exhaustion.
- State whether another refresh entry is legally justified.

## Stop Criteria
- `v5` is not actually exhausted yet.
- The last true-carry probe materially changes the training reading.

## Handoff Condition
- If `v5` exhausts without repairing the gap, initialize only the next refresh entry.
