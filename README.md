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
  - this is useful because it separates “path-shift shape exists” from
    “path-shift causes actual trade damage”
  - current interpretation:
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
