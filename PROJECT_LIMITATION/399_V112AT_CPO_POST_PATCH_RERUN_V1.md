# V1.12AT CPO Post-Patch Rerun V1

- Truth rows: `7`
- Daily samples: `2160`
- Implementation features added in rerun: `7`

## Core targets
- `phase_progression_label`
  - baseline: `0.6543 -> 0.8380`
  - GBDT: `1.0000 -> 1.0000`
- `role_state_label`
  - baseline: `0.6327 -> 0.5062`
  - GBDT: `1.0000 -> 1.0000`
- `catalyst_sequence_label`
  - baseline: `0.6543 -> 0.8380`
  - GBDT: `1.0000 -> 1.0000`

## Guarded targets
- `board_condition_label`
  - baseline: `0.6759 -> 0.8657`
  - GBDT: `1.0000 -> 1.0000`
- `role_transition_label`
  - baseline: `0.4916 -> 0.6561`
  - GBDT: `1.0000 -> 1.0000`
- `failed_role_promotion_label`
  - baseline: `0.6436 -> 0.9571`
  - GBDT: `1.0000 -> 1.0000`

## Implementation family check
- `implementation_board_calendar_family`
  - full accuracy: `1.0000`
  - masked accuracy: `1.0000`
  - drop: `0.0000`

## Closure
- Current-row post-patch stability is explicit.
- Implementation is no longer the active blocker on the current tiny pilot.
- Next lawful move:
  - `consider_bounded_row_geometry_widen_pilot_now_that_current_truth_rows_are_post_patch_stable`
