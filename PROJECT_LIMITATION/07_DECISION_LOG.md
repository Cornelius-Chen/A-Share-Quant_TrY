# A-Share Quant Decision Log

## 目的

本文件记录关键设计决策，保证未来可以追溯“为什么这样做”。

---

## 记录规则

需要记录的决策包括但不限于：

1. 协议升级
2. 研究方向切换
3. 数据口径调整
4. 指标定义变更
5. 回测引擎核心行为变更
6. 策略晋级或淘汰

---

## 模板

### DEC-0001

- Date:
- Title:
- Status: proposed / accepted / superseded / rejected
- Related Protocol Version:
- Related Runs:
- Context:
- Decision:
- Alternatives Considered:
- Expected Benefits:
- Risks:
- Follow-up Actions:

---

## Entries

### DEC-0001

- Date: 2026-03-28
- Title: Establish lab-stage governance baseline before code implementation
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: Existing repo only had charter, protocol, constitution, execution process, and risk limits. The project target is engineering-grade profitability, not a one-off backtest repo.
- Decision: Add governance, roadmap, research direction, experiment, evolution, data, metrics, validation, promotion, lifecycle, postmortem, repository architecture, and future ML policy documents before substantial code implementation.
- Alternatives Considered: Start coding the backtest skeleton immediately and add governance later.
- Expected Benefits: Reduce methodological drift, create durable research assets, and make later implementation choices auditable.
- Risks: Slightly slower initial coding start.
- Follow-up Actions: Use the new document set as the baseline for repository architecture and implementation sequencing.

### DEC-0002

- Date: 2026-03-28
- Title: Build the minimum runnable phase-1 research backbone before any regime or strategy logic
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T101445Z_35146c4e
- Context: The repository had governance documents but no implementation layer. The first engineering milestone needed to create a shared, auditable base that all later strategies can reuse.
- Decision: Implement `pyproject.toml`, YAML configs, sample CSV inputs, `src/a_share_quant/` package scaffolding, conservative daily-bar backtest modules, a run registry, a CLI runner, and phase-1 tests before adding regime or mainline logic.
- Alternatives Considered: Start directly with mainline scoring and strategy family code on top of ad hoc scripts.
- Expected Benefits: Preserve architecture discipline, make experiments reproducible, and reduce rework when regime/trend modules arrive.
- Risks: The first runnable path is intentionally simple and not yet strategy-complete.
- Follow-up Actions: Use this backbone for the next implementation round: sample segmentation, attack permission, and mainline sector scoring.

### DEC-0003

- Date: 2026-03-28
- Title: Implement regime-layer primitives before trend and strategy modules
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T102551Z_6e6d8e64
- Context: Phase-1 produced a runnable backtest backbone, but protocol_v1.0 requires objective segmented backtests and mainline-aware environment gating before any strategy family can be meaningfully compared.
- Decision: Implement `mainline_sector_scorer.py`, `sample_segmenter.py`, and `attack_permission_engine.py` as reusable regime primitives with configurable thresholds and tests, while keeping strategy logic deferred.
- Alternatives Considered: Jump directly to leader hierarchy or Strategy A/B/C wrappers.
- Expected Benefits: Keep the project aligned with segmented bullish-window evaluation and mainline-first environment control.
- Risks: Current scoring and segmentation formulas are still baseline candidates, not final research winners.
- Follow-up Actions: Build trend-layer hierarchy and entry/holding/exit modules on top of these regime outputs.

### DEC-0004

- Date: 2026-03-28
- Title: Implement trend-layer candidate modules before strategy-family wrappers
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T102945Z_8efa8b4d
- Context: After regime primitives were in place, the protocol still required mainline-internal hierarchy, candidate trend filters, and candidate entry rules before any Strategy A/B/C wrapper could be meaningfully compared.
- Decision: Implement `leader_hierarchy_ranker.py`, `trend_filters.py`, and `entry_rules.py` as reusable candidate modules, keeping holding, exit, and strategy-family assembly for later rounds.
- Alternatives Considered: Jump directly to Strategy A/B/C wrappers and hardcode a single trend + entry interpretation.
- Expected Benefits: Preserve modular comparison, keep candidate sets explicit, and avoid early collapse into a single discretionary-looking path.
- Risks: The current scoring and rule formulas are intentionally simple baselines and will need future protocol-guided iteration.
- Follow-up Actions: Build holding, exit, and strategy-family orchestration on top of the current regime and trend modules.

### DEC-0005

- Date: 2026-03-28
- Title: Compose holding, exit, and Strategy A/B/C wrappers on top of shared regime and trend modules
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T103341Z_26f09fc7
- Context: The repo already had regime outputs plus hierarchy, filters, and entry candidates, but still lacked holding/exit semantics and a comparable strategy-family layer.
- Decision: Implement `holding_engine.py`, `exit_guard.py`, a shared `mainline_strategy_base.py`, and Strategy A/B/C wrappers that differ only by allowed hierarchy layers.
- Alternatives Considered: Hardcode buy/sell logic separately inside each strategy file.
- Expected Benefits: Preserve shared logic, make A/B/C strategies directly comparable, and keep protocol changes localized in reusable modules.
- Risks: Holding and exit behavior is still baseline-level and will need richer protocol-driven iteration later.
- Follow-up Actions: Connect the strategy wrappers to metrics/reporting improvements and begin implementing custom mainline-capture metrics.

### DEC-0006

- Date: 2026-03-28
- Title: Implement custom mainline metrics before building a fuller experiment pipeline
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T103505Z_edd50957
- Context: The research protocol requires `mainline_capture_ratio` and `missed_mainline_count`, but the repo only had classic PnL and drawdown metrics.
- Decision: Add a `MainlineWindow` model plus metric functions for capture ratio and missed-count evaluation, with tests, while deferring full pipeline wiring to a later round.
- Alternatives Considered: Leave the custom metrics as documentation-only requirements until a more complete strategy runner exists.
- Expected Benefits: Move the repo closer to protocol completeness and make the custom metrics concrete rather than aspirational.
- Risks: The current metric implementation depends on externally supplied mainline windows and will need richer upstream integration.
- Follow-up Actions: Wire strategy-family runs and mainline windows into reporting so these metrics become part of normal experiment output.

### DEC-0007

- Date: 2026-03-28
- Title: Add a strategy experiment runner that turns shared modules into normal run artifacts
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T104137Z_0af22dea
- Context: The repo already had regime, trend, strategy wrappers, and custom metrics, but they were not yet connected into a standard experiment path with config, sample inputs, reporting, and run registry output.
- Decision: Implement a reusable `StrategyExperimentRunner`, CSV loaders for sector/stock/window inputs, a strategy experiment CLI, sample experiment data/config, and report extras that include generated signals and regime counts.
- Alternatives Considered: Keep strategy composition as library-only code and defer end-to-end experiment wiring to a much later round.
- Expected Benefits: Turn the architecture into a runnable research path, make custom metrics observable in real reports, and reduce the gap between modules and experiments.
- Risks: The current experiment runner still uses a simplified planned-position view when generating future signals and currently drives permissions from sector-trend segmentation only.
- Follow-up Actions: Improve the runner to support richer sample segmentation methods, integrate actual fill-aware position state, and expand reporting.

### DEC-0008

- Date: 2026-03-28
- Title: Add a unified A/B/C strategy suite runner and comparison report
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T104456Z_6acb2bfa
- Context: The repo could already run one strategy-family experiment at a time, but the protocol requires Strategy A/B/C to be compared under one shared framework rather than as isolated runs.
- Decision: Extend the experiment runner with suite support, add a comparison report writer, create a suite CLI/config, and add tests that pin comparable signal-count behavior across A/B/C.
- Alternatives Considered: Keep users responsible for manually launching three separate runs and comparing them outside the repo.
- Expected Benefits: Make “same data, same config, same runner” comparison explicit and reproducible, which is central to the project philosophy.
- Risks: The current suite report is still summary-heavy and not yet a full researcher-facing dashboard.
- Follow-up Actions: Enrich suite reporting with per-strategy trade breakdowns, segmentation summaries, and more detailed comparison artifacts.

### DEC-0009

- Date: 2026-03-28
- Title: Make experiment runner position state fill-aware and enrich suite comparison rankings
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T104815Z_c1fd4941
- Context: The first experiment runner used same-day planned positions, which could blur the difference between generated signals and filled positions. The suite output also needed clearer comparison ranks.
- Decision: Update the strategy experiment runner so positions become active only on the next fill date, block duplicate same-direction signals while fills are pending, and extend suite comparisons with explicit metric ranks and richer aggregate summaries.
- Alternatives Considered: Keep the simpler planned-position model and leave suite comparison logic to external tooling.
- Expected Benefits: Bring signal-generation state closer to the backtest execution model and make A/B/C comparisons easier to interpret directly from repo artifacts.
- Risks: The runner is still not fully broker-state accurate; pending orders are modeled conservatively but without full order lifecycle simulation.
- Follow-up Actions: Continue improving report richness and, if needed, add more detailed order-state simulation later.

### DEC-0010

- Date: 2026-03-28
- Title: Enrich single-strategy and suite reports with window and trade breakdowns
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T105224Z_60adbf9e, 20260328T105224Z_b3c4e8f8
- Context: The pipeline already produced valid summaries, but researchers still needed to open code or reconstruct details to understand which windows were captured and what each strategy actually traded.
- Decision: Add mainline-window breakdowns, trade overviews, and segment overviews to experiment results and surface them in both single-strategy and suite report artifacts.
- Alternatives Considered: Keep reports summary-only and leave richer analysis to ad hoc notebooks or manual inspection.
- Expected Benefits: Make report artifacts closer to actual research documents and reduce the gap between protocol metrics and human interpretation.
- Risks: JSON reports are growing in size and may eventually need a more structured presentation format.
- Follow-up Actions: Consider adding report templates or rendered markdown/HTML views once the metric set and runner semantics stabilize further.

### DEC-0011

- Date: 2026-03-28
- Title: Promote segmentation method to a first-class experiment configuration
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T105908Z_43bcc582, 20260328T105908Z_1163b0d4
- Context: The project already supported multiple segmentation methods inside the segmenter module, but experiment runs still effectively defaulted to sector-only segmentation unless a developer manually rewired code.
- Decision: Add `segmentation_method` to runner/config flow, support `index_trend`, `sector_trend`, and `resonance` directly in experiment execution, and provide index sample data so the richer paths are actually runnable in demo configs.
- Alternatives Considered: Leave multi-method segmentation as a low-level utility and keep experiment configs hardwired to sector-trend segmentation.
- Expected Benefits: Bring the repo closer to the research protocol and make segmented bullish-window experimentation materially more flexible.
- Risks: Additional input requirements for some methods increase configuration surface and sample-data maintenance.
- Follow-up Actions: Expand datasets and experiments so the three segmentation methods can be compared systematically rather than just supported operationally.

### DEC-0012

- Date: 2026-03-28
- Title: Add a formal segmentation-method comparison workflow for one strategy family
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T110151Z_31075b93
- Context: The experiment pipeline could now run one strategy under a chosen segmentation method, but there was still no first-class workflow for comparing `index_trend`, `sector_trend`, and `resonance` under the same strategy and data.
- Decision: Add a reusable segmentation comparison runner, a CLI/config for segmentation-method comparison runs, and report output that ranks methods under one strategy family.
- Alternatives Considered: Require users to manually launch three separate runs and compare them by hand.
- Expected Benefits: Make segmentation-method research protocol-compliant, repeatable, and easier to review.
- Risks: The current demo dataset does not yet separate the methods meaningfully, so comparison infrastructure is ahead of data richness.
- Follow-up Actions: Build richer datasets and experiments that produce materially different outcomes across the supported segmentation methods.
