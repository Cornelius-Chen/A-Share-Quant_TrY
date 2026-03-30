# 62. Catalyst Event Registry Schema V1

## Purpose

This document freezes the first bounded schema for the deferred
`catalyst persistence` context branch.

The key design choice is:

**do not store a single generic "policy/news" label.**

Instead, store a structured catalyst row that captures:

1. source authority
2. execution strength
3. rumor risk
4. persistence / reinforcement
5. consolidation and reacceleration shape

## Why This Schema Exists

Current `V1.2` bottleneck still points to missing carry row diversity.
Recent new substrates keep surfacing opening-led lanes first.

If catalyst persistence helps explain why some lanes stay opening-led while
others can develop into carry-like structures, the repo needs a schema that
can represent that distinction without collapsing into narrative fitting.

## Schema Sections

### Identity

Required fields:

1. `lane_id`
2. `dataset_name`
3. `slice_name`
4. `strategy_name`
5. `symbol`
6. `event_date`
7. `window_start`
8. `window_end`

### Catalyst Source

Required fields:

1. `event_scope`
2. `event_type`
3. `source_authority_tier`
4. `policy_scope`
5. `execution_strength`
6. `rumor_risk_level`
7. `source_tier`
8. `primary_source_ref`

The most important additions here are:

1. `source_authority_tier`
2. `execution_strength`
3. `rumor_risk_level`

These let the repo distinguish:

1. national policy
2. local policy
3. regulator / exchange notice
4. company announcement
5. media pulse
6. rumor-like or "small essay" catalysts

### Persistence Context

Required fields:

1. `persistence_class`
2. `reinforcement_count`
3. `confirmation_delay_days`
4. `followthrough_window_days`
5. `board_pulse_breadth_class`
6. `turnover_concentration_class`

This section is what turns a catalyst row from a label into a persistence
hypothesis.

### Price-Shape Proxy

Required fields:

1. `first_impulse_return_pct`
2. `consolidation_days_after_pulse`
3. `retrace_depth_vs_ma5`
4. `retrace_depth_vs_ma10`
5. `reacceleration_present`
6. `reacceleration_delay_days`

This is the practical answer to the "冲一天、回踩 2-5 天、再上冲" path.

The branch should explicitly preserve:

1. how long the post-pulse digestion lasted
2. how deep the retrace was
3. whether the move reaccelerated after consolidation

### Lane Labels

Required fields:

1. `lane_outcome_label`
2. `context_posture`
3. `notes`

These labels must remain tied to already-frozen lane readings such as:

1. `opening_led`
2. `persistence_led`
3. `carry_row_present`
4. `mixed_fragmented`
5. `not_factor_relevant`

## Research Boundary

Schema v1 does **not** mean:

1. auto-opening a new factor lane
2. promoting catalyst labels into retained features
3. launching a broad NLP/news ingestion system

Schema v1 only means:

1. the branch now has a canonical row format
2. future manual or semi-manual registry seeding can stay consistent
3. the branch can later be audited without relabeling the whole sample

## Current Posture

Current posture is:

**freeze the schema now, keep the branch deferred, and only seed the first
bounded registry when the owner explicitly wants to test whether catalyst
persistence changes a later factor decision.**
