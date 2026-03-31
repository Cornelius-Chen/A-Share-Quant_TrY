# V1.12AG CPO Bounded Label-Draft Assembly V1

## Draft Label Skeleton
- `phase_progression_label`
- `role_state_label`
- `role_transition_label`
- `catalyst_sequence_label`
- `board_condition_label`
- `quiet_window_survival_label`
- `failed_role_promotion_label`
- `branch_upgrade_label`
- `spillover_maturity_boundary_label`
- `residual_core_vs_collapse_label`

## Most Important Guards
- `role_transition_label`
  - must stay provisional until handoff acceptance is visible in-window
- `quiet_window_survival_label`
  - must not quietly consume post-window outcome information
- `failed_role_promotion_label`
  - must separate at-risk promotion from confirmed failure
- `spillover_maturity_boundary_label`
  - must preserve overlay-only posture
- `residual_core_vs_collapse_label`
  - remains confirmed-only review language

## Ambiguity Preservation
- pending rows remain pending:
  - `300620`
  - `300548`
  - `000988`
- overlay-only spillover rows remain diagnostic:
  - `000070`
  - `603228`
  - `001267`
- branch/support rows remain support-only until later evidence justifies any upgrade
