# 63. V12 Bounded Training Pilot V1

## Purpose

This pilot is the first explicit training step under `V1.2`.

It is intentionally narrow:

1. use only already-frozen structured lane artifacts
2. train only a report-only micro model
3. do not touch strategy integration
4. do not touch raw catalyst/news ingestion

## Why This Pilot Exists

The owner explicitly asked to "train and see how it performs."

The safest response is not to jump directly into strategy-level ML. The safest
response is to test whether the repo's current structured lane observables can
separate:

1. `opening_led`
2. `persistence_led`
3. `carry_row_present`

If that fails, later model work is premature.
If that succeeds, later factor work has a firmer base.

## Inputs

Pilot v1 uses:

### Opening-led lanes

1. `market_v1_q2_002371`
2. `theme_q1_002466`
3. `theme_q1_600338`
4. `theme_q1_300518`
5. `market_v3_q4_002049`
6. `market_v4_q2_601919`

### Persistence-led lanes

1. `market_v1_q2_300502`
2. `theme_q1_000155`

### Carry rows

1. `carry_observable_schema_v1` row for `mainline_trend_b`
2. `carry_observable_schema_v1` row for `mainline_trend_c`

## Features

The pilot uses only bounded structured fields:

1. assignment-layer value
2. specialist permission
3. trigger count
4. filter count
5. anchor count
6. anchor alignment
7. anchor junk-block
8. specialist position presence
9. holding health score
10. anchor exit signal count
11. basis advantage in bps
12. challenger carry days
13. same-exit flag
14. pnl delta vs closest

## Model Choice

Pilot v1 uses:

1. leave-one-out validation
2. nearest-centroid classification
3. z-scored features inside each training fold

This choice is deliberate:

1. very small sample
2. high interpretability
3. no hidden black-box dependency

## Boundaries

This pilot must not be misread as:

1. a strategy model
2. a ranking model ready for production
3. a news/catalyst model
4. evidence that raw message ingestion should now drive quant logic

It is only:

**a bounded training check on frozen structural artifacts**

## Success Condition

Success means:

1. structured lane observables do separate the lane classes well enough to
   justify later bounded training work

Success does not mean:

1. the repo is now ready for strategy-level ML
2. the catalyst branch is now ready for training
3. carry is ready for strategy integration
