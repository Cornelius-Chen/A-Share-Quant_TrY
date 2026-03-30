# 61. Catalyst Carry Context Hypothesis Plan

## Purpose

This plan defines a bounded research method for testing one new hypothesis:

**carry-led specialist lanes are more likely to appear in sectors/themes with
persistent external catalysts, while single-pulse catalysts more often produce
opening-led edges that fail to extend into carry.**

The goal is not to reopen broad replay or to turn "policy" into a vague
post-hoc explanation. The goal is to test whether **catalyst persistence**
should become a formal context layer for later factor work.

## Why This Matters

Current `V1.2` bottleneck:

1. the bounded carry lane exists
2. row-isolated carry schema exists
3. the first carry pilot is open in report-only mode
4. but carry row diversity is still too thin

Recent new substrates (`v3`, `v4`) have first surfaced clean
`opening-led` lanes rather than carry breakthroughs.

One plausible reason is that the repo already sees:

1. price-path structure
2. hierarchy admission
3. trend/context internals

but still under-observes:

1. catalyst persistence
2. board-level pulse breadth
3. retrace-and-reacceleration shape after the first impulse

This plan treats that gap as a testable hypothesis, not as a conclusion.

## Hypotheses

### H1

`carry-led` lanes are more likely when the symbol sits inside a
**persistent catalyst environment**, especially one with policy or
industry-level reinforcement across multiple days.

### H2

`opening-led` lanes are more likely when the move is driven by a
**single-pulse catalyst** with weak follow-through.

### H3

The most useful signal is not "policy yes/no", but:

1. catalyst persistence
2. board pulse breadth
3. retrace depth and duration
4. reacceleration confirmation

## Research Posture

This branch is:

1. `report-only`
2. `context-hypothesis-first`
3. `deferred from immediate carry-lane expansion`

It must not:

1. reopen broad replay
2. directly change strategy rules
3. auto-promote policy/news labels into retained factors

## Required Inputs

### Lane Inputs

Use only already-closed or already-bounded lanes as the first sample set:

1. clean opening-led lanes
2. clean persistence-led lanes
3. bounded carry rows
4. mixed lanes with clear acceptance artifacts

The first sample set should be drawn from:

1. `market_research_v1`
2. `market_research_v2_refresh`
3. `market_research_v3_factor_diversity_seed`
4. `market_research_v4_carry_row_diversity_refresh`
5. prior `theme` carry cases already used in the bounded carry lane

### Catalyst Inputs

Use a tiered source model.

#### Tier 1: Official / high-trust

1. `gov.cn` policy announcements
2. ministry / regulator pages when relevant
3. exchange / official market notices
4. `cninfo` company announcements

#### Tier 2: Public market data context

1. sector/theme board histories
2. sector/theme breadth
3. board turnover concentration
4. board-level volume / pulse confirmation

These can be obtained through current public-market ingestion paths,
including AkShare's Eastmoney-oriented board data and public exchange /
announcement sources.

#### Tier 3: Weak supplementary context

1. Eastmoney / similar public news summaries
2. Tonghuashun-like public descriptive pages

These should be used only as weak descriptive support, not as primary truth.

## First Implemented Data Form

Do **not** begin with a full automated NLP/news pipeline.

Begin with a small `catalyst_event_registry_v1` that is:

1. manually or semi-manually seeded
2. tied only to a bounded lane sample
3. structured enough to support later scaling

Suggested fields:

1. `lane_id`
2. `dataset_name`
3. `slice_name`
4. `strategy_name`
5. `symbol`
6. `event_date`
7. `event_scope`:
   - `market`
   - `sector`
   - `theme`
   - `company`
8. `event_type`:
   - `policy`
   - `industry`
   - `company_announcement`
   - `news_pulse`
   - `none_detected`
9. `persistence_class`:
   - `single_pulse`
   - `multi_day_reinforcement`
   - `policy_followthrough`
   - `unclear`
10. `source_tier`
11. `notes`

Schema v1 is now separately frozen in:

- [62_CATALYST_EVENT_REGISTRY_SCHEMA_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/62_CATALYST_EVENT_REGISTRY_SCHEMA_V1.md)

## Market-Structure Proxy Layer

In parallel with the event registry, define a bounded proxy layer:

1. `sector_pulse_breadth`
2. `theme_pulse_breadth`
3. `turnover_concentration_after_pulse`
4. `retrace_days_after_first_impulse`
5. `retrace_depth_vs_ma5`
6. `retrace_depth_vs_ma10`
7. `reacceleration_present`
8. `reacceleration_delay_days`

These are preferable as first-pass quantitative context features because they
are easier to make reproducible than full-text news interpretation.

## Outcome Labels

The lane side must be labeled using existing acceptance vocabulary instead of
new ad hoc language:

1. `opening_led`
2. `persistence_led`
3. `carry_row_present`
4. `mixed_fragmented`
5. `not_factor_relevant`

The purpose is to compare catalyst context **against already-frozen lane
readings**, not to relitigate the lane itself.

## Research Procedure

### Step 1: Build a bounded lane sample

Construct a small sample of already-accepted lanes:

1. `opening-led`
2. `persistence-led`
3. `carry-row-present`

The sample should be large enough to compare categories, but small enough to
stay auditable.

### Step 2: Attach catalyst-event registry rows

For each lane:

1. identify the first structural event date
2. collect catalyst evidence around that window
3. classify persistence class

### Step 3: Attach market-structure proxies

For each lane:

1. compute board pulse breadth
2. compute turnover concentration
3. compute retrace shape
4. compute reacceleration confirmation

### Step 4: Compare lane families

Test whether:

1. `carry-row-present` lanes show higher catalyst persistence
2. `carry-row-present` lanes show broader board confirmation
3. `opening-led` lanes show shallower follow-through and more single-pulse
   behavior
4. retrace-and-reacceleration shape meaningfully separates opening-only from
   later carry continuation

### Step 5: Decide feature posture

Possible outcomes:

1. `promising_context_factor_candidate`
2. `report_only_explanatory_context`
3. `insufficient_signal_keep_deferred`

## Acceptance Criteria

This branch should only advance beyond report-only if all are true:

1. the catalyst persistence variable separates lane classes in more than one
   dataset family
2. the separation is not driven by a single symbolic case
3. the proxy layer agrees with the event layer often enough to avoid pure
   narrative fitting
4. the result changes a real decision boundary for later factor work

If these are not met, the branch remains explanatory-only.

## Stop Conditions

Stop and close the branch if:

1. event labels stay too noisy
2. policy/news classification becomes too manual to scale
3. proxy features fail to separate opening-led vs carry-row-present lanes
4. the result does not change any later factorization decision

## Deliverables

The intended deliverables are:

1. `catalyst_event_registry_v1`
2. `lane_catalyst_context_audit_v1`
3. `catalyst_persistence_hypothesis_check_v1`

Only after these exist should the repo consider:

1. a retained context feature
2. a catalyst-conditioned carry factor branch
3. a broader intraday / execution realism link

## Current Phase Placement

This branch is now officially remembered as:

**a deferred but valid `V1.2` context hypothesis branch**

It should be opened when:

1. current bounded carry lane still lacks row diversity
2. new substrates keep surfacing opening-led lanes first
3. the owner explicitly wants to test whether catalyst persistence explains
   that pattern
