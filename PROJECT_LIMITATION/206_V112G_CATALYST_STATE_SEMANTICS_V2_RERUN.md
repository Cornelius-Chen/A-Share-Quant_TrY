# V1.12G Catalyst-State Semantics V2 Rerun

- Mission: add a bounded v2 semantic layer to `catalyst_state` and rerun the same frozen pilot dataset before any label split or scope growth.
- Scope: same objects, same labels, same time split, report-only only.
- New semantic fields:
  - `catalyst_freshness_state`
  - `cross_day_catalyst_persistence`
  - `theme_breadth_confirmation_proxy`
- Key result:
  - baseline improved from `0.4509` to `0.4628`
  - `high_level_consolidation` optimistic carry false positives fell from `46` to `34`
  - GBDT improved from `0.558` to `0.5655`
  - `high_level_consolidation` optimistic carry false positives fell from `1` to `0`
- Interpretation: the next asset is still the semantic representation, not model-family escalation.
- Boundary: no automatic label split, no wider dataset, no deployment.
