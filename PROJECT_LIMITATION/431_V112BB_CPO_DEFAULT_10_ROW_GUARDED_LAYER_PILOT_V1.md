## V1.12BB Result

- Default bounded pilot layer:
  - `10` rows
  - `2934` samples
- Core targets:
  - `phase_progression_label`
  - `role_state_label`
  - `catalyst_sequence_label`
- Guarded targets:
  - `board_condition_label`
  - `role_transition_label`
  - `failed_role_promotion_label`

### Frozen result
- `core_targets_stable_vs_7_row_baseline = True`
- `guarded_targets_stable_vs_7_row_guarded_baseline = True`
- `core_targets_consistent_vs_prior_10_row_guarded_pilot = True`
- `guarded_targets_consistent_vs_prior_10_row_guarded_pilot = True`

### Key read
- The strongest result is not a new gain spike.
- The strongest result is that the `10`-row guarded layer now behaves as a stable default experimental baseline.
- `role_state_label` still shows the most important structural gain over the old `7`-row baseline:
  - `0.7377 -> 1.0000`

### Trading-side probe on phase target
- guardrail constructive-phase avg `20d` return: `0.0899`
- `GBDT` constructive-phase avg `20d` return: `0.0979`
- guardrail constructive-phase avg max drawdown: `-0.1100`
- `GBDT` constructive-phase avg max drawdown: `-0.1063`

### Boundary
- formal training: closed
- formal signal generation: closed
- `300570`: still outside the default training-facing layer
