# 44. V1.2 Data Expansion And Factorization Prep

## Purpose

This file defines the next active research phase after the current
`V1.1 specialist refinement` loop has correctly entered an explicit waiting
state.

`V1.2` is not a restart of the old replay loop.

It is a new phase with two linked goals:

1. expand the next research input layer with materially different sample
   coverage
2. convert the repo's current mechanism/family/context knowledge into a formal
   factor/feature preparation layer

## Why This Phase Exists

The repo now already knows how to:

1. run and pause a bounded specialist loop
2. reject low-value local replay continuation
3. preserve interpretable family and context findings

The next bottleneck is no longer local replay depth.

The next bottlenecks are:

1. insufficient new suspect geography
2. insufficient feature/factor formalization of what has already been learned

## Top-Level Objectives

### Objective A: Data Expansion

Open a new batch direction that is larger than `market_research_v2_seed`,
but still controlled and interpretable.

The first target is `market_research_v2_refresh`.

This refresh should:

1. expand by missing archetypes rather than by random size
2. remain compatible with the free-data bootstrap path
3. preserve point-in-time discipline as much as the public data allows
4. be auditable before it is replayed

### Objective B: Factorization Prep

Formalize the repo's current research assets into a feature/factor preparation
layer.

This layer should:

1. distinguish retained features from explanatory-only features
2. preserve current family/context findings in a reusable registry
3. prepare later ranking / factor-evaluation / ML work without forcing early
   model training

## Non-Goals

`V1.2` should not:

1. restart wide replay inside already closed `V1.1` slices
2. jump straight into per-sector model training
3. jump straight into heavy unsupervised modeling
4. jump straight into live execution work

## First Workstream Order

The intended order is:

1. define `market_research_v2_refresh` data scope
2. define the data-source inventory and source-of-truth policy
3. bootstrap and audit the refreshed pack
4. run the first refreshed suite and specialist analysis
5. only then open the first formal feature/factor registry layer

## Success Criteria

`V1.2` should be considered on-track when:

1. the repo has one new runnable refreshed research pack beyond `v2_seed`
2. that pack adds materially different suspect geography
3. the repo has a first feature/factor registry skeleton
4. retained vs explanatory-only features are explicitly separated

## Deferred Branches

The following branches are explicitly deferred rather than forgotten:

1. `intraday_data_pilot`
   - purpose: test whether daily-edge conclusions survive more realistic
     intraday execution timing and friction
   - posture: defer until the current `V1.2` data-expansion and
     factorization-prep work has produced a wider retained feature layer
   - reason: intraday data is important for the final goal, but it is not the
     current bottleneck in this phase

## Current Status

`V1.2` is now active rather than only planned.

Completed so far:

1. the data-source inventory is explicit
2. `market_research_v2_refresh` is now runnable and `baseline_ready`
3. the first `v2_refresh` q1/C drawdown lane has been replayed and closed as
   a mixed slice
4. the repo now also has the first formal feature/factor registry artifact
5. the first formal factor-evaluation protocol now exists and has classified
   the current candidate bucket
6. the first bounded factor lane has now opened for
   `carry_in_basis_advantage`
7. the first carry factor design artifact now restricts that lane to
   row-isolated carry design rather than broad pocket scoring
8. the first carry observable schema now exists and makes the lane field-level
   rather than only narrative
9. the first carry scoring design now exists and confirms that the current
   shared B/C rows are fully isomorphic under the bounded score
10. the first carry factor pilot now exists and is correctly limited to a
    report-only micro-pilot
11. the first bounded factorization cycle has now been formally reviewed and
    closed as representative but still bounded
12. `V1.2` phase readiness now explicitly remains open because the first pilot
    still lacks row diversity and needs a later refresh batch
13. the next refresh design is now explicitly aimed at factor-row diversity
    rather than generic sample growth
14. the `market_research_v3_factor_diversity_seed` manifest has now passed its
    gate and is ready for bootstrap
15. `market_research_v3_factor_diversity_seed` has now completed bootstrap,
    audits as `baseline_ready`, and has produced its first suite run
16. `market_research_v3_factor_diversity_seed` has now entered the active
    specialist map, with its first `q4 / mainline_trend_c` capture lane open
17. the first `v3` lane has now been structurally narrowed enough to show
    `002049 / q4 / C` is opening-led rather than persistence-led
18. a short phase-level bottleneck check now confirms that this first `v3`
    lane does not change the main `V1.2` bottleneck reading
19. `V1.2` now has a criteria-first next-refresh entry rather than only a
    generic future-refresh intention
20. `V1.2` now also has frozen symbol-selection criteria for the next `v4`
    carry-row-diversity refresh
21. `V1.2` now has a green `v4` carry-row-diversity manifest and can move
    from criteria-ready to bootstrap-ready
22. `V1.2` now has a `v4` pack that is bootstrap-complete, `baseline_ready`,
    and visible in the active specialist map

Key evidence:

- [45_DATA_SOURCE_INVENTORY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/45_DATA_SOURCE_INVENTORY.md)
- [46_MARKET_RESEARCH_V2_REFRESH_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/46_MARKET_RESEARCH_V2_REFRESH_PLAN.md)
- [market_research_data_audit_v2_refresh.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_refresh.json)
- [market_v2_refresh_q1_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_refresh_q1_drawdown_slice_acceptance_v1.json)
- [feature_factor_registry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_factor_registry_v1.json)
- [factor_evaluation_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/factor_evaluation_protocol_v1.json)
- [carry_in_basis_first_pass_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_in_basis_first_pass_v1.json)
- [carry_factor_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_design_v1.json)
- [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)
- [carry_scoring_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_scoring_design_v1.json)
- [carry_factor_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_pilot_v1.json)
- [v12_factorization_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_factorization_review_v1.json)
- [v12_phase_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_phase_readiness_v1.json)
- [v12_next_refresh_factor_diversity_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_factor_diversity_design_v1.json)
- [market_research_v3_factor_diversity_seed_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_research_v3_factor_diversity_seed_manifest_v1.json)
- [market_research_data_audit_v3_factor_diversity_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v3_factor_diversity_seed.json)
- [20260330T005408Z_70e5fe8c_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260330T005408Z_70e5fe8c_comparison.json)
- [20260330T005654Z_c28cab1a_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260330T005654Z_c28cab1a_comparison.json)
- [specialist_alpha_analysis_v5.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v5.json)
- [market_v3_factor_diversity_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_trade_divergence_capture_c_v1.json)
- [market_v3_factor_diversity_q4_specialist_window_opening_002049_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_specialist_window_opening_002049_v1.json)
- [market_v3_factor_diversity_q4_specialist_window_persistence_002049_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_factor_diversity_q4_specialist_window_persistence_002049_v1.json)
- [market_v3_q4_first_lane_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v3_q4_first_lane_acceptance_v1.json)
- [v12_bottleneck_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_bottleneck_check_v1.json)
- [v12_next_refresh_entry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_entry_v1.json)
- [v12_v4_refresh_criteria_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_v4_refresh_criteria_v1.json)
- [market_research_v4_carry_row_diversity_refresh_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_research_v4_carry_row_diversity_refresh_manifest_v1.json)
- [market_research_data_audit_v4_carry_row_diversity_refresh.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v4_carry_row_diversity_refresh.json)
- [20260330T015501Z_a2b9cc4a_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260330T015501Z_a2b9cc4a_comparison.json)
- [20260330T015559Z_22ccd733_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260330T015559Z_22ccd733_comparison.json)
- [specialist_alpha_analysis_v6.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v6.json)

## Immediate Next Step

The next step is no longer another generic refresh design exercise, bootstrap
plumbing task, basic registry construction, or broad candidate-factor handling.

The next step is:

1. compare `market_research_v3_factor_diversity_seed` against the current
   research map
2. keep the first bounded factor lane focused on
   `carry_in_basis_advantage`
3. keep the current carry pilot in report-only mode until more row diversity
   appears
4. replay only the first `v3` lane that can change the current carry
   row-diversity reading
5. do not yet promote it into the retained-feature pool
6. do not open the second factor lane yet
7. keep penalty-track and thin factors out of the first-pass factor workflow
   until their extra conditions are handled
8. treat `002049 / q4 / C` as the first structural check, not as proof of a
   carry breakthrough
9. keep `v3` lane expansion closed until a later lane changes the current
   opening-led reading
10. keep the main `V1.2` bottleneck defined as missing carry row diversity
    until a later lane or later refresh batch materially changes that reading
11. prepare the next refresh as a criteria-first entry for
    `market_research_v4_carry_row_diversity_refresh` before any new manifest
    is written
12. use the frozen `v4` criteria to draft the next manifest, rather than
    reopening replay or widening the current `v3` map
13. move from manifest-ready to bootstrap before reopening any specialist map
    work
14. after `v4` becomes active in the map, open only one first `v4` lane rather
    than widening replay immediately
15. treat `601919 / q2 / A` as the first `v4` structural check
16. close that first `v4` lane as opening-led if persistence stays absent
17. do not reinterpret the first `v4` lane as a carry breakthrough unless it
    materially changes the current carry-row-diversity bottleneck
18. keep a deferred `catalyst persistence` context hypothesis branch available
    for later testing if new substrates continue surfacing opening-led lanes
    before carry-led ones
## Catalyst Context Branch

A deferred catalyst-persistence context branch now has a frozen row schema:

- [61_CATALYST_CARRY_CONTEXT_HYPOTHESIS_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/61_CATALYST_CARRY_CONTEXT_HYPOTHESIS_PLAN.md)
- [62_CATALYST_EVENT_REGISTRY_SCHEMA_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/62_CATALYST_EVENT_REGISTRY_SCHEMA_V1.md)
- [catalyst_event_registry_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_schema_v1.json)

The branch remains report-only and deferred; it exists to test whether source quality and catalyst persistence can later explain why new substrates surface opening-led lanes before carry-led ones.

## Bounded Training Pilot

`V1.2` now also includes a first bounded training pilot:

- [63_V12_BOUNDED_TRAINING_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/63_V12_BOUNDED_TRAINING_PILOT_V1.md)
- [v12_bounded_training_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_bounded_training_pilot_v1.json)

Current reading:

1. the pilot uses only frozen structured lane artifacts
2. the pilot separates `opening_led`, `persistence_led`, and
   `carry_row_present` cleanly in a tiny leave-one-out nearest-centroid check
3. this is evidence that current structured observables are trainable at a
   bounded report-only level
4. this is not evidence that the repo is ready for strategy-level ML or
   raw-news training

The immediate follow-up check is now also complete:

- [64_V12_TRAINING_READINESS_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/64_V12_TRAINING_READINESS_CHECK_V1.md)
- [v12_training_readiness_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_readiness_check_v1.json)

Current reading from the readiness check:

1. the micro-pilot is informative but still too small
2. carry rows remain duplicated
3. the training branch should remain report-only
4. neither strategy-level ML nor news-branch training should open yet

The next bounded step is now also frozen:

- [65_V12_TRAINING_SAMPLE_EXPANSION_DESIGN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/65_V12_TRAINING_SAMPLE_EXPANSION_DESIGN_V1.md)
- [v12_training_sample_expansion_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_sample_expansion_design_v1.json)
- [66_V12_TRAINING_SAMPLE_MANIFEST_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/66_V12_TRAINING_SAMPLE_MANIFEST_V1.md)
- [v12_training_sample_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_sample_manifest_v1.json)

Current reading:

1. opening-led rows are sufficient for the current micro branch and should stay frozen
2. persistence rows remain thin and should only expand via new clean persistence cases
3. carry rows remain the primary scarcity and should only expand via future true carry rows
4. relabelling penalty-track or deferred basis families into the carry class remains explicitly forbidden

That training manifest is now operationalized by a binding gate:

- [67_V12_TRAINING_SAMPLE_BINDING_GATE_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/67_V12_TRAINING_SAMPLE_BINDING_GATE_V1.md)
- [v12_training_sample_binding_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_sample_binding_gate_v1.json)

Current reading:

1. the current opening-led first lanes from `v3` and `v4` stay outside the training branch
2. future clean persistence rows remain bindable
3. future true carry rows remain bindable
4. the branch now has an explicit operational gate that prevents silent widening

That posture is now exposed as a per-lane check:

- [68_V12_TRAINING_LANE_BINDING_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/68_V12_TRAINING_LANE_BINDING_CHECK_V1.md)
- [v12_training_lane_binding_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_lane_binding_check_v1.json)

Current reading:

1. a newly closed lane may bind only as a clean persistence row or a true carry row
2. the current `v3` and `v4` first lanes remain rejected because they are opening-led
3. the training branch now has a concrete per-lane intake check rather than only a static manifest

The catalyst hypothesis branch has now moved from schema-only to a bounded seed:

- [69_CATALYST_EVENT_REGISTRY_SEED_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/69_CATALYST_EVENT_REGISTRY_SEED_V1.md)
- [catalyst_event_registry_seed_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_seed_v1.json)

Current reading:

1. the catalyst branch now has a small auditable lane sample instead of only a schema
2. the sample mixes opening-led, persistence-led, and carry-row-present cases
3. the next catalyst step is event-field filling, not wide news crawling or immediate modeling

The first bounded catalyst fill is now also open:

- [70_CATALYST_EVENT_REGISTRY_FILL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/70_CATALYST_EVENT_REGISTRY_FILL_V1.md)
- [catalyst_event_registry_fill_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_fill_v1.json)

Current reading:

1. the catalyst branch now has a market-context-only first fill
2. theme-versus-sector scope and mapped context names are now populated for the seed rows where local mappings exist
3. official source authority still remains a later manual or semi-manual fill layer

That later source layer is now partially open:

- [71_CATALYST_EVENT_REGISTRY_SOURCE_FILL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/71_CATALYST_EVENT_REGISTRY_SOURCE_FILL_V1.md)
- [72_CATALYST_SOURCE_REFERENCES_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/72_CATALYST_SOURCE_REFERENCES_V1.md)
- [catalyst_event_registry_source_fill_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_source_fill_v1.json)

Current reading:

1. the catalyst branch now has partial official/high-trust source coverage where context is reasonably clear
2. unresolved rows remain explicitly unresolved
3. this is enough to open a first bounded catalyst-context audit later without pretending the source layer is complete

That first bounded catalyst-context audit is now complete:

- [73_CATALYST_CONTEXT_AUDIT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/73_CATALYST_CONTEXT_AUDIT_V1.md)
- [catalyst_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_context_audit_v1.json)

Current reading:

1. opening rows currently stay in `single_pulse`
2. persistence rows currently cluster in `multi_day_reinforcement`
3. carry rows currently cluster in `policy_followthrough`
4. this is enough to keep the catalyst branch active, but not enough to promote it into a retained factor or a training feature

That catalyst result is now also phase-checked:

- [74_V12_CATALYST_BRANCH_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/74_V12_CATALYST_BRANCH_PHASE_CHECK_V1.md)
- [v12_catalyst_branch_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_catalyst_branch_phase_check_v1.json)

Current reading:

1. the catalyst branch is now real enough to keep active
2. it remains report-only and bounded
3. it does not replace the current `V1.2` main bottleneck of missing carry row diversity

The mainline next-step hunt is now also frozen:

- [75_V12_CARRY_ROW_HUNTING_STRATEGY_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/75_V12_CARRY_ROW_HUNTING_STRATEGY_V1.md)
- [v12_carry_row_hunting_strategy_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_carry_row_hunting_strategy_v1.json)

Current reading:

1. do not open a new refresh batch now
2. do not widen replay
3. keep hunting inside the current `v4` refresh one symbol at a time
4. prioritize basis-spread and carry-duration targets before revisiting exit-alignment
## 2026-03-30 Update: v4 000725 single-symbol hunt closed inactive
- Added `market_v4_q2_symbol_hunt_acceptance_000725_v1.json` and `76_V12_CARRY_ROW_HUNT_000725_V1.md`.
- `000725` closes as `no_active_structural_lane`: `pnl_delta = 0.0`, `opening_present = false`, `persistence_present = false`.
- This keeps the V1.2 primary bottleneck unchanged: carry row diversity is still missing.
- The next bounded hunt target shifts to `600703`; no replay widening and no new refresh is justified.
## 2026-03-30 Update: v4 600703 single-symbol hunt also closes inactive
- Added `market_v4_q2_symbol_hunt_acceptance_600703_v1.json` and `77_V12_CARRY_ROW_HUNT_600703_V1.md`.
- `600703` also closes as `no_active_structural_lane`: `pnl_delta = 0.0`, `opening_present = false`, `persistence_present = false`.
- Two consecutive `basis_spread_diversity` hunts inside v4 have now failed to produce an active structural lane.
- The next bounded hunt target shifts to `600150` from the `carry_duration_diversity` track.
## 2026-03-30 Update: v4 600150 duration-track hunt also closes inactive
- Added `market_v4_q2_symbol_hunt_acceptance_600150_v1.json` and `78_V12_CARRY_ROW_HUNT_600150_V1.md`.
- `600150` closes as `no_active_structural_lane`: `pnl_delta = 0.0`, `opening_present = false`, `persistence_present = false`.
- The checked v4 hunt has now eliminated two `basis_spread_diversity` targets and the first `carry_duration_diversity` target without finding an active carry-supporting lane.
- The next bounded hunt target shifts to `601127`.
## 2026-03-30 Update: v4 601127 duration-track hunt also closes inactive
- Added `market_v4_q2_symbol_hunt_acceptance_601127_v1.json` and `79_V12_CARRY_ROW_HUNT_601127_V1.md`.
- `601127` closes as `no_active_structural_lane`: `pnl_delta = 0.0`, `opening_present = false`, `persistence_present = false`.
- The checked high-priority `basis_spread_diversity` and `carry_duration_diversity` tracks inside the current v4 hunt have now all closed inactive.
- The correct next step is a short phase-level check before touching lower-priority tracks.
## 2026-03-30 Update: v4 q2/A high-priority carry hunt pauses for reassessment
- Added `v12_v4_hunt_phase_check_v1.json` and `80_V12_V4_HUNT_PHASE_CHECK_V1.md`.
- The checked `basis_spread_diversity` and `carry_duration_diversity` targets inside the current v4 hunt are now fully exhausted and all closed inactive.
- `V1.2` primary bottleneck remains `carry_row_diversity_gap`, but this specific `v4 / q2 / A` hunt area should pause before lower-priority tracks.
- The correct next posture is `reassess_v4_hunt_posture_before_cross_dataset_or_exit_alignment_tracks`.
## 2026-03-30 Update: v4 reassessment fixes the substrate reading
- Added `v12_v4_reassessment_v1.json` and `81_V12_V4_REASSESSMENT_V1.md`.
- `v4` remains an active substrate in the wider specialist map, but the checked `q2 / A` high-priority hunt region is now locally exhausted.
- This means the main `V1.2` bottleneck still remains `carry_row_diversity_gap`, while the correct next move is to return to a higher-level batch/substrate decision rather than widening local `v4` replay.
## 2026-03-30 Update: V1.2 batch/substrate decision returns to next refresh prep
- Added `v12_batch_substrate_decision_v1.json` and `82_V12_BATCH_SUBSTRATE_DECISION_V1.md`.
- Current decision: `prepare_next_refresh_batch_instead_of_reopening_existing_local_substrate`.
- `carry_row_diversity_gap` remains the primary bottleneck, `v4` remains active globally, but the checked local v4 hunt is exhausted.
- The correct next move is now to prepare the next refresh batch for carry-row diversity rather than reopen local v3/v4 replay.
## 2026-03-30 Update: V1.2 next refresh entry v2 opens v5
- Added `v12_next_refresh_entry_v2.json` and `83_V12_NEXT_REFRESH_ENTRY_V2.md`.
- The next executable batch entry is now fixed as `market_research_v5_carry_row_diversity_refresh`.
- The required posture is `criteria_first_true_carry_plus_clean_persistence_refresh`.
- The next refresh should target `2` additional true carry rows and `2` additional clean persistence rows, while keeping catalyst context support-only.
## 2026-03-30 Update: v5 refresh criteria frozen
- Added `v12_v5_refresh_criteria_v1.json` and `84_V12_V5_REFRESH_CRITERIA_V1.md`.
- `v5` is now frozen as a training-gap-aware refresh, not a generic carry expansion.
- The next batch must target `2` additional true carry rows and `2` additional clean persistence rows while keeping opening frozen.
- Local `v4 / q2 / A` replay remains excluded from primary v5 sourcing.
## 2026-03-30 Update: v5 manifest v1 ready to bootstrap
- Added `market_research_v5_carry_row_diversity_refresh_manifest_v1.json` and `85_MARKET_RESEARCH_V5_CARRY_ROW_DIVERSITY_REFRESH_PLAN.md`.
- `v5` manifest is green: `4` new symbols, `2` targeting `true_carry_row`, `2` targeting `clean_persistence_row`.
- There is no overlap with the combined reference base, no missing target class, and no opening-clone admission reason.
- The next correct action is to bootstrap `market_research_v5_carry_row_diversity_refresh`.
## 2026-03-30 Update: v5 refresh bootstrapped and entered the active map
- Added `reports/data/market_research_data_audit_v5_carry_row_diversity_refresh.json` with `baseline_ready = true`.
- Added pack-level suite report `reports/20260330T041310Z_130eb2ed_comparison.json`; inside the pack, `mainline_trend_b` and `mainline_trend_c` tie for best total return, capture, and lowest drawdown.
- Added eight-pack time-slice validation report `reports/20260330T041451Z_b6297292_comparison.json`.
- Added `reports/analysis/specialist_alpha_analysis_v8.json`; `market_research_v5_carry_row_diversity_refresh` is now present in the active specialist geography for `baseline_expansion_branch`, but it has not yet produced a top opportunity strong enough to change the current `V1.2` bottleneck reading.
- Current `V1.2` reading stays the same: `carry_row_diversity_gap` remains the primary bottleneck, and the correct next move is to open the first bounded `v5` lane rather than widen old local substrate hunts.
