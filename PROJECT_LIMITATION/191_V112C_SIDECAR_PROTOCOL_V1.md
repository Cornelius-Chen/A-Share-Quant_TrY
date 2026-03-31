# V1.12C Sidecar Protocol V1

- Same dataset, same labels, same time split as `V1.12B`.
- First candidate model families:
  - `hist_gradient_boosting_classifier`
  - `small_mlp_classifier`
- First comparison goal: reduce optimistic false positives in `major_markup` and `high_level_consolidation`.
- Boundary: report-only only; no deployment even if sidecar wins.
