# 67. V12 Training Sample Binding Gate V1

## Purpose

The bounded training branch now has a sample manifest.

It still needs one more operational artifact:

**when a new lane closes, can that row be bound into the training branch or not?**

This gate answers that question.

## Current Reading

The manifest already says:

1. opening-led count is frozen
2. persistence rows still need expansion
3. carry rows still need expansion

So the binding gate should behave accordingly.

## Immediate Consequence

The currently surfaced first lanes from:

1. `market_research_v3_factor_diversity_seed`
2. `market_research_v4_carry_row_diversity_refresh`

are both opening-led first lanes.

Therefore:

1. they should remain outside the bounded training branch
2. they are useful structurally
3. they are not valid new training rows

## What Can Bind Next

The next valid rows must come from:

1. future clean persistence lanes
2. future true carry rows

Not from:

1. more opening clones
2. relabelled penalty-track rows
3. relabelled deferred basis rows

## Why This Matters

Without this gate, the branch could still drift:

1. the manifest would say one thing
2. later lane closures might be added anyway
3. the training branch would silently widen

This gate prevents that drift.
