# V1.12AU CPO Bounded Row-Geometry Widen Pilot V1

## Summary
- Truth rows before widen: `7`
- Rows after widen: `11`
- Added branch rows: `4`
- Sample count: `3175`

## Core targets
- `phase_progression_label`
  - baseline: `0.8380 -> 0.8573`
  - GBDT: `1.0000 -> 1.0000`
- `role_state_label`
  - baseline: `0.5062 -> 0.5498`
  - GBDT: `1.0000 -> 0.8972`
- `catalyst_sequence_label`
  - baseline: `0.8380 -> 0.8573`
  - GBDT: `1.0000 -> 1.0000`

## Guarded targets
- `board_condition_label`
  - baseline: `0.8657 -> 0.8856`
  - GBDT: `1.0000 -> 1.0000`
- `role_transition_label`
  - baseline: `0.6561 -> 0.5721`
  - GBDT: `1.0000 -> 1.0000`
- `failed_role_promotion_label`
  - baseline: `0.9571 -> 0.9604`
  - GBDT: `1.0000 -> 1.0000`

## Closure
- Core stack did not remain fully stable.
- Guarded stack remained stable.
- Next lawful posture:
  - `keep_branch_rows_as_review_only_and_patch_branch_role_geometry_before_any_training_widen`
