# 45. Data Source Inventory

## Purpose

This file records which public data sources the repo can rely on for the next
phase of data expansion.

The goal is not to maximize source count.

The goal is to define:

1. what the repo can realistically fetch
2. what role each source plays
3. where the point-in-time and quality risks live

## Primary Data Paths

### 1. AkShare

AkShare is the repo's primary free-data collection layer.

It is suitable for:

1. A-share stock daily bars
2. index daily bars
3. basic security master fields
4. adjustment factors
5. concept-board and industry-board snapshots
6. concept constituent membership
7. some turnover / market-value / board-level fields

In practice, this often means the repo is indirectly using public pages and
APIs associated with:

1. Eastmoney-style board data
2. CNInfo-linked classification or corporate fields
3. exchange-facing public pages surfaced through AkShare wrappers

### 2. Official / Official-Adjacent Sources

These remain the preferred sources when the repo needs rule-level or
governance-level truth:

1. CNInfo (`cninfo`) for announcements and some classification histories
2. ChinaClear for transfer-fee and clearing fee schedules
3. SSE / SZSE for exchange-rule and investor-fee disclosures
4. `gov.cn` / ministry pages for statutory tax notices

### 3. Direct Website Families The Repo Can Reason About

For the next phase, the repo may explicitly use public data families commonly
surfaced via:

1. Eastmoney
2. Tonghuashun / iFinD-style public market pages
3. CNInfo
4. exchange and clearing websites

However, the repo should prefer:

1. AkShare wrappers for repeated structured collection
2. official sites for fee/rule truth

## Source Roles

### AkShare / Eastmoney-like public market feeds

Use for:

1. scalable batch collection
2. daily bars
3. board/theme/industry context
4. broad suspect discovery

Main risk:

1. point-in-time cleanliness is not guaranteed by default
2. board membership history may require additional repo-side discipline
3. concept/theme labels can drift

### Tonghuashun-like public market pages

Use only as a secondary corroborating family when needed.

Do not make Tonghuashun the primary structured batch source unless there is a
clear field gap that AkShare and current sources cannot cover.

Main risk:

1. scraping stability
2. changing field layouts
3. weak schema guarantees

### Official sites

Use for:

1. fee schedules
2. rule truth
3. tax notices
4. announcement truth where needed

Main risk:

1. lower convenience for wide batch collection
2. some data requires more manual integration work

## V1.2 Default Source Policy

The repo should use the following default policy:

1. AkShare is the primary batch-ingestion source
2. Eastmoney-style board/theme data may be used through AkShare-backed flows
3. official sites remain the preferred rule/fee truth source
4. Tonghuashun-style public data is secondary and only used when it materially
   closes an input gap

## Immediate V1.2 Data Priorities

The first required inputs are:

1. expanded stock daily bars and index bars
2. refreshed concept and sector mappings
3. board/theme turnover concentration context
4. enough new symbols to open a materially different `v2_refresh` suspect set

## Current Recommendation

The repo should now proceed as if:

1. AkShare is sufficient to start `market_research_v2_refresh`
2. Eastmoney-like board/theme coverage is usable through the current bootstrap
   path
3. official sites should only be pulled in selectively for rule and fee truth,
   not as the main batch-ingestion backbone
