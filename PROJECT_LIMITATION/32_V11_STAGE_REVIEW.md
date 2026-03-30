# 32. V1.1 Stage Review

## Purpose

This review does **not** re-open the shared-default promotion question.

Its purpose is narrower:

1. confirm the current research role of `market_research_v1`
2. confirm how specialist geography has changed after `V1` freeze
3. define how specialist refinement should continue without falling back into
   open-ended replay expansion

## Confirmed Conclusions

### 1. `market_research_v1` has changed status

It is no longer:

1. a planned expansion pack
2. a candidate research direction
3. a speculative future substrate

It is now:

1. a `baseline_ready` research pack
2. a real source of new specialist pockets
3. the preferred next suspect-generating pack when specialist work reopens

### 2. Broad freeze remains intact

The repo did **not** change its broad freeze logic in this cycle.

The current high-level state is still:

1. `shared_default` remains the official shared default
2. `buffer_only_012` remains the strongest frozen broad challenger
3. specialist work is allowed to continue
4. specialist work is **not** promotion evidence for the shared default

### 3. Specialist geography has shifted

The main change in this stage is not a new default winner.

The main change is:

1. specialist opportunity geography is now growing from `market_research_v1`
2. the first new drawdown pocket from `market_research_v1` is interpretable
3. the first new q2 capture pocket from `market_research_v1` is interpretable

### 4. Current output shape is now clearer

Under the current feature set and current replay depth, `market_research_v1`
is producing:

1. new pockets
2. clean reuse of existing families
3. clean persistence edges

It is **not yet** producing:

1. a broad explosion of new family assets
2. strong evidence that the current family inventory should be rewritten
3. a reason to treat all new q2 capture pockets as one single mechanism

## Representative Evidence

### Pack Status

- [market_research_data_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v1.json)
  confirms:
  - `canonical_ready_count = 6`
  - `canonical_partial_count = 0`
  - `derived_ready_count = 3`
  - `baseline_ready = true`

### Broad Comparison

- [20260329T111733Z_3e700662_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T111733Z_3e700662_comparison.json)
  confirms:
  - `mainline_trend_c` best total return and capture inside `market_research_v1`
  - `mainline_trend_a` lowest drawdown

### Specialist Geography Shift

- [20260329T112015Z_d5db1be9_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T112015Z_d5db1be9_comparison.json)
  confirms broad freeze remains stable
- [specialist_alpha_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v2.json)
  confirms:
  - strongest new drawdown pocket:
    `market_research_v1 / 2024_q3 / mainline_trend_c`
  - strongest new capture pockets:
    `market_research_v1 / 2024_q2 / mainline_trend_a|b|c`

### First Drawdown Pocket Classification

- [market_v1_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_c_v1.json)
  identifies `300308` as the dominant positive symbol
- [market_v1_q3_cycle_mechanism_300308_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_c_v1.json)
  confirms a clean reuse of the baseline-style drawdown family:
  - `entry_suppression_avoidance`
  - `earlier_exit_loss_reduction`

### First Q2 Capture Pocket Classification

- [market_v1_q2_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_trade_divergence_capture_c_v1.json)
  identifies `300502` as the dominant positive symbol
- [market_v1_q2_specialist_window_persistence_300502_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_persistence_300502_v1.json)
  confirms a clean persistence edge:
  - specialist keeps the window alive on `2024-06-17`
  - both anchors exit with `assignment_became_junk`
  - specialist remains `late_mover` and `structure_intact`

### Second Q2 Capture Pocket Classification

- [market_v1_q2_symbol_timeline_002371_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_symbol_timeline_002371_capture_c_v1.json)
  identifies an additional specialist-only trade on `2024-06-06 -> 2024-06-07`
- [market_v1_q2_specialist_window_opening_002371_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_opening_002371_v1.json)
  confirms a clean opening edge:
  - permission, filters, and entry triggers are already aligned
  - both anchors remain `junk`
  - specialist upgrades the symbol to `late_mover` and opens the extra window

### Q2 Capture Slice Acceptance

- [market_v1_q2_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_capture_slice_acceptance_v1.json)
  now formalizes the current q2 slice verdict:
  - `acceptance_posture = close_market_q2_capture_slice_as_mixed_opening_plus_persistence`
  - `top_positive_symbols = [300502, 002371, 603259]`
  - `mixed_mechanism_confirmed = true`
  - `do_continue_q2_capture_replay = false`

So under the current evidence, q2 should now be treated as closed at the slice
level rather than kept open symbol by symbol.

### Q3 Drawdown Slice Acceptance

- [market_v1_q3_trade_divergence_quality_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_b_v1.json)
  confirms `300308` is also the dominant positive symbol for
  `market_research_v1 / 2024_q3 / mainline_trend_b`
- [market_v1_q3_cycle_mechanism_300308_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_b_v1.json)
  matches the same baseline-style drawdown map already seen in `q3 / C`
- [market_v1_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cross_strategy_cycle_consistency_v1.json)
  formalizes that the negative-cycle map is identical across `B/C`
- [market_v1_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_drawdown_slice_acceptance_v1.json)
  now closes the q3 drawdown slice:
  - `acceptance_posture = close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse`
  - `shared_top_driver = 300308`
  - `identical_negative_cycle_map = true`
  - `do_continue_q3_drawdown_replay = false`

So under the current evidence, q3 should now also be treated as closed at the
slice level rather than replayed symbol by symbol.

### First Q4 Drawdown Read

- [market_v1_q4_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_trade_divergence_quality_c_v1.json)
  identifies `002371` as the current top positive q4/C symbol
- [market_v1_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_002371_c_v1.json)
  shows that this first q4 driver is only a clean single-row
  `entry_suppression_avoidance`

So q4 is **not** yet closed, but its first result lowers the odds that q4 is
about to produce a broad new drawdown-family wave.

### Q4 Drawdown Slice Acceptance

- [market_v1_q4_cycle_mechanism_000977_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_000977_c_v1.json)
  widens q4 beyond pure avoidance by adding:
  - `preemptive_loss_avoidance_shift`
  - `earlier_exit_loss_reduction`
- [market_v1_q4_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_drawdown_slice_acceptance_v1.json)
  now formalizes the q4 slice verdict:
  - `acceptance_posture = close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix`
  - `top_positive_symbols = [002371, 000977, 000858]`
  - `do_continue_q4_drawdown_replay = false`

So under the current evidence, q4 should now also be treated as closed at the
slice level.

## Current Risks

### 1. Misreading new pockets as new family expansion

`market_research_v1` is now productive, but that does not mean it is already
producing a new family wave.

Current evidence still leans toward:

1. clean reuse
2. persistence-edge clarification
3. better pocket geography

not toward:

1. large-scale family frontier expansion

### 2. Reopening wide replay expansion too early

The repo should **not** use `market_research_v1` as an excuse to restart a
large replay queue.

The current stage supports:

1. narrow specialist replay
2. mechanism-first pocket classification

It does **not** support:

1. broad queue restart
2. sample-volume growth without stage control

### 3. Letting stage definition lag behind sample growth

The main reason for this review is to prevent a familiar failure mode:

1. new pockets keep arriving
2. replay keeps moving
3. but phase definition stays stuck in the old state

This review prevents that drift.

## Continue Conditions

Specialist refinement may continue only under these constraints:

1. use `market_research_v1` as the first new suspect substrate
2. keep replay narrow and mechanism-first
3. classify new pockets against the existing family inventory before creating
   any new family label
4. prefer pockets that can change the current stage conclusion, not just add
   another example

## Stop Conditions

The current specialist stage should pause again if any of these become true:

1. new `market_research_v1` pockets continue to collapse into clean reuse of
   existing families
2. new `market_research_v1` pockets add only more persistence/opening
   annotations without changing the current family boundary
3. new replays stop changing the current stage conclusion:
   `market_research_v1` is productive, but still mainly a source of
   interpretable pocket reuse rather than broad new-family discovery
4. a slice-level acceptance report already confirms the current mixed reading
   and continuation would only add more examples without changing the slice
   verdict
5. a q3 drawdown slice already has:
   - the same top positive driver across `B/C`
   - an identical negative-cycle map across `B/C`
   - a slice-level acceptance report that closes it as cross-strategy stable
6. q4 already has:
   - one clean avoidance driver
   - one reduced-loss driver that widens q4 beyond pure avoidance
   - a slice-level acceptance report that closes it as a mixed drawdown slice

If these conditions hold, the correct action is:

1. stop replay expansion
2. strengthen the current inventory
3. wait for a larger or materially different suspect batch

## Validation Status

This stage review is based on successful targeted validation, not a fresh full
regression cycle.

Validated in this stage:

1. `pytest tests/test_bootstrap_derived.py`
   - `6 passed`
2. `pytest tests/test_symbol_timeline_replay.py tests/test_symbol_cycle_delta_analysis.py tests/test_cycle_mechanism_analysis.py`
   - `8 passed`
3. `pytest tests/test_symbol_timeline_replay.py tests/test_specialist_window_opening_analysis.py tests/test_specialist_window_persistence_analysis.py`
   - `3 passed`
4. `pytest tests/test_market_q3_drawdown_slice_acceptance.py tests/test_cross_strategy_cycle_consistency_analysis.py tests/test_cycle_mechanism_analysis.py`
   - `8 passed`

Not rerun in this stage:

1. full `pytest`

So the correct reading is:

1. current narrow path is validated
2. full-suite state remains whatever was last established before this stage

## Stage Verdict

`market_research_v1` has now crossed the boundary from:

- broader pack candidate

to:

- official next suspect-generating substrate

The repo should therefore treat the current `V1.1` state as:

1. broad freeze unchanged
2. specialist geography updated
3. `market_research_v1` confirmed as the next specialist substrate
4. specialist replay allowed only as narrow mechanism-first continuation
5. `market_research_v1 / 2024_q2` is now a closed mixed capture slice
6. `market_research_v1 / 2024_q3` is now a closed cross-strategy baseline-style drawdown slice
7. `market_research_v1 / 2024_q4` is now a closed mixed drawdown slice:
   pure avoidance plus reduced-loss structure
8. the next refinement step is now conditional context, not board-specific
   training:
   [sector_theme_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/sector_theme_context_audit_v1.json)
   recommends:
   - `theme_load_plus_turnover_concentration_context`
   - then `sector_state_heat_breadth_context`
9. the first context branch is now explicit and still narrow:
   [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json)
   recommends:
   - `conditioned_late_quality_on_theme_turnover_context`
   - `defer_sector_heat_branch = true`
10. that conditioned branch has now been tested and closed as non-material:
   - [context_feature_pack_a_conditioned_late_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_v1.json)
     shows real candidate rows only in `q2/q4`, all in mid/high interaction buckets
   - [context_feature_pack_a_conditioned_late_quality_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_acceptance_v1.json)
     closes the branch:
     - `acceptance_posture = close_conditioned_late_quality_branch_as_non_material`
     - `material_improvement_count = 0`
     - `do_promote_conditioned_branch = false`
11. the deferred second context branch has now also been audited and closed as sparse:
   - [context_feature_pack_b_sector_heat_breadth_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_b_sector_heat_breadth_v1.json)
     shows only `1` surviving candidate row, all inside `2024_q4`
   - so the current posture is:
     - `close_sector_heat_breadth_context_branch_as_sparse`
     - `do_continue_context_feature_pack_b = false`
   - therefore the repo should not treat sector heat / breadth as the next retained branch
     and still should not jump to per-sector training
12. the current specialist loop should now pause rather than invent another
    continuation lane:
    - [v11_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v11_continuation_readiness_v1.json)
      concludes:
      - `all_market_v1_slices_closed = true`
      - `all_context_branches_closed = true`
      - `u2_ready = false`
      - `recommended_next_phase = pause_specialist_refinement_and_prepare_new_suspect_batch`
    - therefore the next healthy move is a new suspect batch, not more local
      replay inside the current closed geography
13. the next suspect batch should now be designed by missing context
    archetypes rather than random size expansion:
    - [next_suspect_batch_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_design_v1.json)
      concludes:
      - `recommended_next_batch_name = market_research_v2_seed`
      - `recommended_batch_posture = expand_by_missing_context_archetypes`
      - current missing archetypes:
      - `theme_loaded + balanced_turnover + broad_sector`
      - `theme_loaded + balanced_turnover + narrow_sector`
      - `theme_light + concentrated_turnover + broad_sector`
14. the first `market_research_v2_seed` manifest is now also ready:
    - [next_suspect_batch_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v1.json)
      concludes:
      - `seed_universe_count = 9`
      - `new_symbol_count = 9`
      - `overlap_with_market_v1_count = 0`
      - `missing_archetype_count = 0`
      - `ready_to_bootstrap_market_research_v2_seed = true`
    - therefore the next stage no longer needs another design loop before data
      bootstrap; it can move into controlled `v2_seed` construction
15. `market_research_v2_seed` has now completed that construction step:
    - [market_research_data_audit_v2_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_seed.json)
      confirms:
      - `canonical_ready_count = 6`
      - `canonical_partial_count = 0`
      - `derived_ready_count = 3`
      - `baseline_ready = true`
    - [20260329T130402Z_0e1d8809_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130402Z_0e1d8809_comparison.json)
      shows:
      - `mainline_trend_c` best total return and capture
      - `mainline_trend_b` lowest drawdown
16. the first four-pack validation that includes `market_research_v2_seed`
    now also exists:
    - [20260329T130537Z_f0a9da05_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130537Z_f0a9da05_comparison.json)
      keeps `buffer_only_012` as the broad stability leader
    - [specialist_alpha_analysis_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v3.json)
      shows both specialist branches now have qualifying pockets inside
      `market_research_v2_seed`
    So `v2_seed` is now an active specialist substrate, but still secondary to
    `market_research_v1` under the current stage reading.
17. the first narrow replay inside `market_research_v2_seed` now also exists:
    - [market_v2_seed_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_trade_divergence_capture_c_v1.json)
      identifies `603986` as the dominant q4/C capture symbol
    - [market_v2_seed_q4_specialist_window_opening_603986_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_specialist_window_opening_603986_v1.json)
      confirms a clean opening edge on `2024-12-12`
    - but [market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json)
      also shows a positive trade carried in from before q4
    So the current q4/C read should be treated as a mixed opening-plus-carry
    pocket rather than a clean new family boundary.
18. that q4/C read now also has an explicit stop gate:
    - [market_v2_seed_q4_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_capture_slice_acceptance_v1.json)
      concludes:
      - `acceptance_posture = close_market_v2_seed_q4_capture_slice_as_opening_plus_carry`
      - `do_continue_q4_capture_replay = false`
    So the first `v2_seed` capture slice is now closed under the current
    evidence rather than left as an open replay lane.
19. the first `v2_seed / q3 / C` drawdown lane now also exists:
    - [market_v2_seed_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_trade_divergence_quality_c_v1.json)
      identifies `603986` as the dominant q3/C drawdown symbol
    - [market_v2_seed_q3_cycle_mechanism_603986_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_cycle_mechanism_603986_c_v1.json)
      shows:
      - negative side: `entry_suppression_avoidance`
      - positive side: `entry_suppression_opportunity_cost`
    So the current q3/C lane should be read as a useful but mixed drawdown
    pocket, not a clean new family frontier.
20. that q3/C drawdown read now also has an explicit stop gate:
    - [market_v2_seed_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_drawdown_slice_acceptance_v1.json)
      concludes:
      - `acceptance_posture = close_market_v2_seed_q3_drawdown_slice_as_avoidance_plus_opportunity_cost`
      - `do_continue_q3_drawdown_replay = false`
    So the second `v2_seed` lane is now also closed under the current
    evidence rather than left as an open replay branch.
21. `v2_seed` now also has its own continuation gate:
    - [market_v2_seed_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_continuation_readiness_v1.json)
      concludes:
      - `all_open_v2_seed_lanes_closed = true`
      - `v2_seed_baseline_ready = true`
      - `v2_seed_contributes_specialist_pockets = true`
      - `recommended_next_phase = hold_market_v2_seed_as_secondary_substrate_and_wait_for_next_batch_refresh`
      - `do_continue_current_v2_seed_replay = false`
    So `v2_seed` is now formally bounded: useful enough to keep, but not open
    enough to justify another local replay lane by inertia.
22. the repo now also has a trigger gate for the *next* refresh after
    `v2_seed`:
    - [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json)
      concludes:
      - `v11_current_loop_paused = true`
      - `v2_seed_local_loop_paused = true`
      - `v2_seed_secondary_substrate_status = true`
      - `recommended_next_phase = wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh`
      - `do_open_market_research_v2_refresh_now = false`
    So the repo should not design `market_research_v2_refresh` yet. The next
    refresh must be triggered by a new archetype-gap signal or a materially
    different suspect geography, not by momentum.
23. the repo now also has an operational trigger monitor:
    - [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json)
      currently reads:
      - `active_trigger_count = 0`
      - `archetype_gap_trigger = false`
      - `specialist_geography_trigger = false`
      - `clean_frontier_trigger = false`
      - `secondary_status_break_trigger = false`
      - `recommended_posture = maintain_waiting_state_until_new_trigger`
    So the current phase is not just "paused"; it is explicitly in a
    no-trigger waiting state.
24. the repo now also has a concrete operator checklist for that waiting
    state:
    - [refresh_trigger_action_plan_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_action_plan_v1.json)
      currently reads:
      - `action_mode = idle_wait_state`
      - `action_count = 3`
    So the current wait state is no longer just conceptual; it already has an
    explicit command/order plan for both the idle case and the future trigger
    case.
25. the repo now also has a one-page phase status snapshot:
    - [phase_status_snapshot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/phase_status_snapshot_v1.json)
      currently reads:
      - `current_mode = explicit_no_trigger_wait`
      - `all_gates_aligned = true`
      - `active_trigger_count = 0`
      - `recommended_operator_posture = idle_wait_state`
    So the current phase can now be checked from a single report rather than
    by inspecting all gate layers separately.
26. the repo now also has a one-command refresh chain for that snapshot:
    - [41_PHASE_STATUS_REFRESH_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/41_PHASE_STATUS_REFRESH_RUNBOOK.md)
    - `python scripts/run_phase_status_refresh.py`
    This refreshes readiness -> monitor -> action plan -> snapshot in order,
    without reopening any research lane by itself.
27. the repo now also has a concise console entrypoint:
    - `python scripts/run_phase_status_console.py`
    It prints the current phase mode, trigger count, and next actions from the
    already-refreshed reports.
28. the repo now also has a shortest safe phase guard:
    - [42_PHASE_GUARD_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/42_PHASE_GUARD_RUNBOOK.md)
    - `python scripts/run_phase_guard.py`
    It refreshes the current gate stack and immediately prints the final
    operator-facing read, so the repo now has a single command for the
    question "can anything new happen right now?".

## One-Line Rule

`market_research_v1` is now the default starting point for the next specialist
suspect cycle, but not a reason to reopen uncontrolled replay expansion.
`market_research_v2_seed` is now the first targeted expansion substrate, but
not yet a reason to rewrite the current stage hierarchy. Under the current
evidence, its first q4/C and q3/C lanes are both closed as mixed slice reads,
the pack as a whole is now held as a bounded secondary substrate, and the next
post-v2 refresh is now explicitly gated rather than implied. The current
operational reading is: no trigger is active, so the repo should wait, and
the waiting-state execution order is now already defined. That state is also
compressed into a one-page snapshot.
