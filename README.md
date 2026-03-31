# A-Share-Quant_TrY

Engineering-grade A-share research repo focused on offline backtesting and
mainline trend strategy comparison.

## Current scope

The repository currently contains:

- binding governance documents under `PROJECT_LIMITATION/`
- a first-pass Python package skeleton under `src/a_share_quant/`
- a minimal daily-bar backtest backbone
- early `regime` modules for sample segmentation, sector scoring, and attack permission
- early `trend` modules for hierarchy ranking, trend-filter candidates, and entry-rule candidates
- first-pass holding/exit modules and comparable Strategy A/B/C wrappers
- custom metric implementations for `mainline_capture_ratio` and `missed_mainline_count`
- experiment run registration and JSON reporting
- suite comparison reports with ranking, segment overview, trade overview, and window breakdowns
- configurable segmentation methods across `index_trend`, `sector_trend`, and `resonance`
- matrix comparison across strategy families and segmentation methods
- active schema-first research assets for:
  - `earnings_transmission_carry`
  - `theme_diffusion_carry`
- bounded CPO cycle-reconstruction, cohort-map, labeling-surface, dynamic-role, and feature-family design layers
- bounded review-only candidate-driver preservation for mainline-strength research
- bounded mainline-driver prioritization for `theme_diffusion_carry`
- schema-review-only usage boundaries for the high-priority `theme_diffusion_carry` driver quartet
- bounded archetype-level validation for `theme_diffusion_carry`
- first lawful bounded labeling/training pilot entry for `theme_diffusion_carry`
- sample CSV data and a demo config
- tests for the phase-1 foundation

## Quick start

Create an environment and install the package in editable mode:

```bash
python -m pip install -e .[dev]
```

Run the demo backtest:

```bash
python scripts/run_backtest.py --config config/demo_backtest.yaml
```

Run the demo strategy experiment:

```bash
python scripts/run_strategy_experiment.py --config config/demo_strategy_experiment.yaml
```

Run the comparable A/B/C strategy suite:

```bash
python scripts/run_strategy_suite.py --config config/demo_strategy_suite.yaml
```

Run a segmentation-method comparison for one strategy family:

```bash
python scripts/run_segmentation_comparison.py --config config/demo_segmentation_comparison.yaml
```

Run a full strategy-by-segmentation matrix comparison:

```bash
python scripts/run_strategy_matrix.py --config config/demo_strategy_matrix.yaml
```

Run tests:

```bash
pytest
```

## Free data bootstrap

Install the optional free-data dependencies:

```bash
python -m pip install -e .[free-data]
```

Bootstrap a first-pass free dataset pack with AKShare:

```bash
python scripts/bootstrap_free_data.py --config config/free_data_bootstrap.yaml
```

Use universe files to bootstrap larger research watchlists without bloating the
YAML configs:

```bash
python scripts/bootstrap_free_data.py --config config/baseline_research_free_data_bootstrap.yaml
python scripts/bootstrap_free_data.py --config config/theme_research_free_data_bootstrap.yaml
```

Bootstrap a more realistic daily sector-mapping table from CNInfo industry
change history via AKShare:

```bash
python scripts/bootstrap_sector_mapping.py --config config/bootstrap_sector_mapping.yaml
```

Bootstrap a first-pass concept/theme mapping table from Eastmoney concept boards
via AKShare:

```bash
python scripts/bootstrap_concept_mapping.py --config config/bootstrap_concept_mapping.yaml
```

Run the same concept bootstrap on the larger theme-research watchlist:

```bash
python scripts/bootstrap_concept_mapping.py --config config/theme_research_concept_mapping.yaml
```

Complete the larger research-pack pipeline:

```bash
python scripts/bootstrap_sector_mapping.py --config config/baseline_research_sector_mapping.yaml
python scripts/generate_bootstrap_derived_data.py --config config/baseline_research_derived_data.yaml
python scripts/run_strategy_suite.py --config config/baseline_research_strategy_suite.yaml
python scripts/audit_data_pack.py --config config/baseline_research_data_audit.yaml

python scripts/bootstrap_sector_mapping.py --config config/theme_research_sector_mapping.yaml
python scripts/generate_bootstrap_derived_data.py --config config/theme_research_derived_data.yaml
python scripts/run_strategy_suite.py --config config/theme_research_strategy_suite.yaml
python scripts/audit_data_pack.py --config config/theme_research_data_audit.yaml
```

Use the sequential refresh helper when you want to avoid stale intermediate
outputs inside a dependent research-pack chain:

```bash
python scripts/refresh_research_pack.py --pack baseline_research_v1
python scripts/refresh_research_pack.py --pack theme_research_v1
```

Run the current branch-local baseline suites directly:

```bash
python scripts/run_strategy_suite.py --config config/baseline_research_strategy_suite_expansion.yaml
python scripts/run_strategy_suite.py --config config/theme_research_strategy_suite_strict_quality.yaml
```

Run the same bootstrap flow on a more concept-driven validation universe:

```bash
python scripts/bootstrap_concept_mapping.py --config config/theme_bootstrap_concept_mapping.yaml
python scripts/generate_bootstrap_derived_data.py --config config/theme_bootstrap_derived_data.yaml
python scripts/run_strategy_suite.py --config config/theme_bootstrap_strategy_suite.yaml
python scripts/audit_data_pack.py --config config/theme_bootstrap_data_audit.yaml
```

Compare the original baseline bootstrap pack and the theme-validation pack under
the same strategy family:

```bash
python scripts/run_dataset_comparison.py --config config/dataset_comparison.yaml
```

Compare the larger research packs under the same strategy family:

```bash
python scripts/run_dataset_comparison.py --config config/research_dataset_comparison.yaml
```

Screen named rule candidates across both dataset packs:

```bash
python scripts/run_rule_sweep.py --config config/rule_sweep.yaml
```

Run the same rule sweep on the larger research packs:

```bash
python scripts/run_rule_sweep.py --config config/research_rule_sweep.yaml
python scripts/run_rule_sweep.py --config config/research_rule_sweep_v2.yaml
python scripts/run_rule_sweep.py --config config/baseline_expansion_sweep.yaml
python scripts/run_rule_sweep.py --config config/theme_quality_sweep.yaml
```

After bootstrap completes, you can run a minimal backtest on the exported local
daily bars:

```bash
python scripts/run_backtest.py --config config/bootstrap_backtest.yaml
```

Generate first-pass derived research tables from the bootstrapped local bars:

```bash
python scripts/generate_bootstrap_derived_data.py --config config/bootstrap_derived_data.yaml
```

Run a strategy experiment against the bootstrapped local bars plus the generated
derived tables:

```bash
python scripts/run_strategy_experiment.py --config config/bootstrap_strategy_experiment.yaml
```

Run a comparable A/B/C strategy suite against the same bootstrapped local bars
and generated derived tables:

```bash
python scripts/run_strategy_suite.py --config config/bootstrap_strategy_suite.yaml
```

Audit the current bootstrap data pack and see which canonical tables are still
missing or partial:

```bash
python scripts/audit_data_pack.py --config config/bootstrap_data_audit.yaml
```

Notes:

- the free bootstrap currently targets `daily_bars`, `index_daily_bars`,
  `trading_calendar`, and a fallback-capable `security_master_lite`
- the current real-data path is enough for basic backtest plumbing, but the
  strategy experiment flow now supports a first-pass bootstrap-derived path, but
  those derived tables are still heuristic placeholders rather than final
  protocol-grade research truth
- the bootstrap sector mapping can now come from CNInfo industry-change history,
  which is materially better than the original hand-written symbol-to-sector
  placeholders
- concept/theme mapping now has a dedicated bootstrap path too, but the current
  eight-stock bootstrap universe is still industry-heavy enough that concept
  coverage may remain sparse or empty until the universe expands toward more
  theme-driven names
- a separate theme-validation universe is now provided to exercise the concept
  layer on more topic-driven stocks; on that pack the concept table is non-empty
  and the audit can reach `baseline_ready=true`
- larger research watchlists are now externalized into `config/universes/*.txt`,
  so sample coverage can expand without turning the bootstrap YAML files into
  brittle copy-paste lists
- the larger `theme_research_v1` watchlist already pushes concept coverage above
  the original theme bootstrap pack: `3136` concept rows across `12` symbols and
  `4` concepts (`锂矿概念`, `创新药`, `CRO`, `减肥药`)
- the cross-dataset comparison now makes the tradeoff explicit: the baseline
  pack currently favors `mainline_trend_a` on return/drawdown, while the theme
  pack favors `mainline_trend_c` on capture
- the rule-sweep layer now makes cross-pack rule screening explicit too: the
  current `control_v1` candidate is the most stable across the two packs, while
  `expansion_capture` can win on single-run upside but gives up some stability
- on the larger research packs, both baseline and theme data packs now audit as
  `baseline_ready=true`; the larger `baseline_research_v1` pack currently favors
  `mainline_trend_a` on return while `mainline_trend_b` improves capture
- after a clean sequential rebuild, the larger `theme_research_v1` pack also
  restores A/B/C separation: `mainline_trend_b` leads on return, `mainline_trend_c`
  leads on capture, and `mainline_trend_a` keeps the lowest drawdown
- importantly, the larger research-pack rule sweep flips the stability ranking:
  if the theme pack is read off a stale parallel refresh, but after a clean
  sequential rebuild `control_v1` regains the narrow stability lead over
  `strict_quality` and `expansion_capture`
- the expanded `research_rule_sweep_v2` adds entry/holding-style candidates and
  shows a more useful split: `baseline_research_v1` currently prefers
  `expansion_capture`, while `theme_research_v1` prefers `strict_quality` on
  return/drawdown and `control_v1` on capture
- the narrower single-pack sweeps sharpen that picture further: on
  `baseline_research_v1`, `expansion_capture` and `broad_late_mover` are the
  leading expansion-style candidates; on `theme_research_v1`, `strict_quality`
  is the clear quality/holding leader, with `selective_entry` as the closest
  follow-up candidate
- those local winners are now codified as executable branch baselines too:
  `baseline_research_strategy_suite_expansion.yaml` and
  `theme_research_strategy_suite_strict_quality.yaml`
- the next branch-internal refinement sweeps keep those baselines intact rather
  than overturning them: on the baseline branch,
  `expansion_branch_control` remains the most stable candidate while
  `expansion_regime_guard` only improves the best single return row; on the
  theme branch, `strict_quality_branch_control` remains the most stable
  candidate while `strict_quality_capture_relief` only improves the best
  capture row
- those branch-internal checks now live in
  `baseline_expansion_refinement_sweep.yaml` and
  `theme_strict_quality_refinement_sweep.yaml`, which are intended to refine the
  current local winners before any default-promotion discussion
- a separate cross-pack promotion screen now exists too:
  `branch_promotion_check.yaml` compares `shared_default`, the baseline
  expansion branch, and the theme strict-quality branch under the same
  multi-pack rule-sweep framework; the current result is that
  `theme_capture_relief_branch` is the most stable compromise candidate across
  both larger research packs, even though it is not the best local theme-branch
  winner
- an even narrower `cross_pack_compromise_sweep.yaml` now screens compromise
  candidates around that result; at the moment `balanced_compromise` is the
  strongest shared-default challenger, and it is materialized as executable
  suite configs in `baseline_research_strategy_suite_balanced_compromise.yaml`
  and `theme_research_strategy_suite_balanced_compromise.yaml`
- the current promotion-finalists screen lives in
  `promotion_finalists_check.yaml`; at the moment `balanced_compromise` is ahead
  of `shared_default`, `baseline_expansion_branch`, and
  `theme_strict_quality_branch` on the combined cross-pack stability leaderboard,
  while the branch-local winners still retain the best single capture/drawdown
  rows in their own favored environments
- the repo now has a formal promotion-gate checker too:
  `run_promotion_gate.py` evaluates a challenger against a comparison report
  under explicit thresholds; the current
  `balanced_compromise_promotion_gate.yaml` check passes and writes
  `reports/gates/balanced_compromise_vs_shared_default_gate.json`
- the stricter second-stage validation gate now exists as well:
  `balanced_compromise_validation_gate.yaml`; it currently fails because
  `balanced_compromise` gives back too much capture on the baseline research
  pack, which means it is a real shared-default challenger but not yet a
  `validation-ready` replacement
- the current freeze guidance is recorded in
  `PROJECT_LIMITATION/20_VALIDATION_READY_DEFINITION.md` and
  `PROJECT_LIMITATION/21_V1_FREEZE_CANDIDATES.md`
- the current freeze status is summarized in
  `PROJECT_LIMITATION/22_V1_FREEZE_STATUS.md`; after the latest replay the repo
  is in `freeze-but-do-not-promote-yet` state
- the split between `research V1 complete` and `practical trading not yet ready`
  is now explicit in
  `PROJECT_LIMITATION/23_PRACTICAL_TRADING_ROADMAP.md` and
  `PROJECT_LIMITATION/24_V1_RELEASE_SUMMARY.md`
- a focused `balanced_compromise` capture-recovery check was also run:
  `balanced_compromise_capture_recovery_sweep.yaml` and
  `balanced_capture_recovery_check.yaml`; the current result is that mild
  hierarchy relief can recover some baseline-pack capture, but not enough to
  beat `balanced_compromise` once the comparison returns to both research packs
- the repo now has a formal time-slice validation runner too:
  `run_time_slice_validation.py` with `time_slice_validation.yaml`; on the
  current quarterly 2024 validation slices `balanced_compromise` still leads the
  overall stability leaderboard, while `baseline_expansion_branch` wins more
  capture-heavy slices and `theme_strict_quality_branch` wins more
  lowest-drawdown slices
- the repo now also has an environment-boundary summary layer:
  `run_environment_boundary_analysis.py` with
  `environment_boundary_analysis.yaml`; the current result is explicit:
  `balanced_compromise` is the broad stability candidate,
  `baseline_expansion_branch` is the capture specialist, and
  `theme_strict_quality_branch` is the drawdown specialist
- theme-pack data quality now has its own diagnostic path too:
  `run_theme_data_quality.py` with `theme_data_quality.yaml`; the current report
  shows that the main theme-side risk is not just missing concepts but
  time-invariant primary concept mapping, high concept concentration, and very
  low multi-concept overlap
- a second theme concept-mapping iteration now exists too:
  `theme_research_concept_mapping_v2.yaml` builds
  `theme_research_concept_mapping_v2.csv` with board-history-aware concept
  weighting and date-varying primary concepts instead of a static one-label map
- on `theme_research_v2`, the concept layer quality improves materially:
  `unique_concept_count` rises from `4` to `10`,
  `mean_concepts_per_covered_symbol` rises from `1.083333` to `2.0`,
  `static_primary_symbol_ratio` drops from `1.0` to `0.333333`, and
  `multi_concept_symbol_ratio` rises from `0.083333` to `0.666667`
- the remaining theme-side concept problems are now narrower and clearer:
  one symbol still lacks concept coverage (`002902`), and one primary concept
  still dominates too much (`top_primary_concept_share=0.738079`), but the
  earlier "fully static primary concept" failure mode is no longer the main
  blocker
- the `theme_research_v2` derived pack and suite also run end to end:
  `theme_research_data_audit_v2.json` reaches `baseline_ready=true`, and
  suite run `20260329T044312Z_dbb98804` again shows the expected role split:
  `mainline_trend_c` is best on return/capture while `mainline_trend_a`
  remains lowest-drawdown
- importantly, better theme-data realism did not automatically improve theme-pack
  returns: `theme_v1_v2_dataset_comparison.yaml` shows that the old
  `theme_research_v1` pack still wins on return/capture, while the new
  `theme_research_v2` pack is cleaner but more conservative; this is treated as
  evidence that the old static concept map likely carried optimistic label bias,
  not as a reason to revert the data-quality improvement
- a broader intermediate universe now exists too:
  `config/universes/market_research_v0.txt` plus
  `PROJECT_LIMITATION/25_MARKET_RESEARCH_V0_PLAN.md`; this pack is explicitly
  meant to expand coverage without jumping straight to full-market noise
- the first `market_research_v0` data foundation is already landed:
  `akshare_daily_bars_market_research_v0.csv` has `8218` rows across `34`
  stocks, the index pack has `726` rows across `3` indices, and
  `market_research_sector_mapping_cninfo_v0.csv` provides daily industry
  mapping for the same `34` symbols
- `market_research_v0` now also has concept mapping, derived tables, audit, and
  a runnable strategy suite:
  `market_research_concept_mapping_v0.csv` has `9172` rows, the audit report
  `market_research_data_audit_v0.json` reaches `baseline_ready=true`, and suite
  run `20260329T050350Z_4ce8e316` shows the expected mixed-market split:
  `mainline_trend_b` leads on return, `mainline_trend_c` on capture, and
  `mainline_trend_a` on drawdown
- the three-pack comparison in
  `research_market_dataset_comparison.yaml` places `market_research_v0` between
  the existing baseline and theme packs: it is not as aggressive as
  `baseline_research_v1`, not as theme-heavy as `theme_research_v2`, and
  naturally favors `B/C` more than `A`
- three-pack validation now exists too:
  `time_slice_validation_v2.yaml` and
  `environment_boundary_analysis_v2.yaml` extend quarterly slice validation to
  `baseline_research_v1 + theme_research_v2 + market_research_v0`; the current
  result keeps `balanced_compromise` as the broad stability candidate,
  `baseline_expansion_branch` as the capture specialist, and
  `theme_strict_quality_branch` as the drawdown specialist
- the shared-default challenger has also been retested on all three packs via
  `promotion_finalists_check_v2.yaml` and
  `balanced_compromise_validation_gate_v2.yaml`; the verdict is still
  `do not promote yet`
- importantly, the third pack does not overturn the existing freeze logic:
  the stronger three-pack gate still fails for the same reason as before,
  namely excessive capture regression on the baseline pack, which means the
  blocker is structural rather than an artifact of only using two packs
- there is now a dedicated baseline-capture diagnostic too:
  `run_baseline_capture_diagnostic.py` with
  `baseline_capture_diagnostic_v1.yaml` shows that the blocker is concentrated
  in `baseline_research_v1`, especially `mainline_trend_b/c` and `2024_q4`,
  with the most painful windows centered on `600519_23` and `000333_19`
- a follow-up `baseline_q4_core_hierarchy_validation.yaml` check shows that
  mild core-hierarchy relief can improve Q4 return/drawdown a bit, but it does
  not actually repair the Q4 capture gap; this points the next repair cycle
  away from generic hierarchy loosening and toward more window-specific
  timing/exit investigation
- that window-specific investigation now exists too:
  `run_window_replay_diagnostic.py` with
  `window_replay_diagnostic_v1.yaml` shows that the baseline blocker is not a
  single failure mode:
  `600519_23` is a late-entry problem for `balanced_compromise`, while
  `000333_19` is an early-exit / mainline-replacement problem
- the repo now supports a narrow `AttackPermissionEngine` hysteresis knob via
  `switch_margin_buffer`, defaulting to `0.0` so existing behavior is unchanged
  unless an experiment explicitly turns it on
- the v2 replay check in
  `reports/analysis/baseline_window_replay_diagnostic_v2.json` shows that the
  two baseline-side repair levers are meaningfully different:
  restoring `repair_window=3` fully repairs the `600519_23` miss, while adding
  a small `switch_margin_buffer` improves `000333_19` capture from `0.452641`
  to `0.507922`; combining both repairs recovers the late-entry window
  completely and partially reduces the early-exit damage, but still does not
  match `shared_default` on the `000333_19` replacement-driven exit pattern
- the current implication is narrower and more useful than before:
  the baseline capture blocker is no longer "balanced_compromise is too strict"
  in the abstract; it is specifically a mix of `repair_window` timing loss and
  fast mainline-switch / replacement sensitivity
- after the baseline blocker was repaired, the remaining broad-challenger
  weakness moved to `theme_research_v2`, specifically a small cluster of
  `mainline_trend_c` windows where `balanced_targeted_timing_repair` never
  gets a window position because symbols remain `junk`
- a narrow strategy-side theme repair was tested next via
  `theme_window_replay_diagnostic_v2.yaml`,
  `theme_window_replay_diagnostic_v3.yaml`, and
  `targeted_theme_window_repair_cross_pack_check.yaml`; it can force entry into
  some of the missed windows, but the broad result is worse than keeping
  `balanced_targeted_timing_repair` unchanged
- the repo now has a dedicated pack-wide analysis for that remaining blocker:
  `run_late_mover_admissibility.py` with
  `theme_late_mover_admissibility_v1.yaml` shows that the problem is not just
  three replay windows; on `theme_research_v2`, `balanced_targeted_timing_repair`
  has `13` impacted `mainline_trend_c` windows across `7` symbols, including
  `10` fully blocked windows, and the dominant reasons are still
  `fallback_to_junk` / `low_composite_or_low_resonance`
- the next upstream layer is now measurable too:
  `run_theme_hierarchy_gap_analysis.py` with
  `theme_hierarchy_gap_analysis_v1.yaml` shows that this blocker is dominated
  by a very specific threshold band, not by resonance or broad composite
  failure: all `17` recorded gap days sit below the challenger's
  `late_mover_quality=0.60` threshold while still lying in the incumbent-only
  `0.55~0.60` band
- an experimental `theme_research_v3` derived pack was then built with a small
  concept-aware `late_mover_quality` boost:
  it does reduce the blocker count (`13 -> 10` impacted windows and `10 -> 8`
  blocked windows), but the broader pack result is mixed rather than cleanly
  better, so this remains evidence for the right direction, not a new keeper
  baseline
- a narrower `theme_research_v4` derived pack now exists too:
  instead of a uniform boost, it only lifts concept-supported names inside a
  narrow `late_mover_quality` band and caps them at the band edge; this keeps
  the pack-level suite behavior essentially aligned with `theme_research_v2`
  while cutting the remaining admissibility blocker much more cleanly
  (`13 -> 4` impacted windows and `10 -> 3` fully blocked windows)
- with `theme_research_v4`, the current strongest broad challenger is now
  `balanced_targeted_timing_repair`, not the older `balanced_compromise`
- the latest three-pack challenger check
  [20260329T060122Z_99e67000_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060122Z_99e67000_comparison.json)
  shows `balanced_targeted_timing_repair` ahead of `shared_default` on broad
  rank, mean return, and mean drawdown while only giving back a very small
  amount of capture
- the stricter validation-ready gate still does not promote it yet, but the
  failure mode is now narrower than before:
  the new gate report
  [targeted_timing_repair_validation_gate_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/targeted_timing_repair_validation_gate_v2.json)
  shows capture regression is now inside tolerance, while the remaining misses
  are insufficient `composite_rank_improvement` and insufficient
  `mean_max_drawdown_improvement`
- the updated three-pack time-slice replay
  [20260329T060321Z_a2d656e8_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060321Z_a2d656e8_comparison.json)
  keeps `balanced_targeted_timing_repair` as the most stable broad candidate
  across `baseline_research_v1`, `theme_research_v4`, and `market_research_v0`
- a final narrow refinement sweep around that challenger has now isolated the
  last useful lever: `switch_margin_buffer` itself
  - the first refinement report
    [20260329T060715Z_e2f8dc2a_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060715Z_e2f8dc2a_comparison.json)
    shows that tightening holding / exit rules does not help, while a
    buffer-only variant is the only path that materially improves the broad
    rank
  - the second refinement report
    [20260329T060753Z_bad3ddaa_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060753Z_bad3ddaa_comparison.json)
    shows `buffer_only_012` as the current best micro-variant
  - the guard micro-tuning report
    [20260329T060852Z_0f4c9bd2_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060852Z_0f4c9bd2_comparison.json)
    shows that tiny holding / exit tweaks on top of `buffer_only_012` are
    effectively dead ends
- the latest gate checks
  [buffer_only_012_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_only_012_validation_gate_v1.json)
  and
  [buffer_only_015_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_only_015_validation_gate_v1.json)
  confirm the repo's current position:
  the challenger line is now clearly beyond the old capture blocker, but it is
  still missing the stricter drawdown-improvement bar
- one more ultra-narrow interpolation pass now exists too:
  [20260329T061427Z_eaa04329_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T061427Z_eaa04329_comparison.json)
  and
  [buffer012_top262_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer012_top262_validation_gate_v1.json)
  show that even the closest threshold interpolation only moves
  `mean_max_drawdown_improvement` from `0.002504` to `0.002547`, still below
  the `0.003` gate; this is the clearest sign yet that threshold-only tuning
  is near exhaustion
- the repo now also has a dedicated structural drawdown diagnostic:
  `run_drawdown_gap_analysis.py` with
  [buffer_only_012_drawdown_gap_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/buffer_only_012_drawdown_gap_analysis_v1.json)
  shows that the remaining drawdown gap is not broad and uniform
  - the weakest dataset-strategy pair is `theme_research_v4 / mainline_trend_a`
  - the weakest slice is `theme_research_v4 / 2024_q1`
  - the worst individual rows are the three `theme_research_v4 / 2024_q1`
    strategy rows, with `mainline_trend_c` and `mainline_trend_b` slightly
    worse than `mainline_trend_a`
  this means the next cycle should attack a narrow theme-side structural
  drawdown question, not reopen cross-pack threshold search
- that theme-side pocket is now concrete enough to name:
  `run_slice_trade_divergence.py` and `run_symbol_timeline_replay.py` show that
  `300750` is the clearest repeated driver inside `theme_research_v4 / 2024_q1`
  - [theme_q1_trade_divergence_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_trade_divergence_v1.json)
    identifies `300750` as the worst repeated symbol across all three
    strategies, with the same `-530.7` pnl delta each time
  - [theme_q1_symbol_timeline_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_timeline_300750_v1.json)
    shows why: `buffer_only_012` takes an extra early trade around
    `2024-01-22 -> 2024-01-23`, then misses the profitable
    `2024-02-06 -> 2024-02-07` trade that `shared_default` still captures
  - [theme_q1_symbol_path_shift_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_path_shift_300750_v1.json)
    makes the repeated mechanism explicit across all three strategies:
    the key shift dates are `2024-01-19`, `2024-01-22`, `2024-02-02`,
    `2024-02-05`, and `2024-02-06`
    - `2024-01-19`: challenger's approved sector shifts to `BK1173` and it emits a buy while incumbent does not
    - `2024-02-05`: incumbent still has permission and emits a buy, challenger loses permission entirely
    - `2024-02-02`: challenger's assignment flips to `junk` while incumbent remains `leader`
  this is now strong evidence that the remaining drawdown blocker is a
  combined approval-path and assignment-drift problem, not just a generic
  threshold miss
  - the upstream inputs now make that even more concrete:
    on `2024-01-19`, sector scores show
    `计算机、通信和其他电子设备制造业 = 2.986566` and `BK1173 = 2.880075`,
    so the incumbent rotates while the challenger keeps `BK1173`; this is a
    hysteresis / approval-path effect
    on `2024-02-05`, `BK1173 = 2.583525`, which is above the theme-pack
    default `min_top_score=2.5` but below the challenger's `2.6`, so the
    challenger loses permission on a threshold edge day and misses the later
    profitable `2024-02-06 -> 2024-02-07` trade
  this means the next refinement question is no longer "which threshold is
  better?" but "why does the smoother regime path on theme Q1 shift 300750 into
  a worse trade sequence?"
- the repo now has a second tradable validation case too:
  [theme_q1_symbol_timeline_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_timeline_002466_v1.json)
  and
  [theme_q1_symbol_path_shift_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_path_shift_002466_v1.json)
  show the same two upstream split dates as `300750`
  - `2024-01-19`: approved sector splits between electronics and `BK1173`
  - `2024-02-05`: incumbent keeps permission while challenger loses it
  but `002466` still ends with identical trades and identical pnl on both sides
  - this is useful because it separates “path-shift shape exists�?from
    “path-shift causes actual trade damage�?  - current interpretation:
    `300750` is the first clear damage case, while `002466` is the first
    repeated-mechanism-but-no-damage case
- a third tradable replay now sharpens that picture again:
  [theme_q1_symbol_timeline_002902_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_timeline_002902_v1.json)
  and
  [theme_q1_symbol_path_shift_002902_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_path_shift_002902_v1.json)
  show repeated cross-strategy split dates on `2024-01-23`, `2024-02-05`,
  and `2024-02-28`
  - `2024-01-23`: incumbent stays `leader`, challenger falls to `junk`
  - `2024-02-05`: incumbent keeps permission, challenger loses permission
  - `2024-02-28`: both exit, but for different structural reasons
  yet realized trades and pnl remain identical
  - current interpretation:
    the repo now has three reference classes in the same theme-side pocket
    - `300750`: repeated shape that becomes real trade damage
    - `002466`: repeated approval / permission shape without damage
    - `002902`: repeated assignment divergence without damage
- those three cases are now aggregated into one structural report:
  [theme_damage_transition_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_damage_transition_analysis_v1.json)
  which gives the current best reusable rule:
  repeated approval / permission or assignment splits become promotion-relevant
  only when they also change emitted actions or active-position state
- that rule now has an explicit ranking layer:
  [theme_action_state_divergence_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_action_state_divergence_v1.json)
  shows that only `300750` crosses the repeated action-state trigger
  boundary in the current three-symbol set; `002466` and `002902` stay latent
  even though they repeat structurally similar split dates
- the triggered symbol is now decomposed one level further:
  [theme_trigger_taxonomy_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_trigger_taxonomy_300750_v1.json)
  breaks `300750` into four repeated trigger classes
  - `early_buy_trigger` on `2024-01-19`
  - `forced_sell_trigger` on `2024-01-22`
  - `missed_buy_trigger` on `2024-02-05`
  - `position_gap_exit_trigger` on `2024-02-06`
  which means the remaining theme-side blocker is now a named trigger sequence,
  not a vague local pocket
- those four trigger families now have a first economic ranking too:
  [theme_trigger_priority_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_trigger_priority_300750_v1.json)
  shows that the incumbent-side `missed_buy_trigger -> position_gap_exit_trigger`
  chain is the dominant damage source
  - incumbent-only unique cycle pnl across the three strategies: `1969.137`
  - challenger-only extra-cycle pnl across the three strategies: `377.037`
  so the next repair cycle should start from missed re-entry and position-gap
  exit, not from early-entry suppression
- that dominant chain is now fixed as its own reusable report too:
  [theme_missed_reentry_chain_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_missed_reentry_chain_300750_v1.json)
  shows the cleaner structural statement:
  - `2024-02-05` is a true `permission-loss -> missed buy` day
  - `2024-02-06` is the paired `position-gap exit` day
  - the chain completes in all three strategies
  - incumbent-only missed-cycle pnl across the three strategies is `1969.137`
  which means the remaining theme-side blocker is no longer just a ranked
  trigger family; it is a specific two-date incumbent-side missed re-entry
  chain
- the first date in that chain is now pinned to a concrete regime edge:
  [theme_permission_loss_edge_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_permission_loss_edge_300750_v1.json)
  shows that on `2024-02-05`
  - top sector `BK1173` scores `2.583525`
  - incumbent `shared_default` still approves it because `min_top_score=2.5`
  - challenger `buffer_only_012` rejects it with reason `top_score_below_threshold`
  - the miss is only `0.016475` below the challenger's `2.6` threshold
  - the margin to the second sector is still wide at `0.967343`
  so the current blocker is much more specifically a threshold-edge
  permission-loss issue than a broad regime-ambiguity issue
- that threshold edge has now been tested directly too:
  [20260329T070422Z_3a231b85_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T070422Z_3a231b85_comparison.json)
  and
  [buffer_top258_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_top258_validation_gate_v1.json)
  show that relaxing only `min_top_score` from `2.60` to `2.58`
  - does slightly improve `theme_research_v4` return and drawdown
  - does not restore theme capture
  - does not beat the current `buffer_only_012` branch on composite stability
  - still fails the stricter gate on `mean_max_drawdown_improvement`
  so the repo now has evidence that this local threshold-edge fix is real but
  not sufficient, and not currently worth replacing the stronger frozen
  challenger branch
- that residual blocker is now summarized as an explicit acceptance question too:
  [residual_cost_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/residual_cost_acceptance_v1.json)
  shows the current posture is `freeze_and_accept_residual_cost`
  because
  - the challenger still wins broadly on rank and return
  - the remaining strict-gate gap is only `0.000496`
  - the blocker is localized to `theme_research_v4 / 2024_q1`
  - the obvious cheap local repair only improved drawdown by `0.000005`
  so the repo now has explicit evidence that the remaining blocker is real but
  not cheaply repairable, and therefore better treated as residual cost than
  as a reason to keep grinding threshold tweaks
- with that blocker now frozen, the next V1.1 question has also been formalized:
  [specialist_alpha_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v1.json)
  maps where the specialist branches beat both broad anchors (`shared_default`
  and `buffer_only_012`) in their native metric
  - `baseline_expansion_branch` currently has `7` opportunity pockets
  - `theme_strict_quality_branch` currently has `9` opportunity pockets
  - the single biggest capture pocket is
    `theme_research_v4 / 2024_q1 / mainline_trend_c`
    for `baseline_expansion_branch`
  - the cleanest drawdown pocket is
    `baseline_research_v1 / 2024_q3 / mainline_trend_b,c`
    for `theme_strict_quality_branch`
  this means the next research loop should not start from the frozen blocker
  again; it should start from specialist pockets with non-overlapping edge
- the first capture-specialist pocket is no longer abstract either:
  [specialist_pocket_window_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_pocket_window_analysis_v1.json)
  shows that the `baseline_expansion_branch` edge inside
  `theme_research_v4 / 2024_q1 / mainline_trend_c` is concentrated in only
  `4` improved windows, with `2` windows that both broad anchors miss
  entirely
  - top full-miss driver: `002466_2`, capture edge `0.937549`
  - next full-miss driver: `000155_5`, capture edge `0.408511`
  - secondary partial-capture lifts: `600338_5`, `300518_7`
  this means the next capture-oriented V1.1 loop should start from those
  specific windows, not from another broad search
- the first of those windows is now explained at the daily-state level too:
  [theme_q1_specialist_window_opening_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_002466_v1.json)
  shows that `002466_2` opens on `2024-01-10` because
  `baseline_expansion_branch` upgrades the symbol from `junk` to
  `late_mover` via `late_mover_quality_fallback`
  while both broad anchors still have
  - `permission_allowed = true`
  - the same passed filters
  - the same `mid_trend_follow` trigger
  but keep the symbol in `junk` and emit no buy
  so the first specialist capture case is now clearly a hierarchy-admission
  edge, not a regime-permission edge
- the second full both-anchor miss in the same pocket is now explained too:
  [theme_q1_specialist_window_persistence_000155_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_persistence_000155_v1.json)
  shows that `000155_5` is a persistence edge, not an opening edge
  - all three candidates enter the window
  - on `2024-02-22`, only `baseline_expansion_branch` keeps holding
  - both broad anchors emit `sell` because the symbol falls back to `junk`
  - the specialist keeps `late_mover` plus `structure_intact` and preserves
    the rest of the move
  so the first capture-specialist pocket already splits into two families:
  hierarchy-admission opening edges and persistence edges
- the first partial-capture lift in the same pocket has now been classified too:
  [theme_q1_specialist_window_opening_600338_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_600338_v1.json)
  shows that `600338_5` is still an opening-edge case
  - on `2024-02-21`, only the specialist emits the first buy
  - permission, filters, and entry triggers are already aligned across all candidates
  - the only real difference is again `late_mover` admission versus `junk`
  - anchors later re-enter, so the result is a partial-capture lift instead of a full miss
  this means the first capture pocket still fits inside a two-family taxonomy:
  opening edges and persistence edges
- the last unresolved partial-capture case also fits that same map:
  [theme_q1_specialist_window_opening_300518_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_300518_v1.json)
  shows that `300518_7` is another light opening edge
  - specialist buys first on `2024-03-18`
  - both broad anchors still have permission and the same entry family
  - the decisive difference is still `late_mover` versus `junk`
  - anchors only lag by about one day, so the lift is smaller
  the first capture-specialist pocket is therefore now closed under a compact
  two-family taxonomy: opening edges and persistence edges
- the first drawdown-specialist pocket has also been localized enough to act on:
  the three symbol replays
  [baseline_q3_symbol_timeline_000001_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_symbol_timeline_000001_quality_v1.json),
  [baseline_q3_symbol_timeline_000333_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_symbol_timeline_000333_quality_v1.json),
  and
  [baseline_q3_symbol_timeline_600519_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_symbol_timeline_600519_quality_v1.json)
  show that the cleanest drawdown edge is mostly a `600519` story
  - `000001`: specialist delta `-27.127`
  - `000333`: specialist delta `-359.865`
  - `600519`: specialist delta `+1957.0392`
  and the cycle report
  [baseline_q3_symbol_cycle_delta_600519_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_symbol_cycle_delta_600519_v1.json)
  shows the mechanism at a high level:
  - incumbent-only cycles total `-10698.5493`
  - challenger-only cycles total `-8741.5101`
  so the quality branch's drawdown benefit currently looks more like
  "remove enough bad churn in `600519`" than "improve all three symbols evenly"
- that `600519` drawdown story has now been reduced into a reusable cycle taxonomy:
  [baseline_q3_cycle_mechanism_600519_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_600519_v1.json)
  classifies the first drawdown-specialist pocket into three negative-cycle mechanisms
  - `2024-08-01 -> 2024-08-02`: `entry_suppression_avoidance`
  - `2024-08-09 -> 2024-08-14`: `earlier_exit_loss_reduction`
  - `2024-07-03 -> 2024-07-05`: `later_exit_loss_extension`
  plus one small avoided positive cycle on `2024-08-16 -> 2024-08-20`
  so the first drawdown-specialist pocket is no longer just
  "quality branch improves drawdown"; it is now a compact cycle map that
  later drawdown pockets can be compared against directly
- that baseline-Q3 drawdown map is now confirmed to repeat across both
  `mainline_trend_b` and `mainline_trend_c`:
  [baseline_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cross_strategy_cycle_consistency_v1.json)
  shows an identical three-signature negative-cycle map on `600519` for both strategies
  - `2024-07-03`: `later_exit_loss_extension`
  - `2024-08-01`: `entry_suppression_avoidance`
  - `2024-08-09`: `earlier_exit_loss_reduction`
  so this is no longer just a `mainline_trend_b` anecdote;
  it is a reusable baseline-Q3 drawdown template across `B/C`
- the next drawdown-specialist pocket already shows that this line is not
  one-family only:
  [market_q4_cycle_mechanism_600519_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_600519_c_v1.json)
  shows a different `600519` mechanism on
  `market_research_v0 / 2024_q4 / mainline_trend_c`
  - the key negative-cycle repair is now `preemptive_loss_avoidance_shift`
    (`2024-12-11 -> 2024-12-12` before the incumbent's worse
    `2024-12-13 -> 2024-12-16`)
  - the same pocket also carries a very large
    `entry_suppression_opportunity_cost` on the skipped
    `2024-09-27 -> 2024-10-08` incumbent cycle
  so the drawdown-specialist line now has at least two families:
  a cleaner baseline-Q3 `B/C` template and a more ambiguous market-Q4 family
- the next drawdown-specialist pocket after that adds a third family rather
  than collapsing back into one of the first two:
  [theme_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_c_v1.json)
  shows that `theme_research_v4 / 2024_q4 / mainline_trend_c`
  is mainly a `300750` story and improves drawdown through
  - `earlier_exit_loss_reduction` on `2024-10-28 -> 2024-10-30`
  - `carry_in_basis_advantage` on `2024-11-06 -> 2024-11-07`
  this is different from market-Q4's `preemptive_loss_avoidance_shift`:
  the challenger does not avoid the later cycle entirely; it enters earlier,
  holds through it, and exits on the same day with a much better basis
  the drawdown-specialist line therefore now has at least three families:
  baseline-Q3, market-Q4, and theme-Q4
- the next drawdown pocket does not add a fourth family:
 - the next drawdown pocket does not add a fourth family:
  [theme_q3_cycle_mechanism_002460_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q3_cycle_mechanism_002460_c_v1.json)
  shows that `theme_research_v4 / 2024_q3 / mainline_trend_c`
  mostly reuses the baseline-style `entry_suppression_avoidance` family on
  `002460`
  - avoided bad incumbent-only cycles: `2024-07-12`, `2024-08-01`, `2024-08-14`
  - but with two noisier residual `other_worse_loss_shift` rows on
    `2024-08-30` and `2024-09-27`
  so the drawdown-specialist taxonomy is now doing both things it should:
  it can expand when a genuinely new family appears, and it can also
  recognize when a later pocket is mainly reusing an old family
- the next drawdown pocket after that does add a fourth family:
  [theme_q2_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_300750_c_v1.json)
  shows that `theme_research_v4 / 2024_q2 / mainline_trend_c`
  is mainly a `300750` story and introduces
  `delayed_entry_basis_advantage`
  - incumbent enters on `2024-05-20`
  - challenger waits until `2024-05-21`
  - both exit on `2024-05-22`
  - challenger loses much less because the basis is lower
  this is the mirror image of `carry_in_basis_advantage`, where the
  challenger enters earlier and exits on the same day with a better basis
  the drawdown-specialist taxonomy therefore now has four families:
  baseline-style avoidance, `preemptive_loss_avoidance_shift`,
  `carry_in_basis_advantage`, and `delayed_entry_basis_advantage`
- those four families are now also ranked as a research inventory rather than
  just listed as labels:
  [cycle_family_inventory_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v1.json)
  currently shows
  - `entry_suppression_avoidance` as the strongest reusable family
  - `carry_in_basis_advantage` as the cleanest non-baseline basis family
  - `preemptive_loss_avoidance_shift` as strong but expensive in opportunity cost
  - `entry_suppression_opportunity_cost` as the main toxic family
  so the next drawdown-specialist loop should not start from the most recent
  pocket. It should start from the most promising family.
- `carry_in_basis_advantage` has now crossed the line from "clean pocket" to
  "cross-strategy reusable family":
  [theme_q4_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cross_strategy_cycle_consistency_v1.json)
  shows that `theme_research_v4 / 2024_q4 / 300750` has an identical
  negative-cycle map on both `mainline_trend_b` and `mainline_trend_c`
  - `earlier_exit_loss_reduction` on `2024-10-28 -> 2024-10-30`
  - `carry_in_basis_advantage` on `2024-11-06 -> 2024-11-07`
  and [cycle_family_inventory_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v2.json)
  now lifts `carry_in_basis_advantage` to `report_count = 2` and
  `net_family_edge = 1682.5046` with zero positive opportunity-cost drag
- two cheap follow-up checks did **not** produce a second clean `carry`
  pocket:
  - [theme_q4_cycle_mechanism_300759_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300759_b_v1.json)
    is only `earlier_exit_loss_reduction`
  - [theme_q4_cycle_mechanism_002466_c_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002466_c_v2.json)
    is a mixed pocket with `entry_suppression_avoidance`, `earlier_exit_loss_reduction`,
    and toxic positive-cycle drag
- because of that, next-symbol selection is now driven by a replay queue
  instead of by memory:
  [drawdown_family_candidate_shortlist_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v2.json)
  currently points to `theme_research_v4 / 2024_q3 / mainline_trend_c / 603799`
  as the next top unanalysed drawdown-family candidate
- `theme_q3 / 603799` has now been replayed and rejected as a family
  expansion case:
  [theme_q3_cycle_mechanism_603799_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q3_cycle_mechanism_603799_c_v1.json)
  is a mixed pocket with one clean `entry_suppression_avoidance` row and one
  toxic positive-cycle truncation, so it does not belong in the family inventory
- after excluding it, the replay queue moves on:
  [drawdown_family_candidate_shortlist_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v3.json)
  now points to `market_research_v0 / 2024_q4 / mainline_trend_c / 300750`
  as the next top unanalysed drawdown-family candidate
- `market_q4 / 300750` has now also been checked and turns out to be another
  clean `entry_suppression_avoidance` case, not a new non-baseline family:
  [market_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_300750_c_v1.json)
  contains a single avoided negative cycle on `2024-10-22 -> 2024-10-23`
- after excluding that, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v4.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v4.json)
  now points to `baseline_research_v1 / 2024_q3 / mainline_trend_c / 000333`
  as the next top unanalysed drawdown-family candidate
- `baseline_q3 / 000333 / C` has now also been replayed and turns out to be
  another strong baseline-style reuse case rather than a new non-baseline
  family:
  [baseline_q3_cycle_mechanism_000333_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_000333_c_v1.json)
  is dominated by
  - three `earlier_exit_loss_reduction` rows
  - two `entry_suppression_avoidance` rows
  but still carries two large positive-cycle degradations labeled
  `other_worse_loss_shift`
  (`2024-08-19 -> 2024-08-20` and `2024-09-25 -> 2024-10-09`)
  so it raises confidence in the baseline-style family without extending the
  non-baseline frontier
- after excluding `000333`, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v5.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v5.json)
  now determines the next candidate instead of continuing to replay
  baseline-Q3 reuse cases
- `market_q4 / 002371 / C` has now also been replayed and turns out to be one
  of the cleanest remaining baseline-style pockets, but still not a new family:
  [market_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_002371_c_v1.json)
  contains a single `entry_suppression_avoidance` row on `2024-12-30 -> 2024-12-31`
  and nothing else
- after excluding `002371`, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v6.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v6.json)
  now becomes the authoritative next-candidate list for the drawdown-family search
- [cycle_family_inventory_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v3.json)
  now shows that `preemptive_loss_avoidance_shift` is no longer a one-pocket
  story: it has a second reuse case via `market_q4 / 000858 / C`, but the
  same opportunity-cost baggage also repeats with it
- `theme_q2 / 002466 / C` has now also been replayed and does not become a new
  family asset:
  [theme_q2_cycle_mechanism_002466_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_002466_c_v1.json)
  is a stacked pocket with
  - one `preemptive_loss_avoidance_shift`
  - two `entry_suppression_avoidance` rows
  - one positive `delayed_entry_basis_advantage`
  so it reinforces multiple known mechanisms without extending the frontier
- after excluding `theme_q2 / 002466`, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v8.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v8.json)
  becomes the new authoritative next-candidate list
- `theme_q4 / 002902` has now also been replayed on both `B/C`, and the two
  reports are structurally identical:
  [theme_q4_cycle_mechanism_002902_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002902_b_v1.json)
  and
  [theme_q4_cycle_mechanism_002902_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002902_c_v1.json)
  each contain one `earlier_exit_loss_reduction`, two
  `entry_suppression_avoidance`, and one negative `other_worse_loss_shift`
  this makes `002902` a reusable mixed-pocket example, but still not a clean
  family asset
- after excluding both `002902` rows, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v9.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v9.json)
  becomes the new authoritative next-candidate list
- `market_q4 / 603259 / C` has now also been replayed and turns out to be
  another extremely clean single-row baseline-style case:
  [market_q4_cycle_mechanism_603259_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_603259_c_v1.json)
  contains only one `entry_suppression_avoidance` row on `2024-10-30 -> 2024-10-31`
- after excluding `603259`, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v10.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v10.json)
  becomes the new authoritative next-candidate list
- `theme_q4 / 603087` has now also been replayed on both `B/C`, and both
  reports collapse into the same one-row baseline-style result:
  [theme_q4_cycle_mechanism_603087_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_b_v1.json)
  and
  [theme_q4_cycle_mechanism_603087_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_c_v1.json)
  each contain only one `entry_suppression_avoidance` row
- after excluding both `603087` rows, the replay queue rotates again:
  [drawdown_family_candidate_shortlist_v11.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v11.json)
  becomes the new authoritative next-candidate list
- the current replay loop is now better understood as a
  `feature-limited thinning phase` than as an open-ended family-discovery
  loop:
  [specialist_feature_gap_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_feature_gap_audit_v1.json)
  shows `9` recent pockets collapsing into
  - `mixed_existing_families = 4`
  - `single_row_baseline_reuse = 4`
  - `stacked_family_pocket = 1`
  with `feature_gap_suspect_count = 2` and `thinning_signal = true`
- the two clearest current feature-gap suspects are:
  - `theme_research_v4 / 2024_q4 / 002902`, a `cross_strategy_mixed_repeat`
  - `theme_research_v4 / 2024_q2 / 002466`, a `stacked_known_families` pocket
- because of that, the default next step is no longer `drawdown_family_candidate_shortlist_v12`
  replay. It is a bounded `feature gap -> feature-pack-a -> replay recheck`
  cycle, with phase guardrails now written in
  [26_V11_SPECIALIST_ALPHA_GUARDRAILS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/26_V11_SPECIALIST_ALPHA_GUARDRAILS.md)
- the first bounded feature-expansion cycle is now defined in
  [27_FEATURE_PACK_A_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/27_FEATURE_PACK_A_PLAN.md),
  and it is intentionally narrow:
  - recheck only `theme_q4 / 002902` and `theme_q2 / 002466`
  - add only theme/concept support, hierarchy-margin, approval-edge, and short
    cycle-context features
- `feature-pack-a` v1 has now been executed rather than just planned:
  [feature_pack_a_recheck_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_recheck_v1.json)
  shows `8/8` suspect mechanism rows landing on at least one explicit edge
  after the richer snapshot fields were added to
  [theme_research_stock_snapshots_v5.csv](D:/Creativity/A-Share-Quant_TrY/data/derived/stock_snapshots/theme_research_stock_snapshots_v5.csv)
  the two suspects now split cleanly:
  - `theme_q4 / 002902`: mostly hierarchy / approval-edge with zero concept support
  - `theme_q2 / 002466`: concept-supported hierarchy pocket with repeated
    late-quality and non-junk-composite straddles
  which means the replay queue should stay paused until these two edge types
  are tested directly
- the post-`feature-pack-a` split is now formal rather than verbal:
  [feature_pack_a_triage_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_triage_v1.json)
  and
  [feature_pack_b_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_readiness_v1.json)
  now fix the next-step order:
  1. `theme_q4 / 002902 / B` as a `hierarchy_approval_edge`
  2. `theme_q2 / 002466 / C` as a `concept-supported hierarchy edge`
  This sequence is now written into
  [28_FEATURE_PACK_B_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/28_FEATURE_PACK_B_PLAN.md),
  so the next phase is no longer "expand features in general", but "run the
  cleaner hierarchy/approval lane first"
- track A is now instrumented beyond a coarse label:
  [feature_pack_b_hierarchy_approval_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_v1.json)
  shows that `theme_q4 / 002902 / B` is a coupled edge where
  `late_mover_quality` is the dominant hierarchy bottleneck and
  `score-margin threshold` is the dominant approval bottleneck
  this means the next refinement step should stay inside the
  hierarchy/approval lane rather than reopening replay or jumping to the
  concept-supported lane too early
- track A has now also been tested for cheap local repair paths:
  [feature_pack_b_hierarchy_approval_sweep_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v1.json)
  and
  [feature_pack_b_hierarchy_approval_sweep_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v2.json)
  show that `002902` is explainable but not cheaply fixable:
  more trigger repairs lead to worse symbol-level PnL
  so this lane is now better treated as a negative-but-informative result,
  and the next `feature-pack-b` budget should move to
  `theme_q2 / 002466 / C`
- track B is now also narrowed enough to avoid reopening a broad concept loop:
  [feature_pack_b_concept_supported_hierarchy_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_supported_hierarchy_v1.json)
  shows that `theme_q2 / 002466 / C` is better treated as a
  `concept_to_late_mover` bridge candidate than as a
  `concept_to_non_junk` candidate
  so the next concept-aware refinement should only target late-mover
  admission first
- `feature-pack-b` is now effectively closed under the current feature set:
  [feature_pack_b_concept_late_validation_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_late_validation_v1.json)
  shows that the `002466` concept-to-late lane repaired only one of the two
  target rows and retained just `17.5%` of the original specialist alpha
  so, just like `002902`, it should now be treated as a
  negative-but-informative explanatory lane rather than a promotable
  refinement path
- the next stage is now explicitly `feature-pack-c`, not replay-queue restart:
  [feature_pack_c_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_readiness_v1.json)
  shows both `feature-pack-b` tracks closed and `do_restart_replay_queue = false`
  so the next budget should go only to four local-causal feature groups,
  formalized in
  [29_FEATURE_PACK_C_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/29_FEATURE_PACK_C_PLAN.md)
- unsupervised learning is now allowed only as a **report-only sidecar**,
  not as a direct signal engine:
  [30_UNSUPERVISED_FEATURE_RELATION_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/30_UNSUPERVISED_FEATURE_RELATION_PLAN.md)
  constrains the first pass to lightweight geometry only
  (`correlation`, `redundancy`, `numpy`-level PCA, small pocket grouping)
  and keeps it downstream of `feature-pack-c`
- `feature-pack-c` has now started with a real first-priority rule:
  [feature_pack_c_fallback_reason_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_fallback_reason_analysis_v1.json)
  shows the current suspect pockets are mostly `late_quality`-dominant rather
  than concept-dominant or pure approval-dominant
  so the next implementation step should be `late_quality` residual structure,
  with approval and concept-support features following behind it
- the first residual read is now also in place:
  [feature_pack_c_late_quality_residuals_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_late_quality_residuals_v1.json)
  shows all `8` suspect rows still fail on the raw late-quality stack and that
  concept boost is active on only `1` row
  and the dominant residual contributors are now `stability` and `liquidity`
  so the next pack-C step should stay inside raw late-quality component context
  rather than reopening concept bridges or approval-threshold tuning
- the first `stability/liquidity` context read is also done:
  [feature_pack_c_stability_liquidity_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_stability_liquidity_context_v1.json)
  shows `turnover_share_led = 3`, `mixed_stability_liquidity = 3`, and
  `volatility_led = 0`
  so the next pack-C move should be `turnover-share` context, not a new
  volatility-first branch
- the first turnover-share context read is now also done:
  [feature_pack_c_turnover_share_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_turnover_share_context_v1.json)
  shows one clean `sector_peer_dominance` row and two `balanced_share_weakness`
  rows, with no `broad_attention_deficit`
  so the turnover lane should stay descriptive and local rather than turning
  into a generic attention-deficit hypothesis
- the turnover-share lane is now effectively closed under the current suspect
  set:
  [feature_pack_c_balanced_turnover_weakness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_balanced_turnover_weakness_v1.json)
  shows both `002902` rows are `singleton_sector_masking`, not true reusable
  `balanced_share_weakness`
- because of that, `feature-pack-c` now has a formal explanatory-close posture:
  [feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json)
  concludes:
  - `close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar`
  - `do_continue_pack_c_turnover_branch = false`
  - `do_restart_replay_queue = false`
  - `ready_for_u1_lightweight_geometry = true`
  so the next healthy move is a bounded `U1 lightweight geometry` sidecar, not
  another replay restart and not another turnover-lane refinement
- the first `U1 lightweight geometry` sidecar has now also run and justified
  itself:
  [u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json)
  shows the two current suspect pockets are already geometrically separable
  (`case_centroid_distance = 4.080383`), with
  - concept-support geometry dominating `pc1`
  - late-quality / resonance geometry dominating `pc2`
  so the next-stage work should **not** treat `002902` and `002466` as one
  blended feature branch
- the next sidecar stage is now explicitly parked:
  [u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json)
  shows:
  - `suspect_count = 2`
  - `u1_cases_geometrically_separable = true`
  - `u2_ready = false`
  so the repo should not open clustering yet; it should wait for a larger or
  less separable suspect batch
- the current research conclusion is therefore sharper:
  the remaining `theme` blocker has mostly been narrowed to a small residual
  composite-threshold issue, and the repo no longer needs strategy-side
  theme-admission hacks to study it
- full regression coverage has also been rerun after the latest code-changing
  cycle, and the repo is currently at `54 passed`
- when refreshing the bootstrap-derived research inputs, run the pipeline in
  order: `bootstrap_free_data` (only when the symbol universe changes) ->
  `bootstrap_sector_mapping` -> `bootstrap_concept_mapping` ->
  `generate_bootstrap_derived_data` ->
  `run_strategy_experiment` / `run_strategy_suite`
- the current bootstrap-derived hierarchy is now sector-relative enough to
  produce non-trivial A/B/C separation on the free local dataset, but it is
  still a lab-stage heuristic rather than a production research definition
- the current bootstrap data-pack audit should show `security_master` as ready,
  `daily_bars`, `security_master`, and `adjustment_factors` as ready, with
  `sector_mapping_daily` still the main remaining bootstrap-partial canonical
  table
- `feature-pack-c` is now formally closed as explanatory rather than
  promotable:
  [feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json)
  concludes:
  - `close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar`
  - `do_continue_pack_c_turnover_branch = false`
  - `do_restart_replay_queue = false`
- the first bounded unsupervised sidecar has now also completed and changed a
  real interpretation boundary:
  [u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json)
  shows the two current suspect pockets are geometrically separable, so they
  should not be treated as one blended next-stage feature problem
- clustering remains explicitly parked:
  [u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json)
  shows `u2_ready = false`, so the repo should wait for a larger or less
  separable suspect batch before opening `U2`
- `market_research_v1` is now a complete broad substrate rather than just a
  plan:
  [market_research_data_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v1.json)
  shows `baseline_ready = true`, and
  [20260329T111733Z_3e700662_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T111733Z_3e700662_comparison.json)
  shows:
  - `mainline_trend_c` best total return and capture
  - `mainline_trend_a` lowest drawdown
  - `mainline_trend_b` remains the middle mixed-market profile
- a fresh three-pack time-slice validation with `market_research_v1` now shows
  the broader freeze still holds while specialist geography moves forward:
  [20260329T112015Z_d5db1be9_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T112015Z_d5db1be9_comparison.json)
  keeps `buffer_only_012` as the broad stability leader
- the first `market_research_v1` specialist map is now also in place:
  [specialist_alpha_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v2.json)
  shows:
  - strongest new drawdown pocket:
    `market_research_v1 / 2024_q3 / mainline_trend_c`
  - strongest new capture pockets:
    `market_research_v1 / 2024_q2 / mainline_trend_a|b|c`
  so when specialist refinement eventually reopens, `market_research_v1`
  should now be the first suspect-generating pack instead of `market_research_v0`
- the first `market_research_v1` drawdown replay is now also classified:
  [market_v1_q3_cycle_mechanism_300308_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_c_v1.json)
  shows that `market_research_v1 / 2024_q3 / mainline_trend_c / 300308` is
  not a new family, but a clean reuse of the baseline-style drawdown family
  (`entry_suppression_avoidance + earlier_exit_loss_reduction`)
- the first `market_research_v1` q2 capture replay is now also classified:
  [market_v1_q2_specialist_window_persistence_300502_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_persistence_300502_v1.json)
  shows that `market_research_v1 / 2024_q2 / mainline_trend_c / 300502` is a
  persistence edge:
  the specialist keeps the window alive while both broad anchors sell after the
  symbol falls back to `junk`
- the q2 capture slice is now explicitly mixed rather than persistence-only:
  [market_v1_q2_specialist_window_opening_002371_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_opening_002371_v1.json)
  shows `002371` is a clean opening edge where both anchors already share
  permission and entry triggers but remain `junk` while the specialist upgrades
  the symbol to `late_mover`
- that q2 slice now also has an explicit stop gate:
  [market_v1_q2_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_capture_slice_acceptance_v1.json)
  concludes the current q2 read should be treated as a closed mixed slice,
  rather than a line that should keep expanding symbol by symbol
- the q3 drawdown slice is now also explicitly closed:
  [market_v1_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_drawdown_slice_acceptance_v1.json)
  concludes:
  - `close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse`
  - `shared_top_driver = 300308`
  - `identical_negative_cycle_map = true`
  - `do_continue_q3_drawdown_replay = false`
  so `market_research_v1 / 2024_q3` should now be treated as a closed,
  cross-strategy-stable baseline-style reuse slice
- the first q4 drawdown probe is now also in:
  [market_v1_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_002371_c_v1.json)
  and it lowers novelty rather than widening the family frontier:
  the current top q4/C symbol `002371` is only a clean single-row
  `entry_suppression_avoidance`
  and the second q4 symbol now widens that into a bounded mixed slice:
  [market_v1_q4_cycle_mechanism_000977_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_000977_c_v1.json)
  adds:
  - `preemptive_loss_avoidance_shift`
  - `earlier_exit_loss_reduction`
  so q4 is now formally closed as a mixed drawdown slice via
  [market_v1_q4_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_drawdown_slice_acceptance_v1.json)
- the current phase boundary after these first `market_research_v1` pockets is
  now written down explicitly in
  [32_V11_STAGE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/32_V11_STAGE_REVIEW.md):
  `market_research_v1` is now the default starting substrate for future
  specialist suspects, but continuation must stay narrow and mechanism-first
- the first sector/theme context audit is now also in:
  [sector_theme_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/sector_theme_context_audit_v1.json)
  and it says the next conditioning step should be:
  - `theme_load_plus_turnover_concentration_context`
  - then `sector_state_heat_breadth_context`
  not direct per-sector training
- that first context step is now also validated into an explicit next branch:
  [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json)
  recommends:
  - `conditioned_late_quality_on_theme_turnover_context`
  - `defer_sector_heat_branch = true`
- that first context-conditioned branch has now also been tested and closed as
  non-material:
  [context_feature_pack_a_conditioned_late_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_v1.json)
  identifies real candidate rows only in `q2/q4`, but
  [context_feature_pack_a_conditioned_late_quality_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_acceptance_v1.json)
  shows the retained hierarchy experiment is not worth keeping:
  - `material_improvement_count = 0`
  - `harmed_strategy_count = 1`
  - `do_promote_conditioned_branch = false`
  so sector/theme context remains useful as analysis, not yet as per-sector
  training and not yet as a kept hierarchy rule
- the deferred second context branch has now also been checked directly:
  [context_feature_pack_b_sector_heat_breadth_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_b_sector_heat_breadth_v1.json)
  shows only `1` surviving candidate row, all inside `2024_q4`, so the
  current posture is:
  - `close_sector_heat_breadth_context_branch_as_sparse`
  - `do_continue_context_feature_pack_b = false`
  this keeps sector/theme context at the explanatory layer and still does not
  justify per-sector training
- the current `V1.1` specialist loop now has an explicit stop gate:
  [v11_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v11_continuation_readiness_v1.json)
  concludes:
  - `all_market_v1_slices_closed = true`
  - `all_context_branches_closed = true`
  - `u2_ready = false`
  - `recommended_next_phase = pause_specialist_refinement_and_prepare_new_suspect_batch`
  so the repo should not invent another local replay lane inside the current
  batch; the next productive move is a materially new suspect batch
- that next suspect batch is now also constrained by a design rule:
  [next_suspect_batch_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_design_v1.json)
  concludes:
  - `recommended_next_batch_name = market_research_v2_seed`
  - `recommended_batch_posture = expand_by_missing_context_archetypes`
  - current missing archetypes include:
    - `theme_loaded + balanced_turnover + broad_sector`
    - `theme_loaded + balanced_turnover + narrow_sector`
    - `theme_light + concentrated_turnover + broad_sector`
  so the next batch should be a context-targeted seed, not a random size expansion
- the first `market_research_v2_seed` manifest is now also ready:
  [next_suspect_batch_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v1.json)
  shows:
  - `seed_universe_count = 9`
  - `new_symbol_count = 9`
  - `overlap_with_market_v1_count = 0`
  - `missing_archetype_count = 0`
  - `ready_to_bootstrap_market_research_v2_seed = true`
  so the repo now has a concrete, auditable next batch and does not need
  another design loop before bootstrap
- `market_research_v2_seed` has now completed its first runnable pass:
  [market_research_data_audit_v2_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_seed.json)
  reaches `baseline_ready=true`, and
  [20260329T130402Z_0e1d8809_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130402Z_0e1d8809_comparison.json)
  shows `mainline_trend_c` best total return/capture and `mainline_trend_b`
  lowest drawdown
- the first four-pack validation with `market_research_v2_seed` is now also in:
  [20260329T130537Z_f0a9da05_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130537Z_f0a9da05_comparison.json)
  keeps `buffer_only_012` as the broad stability leader, while
  [specialist_alpha_analysis_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v3.json)
  shows `market_research_v2_seed` already contributes narrow specialist pockets
  under both the capture and drawdown specialists
- the first narrow `v2_seed` replay is now also in:
  [market_v2_seed_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_trade_divergence_capture_c_v1.json)
  identifies `603986` as the dominant q4/C capture symbol, and
  [market_v2_seed_q4_specialist_window_opening_603986_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_specialist_window_opening_603986_v1.json)
  confirms a clean opening edge on `2024-12-12`; but
  [market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json)
  also carries a positive pre-q4 trade, so the current `v2_seed / q4 / C` read
  is mixed rather than a clean new family signal
- that q4/C read is now formally closed too:
  [market_v2_seed_q4_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_capture_slice_acceptance_v1.json)
  concludes:
  - `close_market_v2_seed_q4_capture_slice_as_opening_plus_carry`
  - `do_continue_q4_capture_replay = false`
- the first narrow `v2_seed` q3/C drawdown read is now also in:
  [market_v2_seed_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_trade_divergence_quality_c_v1.json)
  and
  [market_v2_seed_q3_cycle_mechanism_603986_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_cycle_mechanism_603986_c_v1.json)
  which currently read as mixed avoidance plus opportunity cost, not a clean new family
- q3/C is now also formally closed:
  [market_v2_seed_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_drawdown_slice_acceptance_v1.json)
  concludes:
  - `close_market_v2_seed_q3_drawdown_slice_as_avoidance_plus_opportunity_cost`
  - `do_continue_q3_drawdown_replay = false`
- `v2_seed` now also has its own continuation gate:
  [market_v2_seed_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_continuation_readiness_v1.json)
  concludes:
  - `all_open_v2_seed_lanes_closed = true`
  - `recommended_next_phase = hold_market_v2_seed_as_secondary_substrate_and_wait_for_next_batch_refresh`
  - `do_continue_current_v2_seed_replay = false`
- and the repo now also has an explicit post-`v2_seed` refresh gate:
  [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json)
  concludes:
  - `do_open_market_research_v2_refresh_now = false`
  - `recommended_next_phase = wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh`
- and that waiting state now also has a live monitor:
  [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json)
  currently shows:
  - `active_trigger_count = 0`
  - `recommended_posture = maintain_waiting_state_until_new_trigger`
- and that wait state now also has an operator checklist:
  [refresh_trigger_action_plan_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_action_plan_v1.json)
  currently shows:
  - `action_mode = idle_wait_state`
  - `action_count = 3`
- and the whole current gate stack is now compressed into one report:
  [phase_status_snapshot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/phase_status_snapshot_v1.json)
  currently shows:
  - `current_mode = explicit_no_trigger_wait`
  - `all_gates_aligned = true`
  - `active_trigger_count = 0`
- and that stack is now refreshable in one command:
  `python scripts/run_phase_status_refresh.py`
- and readable in one short console command:
  `python scripts/run_phase_status_console.py`
- and available through one shortest safe guarded command:
  `python scripts/run_phase_guard.py`
- and if a genuinely new signal appears, it can now be persisted first via:
  `python scripts/run_refresh_trigger_intake.py ...`
  using canonical trigger types rather than free-form labels
- the default A-share broker commission assumption is now aligned to the
  owner's live contract:
  - `commission_bps = 1.2` (`0.12��`)
  - `min_commission = 5.0`
- the repo now also aligns the statutory A-share stock-fee assumptions to the
  current public fee schedule:
  - `stamp_tax_bps = 5.0` on sells only (`0.05%`)
  - `transfer_fee_bps = 0.1` on both buys and sells (`0.001%`)
  - `exchange_handling_bps = 0.341` on both buys and sells (`0.00341%`)
  - `regulatory_fee_bps = 0.2` on both buys and sells (`0.002%`)

- the repo has now explicitly opened the next main research phase:
  - [44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md)
  - [45_DATA_SOURCE_INVENTORY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/45_DATA_SOURCE_INVENTORY.md)
  current reading:
  - the next active target is `market_research_v2_refresh`
  - AkShare remains the primary batch-ingestion layer
  - official sites remain the preferred fee/rule truth layer
  - direct per-sector training remains deferred

- the repo has now explicitly opened the next main research phase:
  - [44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md)
  - [45_DATA_SOURCE_INVENTORY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/45_DATA_SOURCE_INVENTORY.md)
- the first runnable `V1.2` batch skeleton is now also prepared:
  - [46_MARKET_RESEARCH_V2_REFRESH_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/46_MARKET_RESEARCH_V2_REFRESH_PLAN.md)
  - [config/market_research_v2_refresh_manifest.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_v2_refresh_manifest.yaml)
  - [reports/analysis/next_suspect_batch_manifest_v2_refresh.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v2_refresh.json)
  current reading:
  - the next active target is `market_research_v2_refresh`
  - AkShare remains the primary batch-ingestion layer
  - official sites remain the preferred fee/rule truth layer
  - direct per-sector training remains deferred

- `V1.2` now also has its first formal feature/factor registry:
  - [47_FEATURE_FACTOR_REGISTRY_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/47_FEATURE_FACTOR_REGISTRY_V1.md)
  - [feature_factor_registry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_factor_registry_v1.json)
  current reading:
  - retained features = `4`
  - explanatory-only features = `3`
  - candidate factors = `3`
  - the next `V1.2` step is now `factor_evaluation_protocol_v1`, not more local replay by momentum

- `V1.2` now also has its first factor-evaluation protocol:
  - [48_FACTOR_EVALUATION_PROTOCOL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/48_FACTOR_EVALUATION_PROTOCOL_V1.md)
  - [factor_evaluation_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/factor_evaluation_protocol_v1.json)
  current reading:
  - `carry_in_basis_advantage` = `evaluate_now`
  - `preemptive_loss_avoidance_shift` = `evaluate_with_penalty`
  - `delayed_entry_basis_advantage` = `hold_for_more_sample`

- `V1.2` now also has its first bounded factor lane:
  - [49_CARRY_IN_BASIS_FIRST_PASS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/49_CARRY_IN_BASIS_FIRST_PASS.md)
  - [carry_in_basis_first_pass_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_in_basis_first_pass_v1.json)
  current reading:
  - `carry_in_basis_advantage` is ready for bounded factor design
  - it is still below retained-feature promotion
  - penalty-track and thin factors remain frozen

- `V1.2` now also has the first carry factor design artifact:
  - [50_CARRY_FACTOR_DESIGN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/50_CARRY_FACTOR_DESIGN_V1.md)
  - [carry_factor_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_design_v1.json)
  current reading:
  - carry factor lane is open
  - row isolation is required
  - broad factor scoring remains off

- `V1.2` now also has the first carry observable schema:
  - [51_CARRY_OBSERVABLE_SCHEMA_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/51_CARRY_OBSERVABLE_SCHEMA_V1.md)
  - [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)
  current reading:
  - carry lane remains row-isolated
  - the first explicit required fields are now fixed
  - scoring design is now the next bounded step

- `V1.2` now also has the first carry scoring design:
  - [52_CARRY_SCORING_DESIGN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/52_CARRY_SCORING_DESIGN_V1.md)
  - [carry_scoring_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_scoring_design_v1.json)
  current reading:
  - `carry_score_v1` now exists
  - the lane is ready for a bounded factor pilot
  - strategy integration remains off

- `V1.2` now also has the first carry factor pilot:
  - [53_CARRY_FACTOR_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/53_CARRY_FACTOR_PILOT_V1.md)
  - [carry_factor_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_pilot_v1.json)
  current reading:
  - the pilot is open
  - it is only `report_only_micro_pilot`
  - rankable pilot and strategy integration remain off

- `V1.2` now also has its first factorization review:
  - [54_V12_FACTORIZATION_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/54_V12_FACTORIZATION_REVIEW_V1.md)
  - [v12_factorization_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_factorization_review_v1.json)
  current reading:
  - the first factorization cycle counts as representative
  - it remains bounded
  - the second factor lane stays closed for now

- `V1.2` now also has phase-readiness guidance:
  - [55_V12_PHASE_READINESS_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/55_V12_PHASE_READINESS_V1.md)
  - [v12_phase_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_phase_readiness_v1.json)
  current reading:
  - `V1.2` stays open
  - the next bottleneck is factor row diversity
  - the next healthy move is a later refresh batch, not a second factor lane yet

- `V1.2` now also has the next refresh design:
  - [56_V12_NEXT_REFRESH_FACTOR_DIVERSITY_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/56_V12_NEXT_REFRESH_FACTOR_DIVERSITY_PLAN.md)
  - [v12_next_refresh_factor_diversity_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_factor_diversity_design_v1.json)
  current reading:
  - the next refresh is now justified by factor-row diversity
  - not by generic sample growth
  - the next concrete step is a new manifest for `market_research_v3_factor_diversity_seed`

## V1.2 update
- `market_research_v3_factor_diversity_seed` is now the next executable refresh step rather than a design-only placeholder.
- Manifest gate passed in `reports/analysis/market_research_v3_factor_diversity_seed_manifest_v1.json`.
- The seed adds `8` new symbols and covers all four carry row-diversity targets before bootstrap.

## V1.2 update
- `market_research_v3_factor_diversity_seed` is now bootstrap-complete and `baseline_ready`.
- First suite run: `reports/20260330T005408Z_70e5fe8c_comparison.json`.
- Immediate next step is no longer bootstrap; it is the first specialist comparison against the current carry row-diversity bottleneck.

## V1.2 update
- `market_research_v3_factor_diversity_seed` is now in the active specialist map, not just baseline-ready.
- Six-pack validation report: `reports/20260330T005654Z_c28cab1a_comparison.json`.
- First v3 specialist lane: `market_research_v3_factor_diversity_seed / 2024_q4 / mainline_trend_c`, with `002049` as the top positive capture driver.

## V1.2 update
- The first `market_research_v3_factor_diversity_seed` lane has now been structurally narrowed.
- `market_research_v3_factor_diversity_seed / 2024_q4 / mainline_trend_c / 002049` currently reads as an opening-led lane, not a persistence-led lane.
- Opening evidence: `reports/analysis/market_v3_factor_diversity_q4_specialist_window_opening_002049_v1.json`.
- Persistence check remained empty: `reports/analysis/market_v3_factor_diversity_q4_specialist_window_persistence_002049_v1.json`.
- Current posture remains bounded: do not yet interpret this as a carry-lane structural breakthrough, and do not widen the `v3` replay map.

## V1.2 update
- The first `market_research_v3_factor_diversity_seed` lane is now formally closed by `reports/analysis/market_v3_q4_first_lane_acceptance_v1.json`.
- Current reading: `002049 / 2024_q4 / mainline_trend_c` is opening-led, not persistence-led, and not a carry-lane breakthrough.
- `v3` remains useful as a factor-row-diversity substrate, but second-lane expansion stays closed for now.

## V1.2 update
- `reports/analysis/v12_bottleneck_check_v1.json` confirms that the first `v3` lane does not change the main V1.2 bottleneck.
- Current reading remains: the primary gap is still carry row diversity, not lack of a capture-opening substrate.
- The second `v3` lane remains closed, and V1.2 stays on the factor-row-diversity track.

## V1.2 update
- `reports/analysis/v12_next_refresh_entry_v1.json` now opens a criteria-first next-refresh entry for `market_research_v4_carry_row_diversity_refresh`.
- Current posture is deliberate: prepare the refresh entry now, but do not open a new manifest yet.
- This keeps V1.2 focused on carry row diversity while replay remains closed.

## V1.2 update
- `reports/analysis/v12_v4_refresh_criteria_v1.json` now freezes symbol-selection rules for `market_research_v4_carry_row_diversity_refresh`.
- The next refresh can now move into manifest drafting, but only under carry-schema and row-diversity criteria.
- Replay remains closed while the `v4` manifest is being drafted.

## V1.2 update
- `reports/analysis/market_research_v4_carry_row_diversity_refresh_manifest_v1.json` is now green.
- `market_research_v4_carry_row_diversity_refresh` has moved from criteria-ready to manifest-ready.
- The next mainline step is bootstrap, not replay.

## V1.2 update
- `market_research_v4_carry_row_diversity_refresh` now audits as `baseline_ready` and has completed its first suite run.
- Seven-pack validation and `specialist_alpha_analysis_v6` place `v4` into the active specialist map.
- `v4` already contributes visible specialist geography, but replay remains closed until the first single-lane choice is made.
## V1.2 update
- `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 601919` is now formally closed as an opening-led first lane, not a carry breakthrough.
- The checked late window did not produce a clean persistence edge, so the second `v4` lane remains closed.
- `V1.2` still primarily bottlenecks on missing carry row diversity rather than lack of active substrates.
## V1.2 update
- Added a deferred `catalyst persistence` context hypothesis branch for testing whether opening-led lanes turn into carry-led lanes only under sustained external catalysts.
- The branch is now documented in `PROJECT_LIMITATION/61_CATALYST_CARRY_CONTEXT_HYPOTHESIS_PLAN.md`.
- It remains report-only and does not change the current main bottleneck, which is still missing carry row diversity.
## V1.2 update
- Froze `catalyst_event_registry_schema_v1` as a deferred context branch for testing whether source authority, execution strength, rumor risk, consolidation days, and reacceleration help separate opening-led lanes from carry-capable lanes.
- The schema is formalized in `reports/analysis/catalyst_event_registry_schema_v1.json` and `PROJECT_LIMITATION/62_CATALYST_EVENT_REGISTRY_SCHEMA_V1.md`.
- The branch remains report-only and does not change the current main bottleneck, which is still missing carry row diversity.
## V1.2 update
- Added a first bounded training pilot on frozen structured lane artifacts.
- `reports/analysis/v12_bounded_training_pilot_v1.json` shows that current structured observables cleanly separate `opening_led`, `persistence_led`, and `carry_row_present` in a tiny report-only nearest-centroid check.
- This supports later bounded training work, but it does not yet justify strategy-level ML or raw-news model integration.
## V1.2 update
- `v12_training_readiness_check_v1.json` now confirms that the first bounded training pilot is informative but still too small to justify a larger model step.
- The current bottleneck is unchanged: carry rows are still thin and duplicated.
- Strategy-level ML and news-branch training both remain closed.

Training branch status now includes two additional bounded artifacts:
- [65_V12_TRAINING_SAMPLE_EXPANSION_DESIGN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/65_V12_TRAINING_SAMPLE_EXPANSION_DESIGN_V1.md)
- [66_V12_TRAINING_SAMPLE_MANIFEST_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/66_V12_TRAINING_SAMPLE_MANIFEST_V1.md)

Current reading:
- opening-led samples are sufficient for the current micro branch
- clean persistence rows and true carry rows are the only approved expansion targets
- relabelling neighboring factor families into the carry class remains closed

The training branch now also has an operational binding gate:
- [67_V12_TRAINING_SAMPLE_BINDING_GATE_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/67_V12_TRAINING_SAMPLE_BINDING_GATE_V1.md)
- [v12_training_sample_binding_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_sample_binding_gate_v1.json)

Current reading:
- current `v3` and `v4` opening-led first lanes remain outside the training sample
- future clean persistence rows and future true carry rows remain the only approved binding sources

The training branch now also has a per-lane intake check:
- [68_V12_TRAINING_LANE_BINDING_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/68_V12_TRAINING_LANE_BINDING_CHECK_V1.md)
- [v12_training_lane_binding_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_training_lane_binding_check_v1.json)

Current reading:
- current `v3` and `v4` first lanes are rejected as training additions because they are opening-led
- the next valid training additions must still come from future clean persistence rows or future true carry rows

The catalyst branch now also has a bounded sample seed:
- [69_CATALYST_EVENT_REGISTRY_SEED_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/69_CATALYST_EVENT_REGISTRY_SEED_V1.md)
- [catalyst_event_registry_seed_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_seed_v1.json)

Current reading:
- the catalyst branch now starts from a balanced 2/2/2 lane sample
- the next step is filling event-level fields for this bounded sample, not widening into a full news pipeline

The catalyst branch now also has a bounded sample seed:
- [69_CATALYST_EVENT_REGISTRY_SEED_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/69_CATALYST_EVENT_REGISTRY_SEED_V1.md)
- [catalyst_event_registry_seed_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_seed_v1.json)

Current reading:
- the catalyst branch now starts from a balanced 2/2/2 lane sample
- the next step is filling event-level fields for this bounded sample, not widening into a full news pipeline

The catalyst branch now also has a first bounded fill artifact:
- [70_CATALYST_EVENT_REGISTRY_FILL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/70_CATALYST_EVENT_REGISTRY_FILL_V1.md)
- [catalyst_event_registry_fill_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_fill_v1.json)

Current reading:
- all 6 seeded rows now have a market-context fill
- 4 rows currently map to theme scope and 2 to sector scope
- official source authority remains a later manual or semi-manual fill layer

The catalyst branch now also has a partial source layer:
- [71_CATALYST_EVENT_REGISTRY_SOURCE_FILL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/71_CATALYST_EVENT_REGISTRY_SOURCE_FILL_V1.md)
- [72_CATALYST_SOURCE_REFERENCES_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/72_CATALYST_SOURCE_REFERENCES_V1.md)
- [catalyst_event_registry_source_fill_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_event_registry_source_fill_v1.json)

Current reading:
- 5 seeded rows now have official or high-trust source context
- 1 row remains explicitly unresolved
- the branch is now ready for a first bounded catalyst-context audit

The catalyst branch now also has its first bounded audit:
- [73_CATALYST_CONTEXT_AUDIT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/73_CATALYST_CONTEXT_AUDIT_V1.md)
- [catalyst_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_context_audit_v1.json)

Current reading:
- opening rows currently stay in `single_pulse`
- persistence rows currently cluster in `multi_day_reinforcement`
- carry rows currently cluster in `policy_followthrough`
- the branch stays report-only for now

The catalyst branch now also has:
- [73_CATALYST_CONTEXT_AUDIT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/73_CATALYST_CONTEXT_AUDIT_V1.md)
- [74_V12_CATALYST_BRANCH_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/74_V12_CATALYST_BRANCH_PHASE_CHECK_V1.md)
- [catalyst_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/catalyst_context_audit_v1.json)
- [v12_catalyst_branch_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_catalyst_branch_phase_check_v1.json)

Current reading:
- the catalyst branch shows directional context separation
- it remains active but report-only
- it does not replace the main V1.2 bottleneck of missing carry row diversity

The mainline now also has a frozen carry-row hunting strategy:
- [75_V12_CARRY_ROW_HUNTING_STRATEGY_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/75_V12_CARRY_ROW_HUNTING_STRATEGY_V1.md)
- [v12_carry_row_hunting_strategy_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_carry_row_hunting_strategy_v1.json)

Current reading:
- stay inside the existing `v4` refresh
- do not widen replay
- the next single-symbol carry hunt target is `000725`
## 2026-03-30 Update: 000725 carry-row hunt closed inactive
- Added `PROJECT_LIMITATION/76_V12_CARRY_ROW_HUNT_000725_V1.md`.
- Added `reports/analysis/market_v4_q2_symbol_hunt_acceptance_000725_v1.json`.
- `000725` does not change the carry reading: zero pnl divergence, no opening edge, no persistence edge.
- The next bounded single-symbol hunt should move to `600703`.
## 2026-03-30 Update: 600703 carry-row hunt closed inactive
- Added `PROJECT_LIMITATION/77_V12_CARRY_ROW_HUNT_600703_V1.md`.
- Added `reports/analysis/market_v4_q2_symbol_hunt_acceptance_600703_v1.json`.
- `600703` does not change the carry reading: zero pnl divergence, no opening edge, no persistence edge.
- The next bounded single-symbol hunt should move to `600150`.
## 2026-03-30 Update: 600150 carry-row hunt closed inactive
- Added `PROJECT_LIMITATION/78_V12_CARRY_ROW_HUNT_600150_V1.md`.
- Added `reports/analysis/market_v4_q2_symbol_hunt_acceptance_600150_v1.json`.
- `600150` does not change the carry reading: zero pnl divergence, no opening edge, no persistence edge.
- The next bounded single-symbol hunt should move to `601127`.
## 2026-03-30 Update: 601127 carry-row hunt closed inactive
- Added `PROJECT_LIMITATION/79_V12_CARRY_ROW_HUNT_601127_V1.md`.
- Added `reports/analysis/market_v4_q2_symbol_hunt_acceptance_601127_v1.json`.
- `601127` does not change the carry reading: zero pnl divergence, no opening edge, no persistence edge.
- The next correct action is a phase-level check before touching lower-priority v4 hunt tracks.
## 2026-03-30 Update: v4 q2/A high-priority hunt paused
- Added `reports/analysis/v12_v4_hunt_phase_check_v1.json`.
- The current `v4 / q2 / A` hunt has exhausted its checked high-priority tracks without surfacing an active carry-supporting lane.
- The next correct action is a reassessment of the current v4 hunt posture, not immediate expansion into lower-priority symbols.
## 2026-03-30 Update: v4 reassessment completed
- Added `reports/analysis/v12_v4_reassessment_v1.json`.
- `v4` remains active as a substrate, but its checked `q2 / A` high-priority hunt region is locally exhausted.
- The next correct action is a higher-level `V1.2` decision, not more local `v4` replay.
## 2026-03-30 Update: V1.2 returns to next refresh prep
- Added `reports/analysis/v12_batch_substrate_decision_v1.json`.
- Added `PROJECT_LIMITATION/82_V12_BATCH_SUBSTRATE_DECISION_V1.md`.
- Current reading: do not reopen local `v3` or `v4` replay; instead prepare the next refresh batch for carry-row diversity.
## 2026-03-30 Update: v5 refresh entry prepared
- Added `reports/analysis/v12_next_refresh_entry_v2.json`.
- Added `PROJECT_LIMITATION/83_V12_NEXT_REFRESH_ENTRY_V2.md`.
- Current reading: prepare `market_research_v5_carry_row_diversity_refresh` as a `criteria_first_true_carry_plus_clean_persistence_refresh` batch.
- Local `v3/v4` replay remains closed.
## 2026-03-30 Update: v5 criteria frozen
- Added `reports/analysis/v12_v5_refresh_criteria_v1.json`.
- Added `PROJECT_LIMITATION/84_V12_V5_REFRESH_CRITERIA_V1.md`.
- Current reading: `market_research_v5_carry_row_diversity_refresh` is a `training-gap-aware` refresh targeting true carry rows first and clean persistence rows second.
## 2026-03-30 Update: v5 manifest ready
- Added `reports/analysis/market_research_v5_carry_row_diversity_refresh_manifest_v1.json`.
- Added `PROJECT_LIMITATION/85_MARKET_RESEARCH_V5_CARRY_ROW_DIVERSITY_REFRESH_PLAN.md`.
- Current reading: `market_research_v5_carry_row_diversity_refresh` is ready to bootstrap with `4` new symbols across `true_carry_row` and `clean_persistence_row` targets.
- `market_research_v5_carry_row_diversity_refresh` is now fully bootstrapped (`baseline_ready = true`), validated in the eight-pack `time_slice_validation_v9` run (`reports/20260330T041451Z_b6297292_comparison.json`), and included in `reports/analysis/specialist_alpha_analysis_v8.json`.
- Added long-horizon autonomy governance: [86_LONG_HORIZON_AUTONOMY_POLICY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/86_LONG_HORIZON_AUTONOMY_POLICY.md)
- `market_research_v5_carry_row_diversity_refresh` first lane (`002273 / 2024_q2 / mainline_trend_b`) closes as opening-led, not a carry breakthrough: [market_v5_q2_first_lane_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v5_q2_first_lane_acceptance_v1.json)
- `market_research_v5_carry_row_diversity_refresh` is now locally exhausted as a bounded refresh. The final true-carry probe `000099 / 2024_q2 / mainline_trend_b` closes as opening-led, not true carry: [market_v5_q2_last_carry_probe_acceptance_000099_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v5_q2_last_carry_probe_acceptance_000099_v1.json)
- `V1.2` therefore stays constrained by `carry_row_diversity_gap`, and the next legal action has been frozen as a new entry rather than a widened replay: [v12_next_refresh_entry_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_entry_v3.json)- `market_research_v6_catalyst_supported_carry_persistence_refresh` is now manifest-ready: [market_research_v6_catalyst_supported_carry_persistence_refresh_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_research_v6_catalyst_supported_carry_persistence_refresh_manifest_v1.json)
- `v6` keeps the primary objective unchanged (`2` true carry rows plus `2` clean persistence rows) while using catalyst context only as bounded symbol-selection support.
### 2026-03-30 update
- `market_research_v6_catalyst_supported_carry_persistence_refresh` is active and baseline-ready.
- Its first bounded lane (`600118 / 2024_q3 / mainline_trend_c`) closed as opening-led, not true carry.
- `v12_v6_first_lane_phase_check_v1` and `v12_v6_reassessment_v1` now block local second-lane widening while keeping `v6` as an active substrate.

### 2026-03-30 waiting-state update
- `V1.2` has entered explicit waiting state after `v6` local actions exhausted without changing the primary bottleneck.
- No `v7` branch was opened; valid next actions are now limited to waiting-state summaries and restart-entry preservation until a new trigger or owner phase switch appears.

### 2026-03-30 V1.3 update
- `V1.3 Catalyst And Concept Context Infrastructure` is now open.
- Early V1.3 artifacts are bounded and replay-independent: concept mapping inventory, concept seed, concept source fill, concept context audit, and phase check.
- Current V1.3 posture is `keep_v13_active_but_bounded_as_context_infrastructure`.

### 2026-03-30 concept confidence update
- `V1.3` now includes frozen concept mapping confidence and symbol-link rules.
- Concept mappings must pass source-quality and market-confirmation gates before they can be treated as bounded research context.

### 2026-03-30 concept registry update
- `V1.3` now includes a bounded provisional concept registry.
- Current concept rows are usable for bounded context but remain `provisional_market_confirmed_indirect` until manual symbol-link mode assignment is completed.

### 2026-03-30 concept registry reclassification update
- V1.3 now includes bounded manual symbol-link proof and a reclassified concept registry.
- Current split: 3 core_confirmed rows and 1 market_confirmed_indirect row.
- Bounded usage rules are frozen: concept rows can support bounded research context, but none can enter the strategy mainline.
- V1.3 has therefore closed as bounded context-infrastructure success and now sits in explicit waiting state pending a new owner phase switch or trigger.
### 2026-03-30 V1.4 update
- V1.4 Context Consumption Pilot is now open.
- The first bounded context consumption protocol is frozen and remains report-only.
- V1.4 can consume bounded concept and catalyst context, but it still cannot integrate into the strategy mainline or formal model work.
### 2026-03-30 V1.4 context feature schema update
- V1.4 now includes a bounded report-only context feature schema.
- The next legal step is a bounded discrimination check; strategy integration and formal model work remain disallowed.
### 2026-03-30 V1.4 discrimination and closure update
- V1.4 completed a bounded report-only discrimination cycle.
- Stable directional separation is present, but promotion and strategy integration remain disallowed.
- V1.4 therefore closes as bounded context-consumption success and now sits in explicit waiting state.
### 2026-03-30 V1.5 update
- `V1.5 Retained-Feature Candidacy Review` is now open.
- The first bounded candidacy-review protocol is frozen.
- `V1.5` may review report-only context features for candidacy, but promotion and strategy integration remain disallowed.
### 2026-03-30 V1.5 review and closure update
- `V1.5` completed a bounded retained-feature candidacy review.
- Current result: `4` provisional candidacy features, `1` hold-for-more-evidence feature, `0` promotions.
- `V1.5` therefore closes as bounded candidacy-review success and now sits in explicit waiting state.
### 2026-03-30 V1.6 update
- `V1.6 Provisional Candidacy Stability Review` is now open.
- The first bounded stability-review protocol is frozen.
- `V1.6` may review provisional candidacy stability, but promotion and strategy integration remain disallowed.
### 2026-03-30 V1.6 review and closure update
- `V1.6` completed a bounded provisional-candidacy stability review.
- Current result: `4` features continue provisional candidacy, `0` hold, `0` drop, and `0` promotions.
- `V1.6` therefore closes as bounded stability-review success and now sits in explicit waiting state.### 2026-03-30 V1.7 update
- `V1.7 Promotion-Evidence Generation` is now open.
- The first bounded promotion-evidence protocol is frozen.
- `V1.7` may define what new evidence is required to change promotion judgment, but it still cannot promote features, integrate into strategy, or open local-model work.
### 2026-03-30 V1.7 review and closure update
- `V1.7` completed a bounded promotion-evidence generation cycle.
- Current result: `4` features remain below promotion threshold, but each now has explicit bounded shortfalls and minimum evidence paths.
- `V1.7` therefore closes as bounded promotion-evidence generation success and now sits in explicit waiting state.
### 2026-03-30 V1.8A update
- `V1.8A Sample Breadth Expansion` is now open.
- The first bounded sample-breadth protocol is frozen.
- `V1.8A` currently targets only `single_pulse_support` and `policy_followthrough_support`, and it still cannot promote features, integrate into strategy, or widen into generic replay growth.
### 2026-03-30 V1.8A review and closure update
- `V1.8A` completed a bounded sample-breadth expansion cycle.
- Current result: `2` target features now have explicit lawful breadth-entry designs, but sample collection, promotion, and strategy integration remain disallowed.
- `V1.8A` therefore closes as bounded sample-breadth expansion success and now sits in explicit waiting state.
### 2026-03-30 V1.8B review and closure update
- `V1.8B` completed a bounded breadth sample admission-gate cycle.
- Current result: both breadth-target features now have explicit lawful admission gates, but sample collection, promotion, and strategy integration remain disallowed.
- `V1.8B` therefore closes as bounded admission-gate success and now sits in explicit waiting state.
### 2026-03-30 V1.8C review and closure update
- `V1.8C` completed a screened bounded collection cycle.
- Current result: `5` lawful new breadth-evidence cases were admitted across the two target features, with `0` sample-limit breaches.
- `V1.8C` therefore closes as bounded screened collection success and now sits in explicit waiting state.
### 2026-03-30 V1.9 review and closure update
- `V1.9 Breadth Evidence Re-Review` completed a bounded re-review cycle after `V1.8C` collection.
- Current result: `single_pulse_support` materially reduced its breadth gap and shifted primary shortfall to `non_redundancy_stress_gap`; `policy_followthrough_support` improved only partially and remains primarily breadth-limited.
- `V1.9` therefore closes as bounded breadth-evidence re-review success and now sits in explicit waiting state.
### 2026-03-30 V1.10A review and closure update
- `V1.10A Policy Followthrough Cross-Family Breadth Probe` completed as a one-off owner-led probe.
- Current result: the bounded pool exposed `2` visible policy-followthrough candidates and `0` admissible cross-family cases; both visible candidates remained inside the current `300750` anchor family.
- `V1.10A` therefore closes as successful negative probe and now sits in explicit waiting state, with no automatic `V1.10B+`.
### 2026-03-30 Governance tuning update
- The autonomy policy now distinguishes `exploration_layer` from `admission_and_mainline_layer`.
- Design-first memos, acquisition plans, feature hypotheses, trigger-source maps, and time-boxed exception phases are now explicitly legal at the exploration layer.
- Promotion, validation, retained-feature admission, and strategy-mainline integration remain strict and unchanged.
### 2026-03-30 Governance upgrade
- Strengthened the long-horizon autonomy policy to block same-pool micro-phase repetition.
- Added `Solution Shift Mode`, which forces future stalled branches to output a memo choosing between data acquisition, feature hypothesis, method change, or freeze, instead of continuing bounded review loops.
### 2026-03-30 V1.11 review and closure update
- `V1.11 Sustained Catalyst Evidence Acquisition Infrastructure` completed as an exploration-layer infrastructure phase.
- Current result: the project now has a frozen acquisition basis for future catalyst evidence, including acquisition scope, source hierarchy, admissibility, family novelty rules, point-in-time recording rules, refresh cadence, and a bounded first-pilot plan.
- `V1.11` therefore closes as sustained acquisition infrastructure success and now sits in explicit waiting state; the bounded first pilot is prepared but not auto-opened.
### 2026-03-30 V1.11A review and closure update
- `V1.11A Bounded First Catalyst Acquisition Pilot` completed as the first owner-reviewed execution phase on top of the frozen `V1.11` infrastructure.
- Current result: the pilot screened `5` resolved catalyst rows and admitted `2` new non-anchor candidates (`000155`, `300502`) with `0` cap breaches, validating the acquisition path under bounded rules.
- Important boundary: this did **not** create direct new `policy_followthrough` breadth evidence and did **not** open retained-feature promotion or strategy integration.
- `V1.11A` therefore closes as bounded first acquisition pilot success and now sits in explicit waiting state with no automatic follow-on.
### 2026-03-30 V1.12 review and closure update
- `V1.12 Single Price-Cycle Experimental Training Pilot` completed as a bounded training-definition phase.
- Current result: the project froze one first experiment rather than widening immediately: `earnings_transmission_carry` with `optical_link_price_and_demand_upcycle` as the pilot archetype.
- The first training grammar is now explicit: one sample unit (`symbol_day_within_one_price_cycle_window`), four feature blocks (catalyst state, earnings transmission bridge, expectation gap, price confirmation), three label targets, and time-split/report-only validation rules.
- `V1.12` therefore closes as single-cycle training definition success and now sits in explicit waiting state; bounded pilot data assembly is prepared but not auto-opened.
### 2026-03-30 V1.12A review and closure update
- `V1.12A Bounded Pilot Data Assembly` completed as the first owner-correction-ready pilot dataset draft.
- Current result: the first bounded object pool contains `300502` 新易盛, `300308` 中际旭创, and `300394` 天孚通信, with explicit correction slots for object inclusion, role guesses, cycle windows, and owner notes.
- Important boundary: this is still a draft review sheet, not a trained dataset, and training remains blocked until owner correction happens.
- `V1.12A` therefore closes as owner-correction-ready pilot data assembly success and now sits in explicit waiting state.
### 2026-03-30 V1.12A owner-correction integration update
- The first owner correction has been integrated into the pilot draft.
- Current result: `300308` 中际旭创 now carries an explicit multi-stage cycle sketch and becomes the first benchmark row inside the partial pilot dataset draft.
- Remaining gap: `300502` 新易盛 and `300394` 天孚通信 still need cycle-window correction before the pilot dataset can move to the next labeling step.
### 2026-03-30 V1.12A price-cycle inference update
- A first price-structure inference pass has now been added for the two unresolved symbols.
- Current result: `300502` 新易盛 and `300394` 天孚通信 now carry coarse cycle-window drafts derived from daily bars plus weekly/monthly aggregation, while `300308` remains the owner-corrected benchmark anchor.
- Important boundary: this is still a calibration draft only. Training remains blocked until the owner confirms or corrects these two inferred windows.
### 2026-03-30 V1.12A unified calibration draft update
- `300308` is no longer treated as a special owner-only anchor.
- Current result: all three pilot symbols now carry cycle-window drafts generated under one unified price-structure method; the older `300308` owner window is kept only as a calibration reference.
- Important boundary: this is still a calibration draft only. Training remains blocked until the owner confirms or corrects the unified draft.
### 2026-03-30 V1.12B first trainable pilot dataset and baseline update
- The unified `V1.12A` draft has now been accepted and frozen into the first trainable optical-link pilot dataset.
- The project now has its first report-only time-split baseline readout on that dataset: `2238` samples, `3` carry-outcome classes, `0.4509` test accuracy.
- This is the first executable training-chain checkpoint for the new single-cycle experiment, but it still does **not** authorize strategy training, black-box deployment, or wider object expansion.
### 2026-03-30 V1.12C hotspot review and sidecar-protocol update
- The first baseline error map is now explicit: the current model is too optimistic in `major_markup` and `high_level_consolidation`.
- The project now has a first frozen black-box sidecar comparison basis on the same dataset, same labels, and same time split as `V1.12B`.
- This still does **not** authorize sidecar deployment; it only prepares the next bounded comparison experiment.
### 2026-03-30 V1.12D first same-dataset black-box sidecar result
- The first black-box sidecar comparison has now been executed on the exact same optical-link pilot dataset and time split as `V1.12B`.
- `hist_gradient_boosting_classifier` is the current best sidecar: test accuracy improved from `0.4509` to `0.558`, and optimistic carry false positives fell sharply in the known hotspot stages.
- This is the first evidence that a bounded non-linear sidecar may capture structure the simple baseline misses, but it remains strictly **report-only** and does **not** authorize deployment.
### 2026-03-30 V1.12E GBDT attribution review result
- The first sidecar gain is now explained at block level instead of only by leaderboard score.
- The current most useful block is `catalyst_state`: removing it leaves `major_markup` false positives flat but blows up `high_level_consolidation` false positives from `1` to `53`.
- This shifts the next decision basis toward feature/label refinement around late-stage catalyst persistence rather than immediate model-family widening or deployment.
### 2026-03-30 V1.12F refinement-design result
- The next immediate problem is now classified more cleanly: it is **not** primarily a data-gap issue and **not** primarily a catalyst-weight issue.
- The current primary bottleneck is `feature_definition_or_non_redundancy_gap`.
- The next bounded refinement should target `catalyst_state` semantics first, especially:
  - freshness
  - cross-day persistence
  - breadth confirmation
### 2026-03-30 V1.12G semantic-v2 rerun result
- The catalyst-state refinement path has now been executed on the same frozen optical-link pilot without widening scope or touching deployment posture.
- Three new semantic fields were added: `catalyst_freshness_state`, `cross_day_catalyst_persistence`, and `theme_breadth_confirmation_proxy`.
- The bounded rerun is directionally positive in both models:
  - baseline accuracy: `0.4509 -> 0.4628`
  - GBDT accuracy: `0.558 -> 0.5655`
- The real gain is phase-specific rather than global. `high_level_consolidation` optimistic carry false positives fell:
  - baseline: `46 -> 34`
  - GBDT: `1 -> 0`
- Current posture: preserve this semantic-v2 delta for owner review before any label split, dataset widening, or stronger model escalation.
### 2026-03-30 Subagent exploration posture update
- The project now has a frozen subagent exploration policy and first bounded backlog.
- Subagents are **not** treated as replacement thinkers for the mainline. They are reserved for repetitive, low-risk exploratory support under fixed data, fixed rules, and fixed outputs.
- Current lawful ready-now tasks are narrow:
  - hotspot bucketization for `high_level_consolidation` / `major_markup`
  - bounded ablation on the three semantic catalyst-state fields
- Current posture remains conservative: no label rewrite, no phase switching, no open-ended model search, and no automatic dataset growth through subagent use.
### 2026-03-30 Subagent drafting/structuring refinement
- The subagent role is now defined more precisely as four task types:
  - exploration
  - drafting
  - structuring
  - execution
- This matters because some valuable work is not pure exploration. Candidate substate discovery for `high_level_consolidation` is now explicitly lawful as a review-only drafting/structuring task.
- Review cadence is now typed rather than uniform:
  - `structuring` / `execution`: review by bounded volume or time
  - `drafting` / `exploration`: review by bounded thematic stage
- No candidate draft may directly become a formal label, schema, or phase decision.
### 2026-03-30 V1.12I label-refinement review protocol
- The project now has a frozen review standard for deciding whether a candidate stage split deserves bounded follow-up.
- This phase does **not** split labels. It only defines what future candidate buckets must prove:
  - distinct error behavior
  - distinct semantic-v2 profiles
  - review value without excessive fragmentation
- Current posture: review-only governance success, now waiting for candidate-structure evaluation.
### 2026-03-30 First subagent hotspot bucketization result
- The first lawful subagent output is now usable.
- `high_level_consolidation` and `major_markup` misreads are not random; they can be organized into `8` reviewable buckets.
- Current posture: still no automatic label split, but the project now has both:
  - a candidate-structure draft
  - a frozen protocol for judging that draft
### 2026-03-30 V1.12J candidate-structure review result
- The first candidate-structure draft has now been judged against the frozen `V1.12I` protocol.
- Result:
  - `high_level_consolidation`: eligible for bounded drafting follow-up
  - `major_markup`: keep on the feature side for now
  - no formal label split authorized
- This sharply narrows the next legal move. If any bounded label-adjacent follow-up is opened, it should stay inside `high_level_consolidation` only.
### 2026-03-30 V1.12K high-level consolidation candidate-substate draft
- The bounded follow-up has now been executed only inside `high_level_consolidation`.
- Current result:
  - `3` review-only candidate substates drafted
  - `1` thin bucket excluded
  - still no formal label split
- This means the project now has a concrete candidate-substate draft to review, rather than only bucket-level structure.
### 2026-03-30 Subagent hotspot bucketization result
- The first bounded subagent task has now completed: hotspot bucketization for `high_level_consolidation` and `major_markup`.
- Result shape:
  - `8` total buckets
  - `306` target-stage rows considered
  - `255` baseline misreads
  - `200` GBDT misreads
  - `149` rows misread by both
- The buckets are reviewable and stage-specific, but still coarse enough to be useful only as a structuring draft. They do not change labels or phase judgment.
### 2026-03-30 V1.12L candidate-substate owner review
- The `V1.12K` draft has now been reduced through owner-level review rather than widened immediately.
- Result:
  - `2` preserved review-only candidate substates
  - `1` mixed inner-drafting target
  - `0` formal label splits
- Current posture:
  - keep the two preserved review-only substates frozen
  - keep the mixed stall cluster only as an optional future target
  - do not auto-open any further drafting step
### 2026-03-30 V1.12M mixed stall inner drafting
- The owner then explicitly reopened only the mixed high-level stall target for one bounded inner pass.
- Result:
  - `2` preserved review-only inner candidates
  - `1` unresolved residue
  - `0` formal label splits
- The most useful new pocket is `candidate_quiet_contraction_stall_recoverable`, which is carry-heavy even though price and relative strength remain soft.
- Current posture:
  - keep the inner draft frozen for review
  - do not auto-open schema change
  - do not auto-open further follow-up
### 2026-03-30 V1.12N review-only shadow rerun
- The inner-draft pieces from `V1.12M` were then tested as review-only shadow features on the same frozen pilot.
- Result:
  - baseline: `0.4628 -> 0.4628`
  - GBDT: `0.5655 -> 0.5655`
  - stage-specific false positives unchanged
- Interpretation:
  - the inner draft is currently descriptive, not incrementally predictive
  - this is a useful negative result
  - no feature promotion or label action is justified from this rerun
### 2026-03-30 V1.13 theme-diffusion carry reentry
- After `V1.12N`, the project formally stops treating the `high_level_consolidation` inner-refinement line as a predictive frontier.
- `theme_diffusion_carry` is now selected as the next higher-leverage carry family.
- Frozen seed archetypes:
- `commercial_space_mainline`
- `stablecoin_theme_cycle`
- `low_altitude_economy_cycle`
- Current posture:
  - schema-first
  - review-only
  - no automatic model escalation
### 2026-03-30 V1.13F commercial-space pilot data assembly
- The first lawful downstream pilot is now concrete rather than abstract.
- A bounded draft object pool has been frozen for `commercial_space_mainline`.
- Current draft objects:
  - `002085`
  - `000738`
  - `600118`
- Current reading:
  - one dense leader seed
  - two weaker owner-correctable draft objects
- Current posture:
  - owner review required before label freeze
  - no auto training
  - no auto archetype widening
### 2026-03-30 V1.13G commercial-space deep archetype scope
- The owner then widened the commercial-space line from a small pilot correction task into a deeper archetype study.
- The project now freezes this as a lawful bounded study scope rather than jumping straight into training.
- Current structure:
  - `3` validated local seeds
  - `16` owner-named candidates
  - `8` bounded study dimensions
- Current posture:
  - deep-study scope is open and preserved
  - training still closed
  - label freeze still closed
### 2026-03-30 V1.12O optical-link deep archetype scope
- The owner then reprioritized back to `CPO / optical-link` before commercial-space pilot widening.
- The project now freezes the optical-link line as a lawful deep-study archetype instead of returning to the already-closed `high_level_consolidation` refinement pocket.
- Current structure:
  - `3` validated local seeds
  - `6` review-only adjacent candidates
  - `8` bounded study dimensions
- Current posture:
  - automatic dataset widening closed
  - automatic training closed
  - next lawful move is bounded adjacent-candidate validation or bounded cohort-widening review
### 2026-03-30 V1.12P CPO full-cycle information registry
- The CPO line now has a broad review-first registry rather than only a narrow three-name training pilot.
- Current structure:
  - `6` information layers
  - `20` cohort rows
  - `10` source anchors
  - `4` explicit remaining gaps
- Current posture:
  - omission control prioritized over early purity
  - training still closed
  - feature promotion still closed
  - next lawful move is owner discussion on missing information, then bounded adjacent-candidate validation

### 2026-03-30 V1.12Q CPO registry schema hardening
- `V1.12Q` froze a harder CPO full-cycle registry schema with `6` cycle stages, `9` information layers, `5` buckets, and `38` review-first feature slots.
- Parallel collection is now bounded by schema: first draft batch preserved `14` adjacent official anchors, `6` chronology-source anchors, and `10` future catalyst-calendar anchors.
- Training, feature promotion, execution, and signal generation remain closed.

### 2026-03-30 V1.12R adjacent cohort validation
- `V1.12R` reviewed `14` adjacent/branch-extension CPO rows using the first official-anchor batch.
- `5` rows were preserved as bounded validated review assets; `9` remain pending role-split or branch cleanup.
- Training and feature promotion remain closed; chronology normalization is next.

### 2026-03-30 V1.12S CPO chronology normalization
- `V1.12S` normalized the CPO timing surface into `9` chronology segments, `10` timing-gap rows, and `10` normalized catalyst-calendar anchors.
- Training and feature promotion remain closed; spillover truth-check is the next cleaning step.

### 2026-03-30 V1.12T CPO spillover truth-check
- `V1.12T` reviewed `3` mixed-relevance CPO spillover rows after chronology normalization.
- All `3` rows were preserved; `2` are now explicit A-share spillover-factor candidates and `1` is retained as a weaker pure name-bonus / board-follow row.
- Training and feature promotion remain closed; the next lawful move is owner review of overall CPO foundation completeness and research readiness.

### 2026-03-30 V1.12U CPO foundation completeness and research-readiness review
- `V1.12U` froze the explicit readiness judgment for the cleaned CPO information foundation.
- The foundation is now considered normed and complete enough for bounded deep research, but still not complete enough for formal training.
- `4` material gaps remain open: unresolved adjacent role splits, missing daily board chronology series, future catalyst calendar operationalization, and spillover factor truth-testing.

### 2026-03-30 V1.12V CPO daily board chronology operationalization
- `V1.12V` operationalized the board chronology gap into a bounded daily table target.
- The phase froze `5` daily series, `12` operational columns, and `4` source-precedence tiers.
- Training and feature promotion remain closed; the board chronology layer is now operationalized but not fully backfilled.

### 2026-03-30 V1.12W CPO future catalyst calendar operationalization
- `V1.12W` operationalized the future-visible catalyst gap into a bounded recurring calendar target.
- The phase froze `10` recurring anchors, `12` operational columns, and `4` source-precedence tiers.
- Training and feature promotion remain closed; the future catalyst calendar is now operationalized but not fully maintained.

### 2026-03-30 V1.12X CPO spillover sidecar probe
- `V1.12X` reviewed the `3` preserved spillover rows with a bounded sidecar posture.
- `2` rows remain bounded A-share spillover-factor candidates and `1` remains weaker name-bonus / board-follow memory only.
- Training and feature promotion remain closed; the spillover layer now has explicit candidate-vs-memory separation.

### 2026-03-30 V1.12Y CPO adjacent role-split sidecar probe
- `V1.12Y` reviewed the `9` unresolved adjacent rows from `V1.12R` with a bounded sidecar posture.
- `6` rows are now split-ready review assets and `3` remain still-pending mixed rows.
- Training and feature promotion remain closed; the adjacent layer is now materially cleaner.

### 2026-03-30 V1.12Z CPO bounded cycle reconstruction entry
- `V1.12Z` opened the first bounded downstream experiment for the cleaned CPO line.
- The phase froze an ambiguity-preserving cycle-reconstruction protocol using the cleaned adjacent and spillover layers.
- Training and feature promotion remain closed; the next lawful move is the bounded reconstruction pass itself.
### 2026-03-30 CPO research-process record
- Added a reusable process record for the whole `V1.12P -> V1.12Z` CPO foundation chain:
  - [323_CPO_DATA_COLLECTION_AND_RESEARCH_PROCESS_RECORD_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/323_CPO_DATA_COLLECTION_AND_RESEARCH_PROCESS_RECORD_V1.md)
  - [v112_cpo_data_collection_and_research_process_record_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112_cpo_data_collection_and_research_process_record_v1.json)
- This record is intended to support paper writing and later sector transfer, especially around:
  - omission-control ordering
  - review-only preservation of noise and spillover
  - bounded subagent usage
  - experiment-entry gating

### 2026-03-30 V1.12Z operational charter
- Added:
  - [324_V112Z_OPERATIONAL_CHARTER.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/324_V112Z_OPERATIONAL_CHARTER.md)
  - [325_V112Z_OPERATIONAL_CHARTER_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/325_V112Z_OPERATIONAL_CHARTER_V1.md)
  - [v112z_operational_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112z_operational_charter_v1.json)
- This freezes the current execution doctrine for the CPO line:
  - cycle absorption first
  - black-box as primary discovery layer
  - white-box as guardrail
  - owner-facing narrative as mandatory acceptance layer

### 2026-03-30 V1.12Z report-only model payoff probe
- Added:
  - [326_V112Z_REPORT_ONLY_MODEL_PAYOFF_PROBE.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/326_V112Z_REPORT_ONLY_MODEL_PAYOFF_PROBE.md)
  - [327_V112Z_MODEL_PAYOFF_PROBE_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/327_V112Z_MODEL_PAYOFF_PROBE_V1.md)
  - [v112z_model_payoff_probe_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112z_model_payoff_probe_v1.json)
- Current same-dataset payoff readout:
  - guardrail baseline remains useful
  - `hist_gradient_boosting_classifier_v2` is currently the strongest report-only model by bounded non-overlap trade quality

### 2026-03-30 V1.12Z bounded cycle reconstruction pass
- Added:
  - [328_V112Z_BOUNDED_CYCLE_RECONSTRUCTION_PASS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/328_V112Z_BOUNDED_CYCLE_RECONSTRUCTION_PASS.md)
  - [329_V112Z_BOUNDED_CYCLE_RECONSTRUCTION_PASS_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/329_V112Z_BOUNDED_CYCLE_RECONSTRUCTION_PASS_V1.md)
  - [v112z_bounded_cycle_reconstruction_pass_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112z_bounded_cycle_reconstruction_pass_v1.json)
- Current result:
  - the CPO line is now reconstructable as a multi-wave cycle with explicit role transitions and spillover overlays
  - residual ambiguity remains explicit
  - bounded cohort mapping or bounded labeling review is now supportable
  - formal training and execution remain closed

### 2026-03-30 V1.12AA CPO bounded cohort map
- Added:
  - [330_V112AA_CPO_BOUNDED_COHORT_MAP.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/330_V112AA_CPO_BOUNDED_COHORT_MAP.md)
  - [331_V112AA_CPO_BOUNDED_COHORT_MAP_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/331_V112AA_CPO_BOUNDED_COHORT_MAP_V1.md)
  - [v112aa_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aa_phase_charter_v1.json)
  - [v112aa_cpo_bounded_cohort_map_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json)
  - [v112aa_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aa_phase_check_v1.json)
  - [v112aa_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aa_phase_closure_check_v1.json)
- Current result:
  - the CPO line now has a frozen object-role-time matrix
  - later admissibility is explicit
  - spillover remains outside core truth
  - pending rows remain explicit
  - labeling and training remain closed

### 2026-03-30 V1.12AB CPO bounded labeling review
- Added:
  - [332_V112AB_CPO_BOUNDED_LABELING_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/332_V112AB_CPO_BOUNDED_LABELING_REVIEW.md)
  - [333_V112AB_CPO_BOUNDED_LABELING_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/333_V112AB_CPO_BOUNDED_LABELING_REVIEW_V1.md)
  - [v112ab_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ab_phase_charter_v1.json)
  - [v112ab_cpo_bounded_labeling_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json)
  - [v112ab_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ab_phase_check_v1.json)
  - [v112ab_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ab_phase_closure_check_v1.json)
- Current result:
  - later labeling surfaces are explicit
  - overlay and pending rows remain outside formal truth
  - formal label freeze and training remain closed

### 2026-03-30 V1.12AC CPO unsupervised role-challenge probe
- Added:
  - [334_V112AC_UNSUPERVISED_ROLE_CHALLENGE_PROBE.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/334_V112AC_UNSUPERVISED_ROLE_CHALLENGE_PROBE.md)
  - [335_V112AC_UNSUPERVISED_ROLE_CHALLENGE_PROBE_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/335_V112AC_UNSUPERVISED_ROLE_CHALLENGE_PROBE_V1.md)
  - [336_V112AC_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/336_V112AC_PHASE_CHECK_V1.md)
  - [337_V112AC_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/337_V112AC_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ac_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ac_phase_charter_v1.json)
  - [v112ac_unsupervised_role_challenge_probe_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ac_unsupervised_role_challenge_probe_v1.json)
  - [v112ac_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ac_phase_check_v1.json)
  - [v112ac_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ac_phase_closure_check_v1.json)
- Current result:
  - the current manual role grammar is partly supported and partly challenged by latent structure
  - a clean pending quiet-window pocket exists
  - late-cycle extension and spillover still mix in data-side structure
  - clustering remains review-only and cannot legislate new formal roles

### 2026-03-30 V1.12AD CPO dynamic role-transition feature review
- Added:
  - [338_V112AD_DYNAMIC_ROLE_TRANSITION_FEATURE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/338_V112AD_DYNAMIC_ROLE_TRANSITION_FEATURE_REVIEW.md)
  - [339_V112AD_DYNAMIC_ROLE_TRANSITION_FEATURE_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/339_V112AD_DYNAMIC_ROLE_TRANSITION_FEATURE_REVIEW_V1.md)
  - [340_V112AD_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/340_V112AD_PHASE_CHECK_V1.md)
  - [341_V112AD_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/341_V112AD_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ad_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ad_phase_charter_v1.json)
  - [v112ad_dynamic_role_transition_feature_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ad_dynamic_role_transition_feature_review_v1.json)
  - [v112ad_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ad_phase_check_v1.json)
  - [v112ad_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ad_phase_closure_check_v1.json)
- Current result:
  - static role buckets have been upgraded into a bounded dynamic role-transition layer
  - role migration and role replacement risk are now explicit review features
  - governance remains closed

### 2026-03-30 V1.12AE CPO feature-brainstorm integration
- Added:
  - [342_V112AE_CPO_FEATURE_BRAINSTORM_INTEGRATION.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/342_V112AE_CPO_FEATURE_BRAINSTORM_INTEGRATION.md)
  - [343_V112AE_CPO_FEATURE_BRAINSTORM_INTEGRATION_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/343_V112AE_CPO_FEATURE_BRAINSTORM_INTEGRATION_V1.md)
  - [v112ae_feature_brainstorm_integration_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ae_feature_brainstorm_integration_v1.json)
- Current result:
  - the first multi-explorer feature brainstorm batch is now compressed into a bounded shortlist
  - strongest additions are time-geometry, role-handoff, and weak-cohort migration features
  - all outputs remain review-only

### 2026-03-30 V1.12AG CPO bounded label-draft assembly
- Added:
  - [348_V112AG_CPO_BOUNDED_LABEL_DRAFT_ASSEMBLY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/348_V112AG_CPO_BOUNDED_LABEL_DRAFT_ASSEMBLY.md)
  - [349_V112AG_CPO_BOUNDED_LABEL_DRAFT_ASSEMBLY_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/349_V112AG_CPO_BOUNDED_LABEL_DRAFT_ASSEMBLY_V1.md)
  - [350_V112AG_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/350_V112AG_PHASE_CHECK_V1.md)
  - [351_V112AG_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/351_V112AG_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ag_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ag_phase_charter_v1.json)
  - [v112ag_cpo_bounded_label_draft_assembly_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ag_cpo_bounded_label_draft_assembly_v1.json)
  - [v112ag_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ag_phase_check_v1.json)
  - [v112ag_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ag_phase_closure_check_v1.json)
- Current result:
  - the CPO draft label layer is now assembled as a bounded integrity object rather than a hidden training launch
  - major labels now have explicit family support and anti-leakage posture
  - pending, overlay-only, and confirmed-only regions remain explicitly preserved

### 2026-03-30 V1.12AH factor candidate preservation rule
- Added:
  - [352_V112AH_FACTOR_CANDIDATE_PRESERVATION_RULE.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/352_V112AH_FACTOR_CANDIDATE_PRESERVATION_RULE.md)
  - [353_V112AH_FACTOR_CANDIDATE_PRESERVATION_RULE_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/353_V112AH_FACTOR_CANDIDATE_PRESERVATION_RULE_V1.md)
  - [v112ah_factor_candidate_preservation_rule_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ah_factor_candidate_preservation_rule_v1.json)
- Current result:
  - speculative, overlay, blind-spot, and pending candidates now have an explicit preservation rule
  - future trimming must state explicit reasons rather than silently dropping weak-looking candidates

### 2026-03-30 V1.12AI CPO label-draft integrity owner review
- Added:
  - [354_V112AI_CPO_LABEL_DRAFT_INTEGRITY_OWNER_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/354_V112AI_CPO_LABEL_DRAFT_INTEGRITY_OWNER_REVIEW.md)
  - [355_V112AI_CPO_LABEL_DRAFT_INTEGRITY_OWNER_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/355_V112AI_CPO_LABEL_DRAFT_INTEGRITY_OWNER_REVIEW_V1.md)
  - [356_V112AI_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/356_V112AI_PHASE_CHECK_V1.md)
  - [357_V112AI_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/357_V112AI_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ai_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ai_phase_charter_v1.json)
  - [v112ai_cpo_label_draft_integrity_owner_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ai_cpo_label_draft_integrity_owner_review_v1.json)
  - [v112ai_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ai_phase_check_v1.json)
  - [v112ai_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ai_phase_closure_check_v1.json)
- Current result:
  - the CPO bounded label draft is now owner-tiered without any silent drop
  - only the ready and guarded labels may move into the next bounded dataset assembly step

### 2026-03-30 V1.12AJ CPO bounded label-draft dataset assembly
- Added:
  - [358_V112AJ_CPO_BOUNDED_LABEL_DRAFT_DATASET_ASSEMBLY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/358_V112AJ_CPO_BOUNDED_LABEL_DRAFT_DATASET_ASSEMBLY.md)
  - [359_V112AJ_CPO_BOUNDED_LABEL_DRAFT_DATASET_ASSEMBLY_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/359_V112AJ_CPO_BOUNDED_LABEL_DRAFT_DATASET_ASSEMBLY_V1.md)
  - [360_V112AJ_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/360_V112AJ_PHASE_CHECK_V1.md)
  - [361_V112AJ_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/361_V112AJ_PHASE_CLOSURE_CHECK_V1.md)
  - [v112aj_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aj_phase_charter_v1.json)
  - [v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aj_cpo_bounded_label_draft_dataset_assembly_v1.json)
  - [v112aj_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aj_phase_check_v1.json)
  - [v112aj_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aj_phase_closure_check_v1.json)
- Current result:
  - the first dataset-shaped CPO label draft now exists
  - truth-candidate rows and context-only rows are explicitly separated
  - review-only and confirmed-only labels remain outside draft truth

### 2026-03-30 V1.12AK CPO bounded feature binding review
- Added:
  - [362_V112AK_CPO_BOUNDED_FEATURE_BINDING_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/362_V112AK_CPO_BOUNDED_FEATURE_BINDING_REVIEW.md)
  - [363_V112AK_CPO_BOUNDED_FEATURE_BINDING_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/363_V112AK_CPO_BOUNDED_FEATURE_BINDING_REVIEW_V1.md)
  - [364_V112AK_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/364_V112AK_PHASE_CHECK_V1.md)
  - [365_V112AK_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/365_V112AK_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ak_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ak_phase_charter_v1.json)
  - [v112ak_cpo_bounded_feature_binding_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ak_cpo_bounded_feature_binding_review_v1.json)
  - [v112ak_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ak_phase_check_v1.json)
  - [v112ak_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ak_phase_closure_check_v1.json)
- Current result:
  - row-level feature binding is now explicit on the current truth-candidate set
  - not every admitted label binds meaningfully on current rows

### 2026-03-30 V1.12AL CPO bounded training readiness review
- Added:
  - [366_V112AL_CPO_BOUNDED_TRAINING_READINESS_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/366_V112AL_CPO_BOUNDED_TRAINING_READINESS_REVIEW.md)
  - [367_V112AL_CPO_BOUNDED_TRAINING_READINESS_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/367_V112AL_CPO_BOUNDED_TRAINING_READINESS_REVIEW_V1.md)
  - [368_V112AL_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/368_V112AL_PHASE_CHECK_V1.md)
  - [369_V112AL_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/369_V112AL_PHASE_CLOSURE_CHECK_V1.md)
  - [v112al_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112al_phase_charter_v1.json)
  - [v112al_cpo_bounded_training_readiness_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112al_cpo_bounded_training_readiness_review_v1.json)
  - [v112al_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112al_phase_check_v1.json)
  - [v112al_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112al_phase_closure_check_v1.json)
- Current result:
  - current CPO draft data is sufficient for an **extremely small** core-skeleton pilot
  - representative training is still not lawful
  - the current primary bottleneck is `feature_implementation`
  - the current secondary bottleneck is `row_geometry`

### 2026-03-30 V1.12AM CPO extremely small core-skeleton training pilot
- Added:
  - [370_V112AM_CPO_EXTREMELY_SMALL_CORE_SKELETON_TRAINING_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/370_V112AM_CPO_EXTREMELY_SMALL_CORE_SKELETON_TRAINING_PILOT.md)
  - [371_V112AM_CPO_EXTREMELY_SMALL_CORE_SKELETON_TRAINING_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/371_V112AM_CPO_EXTREMELY_SMALL_CORE_SKELETON_TRAINING_PILOT_V1.md)
  - [372_V112AM_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/372_V112AM_PHASE_CHECK_V1.md)
  - [373_V112AM_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/373_V112AM_PHASE_CLOSURE_CHECK_V1.md)
  - [v112am_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112am_phase_charter_v1.json)
  - [v112am_cpo_extremely_small_core_skeleton_training_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112am_cpo_extremely_small_core_skeleton_training_pilot_v1.json)
  - [v112am_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112am_phase_check_v1.json)
  - [v112am_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112am_phase_closure_check_v1.json)
- Current result:
  - the first lawful core-skeleton experiment has now been run
  - `GBDT` outperformed the guardrail on all `3` current core targets
  - the strongest gain was on `phase_progression_label`
  - formal training and signal rights remain closed

### 2026-03-30 V1.12AN CPO core-skeleton pilot result review
- Added:
  - [374_V112AN_CPO_CORE_SKELETON_PILOT_RESULT_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/374_V112AN_CPO_CORE_SKELETON_PILOT_RESULT_REVIEW.md)
  - [375_V112AN_CPO_CORE_SKELETON_PILOT_RESULT_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/375_V112AN_CPO_CORE_SKELETON_PILOT_RESULT_REVIEW_V1.md)
  - [376_V112AN_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/376_V112AN_PHASE_CHECK_V1.md)
  - [377_V112AN_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/377_V112AN_PHASE_CLOSURE_CHECK_V1.md)
  - [v112an_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112an_phase_charter_v1.json)
  - [v112an_cpo_core_skeleton_pilot_result_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112an_cpo_core_skeleton_pilot_result_review_v1.json)
  - [v112an_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112an_phase_check_v1.json)
  - [v112an_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112an_phase_closure_check_v1.json)
- Current result:
  - `phase` and `catalyst_sequence` are currently learned mainly through `catalyst_presence_family`
  - `role_state` is currently learned mainly through `role_prior_family`
  - the hardest residual problem is secondary-row role separation

### 2026-03-30 V1.12AO CPO role-layer patch pilot
- Added:
  - [378_V112AO_CPO_ROLE_LAYER_PATCH_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/378_V112AO_CPO_ROLE_LAYER_PATCH_PILOT.md)
  - [379_V112AO_CPO_ROLE_LAYER_PATCH_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/379_V112AO_CPO_ROLE_LAYER_PATCH_PILOT_V1.md)
  - [380_V112AO_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/380_V112AO_PHASE_CHECK_V1.md)
  - [381_V112AO_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/381_V112AO_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ao_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ao_phase_charter_v1.json)
  - [v112ao_cpo_role_layer_patch_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ao_cpo_role_layer_patch_pilot_v1.json)
  - [v112ao_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ao_phase_check_v1.json)
  - [v112ao_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ao_phase_closure_check_v1.json)
- Current result:
  - `role_state` improved materially without widening geometry
  - `role_state` GBDT accuracy: `0.7377 -> 1.0000`
  - max role confusion bucket: `58 -> 0`
  - the most important new family is `role_patch_microstructure_family`
  - formal training and signal rights remain closed

### 2026-03-30 V1.12AP CPO bounded secondary widen pilot
- Added:
  - [382_V112AP_CPO_BOUNDED_SECONDARY_WIDEN_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/382_V112AP_CPO_BOUNDED_SECONDARY_WIDEN_PILOT.md)
  - [383_V112AP_CPO_BOUNDED_SECONDARY_WIDEN_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/383_V112AP_CPO_BOUNDED_SECONDARY_WIDEN_PILOT_V1.md)
  - [384_V112AP_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/384_V112AP_PHASE_CHECK_V1.md)
  - [385_V112AP_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/385_V112AP_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ap_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ap_phase_charter_v1.json)
  - [v112ap_cpo_bounded_secondary_widen_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ap_cpo_bounded_secondary_widen_pilot_v1.json)
  - [v112ap_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ap_phase_check_v1.json)
  - [v112ap_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ap_phase_closure_check_v1.json)
- Current result:
  - the patched CPO core skeleton survived one lawful widen step without widening row geometry
  - all `3` guarded targets remained learnable
  - best guarded target: `role_transition_label`
  - formal training and signal rights remain closed

### 2026-03-30 V1.12AQ CPO feature implementation patch review
- Added:
  - [386_V112AQ_CPO_FEATURE_IMPLEMENTATION_PATCH_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/386_V112AQ_CPO_FEATURE_IMPLEMENTATION_PATCH_REVIEW.md)
  - [387_V112AQ_CPO_FEATURE_IMPLEMENTATION_PATCH_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/387_V112AQ_CPO_FEATURE_IMPLEMENTATION_PATCH_REVIEW_V1.md)
  - [390_V112AQ_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/390_V112AQ_PHASE_CHECK_V1.md)
  - [391_V112AQ_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/391_V112AQ_PHASE_CLOSURE_CHECK_V1.md)
  - [v112aq_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aq_phase_charter_v1.json)
  - [v112aq_cpo_feature_implementation_patch_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aq_cpo_feature_implementation_patch_review_v1.json)
  - [v112aq_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aq_phase_check_v1.json)
  - [v112aq_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aq_phase_closure_check_v1.json)
- Current result:
  - implementation patching must precede any row-geometry widen
  - minimum bounded patch scope = `6` rules
  - row-geometry widen remains closed

### 2026-03-30 V1.12AR CPO feature implementation patch spec freeze
- Added:
  - [388_V112AR_CPO_FEATURE_IMPLEMENTATION_PATCH_SPEC_FREEZE.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/388_V112AR_CPO_FEATURE_IMPLEMENTATION_PATCH_SPEC_FREEZE.md)
  - [389_V112AR_CPO_FEATURE_IMPLEMENTATION_PATCH_SPEC_FREEZE_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/389_V112AR_CPO_FEATURE_IMPLEMENTATION_PATCH_SPEC_FREEZE_V1.md)
  - [392_V112AR_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/392_V112AR_PHASE_CHECK_V1.md)
  - [393_V112AR_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/393_V112AR_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ar_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ar_phase_charter_v1.json)
  - [v112ar_cpo_feature_implementation_patch_spec_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ar_cpo_feature_implementation_patch_spec_v1.json)
  - [v112ar_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ar_phase_check_v1.json)
  - [v112ar_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ar_phase_closure_check_v1.json)
- Current result:
  - the minimum board/calendar patch rule set is now frozen
  - the next lawful move is `bounded_implementation_backfill_on_current_truth_rows`
  - row-geometry widen and formal training remain closed

### 2026-03-30 V1.12AS CPO bounded implementation backfill
- Added:
  - [394_V112AS_CPO_BOUNDED_IMPLEMENTATION_BACKFILL.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/394_V112AS_CPO_BOUNDED_IMPLEMENTATION_BACKFILL.md)
  - [395_V112AS_CPO_BOUNDED_IMPLEMENTATION_BACKFILL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/395_V112AS_CPO_BOUNDED_IMPLEMENTATION_BACKFILL_V1.md)
  - [396_V112AS_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/396_V112AS_PHASE_CHECK_V1.md)
  - [397_V112AS_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/397_V112AS_PHASE_CLOSURE_CHECK_V1.md)
  - [v112as_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112as_phase_charter_v1.json)
  - [v112as_cpo_bounded_implementation_backfill_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112as_cpo_bounded_implementation_backfill_v1.json)
  - [v112as_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112as_phase_check_v1.json)
  - [v112as_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112as_phase_closure_check_v1.json)
- Current result:
  - all `6` frozen implementation rules are now backfilled on the current `7` truth rows
  - board/calendar coverage is explicit at `1.0`
  - the next lawful move is a post-patch rerun before any row-geometry widen

### 2026-03-30 V1.12AT CPO post-patch rerun
- Added:
  - [398_V112AT_CPO_POST_PATCH_RERUN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/398_V112AT_CPO_POST_PATCH_RERUN.md)
  - [399_V112AT_CPO_POST_PATCH_RERUN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/399_V112AT_CPO_POST_PATCH_RERUN_V1.md)
  - [400_V112AT_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/400_V112AT_PHASE_CHECK_V1.md)
  - [401_V112AT_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/401_V112AT_PHASE_CLOSURE_CHECK_V1.md)
  - [v112at_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112at_phase_charter_v1.json)
  - [v112at_cpo_post_patch_rerun_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112at_cpo_post_patch_rerun_v1.json)
  - [v112at_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112at_phase_check_v1.json)
  - [v112at_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112at_phase_closure_check_v1.json)
- Current result:
  - current-row post-patch rerun stayed stable on both core and guarded targets
  - implementation backfill did not create extra `GBDT` gain on the current tiny pilot
  - implementation is therefore no longer the active blocker on the current truth rows
  - the next lawful move is to consider a bounded row-geometry widen pilot

### 2026-03-30 V1.12AU CPO bounded row-geometry widen pilot
- Added:
  - [402_V112AU_CPO_BOUNDED_ROW_GEOMETRY_WIDEN_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/402_V112AU_CPO_BOUNDED_ROW_GEOMETRY_WIDEN_PILOT.md)
  - [403_V112AU_CPO_BOUNDED_ROW_GEOMETRY_WIDEN_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/403_V112AU_CPO_BOUNDED_ROW_GEOMETRY_WIDEN_PILOT_V1.md)
  - [404_V112AU_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/404_V112AU_PHASE_CHECK_V1.md)
  - [405_V112AU_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/405_V112AU_PHASE_CLOSURE_CHECK_V1.md)
  - [v112au_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112au_phase_charter_v1.json)
  - [v112au_cpo_bounded_row_geometry_widen_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112au_cpo_bounded_row_geometry_widen_pilot_v1.json)
  - [v112au_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112au_phase_check_v1.json)
  - [v112au_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112au_phase_closure_check_v1.json)
- Current result:
  - branch-row widen did not preserve full core stability
  - the break is concentrated in `role_state_label`
  - guarded targets remain stable
  - branch rows should stay review-only for now

### 2026-03-30 V1.12AV CPO branch role geometry patch pilot
- Added:
  - [406_V112AV_CPO_BRANCH_ROLE_GEOMETRY_PATCH_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/406_V112AV_CPO_BRANCH_ROLE_GEOMETRY_PATCH_PILOT.md)
  - [407_V112AV_CPO_BRANCH_ROLE_GEOMETRY_PATCH_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/407_V112AV_CPO_BRANCH_ROLE_GEOMETRY_PATCH_PILOT_V1.md)
  - [408_V112AV_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/408_V112AV_PHASE_CHECK_V1.md)
  - [409_V112AV_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/409_V112AV_PHASE_CLOSURE_CHECK_V1.md)
  - [v112av_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112av_phase_charter_v1.json)
  - [v112av_cpo_branch_role_geometry_patch_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112av_cpo_branch_role_geometry_patch_pilot_v1.json)
  - [v112av_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112av_phase_check_v1.json)
  - [v112av_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112av_phase_closure_check_v1.json)
- Current result:
  - widened branch geometry is patchable
  - `role_state` recovered from `0.8972` to `1.0000`
  - core and guarded targets are stable again
  - next lawful move is to review whether branch rows can leave review-only and enter a guarded training context

### 2026-03-30 V1.12AW CPO branch guarded admission review
- Added:
  - [410_V112AW_CPO_BRANCH_GUARDED_ADMISSION_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/410_V112AW_CPO_BRANCH_GUARDED_ADMISSION_REVIEW.md)
  - [411_V112AW_CPO_BRANCH_GUARDED_ADMISSION_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/411_V112AW_CPO_BRANCH_GUARDED_ADMISSION_REVIEW_V1.md)
  - [412_V112AW_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/412_V112AW_PHASE_CHECK_V1.md)
  - [413_V112AW_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/413_V112AW_PHASE_CLOSURE_CHECK_V1.md)
  - [v112aw_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aw_phase_charter_v1.json)
  - [v112aw_cpo_branch_guarded_admission_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aw_cpo_branch_guarded_admission_review_v1.json)
  - [v112aw_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aw_phase_check_v1.json)
  - [v112aw_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112aw_phase_closure_check_v1.json)
- Current result:
  - `688498 / 688313 / 300757` can move from review-only into guarded training context
  - `300570` remains review-only
  - the next lawful move is to run a guarded branch-admitted pilot before any broader row widen

### 2026-03-30 V1.12AX CPO guarded branch-admitted pilot
- Added:
  - [414_V112AX_CPO_GUARDED_BRANCH_ADMITTED_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/414_V112AX_CPO_GUARDED_BRANCH_ADMITTED_PILOT.md)
  - [415_V112AX_CPO_GUARDED_BRANCH_ADMITTED_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/415_V112AX_CPO_GUARDED_BRANCH_ADMITTED_PILOT_V1.md)
  - [416_V112AX_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/416_V112AX_PHASE_CHECK_V1.md)
  - [417_V112AX_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/417_V112AX_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ax_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ax_phase_charter_v1.json)
  - [v112ax_cpo_guarded_branch_admitted_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ax_cpo_guarded_branch_admitted_pilot_v1.json)
  - [v112ax_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ax_phase_check_v1.json)
  - [v112ax_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ax_phase_closure_check_v1.json)
- Current result:
  - the `3` guarded-admitted branch rows can be tested without recreating the earlier branch collapse
  - core and guarded targets remain stable
  - the next lawful move is to review whether these guarded branch rows can enter the next bounded training layer

### 2026-03-30 V1.12AY CPO guarded branch training-layer review
- Added:
  - [418_V112AY_CPO_GUARDED_BRANCH_TRAINING_LAYER_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/418_V112AY_CPO_GUARDED_BRANCH_TRAINING_LAYER_REVIEW.md)
  - [419_V112AY_CPO_GUARDED_BRANCH_TRAINING_LAYER_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/419_V112AY_CPO_GUARDED_BRANCH_TRAINING_LAYER_REVIEW_V1.md)
  - [420_V112AY_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/420_V112AY_PHASE_CHECK_V1.md)
  - [421_V112AY_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/421_V112AY_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ay_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ay_phase_charter_v1.json)
  - [v112ay_cpo_guarded_branch_training_layer_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ay_cpo_guarded_branch_training_layer_review_v1.json)
  - [v112ay_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ay_phase_check_v1.json)
  - [v112ay_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ay_phase_closure_check_v1.json)
- Current result:
  - the same `3` branch rows can enter the next bounded training-facing layer under guarded posture
  - `300570` remains review-only
  - the next lawful move is to consider extending the bounded training layer with guarded branch rows only

### 2026-03-30 V1.12AZ CPO bounded training layer extension
- Added:
  - [422_V112AZ_CPO_BOUNDED_TRAINING_LAYER_EXTENSION.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/422_V112AZ_CPO_BOUNDED_TRAINING_LAYER_EXTENSION.md)
  - [423_V112AZ_CPO_BOUNDED_TRAINING_LAYER_EXTENSION_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/423_V112AZ_CPO_BOUNDED_TRAINING_LAYER_EXTENSION_V1.md)
  - [424_V112AZ_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/424_V112AZ_PHASE_CHECK_V1.md)
  - [425_V112AZ_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/425_V112AZ_PHASE_CLOSURE_CHECK_V1.md)
  - [v112az_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112az_phase_charter_v1.json)
  - [v112az_cpo_bounded_training_layer_extension_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112az_cpo_bounded_training_layer_extension_v1.json)
  - [v112az_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112az_phase_check_v1.json)
  - [v112az_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112az_phase_closure_check_v1.json)
- Current result:
  - the bounded training-facing layer now contains `10` rows
  - the added `3` branch rows remain guarded
  - `300570` remains outside
  - the next lawful move is to review whether this 10-row layer can replace the old 7-row baseline for the next pilot

### 2026-03-30 V1.12BA CPO 10-row layer replacement review
- Added:
  - [426_V112BA_CPO_10_ROW_LAYER_REPLACEMENT_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/426_V112BA_CPO_10_ROW_LAYER_REPLACEMENT_REVIEW.md)
  - [427_V112BA_CPO_10_ROW_LAYER_REPLACEMENT_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/427_V112BA_CPO_10_ROW_LAYER_REPLACEMENT_REVIEW_V1.md)
  - [428_V112BA_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/428_V112BA_PHASE_CHECK_V1.md)
  - [429_V112BA_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/429_V112BA_PHASE_CLOSURE_CHECK_V1.md)
  - [v112ba_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ba_phase_charter_v1.json)
  - [v112ba_cpo_10_row_layer_replacement_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ba_cpo_10_row_layer_replacement_review_v1.json)
  - [v112ba_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ba_phase_check_v1.json)
  - [v112ba_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ba_phase_closure_check_v1.json)
- Current result:
  - the `10`-row guarded layer replaces the `7`-row baseline for the next bounded pilot
  - guarded branch boundaries remain active
  - the next lawful move is to open the next bounded pilot on the `10`-row guarded layer

### 2026-03-30 V1.12BB CPO default 10-row guarded-layer pilot
- Added:
  - [430_V112BB_CPO_DEFAULT_10_ROW_GUARDED_LAYER_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/430_V112BB_CPO_DEFAULT_10_ROW_GUARDED_LAYER_PILOT.md)
  - [431_V112BB_CPO_DEFAULT_10_ROW_GUARDED_LAYER_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/431_V112BB_CPO_DEFAULT_10_ROW_GUARDED_LAYER_PILOT_V1.md)
  - [432_V112BB_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/432_V112BB_PHASE_CHECK_V1.md)
  - [433_V112BB_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/433_V112BB_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bb_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bb_phase_charter_v1.json)
  - [v112bb_cpo_default_10_row_guarded_layer_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bb_cpo_default_10_row_guarded_layer_pilot_v1.json)
  - [v112bb_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bb_phase_check_v1.json)
  - [v112bb_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bb_phase_closure_check_v1.json)
- Current result:
  - the `10`-row guarded layer is now the default bounded experimental baseline
  - core and guarded targets both stay stable against the prior lawful baselines
  - later row widen should be judged against this frozen `10`-row baseline, not the old `7`-row skeleton

### 2026-03-30 V1.12BC CPO portfolio objective protocol
- Added:
  - [434_V112BC_CPO_PORTFOLIO_OBJECTIVE_PROTOCOL.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/434_V112BC_CPO_PORTFOLIO_OBJECTIVE_PROTOCOL.md)
  - [435_V112BC_CPO_PORTFOLIO_OBJECTIVE_PROTOCOL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/435_V112BC_CPO_PORTFOLIO_OBJECTIVE_PROTOCOL_V1.md)
  - [436_V112BC_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/436_V112BC_PHASE_CHECK_V1.md)
  - [437_V112BC_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/437_V112BC_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bc_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bc_phase_charter_v1.json)
  - [v112bc_cpo_portfolio_objective_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bc_cpo_portfolio_objective_protocol_v1.json)
  - [v112bc_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bc_phase_check_v1.json)
  - [v112bc_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bc_phase_closure_check_v1.json)
- Current result:
  - the project now has a frozen three-track portfolio objective grammar
  - hindsight upper-bound benchmarking is separated from no-leak experimental tracks
  - a hard marginal-gain stop rule is frozen for later model-zoo exploration

### 2026-03-30 V1.12BD market regime overlay feature review
- Added:
  - [438_V112BD_MARKET_REGIME_OVERLAY_FEATURE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/438_V112BD_MARKET_REGIME_OVERLAY_FEATURE_REVIEW.md)
  - [439_V112BD_MARKET_REGIME_OVERLAY_FEATURE_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/439_V112BD_MARKET_REGIME_OVERLAY_FEATURE_REVIEW_V1.md)
  - [440_V112BD_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/440_V112BD_PHASE_CHECK_V1.md)
  - [441_V112BD_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/441_V112BD_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bd_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bd_phase_charter_v1.json)
  - [v112bd_market_regime_overlay_feature_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bd_market_regime_overlay_feature_review_v1.json)
  - [v112bd_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bd_phase_check_v1.json)
  - [v112bd_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bd_phase_closure_check_v1.json)
- Current result:
  - the project now has a lawful market-regime overlay family
  - broad market, liquidity, board-style, and sector ETF context can be tested as overlay context without replacing core CPO truth

### 2026-03-30 V1.12BE CPO oracle upper-bound benchmark
- Added:
  - [442_V112BE_CPO_ORACLE_UPPER_BOUND_BENCHMARK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/442_V112BE_CPO_ORACLE_UPPER_BOUND_BENCHMARK.md)
  - [443_V112BE_CPO_ORACLE_UPPER_BOUND_BENCHMARK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/443_V112BE_CPO_ORACLE_UPPER_BOUND_BENCHMARK_V1.md)
  - [444_V112BE_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/444_V112BE_PHASE_CHECK_V1.md)
  - [445_V112BE_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/445_V112BE_PHASE_CLOSURE_CHECK_V1.md)
  - [v112be_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112be_phase_charter_v1.json)
  - [v112be_cpo_oracle_upper_bound_benchmark_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112be_cpo_oracle_upper_bound_benchmark_v1.json)
  - [v112be_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112be_phase_check_v1.json)
  - [v112be_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112be_phase_closure_check_v1.json)
- Current result:
  - the project now has a hindsight-only upper-bound portfolio benchmark on the same lawful `10`-row CPO layer
  - future no-leak aggressive and neutral tracks can compare themselves against an explicit upper-bound line instead of an abstract ceiling

### 2026-03-30 V1.12BF CPO aggressive no-leak black-box portfolio pilot
- Added:
  - [446_V112BF_CPO_AGGRESSIVE_NO_LEAK_BLACK_BOX_PORTFOLIO_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/446_V112BF_CPO_AGGRESSIVE_NO_LEAK_BLACK_BOX_PORTFOLIO_PILOT.md)
  - [447_V112BF_CPO_AGGRESSIVE_NO_LEAK_BLACK_BOX_PORTFOLIO_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/447_V112BF_CPO_AGGRESSIVE_NO_LEAK_BLACK_BOX_PORTFOLIO_PILOT_V1.md)
  - [448_V112BF_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/448_V112BF_PHASE_CHECK_V1.md)
  - [449_V112BF_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/449_V112BF_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bf_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bf_phase_charter_v1.json)
  - [v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1.json)
  - [v112bf_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bf_phase_check_v1.json)
  - [v112bf_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bf_phase_closure_check_v1.json)
- Current result:
  - the project now has its first true no-leak aggressive portfolio line on the lawful `10`-row CPO layer
  - the line is profitable, but still very far from the oracle ceiling and still much worse on drawdown

### 2026-03-30 V1.12BG CPO oracle-vs-no-leak gap review
- Added:
  - [450_V112BG_CPO_ORACLE_VS_NO_LEAK_GAP_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/450_V112BG_CPO_ORACLE_VS_NO_LEAK_GAP_REVIEW.md)
  - [451_V112BG_CPO_ORACLE_VS_NO_LEAK_GAP_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/451_V112BG_CPO_ORACLE_VS_NO_LEAK_GAP_REVIEW_V1.md)
  - [452_V112BG_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/452_V112BG_PHASE_CHECK_V1.md)
  - [453_V112BG_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/453_V112BG_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bg_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bg_phase_charter_v1.json)
  - [v112bg_cpo_oracle_vs_no_leak_gap_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bg_cpo_oracle_vs_no_leak_gap_review_v1.json)
  - [v112bg_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bg_phase_check_v1.json)
  - [v112bg_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bg_phase_closure_check_v1.json)
- Current result:
  - the remaining gap is now explicitly attributed to risk-control and stage-maturity filtering
  - the next lawful no-leak line can therefore use a selective gate stack instead of blindly copying the aggressive objective

### 2026-03-30 V1.12BH CPO neutral selective no-leak portfolio pilot
- Added:
  - [454_V112BH_CPO_NEUTRAL_SELECTIVE_NO_LEAK_PORTFOLIO_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/454_V112BH_CPO_NEUTRAL_SELECTIVE_NO_LEAK_PORTFOLIO_PILOT.md)
  - [455_V112BH_CPO_NEUTRAL_SELECTIVE_NO_LEAK_PORTFOLIO_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/455_V112BH_CPO_NEUTRAL_SELECTIVE_NO_LEAK_PORTFOLIO_PILOT_V1.md)
  - [456_V112BH_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/456_V112BH_PHASE_CHECK_V1.md)
  - [457_V112BH_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/457_V112BH_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bh_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bh_phase_charter_v1.json)
  - [v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1.json)
  - [v112bh_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bh_phase_check_v1.json)
  - [v112bh_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bh_phase_closure_check_v1.json)
- Current result:
  - the project now has a cash-accepting selective no-leak line on the same lawful `10`-row CPO layer
  - this line currently improves both total return and max drawdown versus the aggressive no-leak track

### 2026-03-30 V1.12BI CPO cross-sectional ranker pilot
- Added:
  - [458_V112BI_CPO_CROSS_SECTIONAL_RANKER_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/458_V112BI_CPO_CROSS_SECTIONAL_RANKER_PILOT.md)
  - [459_V112BI_CPO_CROSS_SECTIONAL_RANKER_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/459_V112BI_CPO_CROSS_SECTIONAL_RANKER_PILOT_V1.md)
  - [460_V112BI_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/460_V112BI_PHASE_CHECK_V1.md)
  - [461_V112BI_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/461_V112BI_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bi_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bi_phase_charter_v1.json)
  - [v112bi_cpo_cross_sectional_ranker_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bi_cpo_cross_sectional_ranker_pilot_v1.json)
  - [v112bi_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bi_phase_check_v1.json)
  - [v112bi_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bi_phase_closure_check_v1.json)
- Current result:
  - the project now has a direct ranking no-leak comparison line on the same lawful `10`-row CPO layer
  - ranking improves versus the aggressive line, but still does not beat the current neutral selective baseline

### 2026-03-30 V1.12BJ CPO neutral teacher gate pilot
- Added:
  - [462_V112BJ_CPO_NEUTRAL_TEACHER_GATE_PILOT.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/462_V112BJ_CPO_NEUTRAL_TEACHER_GATE_PILOT.md)
  - [463_V112BJ_CPO_NEUTRAL_TEACHER_GATE_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/463_V112BJ_CPO_NEUTRAL_TEACHER_GATE_PILOT_V1.md)
  - [464_V112BJ_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/464_V112BJ_PHASE_CHECK_V1.md)
  - [465_V112BJ_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/465_V112BJ_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bj_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bj_phase_charter_v1.json)
  - [v112bj_cpo_neutral_teacher_gate_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bj_cpo_neutral_teacher_gate_pilot_v1.json)
  - [v112bj_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bj_phase_check_v1.json)
  - [v112bj_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bj_phase_closure_check_v1.json)
- Current result:
  - the project now has an explicit teacher-distillation comparison line for the neutral selective track
  - the current naive gate-imitation version collapses to all cash and therefore does not add a usable portfolio behavior

### 2026-03-30 V1.12BK CPO tree/ranker search
- Added:
  - [466_V112BK_CPO_TREE_RANKER_SEARCH.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/466_V112BK_CPO_TREE_RANKER_SEARCH.md)
  - [467_V112BK_CPO_TREE_RANKER_SEARCH_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/467_V112BK_CPO_TREE_RANKER_SEARCH_V1.md)
  - [468_V112BK_PHASE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/468_V112BK_PHASE_CHECK_V1.md)
  - [469_V112BK_PHASE_CLOSURE_CHECK_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/469_V112BK_PHASE_CLOSURE_CHECK_V1.md)
  - [v112bk_phase_charter_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bk_phase_charter_v1.json)
  - [v112bk_cpo_tree_ranker_search_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bk_cpo_tree_ranker_search_v1.json)
  - [v112bk_phase_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bk_phase_check_v1.json)
  - [v112bk_phase_closure_check_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112bk_phase_closure_check_v1.json)
- Current result:
  - the project now has a bounded no-leak tree/ranker search branch on the lawful `10`-row CPO layer
  - the best cheap tree variant improves return versus the neutral line, but fails the drawdown guard, so it is still not a replacement for the neutral selective baseline

### 2026-03-31 V1.12CH packaging mainline template freeze
- Added:
  - [v112ch_packaging_mainline_template_freeze_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v112ch_packaging_mainline_template_freeze_v1.json)
- Current result:
  - `packaging_process_enabler` is now frozen as the first refined cluster mainline template asset
  - `laser_chip_component` remains an `eligibility-only` template member
  - `silicon_photonics_component` remains outside the template mainline as an isolated diagnostic path
