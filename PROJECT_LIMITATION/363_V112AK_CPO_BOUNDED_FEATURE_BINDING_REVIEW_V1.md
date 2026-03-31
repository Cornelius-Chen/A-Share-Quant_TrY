# V1.12AK CPO Bounded Feature Binding Review V1

## Binding Counts
- evaluated bindings: `56`
- direct bindable: `21`
- guarded bindable: `17`
- row-specific blocked: `18`

## Main Findings
- `phase_progression_label`, `role_state_label`, and `catalyst_sequence_label` bind cleanly across the current truth-candidate set.
- `board_condition_label` remains usable, but only with operational-gap guard.
- `quiet_window_survival_label` is globally admitted yet currently weak on the present truth-candidate geometry.
- `spillover_maturity_boundary_label` is globally admitted but not meaningfully bindable on the current primary/secondary truth rows.

## Interpretation
- global admission is not the same as local row-level usability
- this phase prevents the system from treating allowed labels as universally usable
