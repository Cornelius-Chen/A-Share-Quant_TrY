# Information Center Structure

This is the full scaffold for the A-share unified information center.

## Code Layer

- `identity/`
  - `models/`
  - `pipelines/`
  - `services/`
- `taxonomy/`
  - `concepts/`
  - `sectors/`
  - `business_reference/`
  - `concept_purity/`
  - `cross_theme/`
- `market/`
  - `daily/`
  - `intraday/`
  - `board_state/`
  - `limit_halt/`
- `events/`
  - `sources/`
  - `documents/`
  - `claims/`
  - `evidence/`
  - `event_objects/`
  - `linking/`
- `attention/`
  - `signals/`
  - `anchors/`
  - `decoys/`
  - `bursts/`
- `quality/`
  - `source_tiers/`
  - `corroboration/`
  - `contradictions/`
  - `reposts/`
- `labels/`
  - `facts/`
  - `semantics/`
  - `states/`
  - `governance/`
- `features/`
  - `symbolic/`
  - `statistical/`
  - `representation/`
  - `registry/`
- `pti/`
  - `ledger/`
  - `time_slice/`
  - `state_transition/`
- `replay/`
  - `shadow/`
  - `execution_journals/`
  - `cost_models/`
- `serving/`
  - `research/`
  - `shadow/`
  - `live_like/`
- `automation/`
  - `ingest_jobs/`
  - `pipeline_jobs/`
  - `review_jobs/`
  - `retention_jobs/`
  - `orchestration/`
- `governance/`
  - `catalogs/`
  - `schemas/`
  - `datasets/`
  - `heartbeats/`
  - `freeze_reopen/`
  - `ops/`

## Data Layer

- `data/raw/info_center/`
  - `sources/official/`
  - `sources/media/`
  - `sources/community/`
  - `documents/`
  - `market/daily/`
  - `market/intraday/`
  - `attention/`
- `data/derived/info_center/`
  - `normalized/identity/`
  - `normalized/taxonomy/`
  - `normalized/events/`
  - `normalized/attention/`
  - `normalized/market/`
  - `feature_views/symbolic/`
  - `feature_views/statistical/`
  - `feature_views/representation/`
  - `time_slices/`
  - `replay/shadow/`
  - `replay/live_like/`
- `data/reference/info_center/`
  - `identity/`
  - `taxonomy/`
  - `business_reference/`
  - `concept_purity/`
  - `source_master/`
  - `document_registry/`
  - `claim_registry/`
  - `event_registry/`
  - `evidence_span_registry/`
  - `attention_registry/`
  - `quality_registry/`
  - `label_registry/`
  - `feature_registry/`
  - `state_transition_journal/`
  - `shadow_execution_journal/`
- `data/external/info_center/`
  - `source_health/`
  - `license_registry/`
- `data/temp/info_center/`
  - `ingest_staging/`
  - `materialization/`
  - `candidate_search/`
  - `review_queue/`
  - `retention_queue/`
  - `quarantine/`
  - `cache/`

The scaffold is intentionally full before population. Fill it layer-by-layer rather than creating ad hoc branch-specific storage later.

## Operating Principle: In and Out

The information center is not a passive warehouse.

- `ingest_jobs/`:
  stable, repeatable collection from external sources into raw/staging layers
- `pipeline_jobs/`:
  normalization, extraction, linking, labeling, and materialization into reference/derived layers
- `review_jobs/`:
  exception review, contradiction review, low-confidence review, and manual override queues
- `retention_jobs/`:
  TTL eviction, compaction, rollup, cold archive, and low-value clutter cleanup
- `orchestration/`:
  scheduling, dependency control, retries, health checks, and run manifests

The default rule is:
- information must be able to come in repeatedly and reproducibly
- information must be able to leave hot storage on schedule
- only structured truth and necessary journals stay long-lived
