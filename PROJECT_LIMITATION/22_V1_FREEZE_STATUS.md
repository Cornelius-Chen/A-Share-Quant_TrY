# V1 Freeze Status

## Current Status

The project is now in a controlled freeze-preparation stage.

This means:

1. The repo already has an official shared default.
2. The repo already has a stronger broad shared-default challenger.
3. The older challenger line passed the first promotion gate, but the current strongest challenger still has not cleared the stricter validation-ready bar.
4. The challenger line is therefore still frozen below promotion.
5. The repo has completed a fresh regression replay after adding the gate logic.

## Official V1 Default

`shared_default`

Current official status:

- still frozen as the shared default
- still the public baseline for comparison
- not yet replaced

Representative configs:

- [baseline_research_strategy_suite.yaml](D:/Creativity/A-Share-Quant_TrY/config/baseline_research_strategy_suite.yaml)
- [theme_research_strategy_suite.yaml](D:/Creativity/A-Share-Quant_TrY/config/theme_research_strategy_suite.yaml)
- [theme_research_strategy_suite_v2.yaml](D:/Creativity/A-Share-Quant_TrY/config/theme_research_strategy_suite_v2.yaml)
- [market_research_strategy_suite_v0.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_strategy_suite_v0.yaml)

## Strongest Shared-Default Challenger

`balanced_targeted_timing_repair`

Current status:

- promotion frontrunner
- stronger than `shared_default` in the latest three-pack broad comparison
- stricter validation-ready gate still failed
- therefore: not yet promoted

Representative configs:

- [targeted_timing_repair_cross_pack_check_v2.yaml](D:/Creativity/A-Share-Quant_TrY/config/targeted_timing_repair_cross_pack_check_v2.yaml)
- [targeted_timing_repair_validation_gate_v2.yaml](D:/Creativity/A-Share-Quant_TrY/config/targeted_timing_repair_validation_gate_v2.yaml)

## Why Promotion Is Still Frozen

The blocking reason is explicit:

- the repo no longer has a large three-pack capture-regression problem
- but the newest broad challenger still falls short of the stricter promotion
  bar on two stability metrics:
  `composite_rank_improvement` and `mean_max_drawdown_improvement`

Evidence:

- first-stage gate report:
  [balanced_compromise_vs_shared_default_gate.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/balanced_compromise_vs_shared_default_gate.json)
- second-stage gate report:
  [balanced_compromise_validation_ready_gate.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/balanced_compromise_validation_ready_gate.json)
- stronger three-pack second-stage gate report:
  [balanced_compromise_validation_ready_gate_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/balanced_compromise_validation_ready_gate_v2.json)
- focused recovery comparison:
  [20260329T035657Z_9bf44b74_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T035657Z_9bf44b74_comparison.json)
- latest broad challenger comparison:
  [20260329T060122Z_99e67000_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060122Z_99e67000_comparison.json)
- latest strict gate report:
  [targeted_timing_repair_validation_gate_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/targeted_timing_repair_validation_gate_v2.json)
- latest three-pack time-slice validation:
  [20260329T060321Z_a2d656e8_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060321Z_a2d656e8_comparison.json)
- latest narrow refinement reports:
  [20260329T060715Z_e2f8dc2a_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060715Z_e2f8dc2a_comparison.json),
  [20260329T060753Z_bad3ddaa_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060753Z_bad3ddaa_comparison.json),
  [20260329T060852Z_0f4c9bd2_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060852Z_0f4c9bd2_comparison.json)
- latest micro-branch gate reports:
  [buffer_only_012_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_only_012_validation_gate_v1.json),
  [buffer_only_015_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_only_015_validation_gate_v1.json)

## Regression Replay Status

Latest freeze-oriented replay status:

1. Full test suite passed after the latest code-changing cycle: `54 passed`
2. Baseline shared-default suite replayed successfully:
   [20260329T035317Z_357001ee_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T035317Z_357001ee_comparison.json)
3. Theme shared-default suite replayed successfully:
   [20260329T035317Z_c74026d3_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T035317Z_c74026d3_comparison.json)
4. First-stage promotion gate replayed successfully
5. Second-stage validation gate replayed successfully and failed for a clear reason
6. Three-pack validation reran on `baseline_research_v1 + theme_research_v4 + market_research_v0`
7. The latest broad challenger still failed the stricter gate, but now for a narrower stability-improvement reason rather than a large capture-regression breach
8. The newest micro-refinement cycle shows that `switch_margin_buffer` is still the only lever with a meaningful signal; tiny holding / exit tweaks do not close the final gate gap
9. A final interpolation pass around that branch still failed on the same drawdown-improvement threshold, which means the repo has likely reached the limit of what threshold-only refinement can do on this challenger line
10. The new structural drawdown diagnostic localizes the remaining blocker to a theme-side pocket, especially `theme_research_v4 / 2024_q1`, rather than a broad cross-pack weakness
11. Symbol-level replay now has two concrete reference cases inside that pocket:
    `300750` is the first repeated damage case, while `002466` shows the same
    approval-path and permission split dates without converting them into a pnl
    gap. This reduces the risk that the repo is overfitting to a single symbol,
    but it also means the remaining blocker is conditional: the path shift only
    becomes promotion-relevant when it crosses a tradable state boundary
12. A third tradable replay, `002902`, now adds an assignment-divergence case:
    repeated leader-vs-junk and permission splits can exist without changing
    realized trades. The repo therefore has better evidence that the remaining
    blocker is conditional and state-transition dependent, not a universal
    damage pattern
13. The current best working rule for that pocket is now explicit:
    repeated theme-side path shifts matter only after they change emitted
    actions or active-position state. The repo therefore should not treat
    repeated shift dates alone as promotion evidence
14. That rule now has a ranking layer too: in the current three-symbol set,
    only `300750` crosses the repeated action-state trigger boundary, while
    `002466` and `002902` remain latent. Future theme-side replay work should
    prioritize symbols that already cross that boundary
15. Inside that triggered symbol, the blocker is now decomposed into four
    explicit trigger classes: early buy, forced sell, missed buy, and
    position-gap exit. Future repair work should target one trigger family at
    a time rather than treat the whole `300750` sequence as a single opaque
    failure
16. `feature-pack-c` is now explicitly closed as explanatory. The current
    specialist line should therefore stay parked unless a genuinely new suspect
    batch appears:
    [feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json)
17. `U1 lightweight geometry` successfully improved interpretation quality,
    but it also justified *not* opening clustering:
    [u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json),
    [u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json)
18. `market_research_v1` is now fully runnable and should be treated as the
    next broad substrate for future suspect generation, not as a new default
    validation pack:
    [market_research_data_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v1.json),
    [20260329T111733Z_3e700662_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T111733Z_3e700662_comparison.json)
19. A fresh three-pack validation with `market_research_v1` now confirms two
    things at once:
    - the broad freeze is still intact
    - the next specialist suspect geography should begin on `market_research_v1`
    Evidence:
    [20260329T112015Z_d5db1be9_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T112015Z_d5db1be9_comparison.json),
    [specialist_alpha_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v2.json)
20. The current `V1.1` phase boundary is now explicitly frozen in
    [32_V11_STAGE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/32_V11_STAGE_REVIEW.md).
    Further specialist continuation should be judged against that review rather
    than inferred from the latest few replay reports.
16. Those four trigger classes are no longer equal in priority. The current
    economic ranking says the incumbent-side `missed_buy -> position-gap exit`
    chain dominates the damage, while the challenger-side `early_buy -> forced
    sell` chain is secondary. Future repair work should start with the
    incumbent-side chain first
17. That dominant branch is now confirmed as a complete repeated chain rather
    than just a ranked trigger family:
    [theme_missed_reentry_chain_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_missed_reentry_chain_300750_v1.json)
    shows that on `2024-02-05` the challenger loses permission and emits no
    buy, and on `2024-02-06` the incumbent still holds the resulting position
    and exits it while the challenger has no position to exit. The remaining
    blocker is therefore best described as an incumbent-side missed re-entry
    chain, not as a broad global stability failure
18. The first date in that chain is also now pinned to a narrow regime edge:
    [theme_permission_loss_edge_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_permission_loss_edge_300750_v1.json)
    shows that on `2024-02-05` the top sector is still clearly dominant, but
    its score (`2.583525`) sits just below the challenger's `2.6` threshold
    while staying above the incumbent's `2.5` threshold. The blocker is
    therefore a very small threshold-edge permission loss, not a broad ranking
    ambiguity or a large regime-path failure
19. That narrow threshold edge has now been tested directly and does not close
    the freeze gap:
    [20260329T070422Z_3a231b85_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T070422Z_3a231b85_comparison.json)
    and
    [buffer_top258_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_top258_validation_gate_v1.json)
    show that relaxing only `min_top_score` from `2.60` to `2.58` slightly
    helps the local theme row but still fails the stricter gate on
    `mean_max_drawdown_improvement`, and it does not beat `buffer_only_012`
    on composite stability. The repo therefore should treat this threshold-edge
    repair as tested but insufficient
20. The repo now has an explicit acceptance posture for the remaining blocker:
    [residual_cost_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/residual_cost_acceptance_v1.json)
    summarizes the current stance as `freeze_and_accept_residual_cost`
    because the remaining strict-gate gap is small, localized to
    `theme_research_v4 / 2024_q1`, and not cheaply repairable through the
    obvious threshold-edge tweak. Further threshold grinding is therefore not
    the recommended next use of research effort
21. The next recommended use of research effort is now explicit too:
    [specialist_alpha_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v1.json)
    shows where specialist branches beat both broad anchors. The freeze status
    therefore no longer points back to the same blocker; it points forward to
    new V1.1 alpha pockets such as `theme_research_v4 / 2024_q1` for capture
    work and `baseline_research_v1 / 2024_q3` for drawdown work
22. The first capture-oriented specialist pocket has now been reduced from a
    slice-level ranking to a replayable window list:
    [specialist_pocket_window_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_pocket_window_analysis_v1.json)
    shows that `baseline_expansion_branch` beats both broad anchors inside
    `theme_research_v4 / 2024_q1 / mainline_trend_c` through only `4`
    improved windows, with `2` full both-anchor misses. The highest-priority
    next replay targets are therefore `002466_2` and `000155_5`, not another
    broad capture sweep
23. The first replay target now has a concrete upstream explanation too:
    [theme_q1_specialist_window_opening_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_002466_v1.json)
    shows that `002466_2` opens on `2024-01-10` not because the specialist has
    looser regime permission, but because it upgrades the symbol from `junk`
    to `late_mover` while both broad anchors keep permission, filters, and
    entry triggers aligned. The next capture-specialist question is therefore
    a hierarchy-admission question first, not a regime-threshold question
24. The second full both-anchor miss inside the same pocket now has a different
    mechanism:
    [theme_q1_specialist_window_persistence_000155_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_persistence_000155_v1.json)
    shows that `000155_5` is not opened earlier than the anchors. Instead, all
    three candidates enter, but on `2024-02-22` only the specialist keeps the
    position alive while both broad anchors emit `sell`. The first capture
    pocket therefore already splits into at least two families:
    hierarchy-admission opening edges and persistence edges
25. The first partial-capture lift inside the same pocket now stays inside that
    same taxonomy:
    [theme_q1_specialist_window_opening_600338_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_600338_v1.json)
    shows that `600338_5` is a staggered opening edge, not a third hybrid
    family. The specialist opens the window on `2024-02-21` through the same
    `late_mover` admission upgrade, while both anchors remain in `junk` and
    only enter later. The first capture pocket is therefore still explained by
    two families, not three
26. The last unresolved partial-capture case also stays inside that same map:
    [theme_q1_specialist_window_opening_300518_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_300518_v1.json)
    shows that `300518_7` is another light opening edge. The first
    capture-specialist pocket can therefore be treated as structurally closed
    under a two-family taxonomy:
    opening edges and persistence edges
27. The first drawdown-specialist pocket is now compact enough to reuse too:
    [baseline_q3_cycle_mechanism_600519_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_600519_v1.json)
    shows that the `600519` improvement inside
    `baseline_research_v1 / 2024_q3 / mainline_trend_b`
    is not one generic quality effect. It is a three-part cycle map:
    `entry_suppression_avoidance`, `earlier_exit_loss_reduction`,
    and `later_exit_loss_extension`. The next drawdown-specialist cycle should
    therefore compare later pockets against that mechanism map instead of
    reopening a broad branch search.
28. That same baseline-Q3 drawdown pocket is now confirmed to be strategy-stable across `B/C`:
    [baseline_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cross_strategy_cycle_consistency_v1.json)
    shows that `mainline_trend_b` and `mainline_trend_c` share an identical
    negative-cycle map on `600519`, including the same three signatures:
    `2024-07-03` (`later_exit_loss_extension`),
    `2024-08-01` (`entry_suppression_avoidance`),
    and `2024-08-09` (`earlier_exit_loss_reduction`).
    This pocket should therefore be treated as one reusable baseline-Q3
    structural template, not as two separate strategy-specific drawdown stories.
29. The next drawdown-specialist pocket does **not** simply reuse that same template:
    [market_q4_cycle_mechanism_600519_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_600519_c_v1.json)
    shows that `market_research_v0 / 2024_q4 / mainline_trend_c`
    still centers on `600519`, but the key negative-cycle repair is now
    `preemptive_loss_avoidance_shift` rather than one of the baseline-Q3
    signatures. This means the drawdown-specialist line now contains at least
    two families: the cleaner baseline-Q3 template and a more ambiguous
    market-Q4 family with larger opportunity-cost tradeoffs.
30. A third drawdown-specialist family is now confirmed on
    `theme_research_v4 / 2024_q4 / mainline_trend_c`:
    [theme_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_c_v1.json)
    shows that `300750` improves the pocket through a mix of
    `earlier_exit_loss_reduction` and `carry_in_basis_advantage`.
    This is not the same as market-Q4's `preemptive_loss_avoidance_shift`,
    because the challenger stays in the trade and exits on the same day as the
    incumbent, but from a much better cost basis after entering earlier on
    `2024-11-05`.
31. The baseline-style drawdown family is no longer unique to the original
    `600519` baseline pocket:
    [theme_q3_cycle_mechanism_002460_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q3_cycle_mechanism_002460_c_v1.json)
    shows that `theme_research_v4 / 2024_q3 / mainline_trend_c`
    mostly improves through repeated `entry_suppression_avoidance` on
    `002460`. The pocket is noisier than baseline-Q3 because it still carries
    two worse nearby cycles, but it is the first clear cross-pocket reuse of
    the baseline-style avoidance family.
32. A fourth drawdown-specialist family is now confirmed on
    `theme_research_v4 / 2024_q2 / mainline_trend_c`:
    [theme_q2_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_300750_c_v1.json)
    shows that `300750` improves the pocket through
    `delayed_entry_basis_advantage` on `2024-05-20 -> 2024-05-22`.
    This is the mirror image of `carry_in_basis_advantage`: the challenger
    enters later, exits on the same day, and loses less because it carries a
    lower basis.
33. The drawdown-specialist line now has a first-pass family inventory:
    [cycle_family_inventory_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v1.json)
    currently ranks
    - `entry_suppression_avoidance` as the strongest reusable family
    - `carry_in_basis_advantage` as the cleanest non-baseline basis family
    - `preemptive_loss_avoidance_shift` as strong but burdened by large opportunity cost
    - `entry_suppression_opportunity_cost` as the main toxic family to avoid
    This means the next V1.1 drawdown-specialist loop can be chosen from a
    family asset table instead of from whichever pocket was replayed most recently.
34. `carry_in_basis_advantage` has now crossed the minimum line from
    "clean one-off family" to "cross-strategy reusable family":
    [theme_q4_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cross_strategy_cycle_consistency_v1.json)
    shows that `theme_research_v4 / 2024_q4 / 300750` has an identical
    negative-cycle map on both `mainline_trend_b` and `mainline_trend_c`,
    with the same
    - `earlier_exit_loss_reduction` on `2024-10-28 -> 2024-10-30`
    - `carry_in_basis_advantage` on `2024-11-06 -> 2024-11-07`
    and [cycle_family_inventory_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v2.json)
    now lifts the family to `report_count = 2` and
    `net_family_edge = 1682.5046` with zero positive opportunity-cost drag.
    This still does not affect the official frozen default, but it does make
    `carry_in_basis_advantage` the leading non-baseline family for the next
    specialist expansion loop.
35. The next specialist loop is now selected by a replay shortlist rather
    than by ad hoc symbol choice:
    [drawdown_family_candidate_shortlist_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v2.json)
    excludes the already replayed family anchors and currently points to
    `theme_research_v4 / 2024_q3 / mainline_trend_c / 603799` as the top
    remaining drawdown-family candidate. This matters because `300759` and
    `002466` on `theme_q4` were both checked and neither produced a second
    clean `carry_in_basis_advantage` pocket.
36. `theme_q3 / 603799` has now been checked and deliberately rejected as a
    family-inventory addition:
    [theme_q3_cycle_mechanism_603799_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q3_cycle_mechanism_603799_c_v1.json)
    is a mixed pocket with one clean `entry_suppression_avoidance` row and
    one toxic positive-cycle truncation. After excluding it, the replay queue
    advances to
    [drawdown_family_candidate_shortlist_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v3.json),
    whose current top candidate is `market_research_v0 / 2024_q4 / mainline_trend_c / 300750`.
37. `market_q4 / 300750` has now also been replayed and classified as a
    clean but already-understood baseline-style avoidance case:
    [market_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_300750_c_v1.json)
    contains a single `entry_suppression_avoidance` row and no basis-family
    behavior. After excluding it, the replay queue rotates again to
    [drawdown_family_candidate_shortlist_v4.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v4.json),
    whose current top candidate is `baseline_research_v1 / 2024_q3 / mainline_trend_c / 000333`.
38. `baseline_q3 / 000333 / mainline_trend_c` has now also been replayed and
    classified as a strong but still non-frontier baseline-style reuse case:
    [baseline_q3_cycle_mechanism_000333_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_000333_c_v1.json)
    is dominated by
    - `earlier_exit_loss_reduction` on `2024-08-01 -> 2024-08-05`,
      `2024-08-26 -> 2024-08-29`, and `2024-09-04 -> 2024-09-06`
    - `entry_suppression_avoidance` on `2024-07-05 -> 2024-07-08` and
      `2024-07-15 -> 2024-07-16`
    but it also carries two large positive-cycle degradations
    (`2024-08-19 -> 2024-08-20` and `2024-09-25 -> 2024-10-09`)
    labeled `other_worse_loss_shift`.
    This strengthens the baseline-style family, but it does not extend the
    non-baseline specialist frontier. The replay queue has therefore been
    rotated again to
    [drawdown_family_candidate_shortlist_v5.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v5.json).
39. `market_q4 / 002371 / mainline_trend_c` has now also been replayed and
    classified as a clean single-row baseline-style avoidance case:
    [market_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_002371_c_v1.json)
    contains exactly one `entry_suppression_avoidance` row on
    `2024-12-30 -> 2024-12-31`, with no reduced-loss basis behavior and no
    mixed-cycle baggage. It therefore raises confidence in the baseline-style
    family but does not change the non-baseline specialist frontier. The
    replay queue has been rotated again to
    [drawdown_family_candidate_shortlist_v6.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v6.json).
40. `theme_q2 / 002466 / mainline_trend_c` has now also been replayed and
    classified as a stacked-family pocket rather than a new family asset:
    [theme_q2_cycle_mechanism_002466_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_002466_c_v1.json)
    combines
    - `preemptive_loss_avoidance_shift`
    - two `entry_suppression_avoidance` rows
    - one positive `delayed_entry_basis_advantage`
    This is useful reinforcement evidence for known mechanisms, but it does
    not extend the non-baseline family frontier. The replay queue has been
    rotated again to
    [drawdown_family_candidate_shortlist_v8.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v8.json).
41. `theme_q4 / 002902` has now also been replayed on both
    `mainline_trend_b` and `mainline_trend_c`, and the result is a
    cross-strategy mixed pocket rather than a new family asset:
    [theme_q4_cycle_mechanism_002902_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002902_b_v1.json)
    and
    [theme_q4_cycle_mechanism_002902_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002902_c_v1.json)
    have identical negative-cycle maps containing one
    `earlier_exit_loss_reduction`, two `entry_suppression_avoidance`, and one
    negative `other_worse_loss_shift`. This is useful evidence that mixed
    pockets themselves can repeat across strategies, but it still does not
    extend the non-baseline family frontier. The replay queue has therefore
    been rotated again to
    [drawdown_family_candidate_shortlist_v9.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v9.json).
42. `market_q4 / 603259 / mainline_trend_c` has now also been replayed and
    classified as another clean single-row baseline-style avoidance case:
    [market_q4_cycle_mechanism_603259_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_603259_c_v1.json)
    contains exactly one `entry_suppression_avoidance` row on
    `2024-10-30 -> 2024-10-31`, with no reduced-loss basis behavior and no
    mixed-cycle baggage. It therefore strengthens the baseline-style family
    without extending the non-baseline frontier. The replay queue has been
    rotated again to
    [drawdown_family_candidate_shortlist_v10.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v10.json).
43. `theme_q4 / 603087` has now also been replayed on both `mainline_trend_b`
    and `mainline_trend_c`, and both reports collapse into the same
    single-row baseline-style case:
    [theme_q4_cycle_mechanism_603087_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_b_v1.json)
    and
    [theme_q4_cycle_mechanism_603087_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_c_v1.json)
    each contain exactly one `entry_suppression_avoidance` row, with no
    reduced-loss basis behavior and no mixed baggage. This confirms that
    cross-strategy repetition alone is not enough for family promotion. The
    replay queue has therefore been rotated again to
    [drawdown_family_candidate_shortlist_v11.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v11.json).
44. The specialist replay queue has now reached a formal `feature-limited
    thinning phase` and should no longer be treated as the default next step.
    [specialist_feature_gap_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_feature_gap_audit_v1.json)
    shows:
    - `mixed_existing_families = 4`
    - `single_row_baseline_reuse = 4`
    - `stacked_family_pocket = 1`
    - `feature_gap_suspect_count = 2`
    - `thinning_signal = true`
    This means the current V1.1 blocker is no longer "find the next replay
    candidate". It is "test whether a small feature pack changes the family
    boundary." The phase guardrails are now written down in
    [26_V11_SPECIALIST_ALPHA_GUARDRAILS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/26_V11_SPECIALIST_ALPHA_GUARDRAILS.md),
    and the default next step becomes `feature-pack-a` rather than
    `drawdown_family_candidate_shortlist_v12`.
45. `feature-pack-a` is now formally bounded, so the phase transition is
    executable rather than aspirational. See
    [27_FEATURE_PACK_A_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/27_FEATURE_PACK_A_PLAN.md).
    The immediate recheck targets are:
    - `theme_research_v4 / 2024_q4 / 002902`
    - `theme_research_v4 / 2024_q2 / 002466`
    and the scope is intentionally narrow:
    - theme/concept support features
    - hierarchy intermediate margins
    - approval-edge state
    - short cycle context
    The replay queue stays paused until this pack either changes the family
    boundary or fails cleanly.
46. `feature-pack-a` v1 has now completed its first recheck pass and succeeded
    as a diagnostic stage. [feature_pack_a_recheck_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_recheck_v1.json)
    shows `8/8` suspect mechanism rows landing on at least one explicit
    threshold edge. The current split is:
    - `theme_q4 / 002902`: hierarchy / approval-edge pocket with zero concept support
    - `theme_q2 / 002466`: concept-supported hierarchy pocket with repeated
      late-quality and non-junk-composite straddles
    So the replay queue remains paused. The next refinement step should target
    these two edge types directly instead of resuming queue expansion.
47. The post-`feature-pack-a` next step is now formally split and ordered:
    [feature_pack_a_triage_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_triage_v1.json)
    classifies:
    - `theme_q4 / 002902 / B` as `hierarchy_approval_edge`
    - `theme_q2 / 002466 / C` as `concept_supported_hierarchy_edge`
    and
    [feature_pack_b_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_readiness_v1.json)
    fixes the execution order:
    1. `theme_q4 / 002902 / B`
    2. `theme_q2 / 002466 / C`
    This order is now formalized in
    [28_FEATURE_PACK_B_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/28_FEATURE_PACK_B_PLAN.md).
    The replay queue stays paused while track A is tested first.
48. Track A has now been instrumented enough to stop treating `002902` as a
    generic mixed pocket. [feature_pack_b_hierarchy_approval_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_v1.json)
    shows:
    - `dominant_hierarchy_edge = late_mover_quality`
    - `dominant_approval_edge = score_margin_threshold`
    - `late_quality_straddles = 3`
    - `margin_straddles = 2`
    - `permission_split_rows = 2`
    So `theme_q4 / 002902 / B` should now be treated as a coupled
    hierarchy-plus-approval edge, not as a generic replay candidate and not as
    a concept-driven pocket. The replay queue remains paused while this lane is
    evaluated.
49. Track A has now also completed its first real local sweep cycle, and the
    result is negative-but-informative. The two sweep reports
    [feature_pack_b_hierarchy_approval_sweep_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v1.json)
    and
    [feature_pack_b_hierarchy_approval_sweep_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v2.json)
    show:
    - assignment-side repairs are possible via non-junk relief
    - approval-side repairs are possible via more aggressive margin relief
    - but more repaired trigger dates do **not** translate into better
      symbol-level PnL for `002902`
    Therefore `theme_q4 / 002902 / B` should be treated as an explanatory
    edge, not as a cheap local repair to promote. The next feature budget
    should move to the `002466` concept-supported hierarchy lane.
50. Track B has now been instrumented enough to avoid a second blended feature
    loop. [feature_pack_b_concept_supported_hierarchy_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_supported_hierarchy_v1.json)
    shows that `theme_q2 / 002466 / C` should currently be treated as a
    `concept_to_late_mover` bridge candidate:
    - `concept_supported_late_rows = 2`
    - `concept_supported_non_junk_rows = 2`
    - but the tighter negative margin sits on `late_mover_quality`
    So the next concept-aware refinement should target late-mover admission
    first, not a general concept-to-hierarchy rewrite.
51. `feature-pack-b` can now be treated as closed under the current feature
    set. [feature_pack_b_concept_late_validation_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_late_validation_v1.json)
    shows that the `002466` concept-to-late lane repaired only one of the two
    target rows while collapsing most of the specialist alpha:
    - baseline `v1` pnl delta: `536.724`
    - best tested variant pnl delta: `94.049`
    - best alpha-retention ratio: `0.175228`
    - best repair completion ratio: `0.5`
    So track B should now be treated the same way as track A:
    explanatory success, refinement failure, and no reason to reopen broad
    tuning without a new feature pack.
52. The next phase is now formally `feature-pack-c`, not replay-queue
    expansion. [feature_pack_c_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_readiness_v1.json)
    shows:
    - `track_a_closed = true`
    - `track_b_closed = true`
    - `recommended_next_phase = feature_pack_c_local_causal_edges`
    - `do_restart_replay_queue = false`
    Therefore the correct next move is to add local causal features around
    fallback, late-quality deficits, approval-threshold history, and
    concept-support excess, as defined in
    [29_FEATURE_PACK_C_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/29_FEATURE_PACK_C_PLAN.md).
53. Unsupervised work is now allowed only as a bounded sidecar. See
    [30_UNSUPERVISED_FEATURE_RELATION_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/30_UNSUPERVISED_FEATURE_RELATION_PLAN.md).
    Current rule:
    - keep `feature-pack-c` as the mainline
    - if unsupervised work starts, begin only with lightweight geometry
    - do not let unsupervised outputs enter the trading signal chain directly
54. `feature-pack-c` has now started with a concrete ordering rule rather than
    a generic feature list. [feature_pack_c_fallback_reason_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_fallback_reason_analysis_v1.json)
    shows:
    - `dominant_component_counts = {late_quality: 6, score_margin: 2}`
    - `recommended_first_feature_group = fallback_reason_decomposition_plus_late_quality_residuals`
    So the first pack-C implementation should be late-quality-led local causal
    features, with approval-threshold history and concept-support excess kept
    as secondary follow-up features.
55. The first real `late_quality` residual read is now also in place.
    [feature_pack_c_late_quality_residuals_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_late_quality_residuals_v1.json)
    shows:
    - `dominant_residual_component_counts = {stability: 3, liquidity: 3, sector_strength: 2}`
    - `concept_boost_active_count = 1`
    - `raw_below_threshold_count = 8`
    - `recommended_second_feature_group = late_quality_stability_liquidity_context`
    So pack-C should continue inside the raw late-quality stack rather than
    reopening concept bridges or approval-threshold tuning. The next useful
    explanatory layer is component-context around `stability/liquidity`, with
    `sector_strength` as a secondary contributor.
56. The next pack-C narrowing step is now also fixed.
    [feature_pack_c_stability_liquidity_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_stability_liquidity_context_v1.json)
    shows:
    - `row_count = 6`
    - `local_context_counts = {turnover_share_led: 3, mixed_stability_liquidity: 3}`
    - `volatility_led = 0`
    - `recommended_third_feature_group = late_quality_turnover_share_context`
    So pack-C should not open a volatility-first branch. The next local-causal
    read should focus on turnover-share context, while treating the stability
    side as a mixed residual bucket.
57. The first turnover-share context read is now also complete.
    [feature_pack_c_turnover_share_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_turnover_share_context_v1.json)
    shows:
    - `row_count = 3`
    - `local_turnover_context_counts = {sector_peer_dominance: 1, balanced_share_weakness: 2}`
    - `broad_attention_deficit = 0`
    - `recommended_fourth_feature_group = late_quality_balanced_turnover_context`
    So pack-C should not open a broad-attention branch. The current
    turnover-share evidence splits into one sector-peer dominance row and two
    balanced-share weakness rows, which keeps this lane descriptive rather than
    cheaply repairable.
58. The turnover-share lane has now been explicitly decomposed one step deeper
    and that branch is effectively closed:
    [feature_pack_c_balanced_turnover_weakness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_balanced_turnover_weakness_v1.json)
    shows:
    - `balanced_weakness_counts = {singleton_sector_masking: 2, true_balanced_share_weakness: 0}`
    So the `002902` rows are not evidence for a reusable balanced-turnover
    weakness feature. They are sector-masked rows where sector-relative share
    metrics are structurally uninformative. This removes the last plausible
    reason to keep widening the turnover-share lane.
59. `feature-pack-c` now has a formal acceptance posture too:
    [feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json)
    concludes:
    - `acceptance_posture = close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar`
    - `do_continue_pack_c_turnover_branch = false`
    - `do_restart_replay_queue = false`
    - `ready_for_u1_lightweight_geometry = true`
    This means the next healthy move is no longer another local-causal branch
    inside pack-C. The repo should treat pack-C as an explanatory closure and,
    if specialist refinement continues, open only the bounded `U1 lightweight
    geometry` sidecar described in
    [30_UNSUPERVISED_FEATURE_RELATION_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/30_UNSUPERVISED_FEATURE_RELATION_PLAN.md).
60. The first `U1 lightweight geometry` sidecar has now also completed and it
    justified itself:
    [u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json)
    shows:
    - `case_centroid_distance = 4.080383`
    - `separation_reading = cases_geometrically_separable`
    - `pc1` is dominated by concept-support geometry
    - `pc2` is dominated by late-quality / resonance geometry
    So the two current suspect pockets should no longer be treated as one
    blended next-stage branch. The sidecar changed interpretation quality
    without entering the signal chain, which is exactly the intended U1 role.
61. The next sidecar stage is now explicitly *not* ready:
    [u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json)
    shows:
    - `suspect_count = 2`
    - `u1_cases_geometrically_separable = true`
    - `u2_ready = false`
    - `recommended_next_phase = hold_u2_and_wait_for_larger_or_less_separable_suspect_set`
    So the repo should not open clustering just because U1 succeeded. The
    bounded sidecar remains healthy precisely because it now knows when to
    stop.
62. `market_research_v1 / 2024_q3` now has an explicit slice-level stop gate.
    [market_v1_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_drawdown_slice_acceptance_v1.json)
    concludes:
    - `close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse`
    - `shared_top_driver = 300308`
    - `identical_negative_cycle_map = true`
    - `do_continue_q3_drawdown_replay = false`
    So under the current evidence, future specialist continuation should not
    spend more replay budget on `market_research_v1 / 2024_q3` unless a later
    suspect explicitly breaks this cross-strategy-stable reading.
63. The first `market_research_v1 / 2024_q4` drawdown replay is now also
    classified.
    [market_v1_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_002371_c_v1.json)
    shows the current top q4/C symbol `002371` is only a clean
    `entry_suppression_avoidance` case.
    So q4 stays open, but its first replay lowers the chance that q4 is about
    to produce a broad new drawdown-family frontier.
64. `market_research_v1 / 2024_q4` now also has an explicit slice-level stop
    gate.
    [market_v1_q4_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_drawdown_slice_acceptance_v1.json)
    concludes:
    - `close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix`
    - `top_positive_symbols = [002371, 000977, 000858]`
    - `do_continue_q4_drawdown_replay = false`
    So under the current evidence, q4 should also be treated as a closed slice
    rather than an open replay lane.

## What This Means

V1 is not blocked by missing architecture anymore.

V1 is now blocked by a deliberate research decision:

- either keep `shared_default` frozen
- or improve the challenger until it survives stricter validation-ready criteria

## One-Line Rule

The repo is now in `freeze-but-do-not-promote-yet` status.

## Next Refinement Rule

When specialist refinement resumes, the next line should be:

1. add sector/theme state as conditional context
2. start with `theme_load_plus_turnover_concentration_context`
3. follow with `sector_state_heat_breadth_context` only if needed
4. do **not** start per-sector training from the current evidence alone
5. the first validated narrow branch is now:
   `conditioned_late_quality_on_theme_turnover_context`
