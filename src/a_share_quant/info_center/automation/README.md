# Information Center Automation

Automation is split into five job classes.

## `ingest_jobs/`
- Collect raw information repeatedly from stable sources.
- Output goes to `data/raw/info_center/...` and `data/temp/info_center/ingest_staging/`.

## `pipeline_jobs/`
- Parse, normalize, extract, link, rate, and label.
- Output goes to `data/reference/info_center/...` and `data/derived/info_center/...`.

## `review_jobs/`
- Handle contradictions, low-confidence events, unresolved entity mapping, and manual review queues.
- Output goes to `data/temp/info_center/review_queue/` and reviewed registries.

## `retention_jobs/`
- TTL eviction
- compaction
- rollup
- cold archive handoff
- quarantine cleanup

## `orchestration/`
- Scheduling
- retries
- health checks
- manifests
- dependency ordering

Guiding rule:
- collecting more data is not enough
- the system must also remove, compact, archive, or quarantine data on purpose
