# V1.12G GBDT Pilot V2

- Same bounded comparison basis as `V1.12D`:
  - same dataset
  - same labels
  - same time split
- Result:
  - GBDT v1 test accuracy: `0.558`
  - GBDT v2 test accuracy: `0.5655`
  - `major_markup` optimistic carry false positives: `125 -> 126`
  - `high_level_consolidation` optimistic carry false positives: `1 -> 0`
- Reading:
  - semantic v2 did not materially improve `major_markup`
  - semantic v2 fully removed the remaining `high_level_consolidation` optimistic carry false positive inside this bounded pilot
- Interpretation:
  - the current semantic gain is concentrated and phase-specific
  - the next owner review should inspect whether `high_level_consolidation` now needs bounded label splitting or only better feature semantics
