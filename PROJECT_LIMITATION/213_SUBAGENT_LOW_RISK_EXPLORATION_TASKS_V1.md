# Subagent Low-Risk Exploration Tasks V1

- Current mainline state: `V1.12G` closed successfully and is waiting for owner review before any label split or dataset growth.
- Therefore only bounded support exploration is lawful right now.

## Ready Now

### 1. Hotspot Bucketization
- Scope:
  - `high_level_consolidation`
  - `major_markup`
- Input:
  - `V1.12B` frozen pilot dataset
  - `V1.12G` baseline and GBDT outputs
- Output:
  - grouped misread buckets by stage, symbol, prediction direction, and semantic-v2 feature profile
- Why low-risk:
  - no label changes
  - no model changes
  - no scope changes

### 2. Bounded Catalyst Semantic Ablation Batch
- Scope:
  - `catalyst_freshness_state`
  - `cross_day_catalyst_persistence`
  - `theme_breadth_confirmation_proxy`
- Input:
  - same frozen pilot dataset
  - same split
  - same bounded model family
- Output:
  - marginal hotspot-control contribution of each semantic field
- Why low-risk:
  - fixed environment
  - fixed labels
  - fixed dataset

## Deferred

### 3. Constrained Proxy Generation For Late-Stage Catalyst Decay
- Status: deferred
- Reason:
  - should wait until hotspot buckets and semantic ablation make the missing late-stage semantic more specific
- Boundary:
  - may only combine existing variables
  - may not invent new label definitions
