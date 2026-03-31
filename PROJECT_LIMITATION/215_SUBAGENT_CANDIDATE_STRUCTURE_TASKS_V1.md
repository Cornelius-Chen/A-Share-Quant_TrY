# Subagent Candidate Structure Tasks V1

- Current state: `V1.12G` is closed and waiting for owner review before any label split or dataset growth.
- Therefore current subagent work must remain bounded and review-only.

## Ready Now

### 1. Hotspot Bucketization
- Type: `structuring`
- Review cadence: `volume_or_time_based`
- Scope:
  - `high_level_consolidation`
  - `major_markup`
- Output:
  - grouped misread buckets by stage, symbol, prediction direction, and semantic-v2 profile

### 2. Candidate Substate Clustering For `high_level_consolidation`
- Type: `drafting`
- Review cadence: `stage_based`
- Scope:
  - only existing `high_level_consolidation` rows
  - only existing semantic-v2 features
- Output:
  - `2-4` candidate subclusters
  - per-cluster summary stats
  - representative rows
- Boundary:
  - may suggest that the current label looks too coarse
  - may not define new formal labels

### 3. Bounded Catalyst Semantic Ablation Batch
- Type: `execution`
- Review cadence: `volume_or_time_based`
- Scope:
  - `catalyst_freshness_state`
  - `cross_day_catalyst_persistence`
  - `theme_breadth_confirmation_proxy`
- Output:
  - marginal hotspot-control contribution under the same split and same model family

## Review Rule
- These tasks are useful only if mainline reviews them after the correct cadence trigger.
- If they do not change the future decision basis, they should be discarded rather than refined indefinitely.
