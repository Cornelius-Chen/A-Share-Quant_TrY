# A-Share Quant V1 Data Storage And Ingestion Plan

## Objective

This document turns the data contract into an executable storage and ingestion baseline.

It answers four practical questions:
1. Which datasets must be prepared first
2. Where each dataset should live in the repo
3. Which fields are required for each canonical table
4. In what order data should be acquired, cleaned, and promoted into research inputs

---

## Scope

This document covers the lab-stage data layer for:
1. offline research
2. segmented bullish-window backtests
3. mainline sector scoring
4. intra-mainline stock hierarchy research
5. first-pass Strategy A/B/C comparison

It does not yet define:
1. live market feeds
2. intraday storage
3. broker order/execution logs
4. ML feature stores

---

## Data Principles

1. Canonical storage should be stable before strategy iteration accelerates.
2. Raw vendor data and derived research tables must be separated.
3. Every table must have a clear owner, schema, and update process.
4. Derived tables may change with protocol versions; raw/reference tables should be as source-faithful as possible.
5. Demo CSV files can remain for tests and examples, but real research should migrate toward canonical datasets under `data/`.

---

## Target Data Layout

Recommended repo data layout:

```text
data/
|- sample/
|- raw/
|  |- daily_bars/
|  |- index_daily_bars/
|- reference/
|  |- security_master/
|  |- trading_calendar/
|  |- adjustment_factors/
|  |- sector_mapping_daily/
|  |- concept_mapping_daily/
|- derived/
|  |- sector_snapshots/
|  |- stock_snapshots/
|  |- mainline_windows/
|- external/
```

Directory semantics:

1. `data/sample/`
   Demo and test fixtures only. Small, reviewable, intentionally synthetic or reduced.
2. `data/raw/`
   Source-faithful market time series extracted from providers. Minimal transformation beyond standardization.
3. `data/reference/`
   Slowly changing reference tables required by protocol and universe rules.
4. `data/derived/`
   Research-layer tables generated from raw/reference data under a specific protocol version.
5. `data/external/`
   Temporary dumps, spreadsheets, manual source files, or third-party exports that should not be treated as canonical tables.

---

## Preferred File Format

Near-term rule:
1. Keep CSV compatibility for current loaders and demos.
2. Prefer Parquet for real canonical tables once data volume is non-trivial.

Recommended practice:
1. `sample/` may stay CSV.
2. `raw/`, `reference/`, and `derived/` should prefer Parquet.
3. If a source arrives as CSV or Excel, preserve the original in `external/` and standardize the promoted table into Parquet.

Reason:
1. Current code paths already accept CSV.
2. Canonical research storage should not be locked to CSV once the dataset expands.

---

## Minimum Canonical Dataset Pack

The first formal baseline experiment should not start until these six tables exist:

1. `daily_bars`
2. `index_daily_bars`
3. `security_master`
4. `trading_calendar`
5. `adjustment_factors`
6. `sector_mapping_daily`

These six are the minimum pack because they jointly support:
1. backtest execution realism
2. universe filtering
3. segmented regime detection
4. mainline mapping
5. reproducible return calculations

---

## Canonical Table Specifications

### 1. daily_bars

Suggested path:
`data/raw/daily_bars/`

Granularity:
1. one row per `trade_date + symbol`

Required fields:
1. `trade_date`
2. `symbol`
3. `open`
4. `high`
5. `low`
6. `close`
7. `volume`
8. `turnover`
9. `pre_close`
10. `adjust_factor`
11. `is_st`
12. `is_suspended`
13. `listed_days`

Strongly recommended fields:
1. `turnover_rate`
2. `upper_limit_price`
3. `lower_limit_price`
4. `board`
5. `name`

Immediate compatibility note:
This table should be exportable to the current loader schema used by [loaders.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/loaders.py).

### 2. index_daily_bars

Suggested path:
`data/raw/index_daily_bars/`

Granularity:
1. one row per `trade_date + index_symbol`

Required fields:
1. `trade_date`
2. `symbol`
3. `open`
4. `high`
5. `low`
6. `close`
7. `volume`
8. `turnover`
9. `pre_close`

Strongly recommended fields:
1. `index_name`
2. `adjust_factor` if source provides it consistently

Usage:
1. index-trend segmentation
2. resonance segmentation
3. benchmark context

### 3. security_master

Suggested path:
`data/reference/security_master/`

Granularity:
1. one row per `symbol`

Required fields:
1. `symbol`
2. `name`
3. `list_date`
4. `delist_date`
5. `board`
6. `exchange`

Strongly recommended fields:
1. `is_st_current`
2. `list_status`
3. `share_class`

Usage:
1. new-listing filter
2. board-specific rules
3. universe hygiene

### 4. trading_calendar

Suggested path:
`data/reference/trading_calendar/`

Granularity:
1. one row per `trade_date`

Required fields:
1. `trade_date`
2. `is_open`
3. `prev_open_date`
4. `next_open_date`

Strongly recommended fields:
1. `exchange`
2. `week_of_year`
3. `month_end_flag`

Usage:
1. signal execution alignment
2. next-day fill logic
3. segment construction

### 5. adjustment_factors

Suggested path:
`data/reference/adjustment_factors/`

Granularity:
1. one row per `trade_date + symbol`

Required fields:
1. `trade_date`
2. `symbol`
3. `adjust_factor`

Strongly recommended fields:
1. `factor_source`
2. `factor_version`

Usage:
1. reproducible adjusted-price calculations
2. protecting return comparability across reruns

### 6. sector_mapping_daily

Suggested path:
`data/reference/sector_mapping_daily/`

Granularity:
1. one row per `trade_date + symbol + sector_id`

Required fields:
1. `trade_date`
2. `symbol`
3. `sector_id`
4. `sector_name`
5. `mapping_source`
6. `mapping_version`

Strongly recommended fields:
1. `mapping_level`
2. `weight`
3. `is_primary_sector`

Usage:
1. sector aggregation
2. mainline scoring
3. stock-to-mainline assignment

### 7. concept_mapping_daily

Suggested path:
`data/reference/concept_mapping_daily/`

Granularity:
1. one row per `trade_date + symbol + concept_id`

Required fields:
1. `trade_date`
2. `symbol`
3. `concept_id`
4. `concept_name`
5. `mapping_source`
6. `mapping_version`
7. `is_primary_concept`
8. `weight`

Usage:
1. theme-aware overrides on top of formal industry mapping
2. mainline concept clustering
3. later relation-chain and multi-label theme research

---

## First Derived Tables

These should be generated only after the six canonical tables are stable.

### sector_snapshots

Suggested path:
`data/derived/sector_snapshots/`

Required fields:
1. `trade_date`
2. `sector_id`
3. `sector_name`
4. `persistence`
5. `diffusion`
6. `money_making`
7. `leader_strength`
8. `relative_strength`
9. `activity`
10. `protocol_version`

### stock_snapshots

Suggested path:
`data/derived/stock_snapshots/`

Required fields:
1. `trade_date`
2. `symbol`
3. `sector_id`
4. `sector_name`
5. `expected_upside`
6. `drive_strength`
7. `stability`
8. `liquidity`
9. `late_mover_quality`
10. `resonance`
11. `protocol_version`

### mainline_windows

Suggested path:
`data/derived/mainline_windows/`

Required fields:
1. `window_id`
2. `symbol`
3. `start_date`
4. `end_date`
5. `capturable_return`
6. `segmentation_method`
7. `protocol_version`

---

## Acquisition And Promotion Order

Recommended order:

1. `trading_calendar`
   This is the time spine. Do this first.
2. `security_master`
   Needed before any serious universe filtering.
3. `adjustment_factors`
   Needed before return interpretation is trusted.
4. `daily_bars`
   Core trading data.
5. `index_daily_bars`
   Enables index-trend and resonance segmentation.
6. `sector_mapping_daily`
   Enables mainline-aware research.
7. `sector_snapshots`
   First derived layer for regime scoring.
8. `stock_snapshots`
   First derived layer for hierarchy ranking.
9. `mainline_windows`
   Required for custom capture metrics and formal baseline studies.

Reason for this order:
1. It moves from stable reference data to market data, then from canonical tables to protocol-bound research tables.
2. It minimizes rework if mapping rules or protocol formulas change later.

---

## Promotion Criteria

A table should move from `external/` or ad hoc local dumps into canonical storage only when:

1. field names are standardized
2. primary key is clear
3. date semantics are clear
4. missing-value policy is documented
5. source and version are recorded
6. at least one basic validation check passes

---

## Minimum Validation Checks

Every canonical table should have at least these checks:

1. no duplicate primary-key rows
2. no impossible price relationships such as `high < low`
3. no negative volume or turnover
4. no missing `trade_date`
5. no missing `symbol` where symbol is part of the key
6. row count trend is explainable over time

Additional table-specific checks:

1. `daily_bars`: `pre_close > 0`, `open/high/low/close > 0`
2. `trading_calendar`: no gaps among expected open sessions without explanation
3. `sector_mapping_daily`: no silent mapping-version changes
4. `adjustment_factors`: factor jumps must be source-explainable

---

## Immediate Repo Actions

Short-term implementation plan:

1. keep current sample CSV pipeline alive for tests
2. reserve `data/raw/`, `data/reference/`, `data/derived/`, and `data/external/`
3. next code iteration should add loaders/adapters that can read canonical tables rather than sample-only CSVs
4. derived snapshot generation should gradually replace hand-maintained demo snapshot files

---

## What Not To Do Yet

Do not spend the next round on:

1. minute bars
2. tick/order-book storage
3. seat-level data
4. large ML feature stores
5. news text lakes

These may matter later, but they are not on the critical path for the first formal baseline experiment.

---

## One-Sentence Rule

The next phase should optimize for data trustworthiness and protocol-aligned structure, not for data quantity alone.
