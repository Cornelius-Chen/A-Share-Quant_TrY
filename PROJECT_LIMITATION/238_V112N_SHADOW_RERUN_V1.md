# V112N Shadow Rerun V1

## Shadow Features Added

- `shadow_quiet_contraction_stall_recoverable`
- `shadow_residual_breadth_stall_exhaustion`
- `shadow_unresolved_mixed_stall_residue`

## Rerun Result

- baseline:
  - `0.4628 -> 0.4628`
  - `high_level_consolidation` carry false positives: `34 -> 34`
  - `major_markup` carry false positives: `174 -> 174`

- GBDT:
  - `0.5655 -> 0.5655`
  - `high_level_consolidation` carry false positives: `0 -> 0`
  - `major_markup` carry false positives: `126 -> 126`

## Interpretation

- The `V1.12M` inner draft is currently more descriptive than incrementally predictive.
- It may still help future review or schema thinking.
- It does **not** currently justify feature promotion or label action.
