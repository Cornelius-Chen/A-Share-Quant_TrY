# V1.12G Baseline Readout V2

- Same dataset: `V1.12B` frozen optical-link pilot
- Same posture: time-split, report-only
- Result:
  - baseline v1 test accuracy: `0.4509`
  - baseline v2 test accuracy: `0.4628`
  - `major_markup` optimistic carry false positives: `178 -> 174`
  - `high_level_consolidation` optimistic carry false positives: `46 -> 34`
- Reading:
  - semantic v2 helps even before non-linear modeling
  - the larger improvement still concentrates in `high_level_consolidation`
- Implication: late-stage catalyst semantics matter enough to help a simple readout, so the refinement path remains justified.
