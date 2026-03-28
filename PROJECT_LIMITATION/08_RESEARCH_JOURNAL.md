# A-Share Quant Research Journal

## 目的

本文件用于记录每次重要研究改动后的观察、结果和下一步计划。

它不是结构化 run 注册表的替代品，而是面向人的研究叙述层。

---

## 记录规则

以下情况至少应记录一条 journal：

1. 协议版本升级
2. 样本切分逻辑变化
3. 主线定义或打分逻辑变化
4. 个股分层逻辑变化
5. 趋势过滤、入场、持有、退出逻辑变化
6. 成本、滑点、涨跌停成交模型变化
7. 出现显著结果提升或退化
8. 发现严重 bug、数据污染或结论反转

---

## 模板

### JOURNAL-0001

- Date:
- Author:
- Title:
- Related Decision:
- Related Runs:
- Protocol Version:
- Hypothesis:
- What Changed:
- Expected Impact:
- Observed Result:
- Side Effects / Risks:
- Conclusion:
- Next Step:

---

## Entries

### JOURNAL-0001

- Date: 2026-03-28
- Author: Codex
- Title: Build the research governance baseline before starting the first implementation diff
- Related Decision: DEC-0001
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The project is more likely to stay aligned with profitability goals if governance, data, experiment, and promotion rules are fixed before code grows.
- What Changed: Added roadmap, directions, experiment standard, protocol evolution policy, data contract, metrics spec, promotion gates, validation standard, strategy lifecycle, postmortem log, repository architecture plan, and future ML policy files.
- Expected Impact: Reduce drift, preserve auditability, and make future code review easier.
- Observed Result: Documentation baseline completed; no backtest result yet because implementation has not started.
- Side Effects / Risks: Initial implementation is delayed slightly in exchange for stronger long-term control.
- Conclusion: The delay is justified because the project target is engineering-grade profitability rather than a demo system.
- Next Step: Map repository architecture and code modules to the new governance set, then start building the minimal runnable backbone.

### JOURNAL-0002

- Date: 2026-03-28
- Author: Codex
- Title: Deliver the first runnable phase-1 backbone from an empty repo
- Related Decision: DEC-0002
- Related Runs: 20260328T101445Z_35146c4e
- Protocol Version: protocol_v1.0
- Hypothesis: A simple but conservative daily-bar backbone with audit and reporting is the correct first implementation step because it preserves future comparability across all later strategy families.
- What Changed: Added package scaffolding, YAML configs, sample data, universe filtering, cost model, limit model, next-day execution backtest engine, JSON report writer, run registry, CLI runner, tests, and ignore rules for generated run artifacts.
- Expected Impact: Provide a shared research substrate that later regime, trend, and strategy modules can reuse without creating parallel mini-systems.
- Observed Result: `pytest` passed and the demo run completed successfully, producing a report and a structured run record.
- Side Effects / Risks: The current backbone is intentionally narrow. It does not yet include sample segmentation, mainline scoring, hierarchy ranking, or custom metrics such as `mainline_capture_ratio`.
- Conclusion: The phase-1 foundation is now real and runnable. The next round should focus on regime-layer modules rather than premature strategy sophistication.
- Next Step: Implement `sample_segmenter.py`, `attack_permission_engine.py`, and `mainline_sector_scorer.py` on top of the current backbone.

### JOURNAL-0003

- Date: 2026-03-28
- Author: Codex
- Title: Add the first regime-layer implementation on top of the phase-1 backbone
- Related Decision: DEC-0003
- Related Runs: 20260328T102551Z_6e6d8e64
- Protocol Version: protocol_v1.0
- Hypothesis: Objective segmented bullish-window evaluation should exist before trend and strategy modules; otherwise later comparisons will drift toward unstructured full-history testing.
- What Changed: Added sector-level composite scoring, index/sector/resonance sample segmentation, attack permission gating, regime config placeholders, and dedicated tests.
- Expected Impact: Make the project capable of codified sample segmentation and environment gating, which are required by the research protocol.
- Observed Result: All tests passed after adding the new regime modules, and the demo backtest backbone remained stable.
- Side Effects / Risks: The regime formulas are still intentionally simple. They are valid baseline candidates, not optimized research conclusions.
- Conclusion: Phase-2 has started correctly: the project now has regime primitives without prematurely collapsing into strategy-specific code.
- Next Step: Implement trend-layer modules for hierarchy ranking, trend filters, and entry candidates.

### JOURNAL-0004

- Date: 2026-03-28
- Author: Codex
- Title: Add the first trend-layer candidate modules on top of the regime layer
- Related Decision: DEC-0004
- Related Runs: 20260328T102945Z_8efa8b4d
- Protocol Version: protocol_v1.0
- Hypothesis: Mainline-internal hierarchy and entry/filters should be expressed as explicit candidate modules before strategy wrappers, so later A/B/C strategies can compose them instead of embedding one-off logic.
- What Changed: Added stock-level snapshots and outputs, hierarchy ranking, multiple trend-filter candidates, multiple entry-rule candidates, trend config placeholders, and dedicated tests.
- Expected Impact: Make the repo capable of comparing leader/core/late-mover selection and entry/filter variants under one shared base.
- Observed Result: All tests passed and the demo backbone remained stable after adding the trend layer.
- Side Effects / Risks: The current candidate formulas are heuristics chosen for clean architecture and protocol coverage, not for alpha optimization.
- Conclusion: The project now has the minimum regime + trend substrate needed before starting holding, exit, and strategy-family composition.
- Next Step: Implement `holding_engine.py`, `exit_guard.py`, and the first comparable Strategy A/B/C wrappers.

### JOURNAL-0005

- Date: 2026-03-28
- Author: Codex
- Title: Add holding, exit, and first-pass Strategy A/B/C composition
- Related Decision: DEC-0005
- Related Runs: 20260328T103341Z_26f09fc7
- Protocol Version: protocol_v1.0
- Hypothesis: The repo should assemble Strategy A/B/C by composing shared regime and trend modules, not by re-implementing buy/sell logic three times.
- What Changed: Added holding decisions, exit decisions, holding and exit modules, a shared mainline strategy base, three strategy-family wrappers, config placeholders, and tests that pin buy/sell behavior by layer.
- Expected Impact: Make the project capable of generating comparable strategy-family signals while preserving a single underlying research substrate.
- Observed Result: All tests passed, the demo run remained stable, and strategy tests confirmed that A/B/C differ only by hierarchy-layer exposure.
- Side Effects / Risks: The current strategy wrappers generate signals but are not yet wired into a full experiment pipeline that computes mainline-specific custom metrics.
- Conclusion: The project now has an end-to-end skeleton from regime selection to strategy-family signal generation, which is the minimum viable substrate for the next research round.
- Next Step: Implement richer metrics/reporting, especially `mainline_capture_ratio` and `missed_mainline_count`, then connect strategy runs into a more realistic experiment flow.

### JOURNAL-0006

- Date: 2026-03-28
- Author: Codex
- Title: Implement protocol-level custom mainline metrics
- Related Decision: DEC-0006
- Related Runs: 20260328T103505Z_edd50957
- Protocol Version: protocol_v1.0
- Hypothesis: The project should not postpone `mainline_capture_ratio` and `missed_mainline_count` indefinitely, because they express the core research objective more directly than generic return metrics.
- What Changed: Added a `MainlineWindow` model, implemented custom metric functions, and added unit tests that pin their current behavior.
- Expected Impact: Give the repo a concrete, testable definition for protocol-level mainline capture evaluation.
- Observed Result: All tests passed and the demo backbone remained stable after the metrics additions.
- Side Effects / Risks: The metrics are implemented but not yet injected into the normal backtest/reporting flow, because that still requires a richer strategy-run pipeline and explicit window generation.
- Conclusion: The custom metrics are now real code instead of future placeholders, which reduces protocol drift risk.
- Next Step: Build a more realistic strategy experiment runner that feeds mainline windows and strategy-family outputs into reporting.

### JOURNAL-0007

- Date: 2026-03-28
- Author: Codex
- Title: Connect shared modules into a normal strategy experiment pipeline
- Related Decision: DEC-0007
- Related Runs: 20260328T104137Z_0af22dea
- Protocol Version: protocol_v1.0
- Hypothesis: The repo needs a first real experiment pipeline so that regime outputs, trend candidates, strategy-family wrappers, and custom metrics all meet in one standard run artifact.
- What Changed: Added loaders for sector snapshots, stock snapshots, and mainline windows; implemented `StrategyExperimentRunner`; added a strategy experiment CLI, sample config/data, report extras, and an integration test.
- Expected Impact: Make the project capable of producing strategy-family reports that include `mainline_capture_ratio` and `missed_mainline_count`, not just generic PnL metrics.
- Observed Result: All tests passed, and the demo strategy experiment produced a completed run with custom metrics in the summary. The current sample output showed `mainline_capture_ratio=0.236343` and `missed_mainline_count=2`.
- Side Effects / Risks: The pipeline is still intentionally simple. It currently uses planned positions during signal generation and only demonstrates one segmentation path in the sample CLI.
- Conclusion: The repo now has a true end-to-end experiment path rather than a set of disconnected modules.
- Next Step: Improve experiment realism by making the runner more fill-aware, broadening segmentation support, and expanding report richness.

### JOURNAL-0008

- Date: 2026-03-28
- Author: Codex
- Title: Make Strategy A/B/C directly comparable under one suite run
- Related Decision: DEC-0008
- Related Runs: 20260328T104456Z_6acb2bfa
- Protocol Version: protocol_v1.0
- Hypothesis: The protocol is better enforced if A/B/C are compared by one runner and one report, not by three loosely coordinated commands.
- What Changed: Added suite support to the experiment runner, added a comparison report writer, created a strategy suite CLI/config, and added suite-level tests.
- Expected Impact: Reduce comparison drift and make strategy-family differences easier to evaluate under one shared context.
- Observed Result: The suite run completed successfully and showed a coherent ladder in signal count and capture metrics: A < B < C in exposure, with `mainline_trend_c` producing the highest total return and capture ratio in the sample suite.
- Side Effects / Risks: The suite output is useful but still concise. It does not yet include full per-strategy audit sections or richer analyst-oriented comparison views.
- Conclusion: The repo now supports a true same-frame A/B/C comparison path, which is a major step toward protocol-compliant experimentation.
- Next Step: Improve report richness and runner realism, especially actual fill-aware state handling and more detailed comparison artifacts.

### JOURNAL-0009

- Date: 2026-03-28
- Author: Codex
- Title: Make the experiment runner more fill-aware and the suite report more informative
- Related Decision: DEC-0009
- Related Runs: 20260328T104815Z_c1fd4941
- Protocol Version: protocol_v1.0
- Hypothesis: Strategy experiments become more trustworthy if pending fills are not treated as already-held positions, and suite reports become more useful if they attach explicit metric ranks instead of raw summaries alone.
- What Changed: Updated the runner to apply position changes only on the next fill date, block duplicate same-direction signals while a fill is pending, and added ranking fields plus richer aggregate summaries to suite comparison output.
- Expected Impact: Reduce hidden state drift between signal generation and execution, and make A/B/C comparison artifacts easier to consume directly.
- Observed Result: All tests passed after the runner change, including a regression case that verifies duplicate buys are blocked until the delayed fill arrives. The suite CLI continued to run successfully.
- Side Effects / Risks: The runner is still simplified relative to a full order management system; it does not yet simulate full pending-order lifecycle states beyond conservative blocking.
- Conclusion: The experiment pipeline is now materially closer to execution reality while still staying lightweight enough for the lab stage.
- Next Step: Expand suite reporting depth or start pushing the pipeline toward more realistic experiment datasets and richer segmentation choices.

### JOURNAL-0010

- Date: 2026-03-28
- Author: Codex
- Title: Make reports more useful for actual strategy comparison
- Related Decision: DEC-0010
- Related Runs: 20260328T105224Z_60adbf9e, 20260328T105224Z_b3c4e8f8
- Protocol Version: protocol_v1.0
- Hypothesis: Summary metrics alone are not enough for a serious research workflow; each report should also show which windows were captured, what was traded, and how active the regime gate was.
- What Changed: Added mainline-window breakdowns, segment overviews, and trade overviews to experiment results and exposed them in both single-strategy and suite report outputs.
- Expected Impact: Reduce friction when reviewing experiments and make the report artifacts themselves closer to protocol-compliant evidence.
- Observed Result: All tests passed, and the latest suite report now includes per-strategy ranking plus detailed breakdown fields. The latest single-strategy report includes generated signals, segment overview, trade overview, and per-window capture details.
- Side Effects / Risks: Reports are richer but still JSON-first; they are more informative than before but not yet optimized for polished human presentation.
- Conclusion: The experiment outputs are now substantially more reviewable without leaving the repository workflow.
- Next Step: Either add a more polished rendered report format or expand experiment realism further with additional segmentation modes and richer datasets.

### JOURNAL-0011

- Date: 2026-03-28
- Author: Codex
- Title: Make segmentation method an actual experiment choice instead of a hidden internal capability
- Related Decision: DEC-0011
- Related Runs: 20260328T105908Z_43bcc582, 20260328T105908Z_1163b0d4
- Protocol Version: protocol_v1.0
- Hypothesis: The repo better matches the protocol if experiment configs can directly choose `index_trend`, `sector_trend`, or `resonance`, rather than only exposing one method through the demo path.
- What Changed: Added `segmentation_method` to runner/config flow, added index sample bars, updated demo configs to use `resonance`, and added runner integration coverage for the richer segmentation path.
- Expected Impact: Make experiment setup closer to the documented research process and reduce hidden assumptions in the runner.
- Observed Result: All tests passed, and both the single-strategy and suite demo CLIs ran successfully with the richer segmentation setup.
- Side Effects / Risks: The demo now depends on one more input file for resonance-based runs, which slightly raises sample maintenance burden.
- Conclusion: Segmentation choice is now a real, explicit part of the experiment contract instead of a buried implementation detail.
- Next Step: Add experiments that compare segmentation methods directly, or enrich data/reporting enough to study which segmentation path performs best under the same strategy family.

### JOURNAL-0012

- Date: 2026-03-28
- Author: Codex
- Title: Build a real comparison path across segmentation methods
- Related Decision: DEC-0012
- Related Runs: 20260328T110151Z_31075b93
- Protocol Version: protocol_v1.0
- Hypothesis: The repo should allow one strategy family to compare `index_trend`, `sector_trend`, and `resonance` under one shared experiment contract, rather than relying on manual orchestration.
- What Changed: Added a segmentation comparison runner, a dedicated CLI/config, and tests that cover multi-method comparison output and ranking behavior.
- Expected Impact: Make segmentation-method research directly runnable and easier to review under the same strategy family.
- Observed Result: All tests passed and the segmentation comparison CLI completed successfully. In the current sample data, all three methods produced identical outcome summaries.
- Side Effects / Risks: The comparison workflow is correct, but the current sample dataset is not yet rich enough to show meaningful separation between methods; this is a data-design limitation, not a runner limitation.
- Conclusion: The repository now supports formal segmentation comparison, but the next real research need is richer data that can actually differentiate the methods.
- Next Step: Design more discriminative sample data or real experiment datasets where `index_trend`, `sector_trend`, and `resonance` produce meaningfully different segment sets and results.
