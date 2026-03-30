# 75. V12 Carry Row Hunting Strategy V1

## Purpose

The repo now has:

1. an active `v4` carry-row-diversity refresh
2. a first checked `v4` lane
3. a clear result that the first checked lane was opening-led

So the next question is not whether to widen replay.

It is:

**how should the repo hunt the next true carry row inside the existing v4 refresh?**

## Current Result

The answer is:

1. do not open a new refresh batch
2. do not widen replay
3. hunt one symbol at a time inside `v4`
4. prioritize `basis_spread_diversity` and `carry_duration_diversity`
5. de-prioritize the remaining `exit_alignment_diversity` symbol after the first exit-alignment lane surfaced as opening-led

## Why This Matters

Without this strategy, the repo could drift back into:

1. broad replay
2. arbitrary symbol choice
3. chasing another opening-led lane

This artifact keeps the hunt pointed at the actual bottleneck.
