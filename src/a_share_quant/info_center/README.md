# A-Share Information Center

This package is the code-side scaffold for the unified information center.

Subdirectories:
- `identity`: security master, entity master, alias resolution
- `taxonomy`: concept, sector, business reference, concept purity
- `events`: source, document, claim, evidence span, event objects
- `attention`: heat, anchor, decoy, burst, attention summaries
- `quality`: source quality, corroboration, contradiction, repost controls
- `labels`: fact, semantic, state, governance label registries
- `features`: symbolic, statistical, representation feature registries
- `serving`: time-slice views, point-in-time serving, shadow-facing adapters
- `governance`: schema registry, dataset registry, heartbeat, freeze/reopen controls
- `automation`: repeatable ingest, pipeline, review, retention, and orchestration jobs

This scaffold is intentionally empty-first: structure is fixed before layer-by-layer population.

The center must support both:
- `in`: reproducible information collection and pipeline materialization
- `out`: timed eviction, compaction, archive, and cleanup of low-value or rebuildable data
