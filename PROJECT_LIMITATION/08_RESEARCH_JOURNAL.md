# A-Share Quant Research Journal

## 目的

本文件用于记录每次重要研究改动后的观察、结果和下一步计划�?
它不是结构化 run 注册表的替代品，而是面向人的研究叙述层�?
---

## 记录规则

以下情况至少应记录一�?journal�?
1. 协议版本升级
2. 样本切分逻辑变化
3. 主线定义或打分逻辑变化
4. 个股分层逻辑变化
5. 趋势过滤、入场、持有、退出逻辑变化
6. 成本、滑点、涨跌停成交模型变化
7. 出现显著结果提升或退�?8. 发现严重 bug、数据污染或结论反转

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

### JOURNAL-0013

- Date: 2026-03-28
- Author: Codex
- Title: Build the full strategy-by-segmentation comparison matrix
- Related Decision: DEC-0013
- Related Runs: 20260328T110729Z_d3ba5e4d
- Protocol Version: protocol_v1.0
- Hypothesis: Once strategy-family comparison and segmentation-method comparison both exist, the next useful research view is the full matrix across both dimensions.
- What Changed: Added a matrix comparison runner, CLI/config, tests, and a discriminative sample dataset that now produces materially different outcomes across segmentation methods.
- Expected Impact: Make the repo capable of answering a more realistic research question: which strategy family and segmentation method combination currently looks best under one shared protocol.
- Observed Result: All tests passed. The latest matrix run showed meaningful differentiation, with `mainline_trend_c @ sector_trend` as the best total-return and best-capture combination in the current sample data, while `mainline_trend_a @ index_trend` had the lowest drawdown.
- Side Effects / Risks: The matrix output is powerful but now fairly dense; future human-facing presentation may need something more readable than raw JSON.
- Conclusion: The framework side of the lab-stage system is now substantially complete for first-pass comparative research.
- Next Step: Either improve rendered reporting/presentation or pivot the main effort toward richer real datasets, protocol refinement, and repeated research cycles.

### JOURNAL-0014

- Date: 2026-03-28
- Author: Codex
- Title: Convert the next-step data discussion into a concrete storage and ingestion baseline
- Related Decision: DEC-0014
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: Real research will move faster and stay cleaner if the first canonical data pack, directory structure, and promotion order are defined before provider-specific ingestion code starts to grow.
- What Changed: Added a dedicated storage and ingestion plan, reserved `data/raw/`, `data/reference/`, `data/derived/`, and `data/external/`, and updated repo ignore rules so canonical data can be stored locally without polluting normal code diffs.
- Expected Impact: Reduce ambiguity around what data to collect first and where it should live, while preserving a clean separation between sample fixtures, canonical tables, and derived research products.
- Observed Result: The repo now has a clear answer to the practical question of which data is needed next and how it should be stored, without prematurely binding the project to one external vendor.
- Side Effects / Risks: The plan is intentionally provider-agnostic, so a first real-source integration may still force minor schema or partition-layout refinements.
- Conclusion: The project is now ready to shift from framework construction to actual data assembly with materially less risk of storage-layer drift.
- Next Step: Implement loader/adaptor support for canonical tables and begin collecting the six-table minimum dataset pack.

### JOURNAL-0015

- Date: 2026-03-28
- Author: Codex
- Title: Turn the LLM discussion into an explicit assistant-only policy for the lab stage
- Related Decision: DEC-0015
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The project can benefit from LLM assistance later, but only if the role boundary is written down before implementation pressure and AI enthusiasm blur the line between research assistance and signal authority.
- What Changed: Added an LLM assistant policy that defines allowed near-term uses, forbidden near-term uses, evidence hierarchy, logging requirements, and promotion barriers for any future LLM-assisted component.
- Expected Impact: Preserve room for later AI-enhanced research workflows without letting LLM outputs contaminate protocol-defined segmentation, hierarchy, metrics, or strategy promotion.
- Observed Result: The repo now has a clear governance answer to where LLM can help first: explanation, review, summarization, external-information digestion, and experiment critique.
- Side Effects / Risks: The policy deliberately blocks some attractive AI-first workflows until stronger validation and logging mechanisms exist.
- Conclusion: LLM is now treated as a controlled future assistant, not an implicit shortcut around the research stack.
- Next Step: Keep the current build focused on data assembly and baseline experiments; only revisit LLM implementation after the real-data pipeline is materially underway.

### JOURNAL-0016

- Date: 2026-03-28
- Author: Codex
- Title: Turn the free-data discussion into an actual bootstrap path
- Related Decision: DEC-0016
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The fastest safe way to leave sample-only data behind is to bootstrap a small real-data pack from a free source, but do it through a clearly temporary adapter layer rather than pretending the free source is already the final canonical truth.
- What Changed: Added an AKShare bootstrap module, a CLI script, a starter config, and an optional dependency group so the repo can export first-pass `daily_bars`, `index_daily_bars`, `trading_calendar`, and `security_master_lite` into the reserved local data directories.
- Expected Impact: Give the project an immediate path to test the real-data ingestion workflow without paying for a formal provider on day one.
- Observed Result: The bootstrap path was run successfully against live free-source endpoints. It produced local files for `daily_bars`, `index_daily_bars`, `trading_calendar`, and `security_master_lite`. The `security_master_lite` step had to fall back to configured symbols only because the upstream SZSE code-list endpoint timed out, but the overall bootstrap still completed and confirmed that the repo can now leave sample-only data behind.
- Side Effects / Risks: The bootstrap output still needs field validation, `security_master_lite` is intentionally weaker than the final canonical reference table required by the long-term data contract, and the current Anaconda environment emits noisy NumPy-compatibility warnings from optional pandas acceleration modules during AKShare imports.
- Conclusion: The project has crossed from “free-data idea�?into “free-data ingestion path,�?but this remains a bootstrap stage rather than the final data architecture.
- Next Step: Install the optional dependency, run the bootstrap script, inspect the exported fields, and then implement canonical loaders that read these local tables.

### JOURNAL-0017

- Date: 2026-03-28
- Author: Codex
- Title: Put the bootstrapped free tables onto a real executable path
- Related Decision: DEC-0017
- Related Runs: 20260328T134553Z_caa626ed
- Protocol Version: protocol_v1.0
- Hypothesis: The project will learn more by wiring the first bootstrapped local tables into an actual runnable code path than by waiting for the full derived-data stack to exist before any integration happens.
- What Changed: Added canonical loaders for `trading_calendar` and `security_master`, added a bootstrap-backed backtest config and simple matching signals, and documented the current boundary: basic backtests can now use local real bars, but full strategy experiments still require real derived tables that do not yet exist.
- Expected Impact: Reduce the gap between “data was downloaded�?and “data is actually used by the repo,�?while making the next missing layer explicit.
- Observed Result: The repository now has a concrete local-real-data backtest path instead of only sample-fixture runs and separate bootstrap outputs. The first bootstrap-backed baseline run completed as `20260328T134553Z_caa626ed` using `data/raw/daily_bars/akshare_daily_bars_bootstrap.csv`, with `fill_count=4`, `closed_trade_count=2`, `total_return=-0.000343`, and `max_drawdown=0.000346`.
- Side Effects / Risks: The system is now intentionally in a transitional mixed mode; users can run backtests on bootstrapped bars, but should not confuse that with a fully real-data protocol pipeline yet.
- Conclusion: Real-data integration is now underway in the main code path rather than being isolated to a bootstrap script.
- Next Step: Generate or ingest real `sector_snapshots`, `stock_snapshots`, and `mainline_windows`, then move strategy experiments off sample fixtures as well.

### JOURNAL-0018

- Date: 2026-03-28
- Author: Codex
- Title: Create a temporary derived-data bridge from local bars to strategy experiments
- Related Decision: DEC-0018
- Related Runs: 20260328T135433Z_2fa99fee, 20260328T135433Z_76dcbcba
- Protocol Version: protocol_v1.0
- Hypothesis: Even heuristic derived tables are useful at this stage if they are clearly labeled as bootstrap-only and they let the strategy experiment chain start exercising local real bars instead of remaining trapped on sample fixtures.
- What Changed: Added a bootstrap-derived generator, a manual sector-assignment config, output paths for `sector_mapping_daily`, `sector_snapshots`, `stock_snapshots`, and `mainline_windows`, plus dedicated strategy-experiment and strategy-suite configs that point to those generated files.
- Expected Impact: Shrink the gap between the free bootstrap data layer and the higher-level strategy experiment runner.
- Observed Result: The derived-data generator completed successfully against the local AKShare bars, and the bootstrap-backed strategy experiment completed as `20260328T135433Z_2fa99fee` with `signal_count=128`, `closed_trade_count=63`, `mainline_capture_ratio=0.441295`, and `missed_mainline_count=33`. The bootstrap-backed strategy suite also ran as `20260328T135433Z_76dcbcba`, but all three families produced identical summaries, which confirms the bridge works while also showing that the provisional derived layer is still too coarse to separate A/B/C meaningfully.
- Side Effects / Risks: The generated sectors, stock hierarchy inputs, and windows are heuristics and can support plumbing validation, but they are not yet strong enough to justify serious strategy claims.
- Conclusion: The repo now has a transitional bridge from local bars to strategy experiments, which is the right next step before deeper data-governance refinement.
- Next Step: Tighten the derived-data generation logic so hierarchy and mainline assignment produce more realistic A/B/C separation, or replace the bootstrap heuristics with stronger mapping and snapshot sources.

### JOURNAL-0019

- Date: 2026-03-28
- Author: Codex
- Title: Upgrade the bootstrap sector mapping from manual placeholders to CNInfo industry history
- Related Decision: DEC-0019
- Related Runs: 20260328T140237Z_69ecbb95, 20260328T140238Z_0143987f
- Protocol Version: protocol_v1.0
- Hypothesis: The fastest way to make the free-data strategy path more realistic is not to perfect every derived formula at once, but to improve the weakest upstream input first, which was the hand-written sector mapping.
- What Changed: Added a `sector_mapper` module and a `bootstrap_sector_mapping.py` script that use CNInfo industry-change history through AKShare to generate a daily `sector_mapping_daily` table. Updated the bootstrap-derived generator so it prefers this mapping table when present.
- Expected Impact: Make sector attribution more traceable and reduce one of the most artificial parts of the bootstrap-derived research chain.
- Observed Result: The CNInfo mapping bootstrap generated `726` daily mapping rows for the current local bootstrap bars. After regenerating derived tables, the bootstrap-backed strategy experiment completed as `20260328T140237Z_69ecbb95` with `signal_count=132`, `closed_trade_count=65`, and `mainline_capture_ratio=0.417165`. The bootstrap-backed suite run `20260328T140238Z_0143987f` now shows meaningful family separation: `mainline_trend_a` has the best total return and lowest drawdown in this provisional setup, while `mainline_trend_b` has the best capture ratio.
- Side Effects / Risks: Some early dates remain `UNKNOWN` because the free CNInfo history does not always provide an immediately usable backfilled classification for every symbol across the whole window.
- Conclusion: The free-data path now has a materially better daily sector mapping source, and that improvement is already visible in the strategy-family comparison outputs.
- Next Step: Improve `UNKNOWN` backfill behavior and refine the derived snapshot logic so the mapping upgrade translates into stronger hierarchy and window quality.

### JOURNAL-0020

- Date: 2026-03-28
- Author: Codex
- Title: Make the bootstrap-derived hierarchy less one-dimensional by adding sector-relative stock ranking
- Related Decision: DEC-0020
- Related Runs: 20260328T141400Z_78c73530, 20260328T141908Z_c223ab10
- Protocol Version: protocol_v1.0
- Hypothesis: The next bottleneck in the free-data path is no longer sector attribution but stock-layer construction. If `late_mover_quality` keeps using only coarse absolute features, Strategy C will remain a near-duplicate of Strategy B because the derived layer will almost never emit genuine `late_mover` candidates.
- What Changed: Reworked bootstrap-derived `stock_snapshots` so `expected_upside`, `drive_strength`, `liquidity`, and especially `late_mover_quality` now blend absolute values with per-sector relative ranks. Added a regression test that forces a three-name same-sector case to classify as `leader`, `core`, and `late_mover` instead of collapsing back into `junk`.
- Expected Impact: Increase the share of plausible `late_mover` assignments in the bootstrap-derived research inputs and create more meaningful separation between Strategy B and Strategy C on local free data.
- Observed Result: After regenerating the derived tables, the hierarchy distribution shifted from `leader=440 / core=200 / late_mover=9 / junk=1287` to `leader=776 / core=210 / late_mover=70 / junk=880`. The rerun suite `20260328T141908Z_c223ab10` now shows `mainline_trend_c` as the best capture strategy with `mainline_capture_ratio=0.304235`, while `mainline_trend_a` still leads on total return and drawdown. This is materially closer to the intended A/B/C family behavior than the earlier near-duplicate B/C state in `20260328T141400Z_78c73530`.
- Side Effects / Risks: The free-data bootstrap still has a tiny universe and an uneven sector mix, so the new late-mover assignments should be treated as plumbing-level realism gains, not as evidence that the research protocol has already found a valid tradable edge.
- Conclusion: The free-data path now has enough internal structure to support more credible family-comparison experiments instead of only demonstrating end-to-end wiring.
- Next Step: Expand the bootstrap universe further, reduce single-name sectors, and start using these richer derived tables to design the first real baseline experiment batch.

### JOURNAL-0021

- Date: 2026-03-28
- Author: Codex
- Title: Turn "data preparation" into a measurable gate instead of a vague feeling
- Related Decision: DEC-0021
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The right next move after the richer bootstrap-derived hierarchy is not more strategy complexity, but a hard inventory of the data layer. Without that, the lab can drift into writing strategy code on top of half-finished canonical tables.
- What Changed: Added a data-pack audit module, CLI, config, and tests. Upgraded the free `security_master` bootstrap so configured symbols now include `list_date`, and used the same source to stop exporting all-zero `listed_days` in bootstrap `daily_bars`.
- Expected Impact: Make data readiness explicit and shrink the gap between "bootstrap files exist" and "canonical tables are genuinely usable."
- Observed Result: The audit report now lives at `reports/data/bootstrap_data_audit.json`. On the current local bootstrap pack it reports `canonical_ready_count=3`, `canonical_partial_count=2`, and `canonical_missing_count=1`. After the security-master upgrade, `security_master` moved from partial to ready. The remaining canonical blockers are now sharply defined: `adjustment_factors` is still missing, while `daily_bars` remains partial because `adjust_factor` is still a placeholder and `sector_mapping_daily` remains partial because it is still explicitly bootstrap-grade.
- Side Effects / Risks: Running the full free bootstrap can still be interrupted by slow upstream index endpoints, so targeted re-exports of individual tables are currently safer than always rerunning the entire bundle.
- Conclusion: The project now has a real data-readiness checkpoint. "Prepare the data first" is no longer just a principle; it is now an auditable state with concrete remaining gaps.
- Next Step: Focus the next data iteration on a real `adjustment_factors` path and keep using the audit report as the gate before claiming the canonical pack is baseline-ready.

### JOURNAL-0022

- Date: 2026-03-28
- Author: Codex
- Title: Close the biggest canonical data gap by adding a real qfq adjustment-factor path
- Related Decision: DEC-0022
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: Once `adjustment_factors` becomes a real sourced table instead of a missing requirement, the bootstrap pack can move much closer to a defensible baseline data state, even if some mappings still remain explicitly bootstrap-grade.
- What Changed: Added `adjustment_factors_filename` to the free bootstrap config, taught the bootstrapper to export a per-day factor table from AKShare `qfq-factor` events, and reused those factors when writing `daily_bars.adjust_factor`. Verified the interval semantics against raw vs qfq prices before fixing the expansion rule.
- Expected Impact: Remove the largest remaining canonical-table hole and stop treating `adjust_factor` as a dummy field inside the local bars.
- Observed Result: The audit report advanced from `canonical_ready_count=3 / canonical_partial_count=2 / canonical_missing_count=1` to `canonical_ready_count=5 / canonical_partial_count=1 / canonical_missing_count=0`. `daily_bars`, `security_master`, and `adjustment_factors` are now all marked ready. The only remaining bootstrap-partial canonical table is `sector_mapping_daily`, which is partial by design because the current CNInfo mapping is still explicitly a free-data bootstrap layer.
- Side Effects / Risks: The environment still emits noisy NumPy-compatibility warnings during AKShare imports, and some targeted exports are safer than full-bundle reruns because unrelated upstream endpoints can time out.
- Conclusion: The data-preparation phase just crossed an important threshold: the canonical pack is no longer missing any required table, and the remaining incompleteness is now concentrated in mapping quality rather than missing schema pieces.
- Next Step: Improve `sector_mapping_daily` toward concept/theme-aware coverage and keep the audit report as the gate for declaring the bootstrap data pack baseline-ready.

### JOURNAL-0023

- Date: 2026-03-28
- Author: Codex
- Title: Build the concept/theme mapping path even though the current bootstrap universe is not concept-rich enough yet
- Related Decision: DEC-0023
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: Even before the concept layer produces many useful rows, the project still benefits from getting the architecture right: a separate `concept_mapping_daily` table, dedicated bootstrap script, dedicated loader, audit visibility, and an optional concept-first overlay in the derived mapping stage.
- What Changed: Added a concept mapper module and bootstrap script, added `concept_mapping_daily` loader and audit coverage, and updated bootstrap-derived mapping so primary concept mappings can override industry mappings when concept coverage exists.
- Expected Impact: Make the repo structurally ready for theme-aware A-share research instead of hardwiring industry mapping as the final answer.
- Observed Result: The code path works and the table is now part of the audited data pack, but the first real bootstrap run on the current eight-stock universe produced `0` concept rows. This is consistent with the current local universe being dominated by large-cap banking, property, insurance, and liquor names rather than the kind of theme-driven symbols where Eastmoney concept-board membership is more likely to be informative.
- Side Effects / Risks: If someone only looks at the empty concept table without understanding the universe composition, they might misread it as a failure of the concept-mapping architecture rather than a limitation of the current bootstrap sample.
- Conclusion: The repo now has the correct place for concept/theme mappings, but the next gain will come from feeding it a more concept-relevant symbol set rather than writing more concept-plumbing code.
- Next Step: Expand or fork the bootstrap universe with a more theme-sensitive sample set so the new concept layer can start contributing real signal separation.

### JOURNAL-0024

- Date: 2026-03-28
- Author: Codex
- Title: Validate the concept layer on a dedicated theme-driven bootstrap universe
- Related Decision: DEC-0024
- Related Runs: 20260328T152016Z_99cb04e8
- Protocol Version: protocol_v1.0
- Hypothesis: The empty concept table on the original bootstrap universe was a sample-selection problem, not an architectural problem. A separate topic-driven validation pack should produce non-empty concept mappings and more meaningful concept-aware strategy-family behavior without disturbing the original baseline bootstrap set.
- What Changed: Added a parallel `theme_bootstrap_*` config family, generated a theme-oriented local data pack, generated CNInfo industry mappings plus Eastmoney concept mappings for that universe, and fed those concept-aware mappings through the same bootstrap-derived and strategy-suite pipeline.
- Expected Impact: Provide a proof path that concept-aware mappings can materially exist and flow through the research system before the project commits to folding them into the broader baseline universe.
- Observed Result: The theme concept mapping table now contains `1936` rows across `7` symbols and `3` concepts, with the biggest concepts being `锂矿概念`, `减肥药`, and `创新药`. The theme data-pack audit at `reports/data/theme_bootstrap_data_audit.json` reaches `canonical_ready_count=6`, `canonical_partial_count=0`, `canonical_missing_count=0`, and `baseline_ready=true`. The theme strategy suite run `20260328T152016Z_99cb04e8` shows `mainline_trend_c` as both `best_total_return_strategy` and `best_capture_strategy`, which is exactly the kind of structural difference the concept layer was meant to make easier to observe.
- Side Effects / Risks: This is still a small curated theme sample, so the improved concept coverage should be read as validation of the architecture and data path, not as a market-wide edge claim.
- Conclusion: The concept layer is now empirically validated on a suitable sample set. The earlier zero-row concept result was a universe-choice issue, not a failed design.
- Next Step: Decide whether to selectively merge some theme-sensitive symbols into the main bootstrap universe or to keep a two-pack workflow where the original baseline and the theme-validation pack serve different research purposes.

### JOURNAL-0025

- Date: 2026-03-28
- Author: Codex
- Title: Make the baseline-vs-theme tradeoff visible instead of debating it abstractly
- Related Decision: DEC-0025
- Related Runs: 20260328T152618Z_855f3bd4
- Protocol Version: protocol_v1.0
- Hypothesis: Before merging the theme-sensitive universe into the main baseline workflow, the project should first verify whether the two packs are actually emphasizing different strategy families in a useful way.
- What Changed: Added a dataset-comparison runner and report path that compare baseline and theme bootstrap suites under one shared run, rather than reading two separate suite reports manually.
- Expected Impact: Turn the question "should we merge the universes?" into an evidence-based decision rather than a preference.
- Observed Result: The cross-dataset comparison run `20260328T152618Z_855f3bd4` shows a clean split. On `baseline_bootstrap`, `mainline_trend_a` remains the best total-return strategy. On `theme_bootstrap`, `mainline_trend_c` becomes the best capture strategy and also the best total-return strategy within that pack. The aggregate summary therefore points to `baseline_bootstrap + mainline_trend_a` for best return overall, but `theme_bootstrap + mainline_trend_c` for best capture.
- Side Effects / Risks: These are still small packs, so the comparison should be treated as a structural signal about how the data layers change strategy-family preferences, not as a final investment claim.
- Conclusion: Keeping the two-pack workflow is currently the right decision. The comparison shows they are not redundant; they highlight different strategy strengths.
- Next Step: Continue using the baseline pack as the stable industry-heavy control, and use the theme pack to refine concept-aware research rules before any future selective merge.

### JOURNAL-0026

- Date: 2026-03-28
- Author: Codex
- Title: Move from pack comparison to cross-pack rule screening
- Related Decision: DEC-0026
- Related Runs: 20260329T025326Z_54108c98
- Protocol Version: protocol_v1.0
- Hypothesis: Once baseline and theme packs are both running, the next useful question is no longer which pack prefers A or C, but which named rule candidates remain competitive across both packs at the same time.
- What Changed: Added a `rule_sweep` module, CLI, config, and tests. Each candidate is now a named nested override on top of the dataset pack's base suite config, which means the lab can compare `control_v1`, `strict_quality`, and `expansion_capture` under one shared cross-pack report without duplicating full YAML stacks.
- Expected Impact: Turn the next stage of protocol iteration into repeatable batch screening instead of one-off manual config editing.
- Observed Result: The first rule sweep completed as `20260329T025326Z_54108c98` with `18` comparison rows across `2` datasets, `3` strategies, and `3` candidates. `baseline_bootstrap + expansion_capture + mainline_trend_a` achieved the best single-row total return, while `theme_bootstrap + control_v1 + mainline_trend_c` achieved the best capture. On the aggregate candidate leaderboard, `control_v1` came out as the most stable candidate with `composite_rank_score=25.166667`, beating `expansion_capture` and `strict_quality` on average cross-pack rank even though it did not win every single row.
- Side Effects / Risks: The current leaderboard is still lab-stage and depends on two small curated packs, so "most stable" should be read as "most internally robust in the current research sandbox," not as a production promotion signal.
- Conclusion: The repo now has the right next-layer mechanism for disciplined rule research. We no longer need to choose between "keep the packs separate" and "stop iterating"; the packs can now be used together to pressure-test rule changes.
- Next Step: Expand the candidate set deliberately, especially around trend-filter windows, hierarchy thresholds, and holding strictness, and keep default configs unchanged until a candidate remains strong across both packs over multiple sweeps.

### JOURNAL-0027

- Date: 2026-03-28
- Author: Codex
- Title: Expand the theme-side sample coverage with versioned universe files instead of bloated YAML lists
- Related Decision: DEC-0027
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The next meaningful data gain is not a blind jump to full-market scale, but a controlled expansion of the current research watchlists. The right first move is to make those watchlists versioned and file-based so that coverage can increase without destabilizing the config layer.
- What Changed: Added symbol-file support to the free-data bootstrap config, created `config/universes/baseline_research_v1.txt`, `config/universes/theme_research_v1.txt`, and `config/universes/common_indices_v1.txt`, and added dedicated research-pack bootstrap configs. Then bootstrapped the larger theme research pack and ran a fresh concept-mapping pass against it.
- Expected Impact: Increase concept-layer coverage while keeping the original smaller lab packs intact for continuity.
- Observed Result: The larger theme watchlist bootstrap completed and wrote `akshare_daily_bars_theme_research_v1.csv`, `akshare_adjustment_factors_theme_research_v1.csv`, and `akshare_security_master_theme_research_v1.csv`. The security-master endpoint still hit a connection reset once, but the fallback path worked and did not block the pack. The follow-up concept mapping wrote `theme_research_concept_mapping_v1.csv` with `3136` rows across `12` symbols and `4` concepts. Compared with the earlier theme bootstrap pack (`1936` rows, `7` symbols, `3` concepts), the larger research watchlist materially improved theme coverage and added `CRO` on top of `锂矿概念`, `创新药`, and `减肥药`.
- Side Effects / Risks: The free providers still emit noisy NumPy-compatibility warnings and occasionally reset long-running reference requests, so the expanded pack is more useful but not yet "push-button reliable."
- Conclusion: Sample coverage is now moving in the right direction for the theme side. The repo can grow the research universe without turning configuration management into a mess, and the concept layer responds immediately when the watchlist quality improves.
- Next Step: Add the corresponding derived/suite/audit configs for the larger research packs and start comparing whether the larger theme pack changes the A/B/C family preferences or just reinforces the existing pattern.

### JOURNAL-0028

- Date: 2026-03-28
- Author: Codex
- Title: Convert the larger watchlists into full research packs and see what actually changes
- Related Decision: DEC-0028
- Related Runs: 20260329T030906Z_e45938a1, 20260329T031504Z_f8b47b78, 20260329T031505Z_7fdb1ea8
- Protocol Version: protocol_v1.0
- Hypothesis: Once the larger research watchlists are pushed through the full `sector_mapping -> derived -> suite -> audit` flow, the repo should be able to distinguish whether the next real bottleneck is still sample coverage or has moved into the heuristic derived layer.
- What Changed: Added full research-pack configs for baseline and theme, ran the complete theme research flow, then completed the same flow for the larger baseline research pack and compared the two under one dataset-comparison report.
- Expected Impact: Replace small-pack-only conclusions with a broader first-pass view.
- Observed Result: The larger `theme_research_v1` pack now audits as `baseline_ready=true` and runs end-to-end, but the current derived layer collapses A/B/C into the same result there: `total_return=-0.000286`, `mainline_capture_ratio=0.524624`, `signal_count=44` for all three families in run `20260329T030906Z_e45938a1`. The larger `baseline_research_v1` pack also audits as `baseline_ready=true` and produces much richer separation in run `20260329T031504Z_f8b47b78`: `mainline_trend_a` leads on return (`0.011058`) and drawdown, while `mainline_trend_b` and `mainline_trend_c` improve capture (`0.477081` versus `0.354106`). The cross-pack comparison `20260329T031505Z_7fdb1ea8` therefore shows `baseline_research_v1 + mainline_trend_a` as the best total-return row and `theme_research_v1 + mainline_trend_a` as the best capture row.
- Side Effects / Risks: The theme-side collapse means the current concept-aware derived heuristics are still not separating hierarchy layers strongly enough once the watchlist broadens, even though concept coverage itself improved.
- Conclusion: The repo has now crossed a useful threshold. Sample coverage is no longer the only story; on the larger theme pack, the next bottleneck is clearly the quality of the derived/hierarchy layer rather than the absence of concept data.
- Next Step: Use the larger packs as the new research reference and focus the next protocol iteration on restoring A/B/C differentiation in the theme research pack without giving up the broader concept coverage.

### JOURNAL-0029

- Date: 2026-03-28
- Author: Codex
- Title: Re-run rule screening on the larger research packs and accept that the ranking can change
- Related Decision: DEC-0029
- Related Runs: 20260329T031533Z_b92f4ff0
- Protocol Version: protocol_v1.0
- Hypothesis: If the small-pack sweep identified `control_v1` as the most stable candidate only because the samples were too narrow, then the larger research packs should be able to overturn that ranking.
- What Changed: Added `research_rule_sweep.yaml` and reran the same three named candidates (`control_v1`, `strict_quality`, `expansion_capture`) on the larger `baseline_research_v1` and `theme_research_v1` packs.
- Expected Impact: Tell us whether the first rule-sweep ranking was structurally stable or just a small-sample artifact.
- Observed Result: The ranking changed materially. On the larger research packs, run `20260329T031533Z_b92f4ff0` made `expansion_capture` the most stable candidate with `composite_rank_score=24.0`, ahead of `strict_quality` and `control_v1`. It also captured both the best total-return row (`baseline_research_v1 + expansion_capture + mainline_trend_a`) and the best capture row (`theme_research_v1 + expansion_capture + mainline_trend_a`). By contrast, the earlier small-pack sweep had favored `control_v1`.
- Side Effects / Risks: Because the larger theme pack still collapses A/B/C under the current derived layer, part of this ranking shift may still reflect model-structure limitations rather than pure market truth.
- Conclusion: The project just got an important negative result in the right way: the small-pack rule ranking did not fully generalize. That is useful, because it tells us not to promote default rules off the smaller packs alone.
- Next Step: Keep both sweep layers, but treat the larger-pack sweep as the more important signal and prioritize theme-side hierarchy refinement before changing the default candidate set.

### JOURNAL-0030

- Date: 2026-03-28
- Author: Codex
- Title: Separate a real theme-pack conclusion from a stale-output artifact
- Related Decision: DEC-0030
- Related Runs: 20260329T032028Z_f351ecd3, 20260329T032028Z_f460adb6, 20260329T032028Z_b0c6a7ed, 20260329T032116Z_29515aab
- Protocol Version: protocol_v1.0
- Hypothesis: The earlier "theme research pack collapses A/B/C" conclusion may be contaminated by refresh order rather than by the hierarchy logic itself.
- What Changed: Re-checked the generated files directly, found that the stale `theme_research_sector_mapping_daily_v1.csv` and `theme_research_stock_snapshots_v1.csv` had been carrying only `242` rows and `1` symbol even though the in-memory builder produced `3136` rows and `13` symbols. Added a sequential `refresh_research_pack.py` helper and rebuilt the theme research pack in order.
- Expected Impact: Remove stale intermediate-output risk from the larger research-pack loop and re-evaluate the theme-side result on a clean rebuild.
- Observed Result: After a clean rebuild, the theme research pack no longer collapses. In run `20260329T032028Z_f351ecd3`, `mainline_trend_b` became the best total-return strategy, `mainline_trend_c` became the best capture strategy, and `mainline_trend_a` kept the lowest drawdown. The refreshed cross-pack comparison `20260329T032028Z_f460adb6` now shows `baseline_research_v1 + mainline_trend_a` as the best overall return row, while the theme research pack cleanly expresses its own A/B/C tradeoff instead of flattening. The refreshed larger-pack rule sweep `20260329T032028Z_b0c6a7ed` also changed again: `control_v1` recovered a narrow stability lead over `strict_quality` and `expansion_capture`, which means the prior larger-pack `expansion_capture` lead was also contaminated by stale theme outputs.
- Side Effects / Risks: The broader lesson is uncomfortable but useful: once the project runs multi-step local pipelines, local stale-output contamination can mimic a real research conclusion if refresh order is not controlled.
- Conclusion: The real bottleneck is no longer "theme pack lacks differentiation." The corrected result shows that the current larger theme pack does differentiate A/B/C, and the repo needed a sequencing fix more than another immediate hierarchy formula rewrite.
- Next Step: Use the sequential refresh helper for future research-pack rebuilds, treat the corrected larger-pack results as the new baseline, and only revisit theme-side hierarchy formulas if they still underperform after further clean sweeps.

### JOURNAL-0031

- Date: 2026-03-28
- Author: Codex
- Title: Expand the larger-pack candidate screen and let the two packs disagree on purpose
- Related Decision: DEC-0031
- Related Runs: 20260329T032409Z_f039e3dc
- Protocol Version: protocol_v1.0
- Hypothesis: Once the larger packs are clean, the next useful step is not a code rewrite but a richer candidate screen. If baseline and theme packs genuinely prefer different rule families, the sweep should expose that split instead of hiding it inside one blended leaderboard.
- What Changed: Added `research_rule_sweep_v2.yaml` and screened six candidates on the larger research packs: `control_v1`, `strict_quality`, `expansion_capture`, `fast_entry_relaxed_hold`, `patient_hold_bias`, and `repair_breakout_focus`.
- Expected Impact: Identify whether the next profitable direction is more likely to come from faster entry, looser expansion capture, stricter quality selection, or more patient holding behavior.
- Observed Result: The aggregate leaderboard still gave a narrow edge to `control_v1`, with `expansion_capture` extremely close behind. But the more important result is the pack split. On `baseline_research_v1`, `expansion_capture + mainline_trend_a` produced the best total-return row (`0.013454`) and `expansion_capture + mainline_trend_b` produced the best capture row (`0.505337`). On `theme_research_v1`, `strict_quality + mainline_trend_c` produced the best total-return row (`0.005358`) while `strict_quality + mainline_trend_a` produced the lowest drawdown (`0.002326`); meanwhile the best capture row there remained `control_v1 + mainline_trend_c` (`0.360507`).
- Side Effects / Risks: The expanded candidates still bundle several parameter moves together, so this run tells us which direction to investigate next, not which single knob caused the improvement.
- Conclusion: The larger packs are now disagreeing in an informative way. The baseline pack currently rewards broader expansion capture, while the theme pack rewards stricter quality on return/drawdown and still needs the control rule set for maximum capture.
- Next Step: Split the next follow-up sweeps by intent: one baseline-oriented branch around expansion/entry breadth, and one theme-oriented branch around quality/holding discipline, instead of forcing a single new default candidate too early.

### JOURNAL-0032

- Date: 2026-03-28
- Author: Codex
- Title: Confirm the split by running narrower single-pack sweeps
- Related Decision: DEC-0032
- Related Runs: 20260329T032659Z_e42d39bb, 20260329T032700Z_312321e7
- Protocol Version: protocol_v1.0
- Hypothesis: If the broader v2 sweep is pointing in the right direction, then a baseline-only expansion sweep and a theme-only quality sweep should each produce a cleaner local ranking than the mixed multi-pack leaderboard.
- What Changed: Added and ran `baseline_expansion_sweep.yaml` on `baseline_research_v1` and `theme_quality_sweep.yaml` on `theme_research_v1`.
- Expected Impact: Reduce the next iteration problem from "find one candidate for everything" to "find the best local next move for each research branch."
- Observed Result: The baseline-only expansion sweep `20260329T032659Z_e42d39bb` produced an effective tie at the top between `broad_late_mover` and `expansion_capture` on composite rank (`15.666666` each). `expansion_capture` still owns the best return row and best capture row, while `broad_late_mover` owns the best drawdown row, which suggests the next baseline branch should focus on the tradeoff between wider diffusion capture and slightly more selective late-mover admission. The theme-only quality sweep `20260329T032700Z_312321e7` was cleaner: `strict_quality` became the clear leader with `composite_rank_score=16.0`, beating `selective_entry`, `strict_hold_focus`, and `control_v1`. It also owned the best return row (`strict_quality + mainline_trend_c`) and the best drawdown row (`strict_quality + mainline_trend_a`), while `control_v1 + mainline_trend_c` kept the best capture row.
- Side Effects / Risks: These narrower sweeps improve local interpretability, but they are intentionally no longer cross-pack balanced. A candidate that wins a local branch still has to survive broader comparison before promotion.
- Conclusion: The split is now confirmed. The baseline branch should keep refining expansion breadth versus late-mover breadth, and the theme branch should keep refining strict quality rather than shifting back toward loose expansion.
- Next Step: Design one follow-up sweep that isolates the baseline tradeoff (`expansion_capture` vs `broad_late_mover`) and another that isolates the theme tradeoff (`strict_quality` vs `selective_entry`) with fewer simultaneous parameter moves per candidate.

### JOURNAL-0033

- Date: 2026-03-28
- Author: Codex
- Title: Turn the local sweep winners into executable branch baselines
- Related Decision: DEC-0033
- Related Runs: 20260329T033222Z_3ca87220, 20260329T033222Z_137654fb
- Protocol Version: protocol_v1.0
- Hypothesis: If the local branch winners are real and not just leaderboard artifacts, they should reproduce cleanly when moved from sweep configs into standalone suite configs.
- What Changed: Added `baseline_research_strategy_suite_expansion.yaml` and `theme_research_strategy_suite_strict_quality.yaml`, then ran both directly through the standard strategy-suite CLI.
- Expected Impact: Make the current local best-known branches reusable for future comparisons without redefining the shared default research configs.
- Observed Result: The branch-local suites behaved as expected. `baseline_research_strategy_suite_expansion.yaml` reproduced the baseline branch profile in run `20260329T033222Z_3ca87220`: `mainline_trend_a` kept the best total return (`0.013454`), while `mainline_trend_b` improved capture (`0.505337`). `theme_research_strategy_suite_strict_quality.yaml` reproduced the theme branch profile in run `20260329T033222Z_137654fb`: `mainline_trend_c` became both the best return (`0.005358`) and best capture (`0.221473`) strategy inside that stricter-quality branch, while `mainline_trend_a` kept the lowest drawdown (`0.002326`).
- Side Effects / Risks: These branch-local baselines are useful, but they are not promoted defaults. Promoting them too early would erase the distinction between "shared default" and "best local branch so far."
- Conclusion: The repo now has a cleaner research cadence. Shared defaults remain intact, while the current best-known local branches are executable first-class artifacts instead of conclusions buried in reports.
- Next Step: Keep refining the branch baselines locally, then test whether either branch can survive broader cross-pack comparison strongly enough to justify promotion into the shared defaults.

### JOURNAL-0034

- Date: 2026-03-28
- Author: Codex
- Title: Check whether the branch-local winners survive one more round of narrow refinement
- Related Decision: DEC-0034
- Related Runs: 20260329T033635Z_1e1f73ea, 20260329T033635Z_fe440fe2
- Protocol Version: protocol_v1.0
- Hypothesis: If the current branch-local winners are only temporary bundle artifacts, then one more narrow pass around them should produce a nearby challenger that clearly overtakes them on local stability.
- What Changed: Added `baseline_expansion_refinement_sweep.yaml` on top of `baseline_research_strategy_suite_expansion.yaml` and `theme_strict_quality_refinement_sweep.yaml` on top of `theme_research_strategy_suite_strict_quality.yaml`. The baseline refinement tested slightly stronger regime gating, slightly tighter hold discipline, slight late-mover trimming, and faster breakout timing. The theme refinement tested slight quality relief, faster entry, lighter hold discipline, and smaller score-margin relief.
- Expected Impact: Determine whether the current branch-local baselines are already reasonably centered, or whether there is an obvious nearby tweak worth materializing as the new branch config.
- Observed Result: The branch controls held. On the baseline branch, run `20260329T033635Z_1e1f73ea` kept `expansion_branch_control` as the most stable candidate with `composite_rank_score=17.333333`, even though `expansion_regime_guard + mainline_trend_a` produced the best single total-return row and `expansion_trimmed_late_mover + mainline_trend_a` produced the best single drawdown row. On the theme branch, run `20260329T033635Z_fe440fe2` kept `strict_quality_branch_control` as the most stable candidate with `composite_rank_score=19.333334`; `strict_quality_capture_relief + mainline_trend_c` improved the best capture row, but it gave back enough return/drawdown quality that it did not overtake the control candidate overall.
- Side Effects / Risks: This is a useful stabilizing result, but it also means the easy nearby gains may already be mostly harvested. Future improvement may require either better data/derived quality or a somewhat wider search again, rather than endlessly nudging the same few thresholds.
- Conclusion: The current branch-local baselines remain the right anchors. The repo did not discover a clearly superior nearby challenger in this refinement pass.
- Next Step: Keep the current branch baselines in place and decide whether the next loop should widen the candidate search again, or focus on one deeper knob at a time such as regime margin on baseline or quality gating versus capture relief on theme.

### JOURNAL-0035

- Date: 2026-03-28
- Author: Codex
- Title: Discover that the best cross-pack compromise candidate is not the same as the best local branch winner
- Related Decision: DEC-0035
- Related Runs: 20260329T033806Z_53e93bde
- Protocol Version: protocol_v1.0
- Hypothesis: The branch-local winners may still fail to be the best wider shared-default challengers once they are forced back into the two-pack comparison frame against the shared default.
- What Changed: Added `branch_promotion_check.yaml` and compared five candidates across `baseline_research_v1` and `theme_research_v1`: `shared_default`, `baseline_expansion_branch`, `theme_strict_quality_branch`, `baseline_expansion_regime_guard`, and `theme_capture_relief_branch`.
- Expected Impact: Tell the project whether the next default-promotion conversation should revolve around one of the local branch winners, or around a milder compromise candidate that survives both packs more cleanly.
- Observed Result: Run `20260329T033806Z_53e93bde` produced a useful split. The best single total-return row came from `baseline_expansion_regime_guard + mainline_trend_a`, the best capture row came from `baseline_expansion_branch + mainline_trend_b`, and the lowest drawdown row came from `theme_strict_quality_branch + mainline_trend_a`. But the most stable candidate overall was neither local branch winner nor the shared default: it was `theme_capture_relief_branch` with `composite_rank_score=41.0`, ahead of `baseline_expansion_branch` (`46.5`) and `shared_default` (`46.833333`).
- Side Effects / Risks: This result is subtle and easy to misread. It does not mean the theme capture-relief branch is now the best local theme strategy; it only means it is currently the cleanest broad compromise among this specific promotion-candidate set.
- Conclusion: The project now has a clearer three-layer picture. Local branch winners still matter for branch-specific optimization, but the broader shared-default discussion should likely focus on a milder compromise candidate rather than on simply copying one branch winner across the whole research program.
- Next Step: Run one more targeted cross-pack compromise sweep centered on `theme_capture_relief_branch` versus `shared_default` and one or two nearby hybrids before discussing any shared-default promotion.

### JOURNAL-0036

- Date: 2026-03-28
- Author: Codex
- Title: Replace the first compromise guess with a better shared-default challenger and make it executable
- Related Decision: DEC-0036
- Related Runs: 20260329T033926Z_4693a3d3, 20260329T034007Z_a718a8d5, 20260329T034007Z_a9dbf982
- Protocol Version: protocol_v1.0
- Hypothesis: If `theme_capture_relief_branch` is only the first acceptable compromise and not the real best challenger, then a narrower sweep around it should be able to find a milder hybrid that improves overall stability across both research packs.
- What Changed: Added `cross_pack_compromise_sweep.yaml` with five candidates: `shared_default`, `theme_capture_relief_branch`, `balanced_compromise`, `quality_floor_with_faster_entry`, and `expansion_with_quality_floor`. After the sweep, materialized the winning compromise candidate as `baseline_research_strategy_suite_balanced_compromise.yaml` and `theme_research_strategy_suite_balanced_compromise.yaml`.
- Expected Impact: Give the shared-default conversation a concrete challenger that has survived both a broader promotion screen and a narrower compromise screen.
- Observed Result: The narrower compromise sweep `20260329T033926Z_4693a3d3` replaced the first compromise guess. `balanced_compromise` became the most stable candidate with `composite_rank_score=40.666667`, beating `quality_floor_with_faster_entry` (`42.166667`), `theme_capture_relief_branch` (`45.833333`), and `shared_default` (`52.0`). It also captured the best single total-return row on `baseline_research_v1 + mainline_trend_a`, while `theme_capture_relief_branch + mainline_trend_a` still kept the best drawdown row and `expansion_with_quality_floor + mainline_trend_b` kept the best capture row. The new executable suite configs behaved coherently too: on `baseline_research_v1`, run `20260329T034007Z_a718a8d5` produced `mainline_trend_a` as the best return strategy (`0.013608`) and `mainline_trend_b` as the best capture strategy (`0.398093`); on `theme_research_v1`, run `20260329T034007Z_a9dbf982` produced `mainline_trend_c` as both best return (`0.003085`) and best capture (`0.263239`) while `mainline_trend_a` kept the lowest drawdown (`0.002972`).
- Side Effects / Risks: `balanced_compromise` is a stronger shared-default challenger than `theme_capture_relief_branch`, but it still underperforms the strict-quality local branch on theme-side drawdown discipline and the expansion local branch on baseline-side maximum capture. It is a compromise candidate, not an all-around winner.
- Conclusion: The project now has a cleaner hierarchy of candidates. Shared defaults remain untouched, branch-local winners remain intact, and a more credible shared-default challenger now exists as a first-class executable artifact.
- Next Step: Compare `balanced_compromise` directly against the current shared default and the two branch-local baselines in one final promotion-oriented report before discussing any default change.

### JOURNAL-0037

- Date: 2026-03-28
- Author: Codex
- Title: Confirm the current promotion frontrunner in a finalists-only cross-pack screen
- Related Decision: DEC-0037
- Related Runs: 20260329T034115Z_fbe67ff1
- Protocol Version: protocol_v1.0
- Hypothesis: If `balanced_compromise` is a real shared-default challenger rather than just a broad-sweep artifact, then it should still lead when the comparison is reduced to only the current default and the strongest branch-derived finalists.
- What Changed: Added `promotion_finalists_check.yaml` and compared only four candidates across `baseline_research_v1` and `theme_research_v1`: `shared_default`, `baseline_expansion_branch`, `theme_strict_quality_branch`, and `balanced_compromise`.
- Expected Impact: Produce one concise promotion-oriented ranking that can anchor the next default-promotion discussion without reintroducing the noise of the larger candidate pool.
- Observed Result: Run `20260329T034115Z_fbe67ff1` confirmed `balanced_compromise` as the current promotion frontrunner with `composite_rank_score=32.0`, ahead of `shared_default` (`37.666666`), `baseline_expansion_branch` (`37.833333`), and `theme_strict_quality_branch` (`42.5`). The row-level split stayed intuitive: `balanced_compromise + mainline_trend_a` on `baseline_research_v1` produced the best total-return row, `baseline_expansion_branch + mainline_trend_b` kept the best capture row, and `theme_strict_quality_branch + mainline_trend_a` kept the lowest drawdown row.
- Side Effects / Risks: The ranking is now cleaner, but the tradeoff is explicit: `balanced_compromise` wins by overall stability, not by dominating every specialist metric. That means any promotion should still be gated by whether the project values broad default stability more than preserving the current specialist branch extremes.
- Conclusion: The repo now has a well-structured candidate ladder. `shared_default` remains the official default, the two branch baselines remain the specialist references, and `balanced_compromise` is the clear current frontrunner if a shared-default promotion discussion is opened next.
- Next Step: Move from exploratory comparison into promotion-gate thinking: define what evidence `balanced_compromise` would still need to replace `shared_default` under the project's promotion policy, rather than continuing to add more ad hoc candidates.

### JOURNAL-0038

- Date: 2026-03-28
- Author: Codex
- Title: Evaluate the shared-default challenger through a real promotion gate instead of another sweep
- Related Decision: DEC-0038
- Related Runs: 20260329T034115Z_fbe67ff1
- Protocol Version: protocol_v1.0
- Hypothesis: If `balanced_compromise` is genuinely ready for promotion discussion, then it should be able to pass a formal gate with explicit numeric requirements rather than only leading a comparison leaderboard.
- What Changed: Added `promotion_gate.py`, `run_promotion_gate.py`, and `balanced_compromise_promotion_gate.yaml`. The first gate compares `balanced_compromise` against `shared_default` using the finalists report `20260329T034115Z_fbe67ff1_comparison.json`.
- Expected Impact: Replace ambiguous "looks stronger" language with a repeatable pass/fail artifact for shared-default promotion candidates.
- Observed Result: The gate passed. The resulting report [balanced_compromise_vs_shared_default_gate.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/balanced_compromise_vs_shared_default_gate.json) shows `composite_rank_improvement=5.666666`, `mean_total_return_delta=0.004229`, `mean_max_drawdown_improvement=0.004296`, and `mean_capture_delta=-0.044973`, which stays inside the configured `max_mean_capture_regression=0.05` tolerance. It also records `challenger_total_return_row_wins=3`, while the incumbent had `0`.
- Side Effects / Risks: Passing this gate does not mean the shared default should be replaced immediately. It means the challenger has now cleared a first formal promotion hurdle. The thresholds themselves are still policy choices, and the project may still want an additional validation gate before changing the default config.
- Conclusion: `balanced_compromise` is no longer just the current frontrunner by narrative. It is now the first shared-default challenger in this repo to clear a structured promotion gate.
- Next Step: Decide whether the project wants a second-stage promotion gate, likely focused on validation readiness and out-of-branch robustness, before any actual shared-default replacement.

### JOURNAL-0039

- Date: 2026-03-28
- Author: Codex
- Title: Fail the second-stage validation gate on purpose and learn exactly why the challenger is not ready yet
- Related Decision: DEC-0039
- Related Runs: 20260329T034115Z_fbe67ff1
- Protocol Version: protocol_v1.0
- Hypothesis: A stronger `validation-ready` gate should be able to reject `balanced_compromise` if its global improvements are partly funded by giving back too much capture in one of the research packs.
- What Changed: Extended `promotion_gate.py` with pack-level deltas, added `balanced_compromise_validation_gate.yaml`, created [20_VALIDATION_READY_DEFINITION.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/20_VALIDATION_READY_DEFINITION.md), and added [21_V1_FREEZE_CANDIDATES.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/21_V1_FREEZE_CANDIDATES.md) to make the current freeze state explicit.
- Expected Impact: Replace the ambiguous question "should we promote this now?" with a sharper question: "does the challenger survive stricter per-pack scrutiny?"
- Observed Result: The second-stage report [balanced_compromise_validation_ready_gate.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/balanced_compromise_validation_ready_gate.json) failed as intended. `balanced_compromise` still passed the overall improvement checks and the global capture-regression tolerance, but it failed `max_dataset_mean_capture_regression` because its baseline-pack capture giveback was `0.052659`, above the configured `0.04` ceiling. In other words, the candidate is strong enough to challenge the default, but not yet strong enough to replace it under stricter `validation-ready` standards.
- Side Effects / Risks: This is a productive failure, but it narrows the next research question. If the project keeps pursuing `balanced_compromise`, it now needs to specifically reduce baseline-pack capture loss without giving back the return/drawdown improvements that made the challenger attractive in the first place.
- Conclusion: The repo now has a much cleaner stop condition. `shared_default` stays frozen as the official V1 default, `balanced_compromise` remains the best current challenger, and the reason it is not yet `validation-ready` is explicit rather than speculative.
- Next Step: Run one final V1 freeze pass: full regression, key CLI replay, and an explicit freeze summary that separates official defaults from strong but not-yet-promoted challengers.

### JOURNAL-0040

- Date: 2026-03-28
- Author: Codex
- Title: Complete a freeze-oriented regression replay and lock the repo into a no-drift state
- Related Decision: DEC-0040
- Related Runs: 20260329T035317Z_357001ee, 20260329T035317Z_c74026d3
- Protocol Version: protocol_v1.0
- Hypothesis: If the repo is truly ready for V1 freeze preparation, then the official default flows, the gate flows, and the full automated test suite should all replay cleanly after the new promotion/validation machinery was added.
- What Changed: Re-ran the full `pytest` suite, replayed `baseline_research_strategy_suite.yaml`, replayed `theme_research_strategy_suite.yaml`, reran both gate CLIs, and summarized the outcome in [22_V1_FREEZE_STATUS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/22_V1_FREEZE_STATUS.md).
- Expected Impact: Confirm that the current freeze state is backed by actual regression evidence instead of by narrative continuity alone.
- Observed Result: The replay held. Full tests passed at `41 passed`. The baseline shared-default suite replayed in [20260329T035317Z_357001ee_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T035317Z_357001ee_comparison.json) and the theme shared-default suite replayed in [20260329T035317Z_c74026d3_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T035317Z_c74026d3_comparison.json). The first-stage gate still passed, and the second-stage validation gate still failed for the same explicit reason: excessive baseline-pack capture regression.
- Side Effects / Risks: This is a healthier stopping point than before, but not a finished product. The repo is now much harder to drift accidentally, which means future changes will need to be more deliberate.
- Conclusion: The project has entered a much more honest state. Architecture, data flow, experiments, gates, and replay all hold together; the only thing stopping default promotion is now a specific research deficit rather than missing infrastructure.
- Next Step: Either accept `shared_default` as the V1 freeze default and defer promotion, or run a focused baseline-pack capture-recovery refinement around `balanced_compromise` without reopening broad candidate exploration.

### JOURNAL-0041

- Date: 2026-03-28
- Author: Codex
- Title: Check whether balanced_compromise has an easy nearby capture-recovery fix and accept the negative result
- Related Decision: DEC-0041
- Related Runs: 20260329T035625Z_f75beb65, 20260329T035657Z_9bf44b74
- Protocol Version: protocol_v1.0
- Hypothesis: If the second-stage gate failure is mostly caused by one slightly-too-tight baseline-side threshold, then a small local relaxation around `balanced_compromise` should be able to recover some capture without giving back too much of the return/drawdown improvement.
- What Changed: Added `balanced_compromise_capture_recovery_sweep.yaml` on the baseline pack and tested mild regime relief, hierarchy relief, entry relief, and a small combined relief. Then took the only somewhat plausible recovery path, `balanced_hierarchy_relief`, into a cross-pack comparison via `balanced_capture_recovery_check.yaml`.
- Expected Impact: Find out whether the current blocker is one easy local tuning issue or whether the challenger has already reached a more structural tradeoff boundary.
- Observed Result: The local baseline sweep showed that `balanced_hierarchy_relief` could recover some capture (`mean_mainline_capture_ratio=0.422663` on the baseline pack versus `0.383431` for `balanced_control`), but it also gave back too much return and drawdown quality. When returned to a two-pack comparison in [20260329T035657Z_9bf44b74_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T035657Z_9bf44b74_comparison.json), `balanced_compromise` still remained the most stable candidate (`composite_rank_score=26.0`) ahead of `balanced_hierarchy_relief` (`28.333333`) and `shared_default` (`31.166666`).
- Side Effects / Risks: This is another useful negative result. It suggests that the current capture-regression issue is not solved by a single mild hierarchy relaxation without paying a meaningful price elsewhere.
- Conclusion: There is no obvious one-step local repair for `balanced_compromise` yet. The repo should treat the current freeze state as real, not as a temporary pause before an easy promotion.
- Next Step: Unless the project deliberately wants another deeper shared-default refinement cycle, keep `shared_default` frozen for V1 and treat `balanced_compromise` as a documented but not-yet-promoted challenger.

### JOURNAL-0042

### JOURNAL-0089

- Date: 2026-03-29
- Author: Codex
- Title: Formally split "research V1 complete" from "practical trading ready" and close V1 on the research side
- Related Decision: DEC-0042
- Related Runs: 20260329T035317Z_357001ee, 20260329T035317Z_c74026d3
- Protocol Version: protocol_v1.0
- Hypothesis: The repo has enough evidence to stop calling V1 "unfinished" at the research-foundation level, but not enough evidence to call it tradable. The correct move is to close V1 on the research side and make the practical trading path explicit as the next stage.
- What Changed: Added [23_PRACTICAL_TRADING_ROADMAP.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/23_PRACTICAL_TRADING_ROADMAP.md) and [24_V1_RELEASE_SUMMARY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/24_V1_RELEASE_SUMMARY.md), then updated repo guidance so that the freeze state, release meaning, and next-stage execution gap are explicit.
- Expected Impact: Remove ambiguity around whether the repo should keep expanding the research baseline forever just because practical trading modules are still missing.
- Observed Result: The project now has a cleaner narrative and a cleaner operating state. V1 can be truthfully described as a completed research-system foundation release, while practical trading remains a separate next-stage buildout focused on execution, shadow, broker, and operational controls.
- Side Effects / Risks: This closes one ambiguity but opens a sharper product decision: should the next milestone prioritize `V1.1 research refinement` or `V1.5 practical trading foundation`?
- Conclusion: V1 no longer needs to stay open just because it is not tradable yet. The research operating system is complete enough to freeze; the trading operating system is the next milestone.
- Next Step: Keep V1 frozen on the research side, and choose the next milestone explicitly instead of mixing refinement and trading-foundation work together.

### JOURNAL-0043

- Date: 2026-03-29
- Author: Codex
- Title: Validate the finalists across quarterly slices and accept that the default question is now mostly about environment tradeoffs
- Related Decision: DEC-0043
- Related Runs: 20260329T041309Z_0352bb07
- Protocol Version: protocol_v1.0
- Hypothesis: If `balanced_compromise` is only winning because of global averaging, then fixed time-slice validation should reveal that it collapses or loses its edge once the current finalists are compared quarter by quarter.
- What Changed: Added `time_slice_validation.py`, `run_time_slice_validation.py`, `time_slice_validation.yaml`, and a dedicated test file. Then ran the current finalists (`shared_default`, `balanced_compromise`, `baseline_expansion_branch`, `theme_strict_quality_branch`) across quarterly 2024 slices on both research packs.
- Expected Impact: Move the next research step from abstract "more validation" into a concrete map of which candidate wins which kind of environment.
- Observed Result: The time-slice report [20260329T041309Z_0352bb07_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T041309Z_0352bb07_comparison.json) kept `balanced_compromise` at the top of the overall slice-level stability leaderboard, ahead of `baseline_expansion_branch`, `shared_default`, and `theme_strict_quality_branch`. But the slice winners are not uniform. `baseline_expansion_branch` owns more `best_capture` slices, `theme_strict_quality_branch` owns more `lowest_drawdown` slices, and `balanced_compromise` wins by broader all-around behavior rather than by dominating every quarter. That is useful, because it says the main open question is now environmental boundary management, not candidate discovery.
- Side Effects / Risks: Fixed quarterly slices are still a lightweight validation layer, not a full rolling train/validate loop. They improve the evidence base, but they do not eliminate the need for deeper validation later.
- Conclusion: The repo now knows more precisely what `balanced_compromise` is and is not. It is still the strongest shared-default challenger by broad stability, but it remains a compromise candidate with visible specialist competition in capture-heavy and drawdown-sensitive environments.
- Next Step: Use these slice results to define `V1.1 research refinement` around environment-boundary analysis and theme-data quality, not around opening another broad rule-candidate search.

### JOURNAL-0044

- Date: 2026-03-29
- Author: Codex
- Title: Convert slice validation into a cleaner environment-role map
- Related Decision: DEC-0044
- Related Runs: 20260329T041309Z_0352bb07
- Protocol Version: protocol_v1.0
- Hypothesis: If the finalists really occupy different roles rather than just different leaderboard positions, then a compact environment-boundary summary should make those roles explicit without changing the underlying data.
- What Changed: Added `environment_boundary.py`, `run_environment_boundary_analysis.py`, and `environment_boundary_analysis.yaml`, then generated [environment_boundary_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/environment_boundary_analysis_v1.json) from the quarterly time-slice validation report.
- Expected Impact: Give the next research cycle a cleaner starting point than "compare four candidates again."
- Observed Result: The boundary report made the roles explicit. `balanced_compromise` is the current broad-stability contender, `baseline_expansion_branch` is the current capture specialist, and `theme_strict_quality_branch` is the current drawdown specialist. That fits the earlier slice-level evidence and makes the next V1.1 question sharper: where are the boundaries between these roles, and can any of them be improved without losing their core advantage?
- Side Effects / Risks: This summary improves clarity, but it can also make the roles feel too fixed. They should still be treated as current findings, not eternal truths.
- Conclusion: The repo is now done with broad "who wins?" discovery for this stage. It has moved into "who wins where, and why?" territory.
- Next Step: Start V1.1 by analyzing environment boundaries and theme-data quality instead of opening a new configuration tournament.

### JOURNAL-0045

- Date: 2026-03-29
- Author: Codex
- Title: Confirm that theme-side risk is dominated by static concept mapping rather than by simple coverage gaps
- Related Decision: DEC-0045
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The main weakness in the current theme pack is not merely that one or two symbols are unmapped, but that the concept layer is too static and too concentrated to reflect real A-share theme drift.
- What Changed: Added `theme_data_quality.py`, `run_theme_data_quality.py`, `theme_data_quality.yaml`, and generated [theme_research_data_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data_quality/theme_research_data_quality_v1.json).
- Expected Impact: Replace the vague sentence "theme data quality needs work" with a more operational statement of exactly what is wrong with the current concept layer.
- Observed Result: The report confirmed four concrete issues. Coverage is incomplete (`concept_symbol_coverage_ratio=0.923077`, with `002902` missing concept coverage). More importantly, `static_primary_symbol_ratio=1.0`, which means every covered symbol keeps the same primary concept across the whole period. Concept diversity is weak too: `top_primary_concept_share=0.752592`, and `multi_concept_symbol_ratio=0.083333`, meaning almost every symbol carries only one concept. In practice, this means the current theme pack is likely understating real overlap while also risking time-invariant lookahead contamination.
- Side Effects / Risks: This is a strong directional diagnosis, but it does not yet solve the problem. The current concept-mapping bootstrap remains useful as a first-pass lab input, not as a trusted production-grade theme ontology.
- Conclusion: The next high-value theme-side work is now obvious. Before trusting more theme-strategy refinement, the repo should improve concept timing, concept diversity, and multi-label realism.
- Next Step: Build a better theme-data iteration focused on reducing static primary-concept assignments and improving realistic multi-concept coverage, rather than continuing to tune theme-side strategy thresholds on top of the current concept layer.

### JOURNAL-0046

- Date: 2026-03-29
- Author: Codex
- Title: Replace the static theme concept map with a history-aware v2 and verify that the improvement survives downstream derived/suite runs
- Related Decision: DEC-0046
- Related Runs: 20260329T044312Z_dbb98804
- Protocol Version: protocol_v1.0
- Hypothesis: If the current theme weakness is mainly a concept-layer problem, then a better concept map should measurably improve the quality diagnostics before any strategy retuning is attempted, and the new mapping should still flow cleanly through derived tables and the strategy suite.
- What Changed: Reworked `concept_mapper.py` so concept bootstrap can scan deeper, keep more concepts per symbol, fetch concept-board history directly by board code, and score concepts day by day using board strength plus stock/concept alignment. Added `theme_research_concept_mapping_v2.yaml`, `theme_data_quality_v2.yaml`, `theme_research_derived_data_v2.yaml`, `theme_research_strategy_suite_v2.yaml`, `theme_research_data_audit_v2.yaml`, and `test_concept_mapper.py`.
- Expected Impact: Reduce time-invariant labeling, improve multi-label realism, and make the theme pack a cleaner research substrate before any more theme-side rule refinement.
- Observed Result: The quality report improved materially. `unique_concept_count` rose from `4` to `10`, `mean_concepts_per_covered_symbol` rose from `1.083333` to `2.0`, `static_primary_symbol_ratio` dropped from `1.0` to `0.333333`, and `multi_concept_symbol_ratio` rose from `0.083333` to `0.666667`. The warning set also shrank from four issues to two: the remaining problems are the `002902` coverage gap and still-high primary-concept concentration (`top_primary_concept_share=0.738079`). The downstream `theme_research_v2` derived pack audited as `baseline_ready=true`, and suite run [20260329T044312Z_dbb98804_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T044312Z_dbb98804_comparison.json) kept a sensible theme-side role split with `mainline_trend_c` best on return/capture and `mainline_trend_a` lowest-drawdown.
- Side Effects / Risks: Concept concentration is still too high, and the concept layer still misses one symbol. The new v2 map is better, but it is still a heuristic bootstrap layer, not a final ontology.
- Conclusion: Theme-side refinement can now move forward on a better substrate. The concept layer is no longer dominated by the earlier "static primary concept" failure mode.
- Next Step: Target the two remaining theme-data issues directly: fill the `002902` concept gap and reduce the dominance of the lithium primary theme without regressing the improved multi-concept behavior.

### JOURNAL-0047

- Date: 2026-03-29
- Author: Codex
- Title: Accept that cleaner theme-data labels can reduce backtest attractiveness and treat that as useful evidence
- Related Decision: DEC-0047
- Related Runs: 20260329T044445Z_862707c7
- Protocol Version: protocol_v1.0
- Hypothesis: If `theme_research_v1` was benefiting from overly static concept labels, then moving to a more realistic `theme_research_v2` map might improve data quality even if it slightly weakens the backtest leaderboard.
- What Changed: Added `theme_v1_v2_dataset_comparison.yaml` and compared the old and new theme packs directly after the v2 concept-map rollout.
- Expected Impact: Separate "data realism improved" from "backtest got prettier" and force an explicit decision about which one the project should trust more.
- Observed Result: The comparison report [20260329T044445Z_862707c7_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T044445Z_862707c7_comparison.json) showed that `theme_research_v1` still wins on return/capture (`mainline_trend_b` at `0.00182` total return and `mainline_trend_c` at `0.360507` capture), while `theme_research_v2` is weaker on those same metrics (`mainline_trend_b` at `-0.000277`, `mainline_trend_c` at `0.358937` capture) even though its concept-layer realism is materially better. That is not treated as a failure of the data-quality work. It is treated as evidence that the old theme pack likely carried optimistic label bias.
- Side Effects / Risks: Cleaner labels can make progress look slower because the inflated backtest edge shrinks before the next real improvement is found.
- Conclusion: The project should not revert to `theme_research_v1` just because it looks better. The cleaner but harsher `theme_research_v2` pack is a better refinement substrate.
- Next Step: Keep theme-side work on the v2 pack and attack the two remaining data issues directly: `002902` coverage and primary-concept concentration.

### JOURNAL-0048

- Date: 2026-03-29
- Author: Codex
- Title: Start a broader but still interpretable market-research pack instead of jumping straight to full-market coverage
- Related Decision: DEC-0048
- Related Runs: none
- Protocol Version: protocol_v1.0
- Hypothesis: The next scaling step should be a wider mixed-market validation pack, not immediate all-market coverage, because the repo still needs a controllable environment in which theme-data and mixed-regime effects can be debugged.
- What Changed: Added [25_MARKET_RESEARCH_V0_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/25_MARKET_RESEARCH_V0_PLAN.md), created [market_research_v0.txt](D:/Creativity/A-Share-Quant_TrY/config/universes/market_research_v0.txt), added [market_research_free_data_bootstrap.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_free_data_bootstrap.yaml) and [market_research_sector_mapping.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_sector_mapping.yaml), then bootstrapped the first raw/reference tables.
- Expected Impact: Give the next research cycle a broader validation substrate without yet taking on full-market ontology and data-cleaning cost.
- Observed Result: The first `market_research_v0` pack landed successfully. The raw daily-bar table now has `8218` rows across `34` stocks, the index table has `726` rows across `3` indices, the security master has `34` symbols, the adjustment-factor table has `8228` rows, and the CNInfo daily sector map has `8218` rows across the same `34` symbols. The bootstrap also showed one realistic operational issue: the full free-source security-master endpoint can still reset the connection, so the graceful lite fallback remains necessary.
- Side Effects / Risks: This pack is wider, but it is not yet a full research pack. It does not yet have concept mapping, derived tables, or suite-level validation, so it should be treated as the next substrate, not as a finished comparison pack.
- Conclusion: The project now has a better next step than "go full market." `market_research_v0` is large enough to be more realistic, but still small enough to remain debuggable.
- Next Step: Decide whether the next action on `market_research_v0` should be concept mapping + derived-table generation, or whether the repo should first finish one more theme-v2 data-quality iteration before widening the concept layer further.

### JOURNAL-0049

- Date: 2026-03-29
- Author: Codex
- Title: Turn market_research_v0 into a runnable mixed-market research pack and confirm that it behaves like a bridge between baseline and theme
- Related Decision: DEC-0049
- Related Runs: 20260329T050350Z_4ce8e316, 20260329T050409Z_2a036885
- Protocol Version: protocol_v1.0
- Hypothesis: If `market_research_v0` is a useful intermediate pack, then once concept mapping, derived tables, and the suite are added, it should produce a strategy ranking that is broader and more mixed than the specialist baseline/theme packs rather than simply duplicating one of them.
- What Changed: Added `market_research_concept_mapping_v0.yaml`, `market_research_data_quality_v0.yaml`, `market_research_derived_data_v0.yaml`, `market_research_strategy_suite_v0.yaml`, `market_research_data_audit_v0.yaml`, and `research_market_dataset_comparison.yaml`. Then built the concept map, derived tables, audit report, standalone suite, and three-pack comparison.
- Expected Impact: Promote `market_research_v0` from a raw-data expansion into a real research substrate that can be used in the next validation cycle.
- Observed Result: The pack now runs end to end. The concept map has `9172` rows; the audit [market_research_data_audit_v0.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v0.json) reaches `baseline_ready=true`; and suite run [20260329T050350Z_4ce8e316_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T050350Z_4ce8e316_comparison.json) shows `mainline_trend_b` best on return, `mainline_trend_c` best on capture, and `mainline_trend_a` lowest-drawdown. The three-pack comparison [20260329T050409Z_2a036885_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T050409Z_2a036885_comparison.json) confirms the role: `market_research_v0` sits between `baseline_research_v1` and `theme_research_v2`, leaning naturally toward `B/C` instead of the more concentrated `A` preference of the baseline pack.
- Side Effects / Risks: The concept coverage ratio on the mixed-market pack is only `0.470588`, which is acceptable for a mixed-market validation pack but too low to treat it as a pure theme-ontology pack.
- Conclusion: `market_research_v0` is now a valid third research substrate. It should be treated as a mixed-market validation environment, not as a replacement for either of the specialist packs.
- Next Step: Use this three-pack structure in the next validation cycle, especially when checking whether current shared/default or branch candidates remain stable once the environment broadens beyond the specialist packs.

### JOURNAL-0050

- Date: 2026-03-29
- Author: Codex
- Title: Extend validation to three packs and confirm that the specialist role map still holds
- Related Decision: DEC-0050
- Related Runs: 20260329T050713Z_259349ba
- Protocol Version: protocol_v1.0
- Hypothesis: If the current role map is real rather than an artifact of only using two specialist packs, then once `market_research_v0` is added, the same broad pattern should remain visible: one candidate should still look like the stability contender, one like the capture specialist, and one like the drawdown specialist.
- What Changed: Added `time_slice_validation_v2.yaml` and `environment_boundary_analysis_v2.yaml`, then reran the quarterly slice validation on `baseline_research_v1`, `theme_research_v2`, and `market_research_v0`.
- Expected Impact: Stress the current conclusions with a broader mixed-market environment before reopening any default-promotion discussion.
- Observed Result: The three-pack slice report [20260329T050713Z_259349ba_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T050713Z_259349ba_comparison.json) still kept `balanced_compromise` on top of the overall stability leaderboard (`composite_rank_score=209.416666`). The new boundary report [environment_boundary_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/environment_boundary_analysis_v2.json) confirmed the same role map at higher evidence density: `balanced_compromise` remains the broad stability candidate, `baseline_expansion_branch` is now an even clearer capture specialist (`best_capture_slice_count=6`), and `theme_strict_quality_branch` is the drawdown specialist (`lowest_drawdown_slice_count=8`).
- Side Effects / Risks: More evidence does not automatically simplify decisions. The role map is clearer, but the repo also becomes more obviously multi-objective.
- Conclusion: Adding the third pack strengthened the existing interpretation instead of overturning it.
- Next Step: Push the shared-default challenger through the same three-pack evidence base and see whether the extra pack changes the promotion verdict.

### JOURNAL-0051

- Date: 2026-03-29
- Author: Codex
- Title: Verify that the third pack does not rescue balanced_compromise from the same validation-ready blocker
- Related Decision: DEC-0051
- Related Runs: 20260329T050714Z_c0ed1f58
- Protocol Version: protocol_v1.0
- Hypothesis: If the earlier `balanced_compromise` failure was mostly a two-pack artifact, then once a broader mixed-market pack is included, the challenger might finally pass the stricter validation-ready gate.
- What Changed: Added `promotion_finalists_check_v2.yaml` and `balanced_compromise_validation_gate_v2.yaml`, ran the current finalists across all three packs, and then reran the validation-ready gate against `shared_default`.
- Expected Impact: Either overturn the current freeze logic with stronger evidence, or confirm that the blocker is structural and not an artifact of using too narrow a validation substrate.
- Observed Result: The three-pack finalists comparison [20260329T050714Z_c0ed1f58_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T050714Z_c0ed1f58_comparison.json) again put `balanced_compromise` on top of the composite leaderboard (`46.222222`) ahead of `shared_default` (`52.555555`), `baseline_expansion_branch` (`56.222222`), and `theme_strict_quality_branch` (`67.000001`). The stronger gate [balanced_compromise_validation_ready_gate_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/balanced_compromise_validation_ready_gate_v2.json) still failed, but importantly the reason did not change: the challenger improved total return and drawdown enough on average, yet `max_dataset_mean_capture_regression` still failed because the baseline pack remains above tolerance (`0.052659 > 0.04`).
- Side Effects / Risks: This is another strong negative result. It increases confidence in the freeze decision, but it also means the shared-default problem is now clearly narrow and stubborn rather than broad and accidental.
- Conclusion: The third pack did not save the challenger. The repo should keep the freeze state exactly as it is.
- Next Step: If shared-default work is reopened later, the only justified target is baseline-pack capture recovery without breaking the broader three-pack stability edge.

### JOURNAL-0052

- Date: 2026-03-29
- Author: Codex
- Title: Window replay shows that the baseline capture blocker is split between late entry and fast mainline replacement
- Related Decision: DEC-0052
- Related Runs: baseline_window_replay_diagnostic_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the baseline capture blocker is genuinely narrow, then replaying the worst windows directly should reveal a small number of repeated failure modes rather than a broad "balanced_compromise is weaker everywhere" story.
- What Changed: Added `window_replay_diagnostic_v1.yaml`, implemented `run_window_replay_diagnostic.py`, and replayed the two worst baseline windows (`600519_23`, `000333_19`) for `shared_default` versus `balanced_compromise` on `mainline_trend_b/c`.
- Expected Impact: Replace vague capture-regression language with specific timing/permission/hierarchy failure modes.
- Observed Result: The replay report [baseline_window_replay_diagnostic_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_window_replay_diagnostic_v1.json) made the split explicit. `600519_23` is a late-entry problem: on `2024-12-06`, `balanced_compromise` still had the same entry triggers as `shared_default`, but it lost the only passed trend filter because `repair_window=4` removed the `pullback_repair` confirmation. `000333_19` is different: `balanced_compromise` does enter on time, but on `2024-09-19` and again on `2024-09-23` it exits via `replaced_by_new_mainline`, and later via `assignment_became_junk`, so the damage there is mainly regime-switch / replacement churn rather than missed entry.
- Side Effects / Risks: The replay shows mechanism, but not yet whether the mechanism can be repaired without hurting the broader three-pack stability edge.
- Conclusion: The baseline blocker is now clearly two-part: one entry-timing issue and one fast-regime-switch issue. Generic hierarchy loosening is too blunt for this problem.
- Next Step: Add a narrow, default-off regime switch buffer and combine it with the repair-window reset to test whether the two fixes really attack different parts of the blocker.

### JOURNAL-0053

- Date: 2026-03-29
- Author: Codex
- Title: Targeted timing repairs recover the late-entry window fully and the replacement window only partially
- Related Decision: DEC-0053
- Related Runs: baseline_window_replay_diagnostic_v2
- Protocol Version: protocol_v1.0
- Hypothesis: If the newly diagnosed baseline blocker really is split between a repair-window timing miss and fast mainline replacement churn, then `repair_window=3` and `switch_margin_buffer` should improve different windows instead of behaving like redundant broad loosening.
- What Changed: Added `switch_margin_buffer` to `AttackPermissionEngine`, kept it default-off, created `window_replay_diagnostic_v2.yaml`, and replayed five candidates including `balanced_repair_reset`, `balanced_switch_buffer_010`, and `balanced_targeted_timing_repair`.
- Expected Impact: Test whether the baseline blocker is repairable through narrow mechanism-specific changes instead of broad branch rewrites.
- Observed Result: The replay report [baseline_window_replay_diagnostic_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_window_replay_diagnostic_v2.json) shows a clean separation. `balanced_repair_reset` fully restores the `600519_23` capture loss (`0.0 -> 0.994315`) without changing the `000333_19` outcome. `balanced_switch_buffer_010` leaves `600519_23` untouched, but lifts `000333_19` capture from `0.452641` to `0.507922`. The combined candidate `balanced_targeted_timing_repair` therefore fully recovers the late-entry window and partially reduces the replacement-driven damage, but it still does not match `shared_default` on the `000333_19` pattern.
- Side Effects / Risks: The repair remains narrow and local. The replay proves mechanism-level value, but not yet promotion-level safety. It also implies the remaining blocker is now more specifically about replacement sensitivity than about entry timing.
- Conclusion: This is meaningful progress even though it is not enough to reopen promotion. The repo now knows that the baseline capture blocker can be decomposed and partially repaired with two distinct levers.
- Next Step: If shared-default work is reopened again, the next narrow target should be the remaining replacement-driven exits around `000333_19`, not another pass at generic hierarchy or entry loosening.

### JOURNAL-0054

- Date: 2026-03-29
- Author: Codex
- Title: Strategy-side theme late-mover relief fixes the old no-position pattern only by creating a worse early-participation pattern
- Related Decision: DEC-0054
- Related Runs: 20260329T053932Z_e0bd5d89
- Protocol Version: protocol_v1.0
- Hypothesis: If the remaining `theme_research_v2` blocker for `balanced_targeted_timing_repair` is mainly that `mainline_trend_c` misses a few `late_mover` windows, then a narrow, default-off `late_mover` entry override plus healthy `junk` grace might rescue those windows without hurting the broader three-pack profile.
- What Changed: Added a strategy-level experimental override for `late_mover` admission, then tested `balanced_targeted_theme_late_admit` and `balanced_targeted_theme_window_repair` through `theme_window_replay_diagnostic_v2/v3` and a three-pack cross-check.
- Expected Impact: Determine whether the remaining theme blocker can be repaired at the strategy-admission layer rather than by changing the upstream theme hierarchy/data logic.
- Observed Result: The direct strategy-side fix is not good enough. It does convert some `challenger_no_window_position` cases into entries, but it also creates earlier and noisier participation. The broader cross-pack check [20260329T053932Z_e0bd5d89_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T053932Z_e0bd5d89_comparison.json) keeps `balanced_targeted_timing_repair` as the most stable candidate (`composite_rank_score=38.777778`) ahead of `balanced_targeted_theme_window_repair` (`42.555556`). In other words, the naive theme-side strategy patch improves a few window-level misses while making the overall candidate worse.
- Side Effects / Risks: This is a useful negative result, but it also means the remaining blocker is now more obviously upstream. Continuing to patch it in the strategy layer would likely turn the repo into a collection of window-specific hacks.
- Conclusion: The remaining theme blocker should now be treated as a hierarchy / derived-data admissibility problem, not as a strategy-side entry-permission problem.
- Next Step: Stop expanding strategy-side theme-admit candidates and move the next research cycle toward upstream theme admissibility analysis.

### JOURNAL-0055

- Date: 2026-03-29
- Author: Codex
- Title: Theme late-mover admissibility is a pack-wide blocker, not just a three-window anecdote
- Related Decision: DEC-0055
- Related Runs: theme_late_mover_admissibility_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the remaining `theme_research_v2` blocker is truly upstream, then a full-window admissibility scan should show that the issue extends beyond the three replayed windows and clusters around a small set of hierarchy failure modes.
- What Changed: Added `late_mover_admissibility.py`, `run_late_mover_admissibility.py`, `theme_late_mover_admissibility_v1.yaml`, and a focused unit test. Then ran the analysis on `theme_research_v2` for `shared_default` versus `balanced_targeted_timing_repair` on `mainline_trend_c`.
- Expected Impact: Replace the current narrative of "a few replay windows still look bad" with a pack-wide map of where admissibility fails and how often.
- Observed Result: The report [theme_late_mover_admissibility_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_late_mover_admissibility_v1.json) shows `13` impacted windows across `7` symbols, with `10` fully blocked windows and `3` partial windows. Mean capture regression on these impacted windows is `0.383854`. The top blockers are still the windows we already knew (`300518_25`, `000155_25`, `002466_28`), but the issue clearly extends further (`002460_26`, `002176_25`, `600338_5`, `603799_25`). The dominant assignment reasons are still `fallback_to_junk` and `low_composite_or_low_resonance`.
- Side Effects / Risks: This makes the problem look broader, which is uncomfortable, but it is a more honest picture than continuing to treat it as a few unlucky windows.
- Conclusion: The repo now has enough evidence to stop strategy-side patching on this branch. The remaining theme blocker is a real upstream admissibility problem in the theme hierarchy / derived layer.
- Next Step: The next theme cycle should target upstream admissibility logic, especially the `fallback_to_junk` concentration and the role of low-composite / low-resonance cases, before reopening any broader promotion discussion.

### JOURNAL-0056

- Date: 2026-03-29
- Author: Codex
- Title: A light concept-aware boost reduces the count of blocked theme windows, but does not yet improve the overall theme research pack
- Related Decision: DEC-0056
- Related Runs: 20260329T055538Z_a15322e6, 20260329T055559Z_d9b1c86e
- Protocol Version: protocol_v1.0
- Hypothesis: If the theme blocker is mostly the `0.55 -> 0.60` late-mover-quality band, then a small concept-aware lift in `late_mover_quality` should reduce the number of admissibility-gap windows without needing strategy-side overrides.
- What Changed: Added a default-off concept-support boost path in `bootstrap_derived.py`, generated `theme_research_v3`, then reran the theme suite, late-mover admissibility scan, hierarchy-gap analysis, and `theme_v2_v3_dataset_comparison`.
- Expected Impact: Reduce the number of `theme` windows where the challenger remains `junk` despite valid permission/filter/entry context.
- Observed Result: The upstream boost did move the blocker, but only partway. `theme_late_mover_admissibility_v1` on `theme_research_v2` had `13` impacted windows (`10` blocked); `theme_late_mover_admissibility_v2` on `theme_research_v3` drops that to `10` impacted windows (`8` blocked). So the intervention is directionally useful. But the broader theme-pack comparison [20260329T055559Z_d9b1c86e_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T055559Z_d9b1c86e_comparison.json) is not a clean win: `mainline_trend_c` capture improves (`0.358937 -> 0.373298`) while return and drawdown get worse (`0.000011 -> -0.001849`, `0.006832 -> 0.009983`).
- Side Effects / Risks: This is exactly the kind of mixed result that can become a trap if treated as a promotion-ready fix. The uniform boost helps the blocker count, but it is still too blunt.
- Conclusion: Upstream theme-derived work is the right direction, but `theme_research_v3` is only a weak positive experiment, not a keeper baseline.
- Next Step: Any further theme-derived iteration should be more targeted than a uniform concept boost, likely focusing on the `late_mover_quality_fallback -> fallback_to_junk` transition rather than lifting all concept-rich names equally.

### JOURNAL-0057

- Date: 2026-03-29
- Author: Codex
- Title: Theme v4 keeps the pack-level behavior clean while sharply reducing the remaining admissibility blocker
- Related Decision: DEC-0057
- Related Runs: 20260329T060019Z_8c727a50, 20260329T060020Z_cc6e8259
- Protocol Version: protocol_v1.0
- Hypothesis: If the `theme_research_v3` concept-support boost was directionally right but too blunt, then constraining it to a narrow late-mover-quality band should keep most of the blocker relief while avoiding the broader return / drawdown damage.
- What Changed: Added band-limited and cap-aware concept-support controls to `bootstrap_derived.py`, then generated `theme_research_v4`, reran the suite, reran late-mover admissibility, reran hierarchy-gap analysis, and compared `theme_research_v2` with `theme_research_v4`.
- Expected Impact: Reduce the remaining `theme` admissibility blocker without changing the overall theme pack enough to create a new distortion.
- Observed Result: The narrow repair behaved much better than the uniform one. The new admissibility report [theme_late_mover_admissibility_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_late_mover_admissibility_v3.json) cuts the blocker to `4` impacted windows and `3` blocked windows, down from `13` and `10` on `theme_research_v2`. At the same time, the pack-level comparison [20260329T060020Z_cc6e8259_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060020Z_cc6e8259_comparison.json) stays effectively aligned with `theme_research_v2`, which is much cleaner than the `theme_research_v3` tradeoff.
- Side Effects / Risks: The blocker is not gone; it has mostly shifted from late-mover-quality to a very small residual composite-threshold issue.
- Conclusion: `theme_research_v4` is the first upstream theme-derived iteration that looks like a keeper research pack rather than just a directional experiment.
- Next Step: Re-run the broad challenger check and stricter gate with `theme_research_v4` before changing any more theme-derived logic.

### JOURNAL-0058

- Date: 2026-03-29
- Author: Codex
- Title: Theme v4 improves the broad challenger materially, but not enough to reopen promotion
- Related Decision: DEC-0058
- Related Runs: 20260329T060122Z_99e67000, 20260329T060321Z_a2d656e8
- Protocol Version: protocol_v1.0
- Hypothesis: If `theme_research_v4` truly removed the worst remaining theme-side blocker, then the current broad challenger should look cleaner against `shared_default` across all three packs and quarterly slices, even if it still does not quite pass the stricter promotion gate.
- What Changed: Updated the cross-pack challenger check and the targeted timing repair validation configs to use `theme_research_v4`, then reran the three-pack challenger comparison, validation gate, and quarterly time-slice validation.
- Expected Impact: Learn whether the current blocker is still a theme capture problem or whether the repo has moved on to a smaller promotion gap.
- Observed Result: The three-pack comparison [20260329T060122Z_99e67000_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060122Z_99e67000_comparison.json) now keeps `balanced_targeted_timing_repair` ahead of `shared_default` on broad rank, mean return, and mean drawdown, while capture regression is only `0.004037`. The stricter gate report [targeted_timing_repair_validation_gate_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/targeted_timing_repair_validation_gate_v2.json) still fails, but for a much narrower reason: `composite_rank_improvement` (`4.555554 < 5.0`) and `mean_max_drawdown_improvement` (`0.002242 < 0.003`) are still short, while capture is now inside tolerance. The updated slice report [20260329T060321Z_a2d656e8_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060321Z_a2d656e8_comparison.json) still ranks `balanced_targeted_timing_repair` as the most stable broad candidate.
- Side Effects / Risks: The repo could now be tempted to relax thresholds just because the challenger looks much better; that would be the wrong lesson.
- Conclusion: The old theme blocker is mostly repaired, but the repo still does not have promotion-grade evidence. The freeze should stay in place.
- Next Step: Treat the next cycle as narrow refinement of `balanced_targeted_timing_repair`, focused on improving broad stability metrics without reopening the old theme-admission branch.

### JOURNAL-0059

- Date: 2026-03-29
- Author: Codex
- Title: The last useful broad-challenger lever is the regime switch buffer, not holding or exit micro-tuning
- Related Decision: DEC-0059
- Related Runs: 20260329T060715Z_e2f8dc2a, 20260329T060753Z_bad3ddaa, 20260329T060852Z_0f4c9bd2
- Protocol Version: protocol_v1.0
- Hypothesis: If the remaining gate gap is truly narrow, then a micro-refinement sweep should show one clearly productive lever rather than several equally plausible tweaks.
- What Changed: Ran two narrow refinement sweeps around `balanced_targeted_timing_repair`. The first compared regime smoothing against slightly tighter holding/exit discipline. The second focused only on `switch_margin_buffer` variants and then tested tiny holding/exit tweaks on top of the best buffer-only candidate.
- Expected Impact: Learn whether the repo should keep refining the broad challenger through risk/holding discipline or through smoother regime switching.
- Observed Result: The signal is clean. The first sweep [20260329T060715Z_e2f8dc2a_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060715Z_e2f8dc2a_comparison.json) already showed that holding/exit tightening was not helping, while regime-buffer tuning was. The second sweep [20260329T060753Z_bad3ddaa_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060753Z_bad3ddaa_comparison.json) then identified `buffer_only_012` as the best micro-variant. Its gate report [buffer_only_012_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer_only_012_validation_gate_v1.json) still fails, but only because `mean_max_drawdown_improvement` remains slightly short (`0.002504 < 0.003`) while every other gate check passes. The final guard sweep [20260329T060852Z_0f4c9bd2_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T060852Z_0f4c9bd2_comparison.json) shows that tiny hold/exit tweaks on top of `buffer_only_012` do not improve anything meaningful.
- Side Effects / Risks: This narrows the search space further, which is good for discipline, but it also suggests the repo may be approaching the limit of what can be won through simple threshold tuning alone.
- Conclusion: The remaining refinement target is now extremely specific. If the project reopens shared-default promotion work again, `buffer_only_012` is the right micro-branch to start from, not another round of hold/exit tweaks.
- Next Step: Keep the freeze in place and decide whether the next cycle should keep refining this narrow regime-buffer branch or stop threshold work and move to a deeper structural question.

### JOURNAL-0060

- Date: 2026-03-29
- Author: Codex
- Title: Final threshold interpolation confirms that the broad-challenger gap is no longer a simple parameter-tuning problem
- Related Decision: DEC-0060
- Related Runs: 20260329T061427Z_eaa04329
- Protocol Version: protocol_v1.0
- Hypothesis: If the repo is still missing promotion only because the broad challenger is slightly under-tuned, then a tiny interpolation around `buffer_only_012` should finally push `mean_max_drawdown_improvement` across the `0.003` gate.
- What Changed: Ran one last narrow interpolation pass around `buffer_only_012`, varying only `min_score_margin`, `switch_margin_buffer`, and `min_top_score`, then checked the best nearby variant through a dedicated gate report.
- Expected Impact: Either discover the final threshold-level promotion candidate or establish a credible stopping point for more threshold search.
- Observed Result: The best nearby variant, `buffer012_top262`, is only a marginal move from `buffer_only_012`. Its gate report [buffer012_top262_validation_gate_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/gates/buffer012_top262_validation_gate_v1.json) improves `mean_max_drawdown_improvement` only from `0.002504` to `0.002547`, still below the `0.003` threshold. The comparison report [20260329T061427Z_eaa04329_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T061427Z_eaa04329_comparison.json) confirms that no tiny interpolation in this neighborhood changes the overall picture.
- Side Effects / Risks: This is a useful stopping result, but it also means the next meaningful gain is less likely to come from simple parameter search.
- Conclusion: Threshold-only tuning around the current broad challenger is now close to exhausted. The freeze should stay in place, and the next cycle should ask a deeper structural drawdown question instead of trying more microscopic parameter variants.
- Next Step: Keep `buffer_only_012` as the best threshold-level refinement branch and move the next research cycle away from narrow interpolation.

### JOURNAL-0061

- Date: 2026-03-29
- Author: Codex
- Title: The remaining drawdown gap is now localized to a theme-side pocket rather than spread across all packs
- Related Decision: DEC-0061
- Related Runs: 20260329T061729Z_4197eb4d
- Protocol Version: protocol_v1.0
- Hypothesis: If threshold tuning is already near exhaustion, then the remaining gate miss should show up as a concentrated structural pocket rather than a broad weak average across all packs and strategies.
- What Changed: Added `drawdown_gap_analysis.py`, `run_drawdown_gap_analysis.py`, `buffer_only_012_time_slice_validation_v1.yaml`, and `buffer_only_012_drawdown_gap_analysis_v1.yaml`, then reran a dedicated quarterly validation for `shared_default` versus `buffer_only_012`.
- Expected Impact: Replace the vague statement "drawdown improvement is still a bit short" with an explicit map of where the shortage really lives.
- Observed Result: The report [buffer_only_012_drawdown_gap_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/buffer_only_012_drawdown_gap_analysis_v1.json) shows the remaining blocker is local, not global. The weakest dataset-strategy summary is `theme_research_v4 / mainline_trend_a` with `mean_drawdown_improvement = 8.8e-05`. The weakest slice is `theme_research_v4 / 2024_q1` with `mean_drawdown_improvement = -0.000354`. The worst individual rows are the `theme_research_v4 / 2024_q1` rows, especially `mainline_trend_c` and `mainline_trend_b`, both of which are slightly worse than the incumbent on drawdown in that slice.
- Side Effects / Risks: This diagnosis makes the next cycle narrower, but it also means the next gain is likely to require understanding one pack/slice structure rather than finding a universal threshold tweak.
- Conclusion: The repo no longer has a "broad challenger" problem in the abstract. It has a localized theme-side drawdown pocket.
- Next Step: If refinement continues, the next cycle should study `theme_research_v4 / 2024_q1` directly rather than reopening global threshold search.

### JOURNAL-0062

- Date: 2026-03-29
- Author: Codex
- Title: The localized theme-side drawdown pocket is driven first by a repeated `300750` trade-sequence shift
- Related Decision: DEC-0062
- Related Runs: theme_q1_trade_divergence_v1, theme_q1_symbol_timeline_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the `theme_research_v4 / 2024_q1` drawdown pocket is structural, then the damage should show up as a small number of repeated symbol-level trade-path shifts rather than as diffuse noise across many symbols.
- What Changed: Added `slice_trade_divergence.py`, `run_slice_trade_divergence.py`, `symbol_timeline_replay.py`, and `run_symbol_timeline_replay.py`, then compared `shared_default` against `buffer_only_012` on the weakest slice.
- Expected Impact: Turn the localized drawdown pocket into a concrete trade-path problem with identifiable symbols and dates.
- Observed Result: The first clear driver is `300750`. The divergence report [theme_q1_trade_divergence_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_trade_divergence_v1.json) shows the same `-530.7` pnl delta for `300750` across all three strategies. The timeline replay [theme_q1_symbol_timeline_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_timeline_300750_v1.json) then shows the mechanism: `buffer_only_012` takes an extra losing trade around `2024-01-22 -> 2024-01-23`, and later does not emit the profitable `2024-02-06` buy that `shared_default` still turns into a winning `2024-02-06 -> 2024-02-07` trade.
- Side Effects / Risks: This is strong local evidence, but it still needs one more step of diagnosis before any rule change: the repo does not yet know whether the bad sequence comes primarily from sector-approval path differences, assignment drift, or a combination of both.
- Conclusion: The remaining drawdown blocker is now a concrete symbol-sequence problem, not a vague broad-stability gap.
- Next Step: If the next cycle continues, inspect the approval / assignment path around `300750` on `2024-01-22` and `2024-02-06` directly, then check whether a second symbol shows the same structural pattern before considering any repair.

### JOURNAL-0063

- Date: 2026-03-29
- Author: Codex
- Title: The `300750` blocker is a repeated day-level path shift, not a one-off bad trade
- Related Decision: DEC-0063
- Related Runs: theme_q1_symbol_path_shift_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `300750` is a real structural driver, then the same day-level path-shift dates should repeat across multiple strategies instead of appearing as a one-off artifact in a single trade list.
- What Changed: Added `symbol_path_shift_analysis.py` and `run_symbol_path_shift_analysis.py`, then compared the incumbent and challenger daily paths inside the existing `300750` timeline replay.
- Expected Impact: Distinguish between a mere trade-list curiosity and a real repeated mechanism that can justify deeper structural investigation.
- Observed Result: The report [theme_q1_symbol_path_shift_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_path_shift_300750_v1.json) shows the same repeated shift dates across all three strategies: `2024-01-19`, `2024-01-22`, `2024-02-02`, `2024-02-05`, and `2024-02-06`. The most actionable pattern is: on `2024-01-19` the challenger's approved sector shifts to `BK1173` and it emits a buy that the incumbent does not; on `2024-02-05` the incumbent still has permission and buys while the challenger loses permission entirely; and on `2024-02-02` the challenger's assignment flips to `junk` while the incumbent remains `leader`.
- Side Effects / Risks: This is now strong evidence for one symbol, but it still needs validation on at least one more symbol before the repo treats it as a general repair target.
- Conclusion: The remaining drawdown blocker is now best described as a repeated approval-path and assignment-drift sequence.
- Next Step: The next cycle should look for the same mechanism on a second theme-side symbol before any repair hypothesis is turned into code.

### JOURNAL-0064

- Date: 2026-03-29
- Author: Codex
- Title: The first concrete blocker mechanism splits into hysteresis on one date and threshold-edge permission loss on another
- Related Decision: DEC-0064
- Related Runs: theme_q1_symbol_path_shift_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the repeated `300750` path shift is real, then the key dates should resolve into a small number of specific upstream mechanisms rather than a single vague sequence story.
- What Changed: Inspected the `theme_research_v4` stock snapshots, sector snapshots, and concept mapping around the repeated shift dates after generating the symbol path-shift report.
- Expected Impact: Turn the `300750` sequence into a repair-relevant upstream diagnosis rather than just another descriptive replay.
- Observed Result: The mechanism now splits cleanly. On `2024-01-19`, the sector scores are very close but still ordered in favor of `计算机、通信和其他电子设备制造业` (`2.986566`) over `BK1173` (`2.880075`); the incumbent rotates while the challenger keeps `BK1173`, which is consistent with hysteresis / approval-path persistence. On `2024-02-05`, `BK1173` scores `2.583525`, which is above the theme-pack default `min_top_score=2.5` but below the challenger's `2.6`, so the challenger loses permission on a threshold-edge day and misses the later profitable `2024-02-06 -> 2024-02-07` trade that the incumbent still captures.
- Side Effects / Risks: This is a much sharper mechanism story, but it is still based on one symbol.
- Conclusion: The first concrete blocker is no longer just "approval-path and assignment drift" in general. It is specifically a mix of hysteresis on one borderline rotation date and threshold-edge permission loss on a later re-entry date.
- Next Step: The next cycle should test whether a second symbol in `theme_research_v4 / 2024_q1` shows the same two-part mechanism before any repair idea is entertained.

### JOURNAL-0065

- Date: 2026-03-29
- Author: Codex
- Title: `002466` confirms the path-shift shape without reproducing the `300750` damage case
- Related Decision: DEC-0065
- Related Runs: theme_q1_symbol_timeline_002466_v1, theme_q1_symbol_path_shift_002466_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the `300750` mechanism is structural rather than idiosyncratic, then a second tradable symbol in `theme_research_v4 / 2024_q1` should show the same upstream path-shift dates even if it does not produce the same pnl damage.
- What Changed: Added `theme_q1_symbol_timeline_002466_v1.yaml` and `theme_q1_symbol_path_shift_002466_v1.yaml`, then replayed `shared_default` versus `buffer_only_012` for `002466`.
- Expected Impact: Distinguish between “the mechanism only exists on `300750`�?and “the mechanism is broader, but only sometimes propagates into trade damage.�?- Observed Result: The replay [theme_q1_symbol_timeline_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_timeline_002466_v1.json) and path-shift report [theme_q1_symbol_path_shift_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_path_shift_002466_v1.json) show the same two most important upstream dates as `300750`: `2024-01-19` splits on approved sector (`electronics` versus `BK1173`), and `2024-02-05` splits on permission (`true` versus `false`). Unlike `300750`, however, both candidates for `002466` still execute the same real trade path and finish with identical pnl. The repeated shape is real; the damage requires an additional state transition that `002466` does not cross.
- Side Effects / Risks: This reduces the risk of overfitting to a single symbol, but it also means the repo still needs at least one more intermediate symbol if it wants to fully map when a path shift becomes economically harmful.
- Conclusion: `300750` is not a pure outlier. The upstream path-shift mechanism repeats on another tradable symbol, but the pnl impact is conditional rather than automatic.
- Next Step: Keep the next symbol-level diagnosis narrow and target another tradable theme symbol that is closer to the boundary between “shape repeats�?and “damage repeats.�?
### JOURNAL-0066

- Date: 2026-03-29
- Author: Codex
- Title: `002902` shows repeated assignment divergence and permission loss without producing a second damage case
- Related Decision: DEC-0066
- Related Runs: theme_q1_symbol_timeline_002902_v1, theme_q1_symbol_path_shift_002902_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the remaining theme-side blocker is truly conditional, then a third tradable symbol should be able to repeat some of the same path-shift dates and assignment divergence while still keeping realized trades unchanged.
- What Changed: Added `theme_q1_symbol_timeline_002902_v1.yaml` and `theme_q1_symbol_path_shift_002902_v1.yaml`, then replayed `shared_default` versus `buffer_only_012` for a longer `Q1` range with more trades.
- Expected Impact: Distinguish between “repeated path shifts that merely exist�?and “repeated path shifts that actually alter economic outcomes.�?- Observed Result: The replay [theme_q1_symbol_timeline_002902_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_timeline_002902_v1.json) and path-shift report [theme_q1_symbol_path_shift_002902_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_symbol_path_shift_002902_v1.json) show three repeated cross-strategy dates: `2024-01-23`, `2024-02-05`, and `2024-02-28`. The first and third are primarily assignment-layer splits (`leader` versus `junk`, plus a later exit-reason split), while `2024-02-05` again reproduces the incumbent-permission / challenger-no-permission pattern. Even so, the realized trades and total pnl remain identical across both candidates in all three strategies.
- Side Effects / Risks: This makes the diagnosis more robust, but it also warns that many repeated theme-side splits may stay latent until they cross a tradable state boundary.
- Conclusion: The repo now has three useful symbol-level reference classes in the same pocket: `300750` as the first damage case, `002466` as the first repeated-shape case, and `002902` as the first repeated-assignment-divergence case.
- Next Step: The next cycle should focus less on finding more repeated dates and more on identifying the exact state transition that turns a latent path split into real trade damage.

### JOURNAL-0068

- Date: 2026-03-29
- Author: Codex
- Title: The current three-symbol set now has a clean action-state ranking: only `300750` crosses the trigger boundary
- Related Decision: DEC-0068
- Related Runs: theme_action_state_divergence_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the new action-state boundary is really useful, then the current three-symbol set should separate cleanly into triggered and non-triggered cases without another layer of manual interpretation.
- What Changed: Added `action_state_divergence_analysis.py`, `run_action_state_divergence_analysis.py`, and `theme_action_state_divergence_v1.yaml`, then aggregated the existing symbol path-shift reports one level deeper.
- Expected Impact: Turn the abstract rule “path shifts only matter after they change actions or active position state�?into a concrete ranking tool for future symbol-level triage.
- Observed Result: The report [theme_action_state_divergence_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_action_state_divergence_v1.json) is clean: among `300750`, `002466`, and `002902`, only `300750` has repeated dates that also trigger action-state divergence, specifically `2024-01-19`, `2024-01-22`, `2024-02-05`, and `2024-02-06`. The other two symbols remain fully latent under this stricter ranking.
- Side Effects / Risks: This ranking is useful, but it still comes from a small symbol set and should guide priority rather than act as a hard protocol rule.
- Conclusion: The repo now has a sharper prioritization tool than “find repeated shift dates.�?It can focus on symbols that already cross the action-state boundary.
- Next Step: Use action-state trigger dates as the first filter for any future theme-side replay or structural repair work.

### JOURNAL-0069

- Date: 2026-03-29
- Author: Codex
- Title: `300750` is no longer one vague blocker; it is four repeated trigger classes
- Related Decision: DEC-0069
- Related Runs: theme_trigger_taxonomy_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the `300750` damage case is already narrow enough to repair intelligently, then its repeated action-state trigger dates should decompose into a small number of named trigger classes instead of one blended failure story.
- What Changed: Added `trigger_taxonomy_analysis.py`, `run_trigger_taxonomy_analysis.py`, and `theme_trigger_taxonomy_300750_v1.yaml`, then classified the twelve repeated action-state trigger rows from `300750`.
- Expected Impact: Give the next repair cycle a more precise target than “fix the theme-side blocker.�?- Observed Result: The report [theme_trigger_taxonomy_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_trigger_taxonomy_300750_v1.json) shows four repeated trigger classes, each repeated across all three strategies: `early_buy_trigger` (`2024-01-19`), `forced_sell_trigger` (`2024-01-22`), `missed_buy_trigger` (`2024-02-05`), and `position_gap_exit_trigger` (`2024-02-06`). The current blocker is therefore a four-step sequence, not one undifferentiated failure.
- Side Effects / Risks: The counts are symmetric across strategies, but that still does not prove which trigger type contributes the most economic damage.
- Conclusion: The repo can now stop talking about `300750` as a generic damage case and start ranking repair work by trigger family.
- Next Step: The next cycle should estimate which of the four trigger classes carries the most real damage and prioritize that class first.

### JOURNAL-0070

- Date: 2026-03-29
- Author: Codex
- Title: The first trigger-family priority ranking is clear: missed re-entry beats early entry as the next repair target
- Related Decision: DEC-0070
- Related Runs: theme_trigger_priority_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the four trigger families are not equally important, then the symbol timeline should show a larger unique-cycle pnl disadvantage on one side of the trigger sequence.
- What Changed: Added `trigger_priority_analysis.py`, `run_trigger_priority_analysis.py`, and `theme_trigger_priority_300750_v1.yaml`, then ranked the four trigger families by the unique incumbent-only versus challenger-only cycle pnl they align with.
- Expected Impact: Move the next repair cycle from “which trigger family exists�?to “which trigger family is worth repairing first.�?- Observed Result: The report [theme_trigger_priority_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_trigger_priority_300750_v1.json) is decisive. The incumbent-only unique cycle around `2024-02-06 -> 2024-02-07` contributes `1969.137` across the three strategies, while the challenger-only extra cycle around `2024-01-22 -> 2024-01-23` contributes only `377.037`. This means `missed_buy_trigger` and `position_gap_exit_trigger` are economically dominant, while `early_buy_trigger` and `forced_sell_trigger` are secondary.
- Side Effects / Risks: This ranking is still based on one damage symbol and should not be promoted into a protocol-level rule without more validation.
- Conclusion: The repo now has a real repair order. The next theme-side cycle should start from missed re-entry and position-gap exit, not from early entry suppression.
- Next Step: If repair work resumes, target the `2024-02-05 -> 2024-02-06` chain first and treat the `2024-01-19 -> 2024-01-22` chain as a lower-priority clean-up branch.

### JOURNAL-0071

- Date: 2026-03-29
- Author: Codex
- Title: The dominant theme-side blocker is now a complete two-date missed re-entry chain
- Related Decision: DEC-0071
- Related Runs: theme_missed_reentry_chain_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the trigger-family ranking is already sharp enough, then the leading `missed_buy -> position_gap_exit` branch should appear as a full repeated chain rather than just two loosely related trigger labels.
- What Changed: Added `missed_reentry_chain_analysis.py`, `run_missed_reentry_chain_analysis.py`, and `theme_missed_reentry_chain_300750_v1.yaml`, then replayed only the `2024-02-05 -> 2024-02-06` branch for `300750`.
- Expected Impact: Replace the generic statement "missed re-entry matters most" with a concrete chain-level diagnosis that can guide the next repair cycle.
- Observed Result: The report [theme_missed_reentry_chain_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_missed_reentry_chain_300750_v1.json) shows a complete chain in all three strategies. On `2024-02-05`, the incumbent still has permission, keeps `BK1173`, and emits `buy`, while the challenger has no permission and emits nothing. On `2024-02-06`, both sides again have permission, but only the incumbent carries the resulting position and exits it. The incumbent-only missed-cycle pnl is `1969.137` in aggregate, with `656.379` per strategy.
- Side Effects / Risks: This sharpens the blocker, but it is still a one-symbol damage chain and should remain a local research conclusion until a second damage case is found.
- Conclusion: The current theme-side blocker is no longer best described as four trigger families or one fuzzy local pocket. It is now best described as a complete incumbent-side missed re-entry chain.
- Next Step: If refinement continues, study why the challenger loses permission on `2024-02-05`; the `2024-02-06` position-gap exit should be treated as the downstream consequence of that missed re-entry, not as the first independent repair target.

### JOURNAL-0072

- Date: 2026-03-29
- Author: Codex
- Title: The first date in the dominant chain is a clean threshold-edge permission loss
- Related Decision: DEC-0072
- Related Runs: theme_permission_loss_edge_300750_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the incumbent-side missed re-entry chain is already sharply localized, then the first date in that chain should resolve into one concrete regime-edge explanation rather than stay a generic "theme path" story.
- What Changed: Added `permission_loss_edge_analysis.py`, `run_permission_loss_edge_analysis.py`, and `theme_permission_loss_edge_300750_v1.yaml`, then compared the incumbent and challenger permission state on `2024-02-05` using the real `theme_research_v4` pack plus the existing timeline report.
- Expected Impact: Replace the vague statement "the challenger misses the buy" with a date-level mechanism that can guide the next repair decision.
- Observed Result: The report [theme_permission_loss_edge_300750_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_permission_loss_edge_300750_v1.json) shows a clean edge. On `2024-02-05`, `BK1173` scores `2.583525`, well ahead of the second sector (`1.616182`). The incumbent still approves that top sector under `min_top_score=2.5`, but the challenger rejects it with reason `top_score_below_threshold` under `min_top_score=2.6`. The miss is only `0.016475` below the challenger's threshold, and the action rows show the consequence directly: all three incumbent strategies emit `buy`, while all three challenger strategies emit nothing.
- Side Effects / Risks: This is a sharp mechanism, but it is still localized to one symbol and one slice.
- Conclusion: The first date in the dominant chain is no longer a generic regime-path mystery. It is a narrow threshold-edge permission-loss day.
- Next Step: If refinement continues, decide whether that narrow threshold edge is worth relaxing or whether the repo should accept it as the remaining price of the stricter challenger and keep the freeze unchanged.

### JOURNAL-0073

- Date: 2026-03-29
- Author: Codex
- Title: The obvious `2.60 -> 2.58` threshold-edge repair is real but not strong enough to matter
- Related Decision: DEC-0073
- Related Runs: 20260329T070422Z_3a231b85, buffer_top258_validation_gate_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the remaining blocker is mostly a `0.016475` threshold-edge miss on `2024-02-05`, then directly relaxing only that edge should produce a meaningful three-pack stability improvement.
- What Changed: Added `theme_threshold_edge_relief_sweep_v1.yaml` and `buffer_top258_validation_gate_v1.yaml`, then ran a narrow `2.60 -> 2.59 -> 2.58` sweep and gated the best relaxed candidate.
- Expected Impact: Decide whether the repo should keep studying this threshold edge or accept it as the residual cost of the stricter challenger.
- Observed Result: The local repair is real but small. `buffer_top258` slightly improves the `theme_research_v4` rows relative to `buffer_only_012`, but baseline and market packs stay unchanged, theme capture does not recover, and the stricter gate still fails on `mean_max_drawdown_improvement` (`0.002509 < 0.003`). The candidate also trails `buffer_only_012` on composite stability.
- Side Effects / Risks: This closes the most obvious local repair path, but it does not yet explain what deeper structural change would improve drawdown without reopening older problems.
- Conclusion: The repo should not promote or replace the frozen challenger branch with this threshold-relaxed variant. The threshold edge is now a documented local probe, not the solution.
- Next Step: If refinement continues, the next work should move beyond simple threshold relief and study whether the remaining blocker should simply be accepted as the residual cost of the stricter challenger.

### JOURNAL-0074

- Date: 2026-03-29
- Author: Codex
- Title: The current evidence supports accepting the remaining blocker as residual cost rather than continuing narrow tuning
- Related Decision: DEC-0074
- Related Runs: residual_cost_acceptance_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the remaining blocker is already small, local, and not cheaply repairable, then the repo should be able to justify a freeze posture directly instead of staying in an endless local tuning loop.
- What Changed: Added `residual_cost_acceptance_analysis.py`, `run_residual_cost_acceptance_analysis.py`, and `residual_cost_acceptance_v1.yaml`, then combined the frozen-branch gate, the drawdown-gap localization report, the missed re-entry chain report, and the failed cheap-relief gate into one acceptance summary.
- Expected Impact: Turn the current freeze from a passive "not yet" status into an explicit research decision.
- Observed Result: The report [residual_cost_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/residual_cost_acceptance_v1.json) is decisive enough for the current stage. The challenger still wins broadly on rank and return; the remaining strict-gate shortfall is only `0.000496`; the blocker is localized to `theme_research_v4 / 2024_q1`; and the obvious cheap local repair adds only `0.000005` of drawdown improvement versus the frozen branch. The current posture is therefore `freeze_and_accept_residual_cost`.
- Side Effects / Risks: This is still a V1/V1.1 research-stage conclusion, not a claim that the blocker will never matter again under future broader data.
- Conclusion: The repo now has explicit evidence that more threshold grinding is not the right next use of effort.
- Next Step: If future work returns to this area, it should begin from deeper structure or new data rather than more narrow threshold interpolation.

### JOURNAL-0075

- Date: 2026-03-29
- Author: Codex
- Title: The next V1.1 research loop should start from specialist alpha pockets, not the frozen blocker
- Related Decision: DEC-0075
- Related Runs: 20260329T071117Z_fa50f33e, specialist_alpha_analysis_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the freeze blocker is now small and accepted, then the next valuable V1.1 question should be where specialist branches still beat both broad anchors rather than how to squeeze one more threshold tweak out of the frozen challenger.
- What Changed: Added `time_slice_validation_v3.yaml` to rerun the current four relevant candidates (`shared_default`, `buffer_only_012`, `baseline_expansion_branch`, `theme_strict_quality_branch`) on the three current packs, then added `specialist_alpha_analysis.py` and `specialist_alpha_analysis_v1.yaml` to rank non-overlapping specialist pockets.
- Expected Impact: Redirect the next research cycle from blocker repair to new alpha exploration while keeping the current freeze intact.
- Observed Result: The new time-slice report [20260329T071117Z_fa50f33e_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T071117Z_fa50f33e_comparison.json) still says `buffer_only_012` is the most stable broad candidate. But the new specialist report [specialist_alpha_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v1.json) shows where future edge likely lives: `baseline_expansion_branch` has `7` capture-opportunity pockets, with its strongest one at `theme_research_v4 / 2024_q1 / mainline_trend_c`; `theme_strict_quality_branch` has `9` drawdown-opportunity pockets, with its cleanest one at `baseline_research_v1 / 2024_q3 / mainline_trend_b,c`.
- Side Effects / Risks: These are entry points for V1.1 research, not new defaults or promotion evidence.
- Conclusion: The repo now has a clear next-step map. The old blocker can stay frozen, and the next alpha cycle can start from specialist pockets with non-overlapping edge.
- Next Step: If the next cycle is capture-first, start from `baseline_expansion_branch` on `theme_research_v4 / 2024_q1`. If it is drawdown-first, start from `theme_strict_quality_branch` on `baseline_research_v1 / 2024_q3`.

### JOURNAL-0076

- Date: 2026-03-29
- Author: Codex
- Title: The first capture-specialist pocket is driven by four concrete windows, not a diffuse aggregate effect
- Related Decision: DEC-0076
- Related Runs: specialist_pocket_window_analysis_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `baseline_expansion_branch` truly owns the top capture pocket at `theme_research_v4 / 2024_q1 / mainline_trend_c`, then the edge should reduce to a short list of replayable windows rather than stay a broad slice-level score.
- What Changed: Added `specialist_pocket_window_analysis.py`, `run_specialist_pocket_window_analysis.py`, and `specialist_pocket_window_analysis_v1.yaml`, then compared `baseline_expansion_branch` against `shared_default` and `buffer_only_012` window by window inside the target pocket.
- Expected Impact: Turn the next V1.1 capture cycle into a focused replay sequence instead of another broad sweep.
- Observed Result: The report [specialist_pocket_window_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_pocket_window_analysis_v1.json) shows only `4` improved windows in the whole pocket, and `2` of them are windows both anchors miss entirely. The strongest driver is `002466_2`, where the specialist captures `0.937549` of a `0.054354` window while both anchors stay at `0.0`. The second full both-anchor miss is `000155_5`, with a `0.408511` capture edge. `600338_5` and `300518_7` are still useful, but they are partial-capture improvements rather than fresh window openings.
- Side Effects / Risks: This focuses the next replay cycle tightly, but the pocket remains local and may change as the theme pack evolves.
- Conclusion: The first capture-specialist pocket is now specific enough to work on directly. The repo no longer needs to ask "which slice next"; it can ask "why did `002466_2` and `000155_5` open only under expansion logic?".
- Next Step: Replay `002466_2` first, then `000155_5`, and only after that study the partial-capture lifts in `600338_5` and `300518_7`.

### JOURNAL-0077

- Date: 2026-03-29
- Author: Codex
- Title: `002466_2` opens because the specialist upgrades hierarchy admission one day earlier, not because it loosens regime approval
- Related Decision: DEC-0077
- Related Runs: theme_q1_symbol_timeline_002466_capture_v1, theme_q1_specialist_window_opening_002466_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `002466_2` is the strongest new-window driver inside the first capture-specialist pocket, then the true opening edge should reduce to one concrete day and one concrete upstream difference rather than a vague "expansion branch is looser" explanation.
- What Changed: Added `specialist_window_opening_analysis.py`, `run_specialist_window_opening_analysis.py`, and `theme_q1_specialist_window_opening_002466_v1.yaml`, then reran the `002466` replay using the real `baseline_expansion_branch` override from the three-pack validation instead of the earlier placeholder approximation.
- Expected Impact: Tell the next replay cycle which layer to study first: regime, filters, entries, or hierarchy admission.
- Observed Result: The report [theme_q1_specialist_window_opening_002466_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_002466_v1.json) is unusually clean. On `2024-01-10`, the specialist opens the window while both broad anchors remain blocked. All three candidates share `permission_allowed=true`, the same passed filters, and the same `mid_trend_follow` entry trigger. The only real difference is hierarchy admission: the specialist upgrades `002466` from `junk` to `late_mover` via `late_mover_quality_fallback`, which emits the buy one day earlier and turns the later trade from a loss into a strong captured window.
- Side Effects / Risks: This is a strong local clue, but still just one window. The same pattern should be checked on `000155_5` before it is treated as a reusable specialist-capture mechanism.
- Conclusion: `002466_2` is not a regime-edge case. It is a hierarchy-admission edge.
- Next Step: Replay `000155_5` next and check whether it also opens through a specialist-only non-junk or `late_mover` upgrade while the broad anchors keep the symbol in `junk`.

### JOURNAL-0078

- Date: 2026-03-29
- Author: Codex
- Title: `000155_5` is a persistence edge: the specialist keeps the window alive while broad anchors churn out
- Related Decision: DEC-0078
- Related Runs: theme_q1_symbol_timeline_000155_capture_v1, theme_q1_specialist_window_persistence_000155_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the second full both-anchor miss in the first capture pocket is not opened earlier like `002466_2`, then it should still have one concrete specialist day where the window survives only because the branch refuses to churn out.
- What Changed: Added `specialist_window_persistence_analysis.py`, `run_specialist_window_persistence_analysis.py`, and `theme_q1_specialist_window_persistence_000155_v1.yaml`, then replayed `000155` over the full `2024-02-21 -> 2024-02-29` pocket window.
- Expected Impact: Determine whether the capture pocket is one repeated opening pattern or already splits into multiple specialist edge families.
- Observed Result: The persistence report [theme_q1_specialist_window_persistence_000155_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_persistence_000155_v1.json) shows a different shape from `002466_2`. All three candidates are already in the trade, but on `2024-02-22` the specialist still holds with `structure_intact`, `late_mover`, and `holding_health_score=3.5`, while both broad anchors emit `sell` because the symbol degrades to `junk` and triggers `assignment_became_junk`. The specialist then preserves the window and exits only on `2024-02-28`, turning the rest of the move into a stronger captured segment.
- Side Effects / Risks: This proves the first capture pocket is not one single template; it already contains at least two different specialist mechanisms.
- Conclusion: `000155_5` is not an opening edge. It is a persistence edge.
- Next Step: Move to one of the partial-capture cases, preferably `600338_5`, and test whether it behaves like the opening family, the persistence family, or a third hybrid family.

### JOURNAL-0079

- Date: 2026-03-29
- Author: Codex
- Title: `600338_5` is a staggered opening edge: the specialist opens first and the anchors enter later
- Related Decision: DEC-0079
- Related Runs: theme_q1_symbol_timeline_600338_capture_v1, theme_q1_specialist_window_opening_600338_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `600338_5` is only a partial-capture lift, then it might either define a third hybrid specialist family or simply be a weaker form of the same opening-edge logic already seen in `002466_2`.
- What Changed: Added `theme_q1_symbol_timeline_600338_capture_v1.yaml` and `theme_q1_specialist_window_opening_600338_v1.yaml`, replayed the symbol through the full pocket, and reused the opening analyzer on the exact window.
- Expected Impact: Decide whether the pocket taxonomy should expand or stay compact.
- Observed Result: The report [theme_q1_specialist_window_opening_600338_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_600338_v1.json) shows that `600338_5` is still an opening-edge case. On `2024-02-21`, the specialist emits the first buy while both broad anchors remain flat. Permission is already true for all three, and the same filters and entry triggers are present. The difference again is hierarchy admission: the specialist upgrades the symbol to `late_mover`, while both anchors keep it in `junk`. The anchors later enter the move, which is why this case becomes a partial-capture lift instead of a full both-anchor miss.
- Side Effects / Risks: This keeps the taxonomy compact, but one partial case (`300518_7`) still remains unresolved.
- Conclusion: `600338_5` is not a third family. It is a staggered opening edge.
- Next Step: Replay `300518_7` next and check whether the first capture pocket still fits entirely inside the current two-family taxonomy: opening edges and persistence edges.

### JOURNAL-0080

- Date: 2026-03-29
- Author: Codex
- Title: `300518_7` closes the first capture pocket without forcing a third mechanism family
- Related Decision: DEC-0080
- Related Runs: theme_q1_symbol_timeline_300518_capture_v1, theme_q1_specialist_window_opening_300518_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the last unresolved partial-capture case still behaves like an opening edge, then the first capture-specialist pocket can be treated as structurally closed under a compact two-family taxonomy.
- What Changed: Added `theme_q1_symbol_timeline_300518_capture_v1.yaml` and `theme_q1_specialist_window_opening_300518_v1.yaml`, replayed `300518`, and applied the same opening-edge test used on `002466_2` and `600338_5`.
- Expected Impact: Decide whether the repo should keep expanding the first pocket taxonomy or move on to a higher-level specialist research question.
- Observed Result: The report [theme_q1_specialist_window_opening_300518_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q1_specialist_window_opening_300518_v1.json) confirms a light opening-edge shape. On `2024-03-18`, the specialist emits the first buy while both broad anchors stay flat. Permission remains true for all three; the shared triggers are already present; and the decisive difference is again hierarchy admission: `late_mover` for the specialist versus `junk` for both anchors. The later anchor entry makes this a smaller partial-capture lift than `600338_5`, but not a new mechanism family.
- Side Effects / Risks: This closes the first pocket locally, but does not yet tell the repo how common each family is across later specialist pockets.
- Conclusion: The first capture-specialist pocket no longer needs a third family. It closes cleanly under two families: opening edges and persistence edges.
- Next Step: Move up one level. Either compare opening versus persistence frequency across more pockets, or switch to the drawdown-specialist branch for the next V1.1 cycle.

### JOURNAL-0081

- Date: 2026-03-29
- Author: Codex
- Title: The cleanest drawdown-specialist pocket is mostly a `600519` story
- Related Decision: DEC-0081
- Related Runs: baseline_q3_symbol_timeline_000001_quality_v1, baseline_q3_symbol_timeline_000333_quality_v1, baseline_q3_symbol_timeline_600519_quality_v1, baseline_q3_symbol_cycle_delta_600519_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `theme_strict_quality_branch` really owns the cleanest drawdown-specialist pocket at `baseline_research_v1 / 2024_q3 / mainline_trend_b`, then one symbol should account for most of the branch's realized improvement.
- What Changed: Added three symbol-level replay configs for `000001`, `000333`, and `600519`, then added `symbol_cycle_delta_analysis.py` to compare exact closed-trade cycles between `shared_default` and `theme_strict_quality_branch`.
- Expected Impact: Replace the broad slice-level drawdown story with a concrete symbol-level next target.
- Observed Result: The replay output is decisive enough. `000001` and `000333` both degrade under the quality branch (`-27.127` and `-359.865` versus `shared_default`), while `600519` improves strongly (`+1957.0392`). The cycle-delta report [baseline_q3_symbol_cycle_delta_600519_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_symbol_cycle_delta_600519_v1.json) shows why: the incumbent carries four unique cycles totaling `-10698.5493`, while the challenger's unique cycles total `-8741.5101`. The quality branch does not become magically profitable on every unmatched cycle; it simply removes enough incumbent-only losing churn to dominate the pocket-level edge.
- Side Effects / Risks: Exact-cycle matching is intentionally strict, so nearby but shifted cycles should still be replayed before turning this into a general drawdown-specialist rule.
- Conclusion: The first drawdown-specialist pocket is mostly a `600519` problem, not a balanced three-symbol effect.
- Next Step: Replay `600519` at the date level and study why the quality branch avoids the incumbent-only losing cycles around `2024-07-03`, `2024-08-01`, and `2024-08-09`.

### JOURNAL-0082

- Date: 2026-03-29
- Author: Codex
- Title: `600519` now reduces the first drawdown pocket through three distinct cycle mechanisms
- Related Decision: DEC-0082
- Related Runs: baseline_q3_nearby_cycle_bridge_600519_v1, baseline_q3_cycle_mechanism_600519_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the first drawdown-specialist pocket is already mature enough to be reusable, then the `600519` replay should collapse into a small mechanism set instead of remaining a loose trade list.
- What Changed: Added `cycle_mechanism_analysis.py`, plus `baseline_q3_cycle_mechanism_600519_v1.yaml`, and classified the incumbent-only `600519` cycles using the existing bridge and timeline reports.
- Expected Impact: Replace "quality branch avoids some churn" with a compact, portable drawdown taxonomy.
- Observed Result: The report [baseline_q3_cycle_mechanism_600519_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_600519_v1.json) now fixes the first drawdown pocket under three meaningful negative-cycle mechanisms. `2024-08-01 -> 2024-08-02` is `entry_suppression_avoidance`: the incumbent opens the cycle on `2024-07-31` and the quality branch never takes it. `2024-08-09 -> 2024-08-14` is `earlier_exit_loss_reduction`: both sides open the same bad cycle, but the quality branch exits on `2024-08-12` before the incumbent. `2024-07-03 -> 2024-07-05` is the failure case, `later_exit_loss_extension`: both sides open, but the quality branch exits later and makes the loss worse. The unmatched `2024-08-16 -> 2024-08-20` cycle is only a small avoided positive cycle and does not drive the drawdown edge.
- Side Effects / Risks: This taxonomy is still only anchored on one dominant symbol, so it should be reused on later drawdown pockets before it is treated as a broader law.
- Conclusion: The first drawdown-specialist pocket is no longer a vague "quality helps" claim. It is now a three-part cycle map: avoid some bad cycles entirely, shorten others, and still fail on at least one by holding too long.
- Next Step: Stop broad symbol hunting on this line. Reuse the cycle taxonomy on the next drawdown-specialist pocket and compare whether it shows the same three mechanisms.

### JOURNAL-0083

- Date: 2026-03-29
- Author: Codex
- Title: The first baseline-Q3 drawdown pocket is now confirmed as one shared `B/C` structure
- Related Decision: DEC-0083
- Related Runs: baseline_q3_trade_divergence_quality_c_v1, baseline_q3_symbol_timeline_600519_quality_c_v1, baseline_q3_cycle_mechanism_600519_c_v1, baseline_q3_cross_strategy_cycle_consistency_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `mainline_trend_c` replays the same `600519` drawdown map as `mainline_trend_b`, then the repo should stop treating them as two separate drawdown-specialist investigations.
- What Changed: Added the `mainline_trend_c` trade-divergence config plus a full `600519` replay chain (`timeline -> cycle delta -> nearby bridge -> cycle mechanism`) and then added `cross_strategy_cycle_consistency_analysis.py` to compare the `B` and `C` mechanism reports directly.
- Expected Impact: Decide whether the first drawdown-specialist line has become structurally stable enough to stop replaying it strategy by strategy.
- Observed Result: The new reports [baseline_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_trade_divergence_quality_c_v1.json), [baseline_q3_cycle_mechanism_600519_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_600519_c_v1.json), and [baseline_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cross_strategy_cycle_consistency_v1.json) show an exact match: `mainline_trend_b` and `mainline_trend_c` share the same three negative-cycle signatures on `600519` with the same mechanism labels. The `C` pocket is therefore not a second story; it is the same baseline-Q3 structural pocket repeating across two strategies.
- Side Effects / Risks: This still does not prove that every future drawdown pocket will share the same three-part map, only that this one is already stable across two strategy variants.
- Conclusion: The first drawdown-specialist pocket is now strong enough to treat as a reusable `B/C` template, not just a one-off `mainline_trend_b` replay.
- Next Step: Move to a different drawdown-specialist pocket and test whether it also collapses into the same three-part cycle taxonomy.

### JOURNAL-0084

- Date: 2026-03-29
- Author: Codex
- Title: The next drawdown-specialist pocket introduces a new `preemptive_loss_avoidance_shift` family
- Related Decision: DEC-0084
- Related Runs: market_q4_trade_divergence_quality_c_v1, market_q4_symbol_timeline_600519_quality_c_v1, market_q4_symbol_cycle_delta_600519_c_v1, market_q4_nearby_cycle_bridge_600519_c_v1, market_q4_cycle_mechanism_600519_c_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the next drawdown-specialist pocket is structurally similar to baseline-Q3, then its strongest symbol should reuse the same three negative-cycle mechanisms. If not, the drawdown-specialist line needs a second family.
- What Changed: Added a full replay chain for `market_research_v0 / 2024_q4 / mainline_trend_c`, starting from `slice_trade_divergence` and then drilling into `600519` through timeline, cycle-delta, bridge, and cycle-mechanism reports. I also extended `cycle_mechanism_analysis.py` so a nearby smaller challenger loss that happens *before* the incumbent's worse cycle gets a real name instead of staying buried under `other_reduced_loss_shift`.
- Expected Impact: Decide whether the first drawdown-specialist taxonomy can be reused wholesale or needs to branch.
- Observed Result: The pocket does not reuse the baseline-Q3 template. The symbol-level divergence report [market_q4_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_trade_divergence_quality_c_v1.json) shows that `600519` again dominates the positive delta (`+3133.1599`), but the mechanism report [market_q4_cycle_mechanism_600519_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_600519_c_v1.json) is different. The key negative-cycle repair is now `preemptive_loss_avoidance_shift`: the challenger first realizes a smaller loss on `2024-12-11 -> 2024-12-12`, then avoids the incumbent's larger `2024-12-13 -> 2024-12-16` loss. At the same time, the challenger also skips the incumbent's huge positive `2024-09-27 -> 2024-10-08` cycle, which enters the taxonomy as a large `entry_suppression_opportunity_cost`.
- Side Effects / Risks: This is a more ambiguous drawdown pocket than baseline-Q3 because the branch improves drawdown while also giving up a large positive cycle. It is a valid specialist pocket, but a less clean template.
- Conclusion: The drawdown-specialist line now has at least two families. Baseline-Q3 is a three-part `B/C` structural template; market-Q4 adds a second family built around `preemptive_loss_avoidance_shift` plus significant opportunity cost.
- Next Step: Test one more drawdown-specialist pocket before generalizing. The next useful question is whether `preemptive_loss_avoidance_shift` repeats elsewhere or whether it is unique to this market-Q4 case.

### JOURNAL-0085

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q4 / 300750` introduces a third drawdown-specialist family: `carry_in_basis_advantage`
- Related Decision: DEC-0085
- Related Runs: theme_q4_trade_divergence_quality_c_v1, theme_q4_symbol_timeline_300750_quality_c_v1, theme_q4_symbol_cycle_delta_300750_c_v1, theme_q4_nearby_cycle_bridge_300750_c_v1, theme_q4_cycle_mechanism_300750_c_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the next strongest drawdown-specialist pocket on `theme_research_v4 / 2024_q4 / mainline_trend_c` does not cleanly reuse either the baseline-Q3 or market-Q4 family, then the cycle taxonomy needs a third reduced-loss mechanism.
- What Changed: Added a full replay chain for `theme_q4 / 300750`, then extended `cycle_mechanism_analysis.py` and its tests so a nearby challenger cycle that enters before the incumbent but exits on the same day can be named `carry_in_basis_advantage` instead of staying in a generic catch-all bucket.
- Expected Impact: Decide whether the drawdown-specialist line can still be explained with only two families or whether it now needs a third one.
- Observed Result: The pocket does need a third family. The divergence report [theme_q4_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_trade_divergence_quality_c_v1.json) shows `300750` as the dominant positive driver (`+1464.4411`). The mechanism report [theme_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_300750_c_v1.json) then shows two reduced-loss mechanisms: `earlier_exit_loss_reduction` on `2024-10-28 -> 2024-10-30`, and the new `carry_in_basis_advantage` on `2024-11-06 -> 2024-11-07`, where the challenger buys on `2024-11-05`, keeps the position through `2024-11-06`, and exits with the same `2024-11-07` print as the incumbent but with a much better cost basis.
- Side Effects / Risks: This is now the third drawdown-specialist family in the repo, but it is still supported by one pocket-symbol chain. Reuse across later pockets still matters more than the label itself.
- Conclusion: The drawdown-specialist line no longer has only two families. `theme_q4 / 300750` adds a third one: `carry_in_basis_advantage`.
- Next Step: Move to the next drawdown-specialist pocket and test whether it repeats baseline-Q3, market-Q4, or this new `carry_in_basis_advantage` family.

### JOURNAL-0086

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q3 / 002460` repeats the baseline-style avoidance family rather than creating a fourth one
- Related Decision: DEC-0086
- Related Runs: theme_q3_trade_divergence_quality_c_v1, theme_q3_symbol_timeline_002460_quality_c_v1, theme_q3_symbol_cycle_delta_002460_c_v1, theme_q3_nearby_cycle_bridge_002460_c_v1, theme_q3_cycle_mechanism_002460_c_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the next drawdown-specialist pocket does not clearly reproduce the newer market-Q4 or theme-Q4 families, it may instead provide the first cross-pocket reuse of the older baseline-style `entry_suppression_avoidance` template.
- What Changed: Added a full replay chain for `theme_research_v4 / 2024_q3 / mainline_trend_c` and drilled into the top positive driver `002460`.
- Expected Impact: Decide whether the drawdown-specialist family set keeps expanding or starts repeating.
- Observed Result: The pocket does not add a new family. `002460` is the largest positive driver (`+534.775`), and the mechanism report [theme_q3_cycle_mechanism_002460_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q3_cycle_mechanism_002460_c_v1.json) is dominated by three `entry_suppression_avoidance` rows on `2024-07-12`, `2024-08-01`, and `2024-08-14`. Two weaker `other_worse_loss_shift` rows remain on `2024-08-30` and `2024-09-27`, so the pocket is noisier than baseline-Q3, but it still points back to the same core family: avoid a set of bad incumbent-only cycles rather than transforming them into smaller nearby losses.
- Side Effects / Risks: This reuse case is weaker than baseline-Q3 because the pocket is more mixed and less dominated by one clean symbol-cycle map. It should be read as family reuse, not as a new preferred specialist branch.
- Conclusion: The drawdown-specialist taxonomy is now showing repetition. Baseline-style `entry_suppression_avoidance` has at least one later reuse case outside the original `600519` pocket.
- Next Step: Shift the search toward pockets that might repeat `preemptive_loss_avoidance_shift` or `carry_in_basis_advantage`, since the baseline-style family is no longer unique.

### JOURNAL-0087

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q2 / 300750` adds a fourth drawdown-specialist family: `delayed_entry_basis_advantage`
- Related Decision: DEC-0087
- Related Runs: theme_q2_trade_divergence_quality_c_v1, theme_q2_symbol_timeline_300750_quality_c_v1, theme_q2_symbol_cycle_delta_300750_c_v1, theme_q2_nearby_cycle_bridge_300750_c_v1, theme_q2_cycle_mechanism_300750_c_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If `theme_q2` is not just another baseline-style avoidance pocket, then its top driver should expose a new reduced-loss basis pattern rather than another `entry_suppression_avoidance` repeat.
- What Changed: Added a full replay chain for `theme_research_v4 / 2024_q2 / mainline_trend_c` and then extended `cycle_mechanism_analysis.py` plus tests so a later-entry / same-exit reduced-loss shape can be named `delayed_entry_basis_advantage`.
- Expected Impact: Decide whether the drawdown-specialist line still only has three families or now needs a fourth one.
- Observed Result: The top driver is `300750` (`+802.5721`). Its key negative-cycle repair on `2024-05-20 -> 2024-05-22` is now formalized in [theme_q2_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_300750_c_v1.json) as `delayed_entry_basis_advantage`: the incumbent enters on `2024-05-20`, the challenger waits until `2024-05-21`, both exit on `2024-05-22`, and the challenger loses much less because it entered at a lower basis. The same pocket also contains a positive-cycle `earlier_exit_loss_reduction` row on `2024-04-30 -> 2024-05-09`, but that is secondary to the new negative-cycle family.
- Side Effects / Risks: The new family is currently supported by a single pocket-symbol chain, so it should not yet be overgeneralized.
- Conclusion: The drawdown-specialist taxonomy now has four families, with `carry_in_basis_advantage` and `delayed_entry_basis_advantage` forming a useful mirrored pair.
- Next Step: Future drawdown pockets should now be screened against all four families: baseline-style avoidance, `preemptive_loss_avoidance_shift`, `carry_in_basis_advantage`, and `delayed_entry_basis_advantage`.

### JOURNAL-0088

- Date: 2026-03-29
- Author: Codex
- Title: The drawdown-specialist line now has an asset table, not just a pocket list
- Related Decision: DEC-0088
- Related Runs: cycle_family_inventory_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once four drawdown-specialist families exist, the repo should stop prioritizing by recency and instead rank families by reuse and net edge quality.
- What Changed: Added `cycle_family_inventory.py`, `run_cycle_family_inventory.py`, `cycle_family_inventory_v1.yaml`, and a fixture-backed test. Then aggregated the five confirmed drawdown pocket reports into [cycle_family_inventory_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v1.json).
- Expected Impact: Turn the drawdown-specialist line from a collection of labeled pockets into a managed research inventory.
- Observed Result: The ranking is already useful. `entry_suppression_avoidance` is the top reusable family (`net_family_edge = 4870.1396`) and now repeats across `baseline_q3 / 600519` and `theme_q3 / 002460`. `preemptive_loss_avoidance_shift` is still strong on raw negative-cycle repair (`2101.8677`) but remains burdened by heavy opportunity cost in its source pocket. `carry_in_basis_advantage` is the cleanest of the basis families (`841.2523` net edge, no positive opportunity-cost drag so far), while `delayed_entry_basis_advantage` is weaker (`353.1059`) and still supported by only one pocket. The inventory also makes the toxic side explicit: `entry_suppression_opportunity_cost` is currently the worst family by net edge.
- Side Effects / Risks: The inventory is still small and strategy-specific. It ranks the current drawdown family set; it does not yet prove which one scales best across all future slices.
- Conclusion: The drawdown-specialist loop no longer needs to be driven by whichever pocket was most recently replayed. It now has a first-pass family asset table.
- Next Step: Keep `entry_suppression_avoidance` as the reusable baseline family. For the next non-baseline research loop, prefer pockets that might repeat `carry_in_basis_advantage` rather than chase another `preemptive_loss_avoidance_shift` case with heavy opportunity-cost baggage.
- Conclusion: The repo now has a sharper prioritization tool than “find repeated shift dates.�?It can focus on symbols that already cross the action-state boundary.
- Next Step: Use action-state trigger dates as the first filter for any future theme-side replay or structural repair work.

### JOURNAL-0067

- Date: 2026-03-29
- Author: Codex
- Title: The first reusable transition rule is now explicit: path shifts matter only after they change actions or active position state
- Related Decision: DEC-0067
- Related Runs: theme_damage_transition_analysis_v1
- Protocol Version: protocol_v1.0
- Hypothesis: If the three current symbol classes are already enough to say something reusable, then the repo should be able to summarize a single transition boundary that separates latent theme-side path shifts from real trade damage.
- What Changed: Added `damage_transition_analysis.py`, `run_damage_transition_analysis.py`, and `theme_damage_transition_analysis_v1.yaml`, then aggregated the existing `300750`, `002466`, and `002902` symbol reports into one structural classification report.
- Expected Impact: Replace “we have three interesting examples�?with one reusable research statement that can guide the next cycle.
- Observed Result: The report [theme_damage_transition_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_damage_transition_analysis_v1.json) cleanly separates the current cases into one damage case (`300750`) and two latent cases (`002466`, `002902`). The useful boundary is now explicit: repeated approval/permission or assignment splits only become promotion-relevant when they also change emitted actions or active-position state.
- Side Effects / Risks: This is a good structural rule for the next cycle, but it is still a working hypothesis from a small case set, not a final theorem.
- Conclusion: The repo can stop asking “does a path shift exist?�?and start asking “does this path shift cross the action-state boundary?�?- Next Step: Use this rule to prioritize the next `theme` diagnosis cases and ignore repeated but economically silent split dates unless they coincide with action-state divergence.
- Date: 2026-03-29
- Author: Codex
- Title: `carry_in_basis_advantage` now repeats across `mainline_trend_b / c`
- Related Decision: DEC-0089
- Related Runs: theme_q4_trade_divergence_quality_b_v1, theme_q4_symbol_timeline_300750_quality_b_v1, theme_q4_symbol_cycle_delta_300750_b_v1, theme_q4_nearby_cycle_bridge_300750_b_v1, theme_q4_cycle_mechanism_300750_b_v1, theme_q4_cross_strategy_cycle_consistency_v1, cycle_family_inventory_v2
- Protocol Version: protocol_v1.1
- Hypothesis: If `carry_in_basis_advantage` is truly the cleanest non-baseline family, then the `theme_q4 / 300750` pocket should replay on `mainline_trend_b` with the same negative-cycle map instead of degrading into a weaker nearby-cycle variant.
- What Changed: Completed the missing `mainline_trend_b` replay chain for `theme_research_v4 / 2024_q4 / 300750`, then added a dedicated cross-strategy consistency config and an inventory v2 that includes the new `B` report.
- Expected Impact: Turn `carry_in_basis_advantage` from a clean label into a reusable family that can legitimately drive the next drawdown-specialist loop.
- Observed Result: The duplication is exact. [theme_q4_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cross_strategy_cycle_consistency_v1.json) reports `identical_negative_cycle_map = true` and the same two shared mechanisms across `B/C`. After adding the `B` report, [cycle_family_inventory_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/cycle_family_inventory_v2.json) raises `carry_in_basis_advantage` to `report_count = 2` and `net_family_edge = 1682.5046` while keeping zero positive opportunity-cost drag.
- Side Effects / Risks: This is still a one-symbol family. The result is strong because the map repeats across strategies, but another symbol can still break it.
- Conclusion: `carry_in_basis_advantage` is no longer just the cleanest non-baseline anecdote. It is now a cross-strategy reusable family.
- Next Step: The next drawdown-specialist expansion loop should search for a second symbol or pocket that reuses `carry_in_basis_advantage`.

### JOURNAL-0090

- Date: 2026-03-29
- Author: Codex
- Title: The next drawdown-family loop now starts from a shortlist instead of from memory
- Related Decision: DEC-0090
- Related Runs: theme_q4_cycle_mechanism_300759_b_v1, theme_q4_cycle_mechanism_002466_c_v2, drawdown_family_candidate_shortlist_v2
- Protocol Version: protocol_v1.1
- Hypothesis: If `carry_in_basis_advantage` is going to generalize further, the repo should be able to find the next replay target from a ranked table rather than by manually cycling through familiar symbols.
- What Changed: First checked two cheap follow-up candidates. `300759` on `theme_q4 / mainline_trend_b` is just `earlier_exit_loss_reduction`, not `carry`. `002466` on `theme_q4 / mainline_trend_c` is a mixed pocket dominated by `entry_suppression_avoidance` plus one `earlier_exit_loss_reduction`, not a second clean `carry` case. Then added `family_candidate_shortlist.py`, `run_family_candidate_shortlist.py`, `drawdown_family_candidate_shortlist_v1.yaml`, `drawdown_family_candidate_shortlist_v2.yaml`, and a focused test.
- Expected Impact: Stop hand-picking the next drawdown-specialist symbol and turn replay selection into a reproducible step.
- Observed Result: [drawdown_family_candidate_shortlist_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v2.json) now ranks the next unanalysed candidates after excluding already replayed family anchors. The current top row is `theme_research_v4 / 2024_q3 / mainline_trend_c / 603799` with `pnl_delta = 436.375` and zero trade-count gap. The table also confirms that the newly checked `theme_q4` symbols did not add a second `carry` pocket.
- Side Effects / Risks: The shortlist is still a heuristic. It can surface noisy mixed pockets, especially when the candidate keeps both trade counts high.
- Conclusion: The drawdown-specialist line no longer needs to choose the next symbol ad hoc. It now has a replay queue.
- Next Step: Use the shortlist winner `theme_q3 / 603799 / mainline_trend_c` as the next replay target.

### JOURNAL-0091

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q3 / 603799` is a mixed pocket, so the shortlist moves on
- Related Decision: DEC-0091
- Related Runs: theme_q3_symbol_timeline_603799_quality_c_v1, theme_q3_symbol_cycle_delta_603799_c_v1, theme_q3_nearby_cycle_bridge_603799_c_v1, theme_q3_cycle_mechanism_603799_c_v1, drawdown_family_candidate_shortlist_v3
- Protocol Version: protocol_v1.1
- Hypothesis: If `theme_q3 / 603799 / mainline_trend_c` is a good next replay target, it should either strengthen an existing family or expose a cleaner non-baseline family than the remaining shortlist rows.
- What Changed: Replayed the full `603799` chain, then refreshed the candidate shortlist with that symbol excluded.
- Expected Impact: Either promote `603799` into the family inventory or clear it out of the queue and move to a cleaner next candidate.
- Observed Result: `603799` is mixed. [theme_q3_cycle_mechanism_603799_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q3_cycle_mechanism_603799_c_v1.json) contains one `entry_suppression_avoidance` row on `2024-08-01 -> 2024-08-02`, but it is offset by a positive-cycle truncation on `2024-09-27 -> 2024-10-10` classified as `other_worse_loss_shift`. That is not clean enough to enter the family inventory. After excluding it, [drawdown_family_candidate_shortlist_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v3.json) now ranks `market_research_v0 / 2024_q4 / mainline_trend_c / 300750` as the next replay target.
- Side Effects / Risks: The next shortlist leader may also be mixed. The shortlist remains a queue, not a guarantee.
- Conclusion: `603799` was a useful filter step, not a new family asset.
- Next Step: Replay `market_q4 / 300750 / mainline_trend_c`.

### JOURNAL-0092

- Date: 2026-03-29
- Author: Codex
- Title: `market_q4 / 300750` is clean but not new, so the replay queue rotates again
- Related Decision: DEC-0092
- Related Runs: market_q4_symbol_timeline_300750_quality_c_v1, market_q4_symbol_cycle_delta_300750_c_v1, market_q4_nearby_cycle_bridge_300750_c_v1, market_q4_cycle_mechanism_300750_c_v1, drawdown_family_candidate_shortlist_v4
- Protocol Version: protocol_v1.1
- Hypothesis: If `market_q4 / 300750 / mainline_trend_c` is still on top after excluding earlier pockets, it should either strengthen a non-baseline family or prove that the shortlist needs another rotation.
- What Changed: Replayed the full `market_q4 / 300750` chain and then refreshed the queue again with that symbol excluded.
- Expected Impact: Either surface a non-baseline family reuse or clear another baseline-style pocket out of the candidate list.
- Observed Result: [market_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_300750_c_v1.json) is very clean but not new: it is a single `entry_suppression_avoidance` row on `2024-10-22 -> 2024-10-23`. After excluding it, [drawdown_family_candidate_shortlist_v4.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v4.json) now ranks `baseline_research_v1 / 2024_q3 / mainline_trend_c / 000333` as the next replay target.
- Side Effects / Risks: The replay queue is working as intended, but it still needs repeated pruning because many high-delta rows are baseline-style reuse rather than new family structure.
- Conclusion: `market_q4 / 300750` strengthens the baseline-style avoidance family but does not advance the non-baseline search.
- Next Step: Replay `baseline_q3 / 000333 / mainline_trend_c`.

### JOURNAL-0093

- Date: 2026-03-29
- Author: Codex
- Title: `baseline_q3 / 000333 / C` strengthens the baseline-style template but does not advance the non-baseline search
- Related Decision: DEC-0093
- Related Runs: baseline_q3_symbol_timeline_000333_quality_c_v1, baseline_q3_symbol_cycle_delta_000333_c_v1, baseline_q3_nearby_cycle_bridge_000333_c_v1, baseline_q3_cycle_mechanism_000333_c_v1, drawdown_family_candidate_shortlist_v5
- Protocol Version: protocol_v1.1
- Hypothesis: If `baseline_research_v1 / 2024_q3 / mainline_trend_c / 000333` sits on top of the refreshed replay queue, it should either broaden the baseline-style drawdown family enough to change inventory confidence or expose a different mechanism frontier.
- What Changed: Added the full `000333 / C` replay chain and then refreshed the shortlist with `000333` excluded.
- Expected Impact: Either promote a stronger shared baseline-style family template or clear another familiar reuse case out of the way so the queue can keep searching for non-baseline reusable structure.
- Observed Result: [baseline_q3_cycle_mechanism_000333_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_000333_c_v1.json) is heavily baseline-style. It contains three `earlier_exit_loss_reduction` rows (`2024-08-01`, `2024-08-26`, `2024-09-04`) and two `entry_suppression_avoidance` rows (`2024-07-05`, `2024-07-15`). But it also carries two large positive-cycle degradations on `2024-08-19 -> 2024-08-20` and `2024-09-25 -> 2024-10-09`, both labeled `other_worse_loss_shift`. That makes it a strong reuse case, not a clean new asset. The queue has therefore been rotated again via [drawdown_family_candidate_shortlist_v5.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v5.json).
- Side Effects / Risks: The next candidates will likely be noisier because many of the high-signal baseline-style rows are now excluded.
- Conclusion: `000333 / C` raises confidence in the baseline-style family, but it does not move the non-baseline family frontier.
- Next Step: Follow the refreshed queue instead of replaying more baseline-Q3 reuse cases.

### JOURNAL-0094

- Date: 2026-03-29
- Author: Codex
- Title: `market_q4 / 002371 / C` is one of the cleanest baseline-style pockets, but still not a new family asset
- Related Decision: DEC-0094
- Related Runs: market_q4_symbol_timeline_002371_quality_c_v1, market_q4_symbol_cycle_delta_002371_c_v1, market_q4_nearby_cycle_bridge_002371_c_v1, market_q4_cycle_mechanism_002371_c_v1, drawdown_family_candidate_shortlist_v6
- Protocol Version: protocol_v1.1
- Hypothesis: If the replay queue is still surfacing candidates that matter for the non-baseline search frontier, then `market_q4 / 002371 / C` should either add a new mechanism family or at least combine baseline-style avoidance with a second nontrivial reduced-loss row.
- What Changed: Added the full `002371 / C` replay chain and then refreshed the queue with `002371` excluded.
- Expected Impact: Either capture another reusable family clue or deliberately clear out one more clean-but-old baseline-style case.
- Observed Result: [market_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_002371_c_v1.json) is extremely clean but also extremely familiar: one `entry_suppression_avoidance` row on `2024-12-30 -> 2024-12-31`, no reduced-loss basis behavior, no mixed-cycle drag, and no additional mechanism evidence. That makes it a useful confidence-raising case for the baseline-style family, but not a frontier-expanding specialist asset. The queue is therefore rotated again via [drawdown_family_candidate_shortlist_v6.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v6.json).
- Side Effects / Risks: The remaining queue will likely get noisier now that both mixed and clean baseline-style cases are being stripped out.
- Conclusion: Cleanness is not enough. `002371 / C` confirms baseline-style avoidance but does not justify a new family label.
- Next Step: Pull the next candidate from the refreshed shortlist instead of deepening the baseline-style catalogue.

### JOURNAL-0095

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q2 / 002466 / C` is a stacked-family pocket, not a clean new asset
- Related Decision: DEC-0095
- Related Runs: theme_q2_symbol_timeline_002466_quality_c_v1, theme_q2_symbol_cycle_delta_002466_c_v1, theme_q2_nearby_cycle_bridge_002466_c_v1, theme_q2_cycle_mechanism_002466_c_v1, cycle_family_inventory_v3, drawdown_family_candidate_shortlist_v8
- Protocol Version: protocol_v1.1
- Hypothesis: If the remaining queue still contains frontier-changing candidates, then `theme_q2 / 002466 / C` should either cleanly repeat one of the non-baseline families or expose a new mechanism family worth promoting.
- What Changed: Added the full `theme_q2 / 002466 / C` replay chain, reviewed the mechanism map, and then refreshed the queue with `002466` excluded.
- Expected Impact: Either discover another clean non-baseline family case or formalize that some high-delta rows are best understood as stacked-family pockets rather than as new assets.
- Observed Result: [theme_q2_cycle_mechanism_002466_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_002466_c_v1.json) stacks multiple known mechanisms in one pocket: one `preemptive_loss_avoidance_shift`, two `entry_suppression_avoidance` rows, and one positive `delayed_entry_basis_advantage`. That makes it valuable as reinforcement evidence, but not clean enough to enter the family inventory as a separate asset. The queue therefore rotates again via [drawdown_family_candidate_shortlist_v8.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v8.json).
- Side Effects / Risks: The more the queue moves down, the more likely it is that remaining candidates are mixed, stacked, or simply weaker.
- Conclusion: `theme_q2 / 002466 / C` increases confidence that families can stack in one sequence, but it does not expand the family frontier.
- Next Step: Use the refreshed shortlist to keep searching for a candidate that changes the inventory boundary rather than merely combining known families.

### JOURNAL-0096

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q4 / 002902` repeats across `B/C`, but only as a mixed pocket
- Related Decision: DEC-0096
- Related Runs: theme_q4_symbol_timeline_002902_quality_b_v1, theme_q4_symbol_cycle_delta_002902_b_v1, theme_q4_nearby_cycle_bridge_002902_b_v1, theme_q4_cycle_mechanism_002902_b_v1, theme_q4_symbol_timeline_002902_quality_c_v1, theme_q4_symbol_cycle_delta_002902_c_v1, theme_q4_nearby_cycle_bridge_002902_c_v1, theme_q4_cycle_mechanism_002902_c_v1, drawdown_family_candidate_shortlist_v9
- Protocol Version: protocol_v1.1
- Hypothesis: If `theme_q4 / 002902` sits on top of the queue on both `mainline_trend_b` and `mainline_trend_c`, then it should either expose a clean cross-strategy family or prove that some cross-strategy repeats are still too mixed to promote.
- What Changed: Added the full `002902` replay chains for both `B` and `C`, then refreshed the queue with both rows excluded.
- Expected Impact: Clarify whether cross-strategy repeatability alone is enough to treat a pocket as a family asset.
- Observed Result: The repetition is exact, but the content is still mixed. Both [theme_q4_cycle_mechanism_002902_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002902_b_v1.json) and [theme_q4_cycle_mechanism_002902_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_002902_c_v1.json) share the same four-row map: one `earlier_exit_loss_reduction`, two `entry_suppression_avoidance`, and one negative `other_worse_loss_shift`. That is strong evidence that mixed pockets themselves can repeat across strategies, but it still does not justify a clean family-inventory promotion. The queue has therefore been rotated again via [drawdown_family_candidate_shortlist_v9.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v9.json).
- Side Effects / Risks: The queue will increasingly consist of weaker or more ambiguous rows now that both clean baseline-style and strong mixed repeats are being stripped out.
- Conclusion: `002902` is a reusable mixed-pocket example, not a new family asset.
- Next Step: Continue from the refreshed shortlist rather than replaying the same mixed symbol across more strategy variants.

### JOURNAL-0097

- Date: 2026-03-29
- Author: Codex
- Title: `market_q4 / 603259 / C` is clean but still only a single-row baseline-style avoidance case
- Related Decision: DEC-0097
- Related Runs: market_q4_symbol_timeline_603259_quality_c_v1, market_q4_symbol_cycle_delta_603259_c_v1, market_q4_nearby_cycle_bridge_603259_c_v1, market_q4_cycle_mechanism_603259_c_v1, drawdown_family_candidate_shortlist_v10
- Protocol Version: protocol_v1.1
- Hypothesis: If the queue still contains frontier-changing candidates, then `market_q4 / 603259 / C` should offer more than a single avoided cycle.
- What Changed: Added the full `603259 / C` replay chain and then refreshed the queue again with `603259` excluded.
- Expected Impact: Either add a richer market-Q4 example to the specialist-family map or intentionally clear another low-complexity baseline-style row out of the way.
- Observed Result: [market_q4_cycle_mechanism_603259_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_603259_c_v1.json) contains only one `entry_suppression_avoidance` row on `2024-10-30 -> 2024-10-31`. It is even cleaner than most recent queue cases, but it still does not move the non-baseline family frontier. The queue has therefore been rotated again via [drawdown_family_candidate_shortlist_v10.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v10.json).
- Side Effects / Risks: The replay queue is now clearly losing many of its easy clean cases, which increases the chance that the remaining rows are mostly weak or noisy.
- Conclusion: `603259 / C` is confidence-raising evidence for baseline-style avoidance, not a new asset.
- Next Step: Continue from the refreshed shortlist instead of building out a longer gallery of single-row avoidance examples.

### JOURNAL-0098

- Date: 2026-03-29
- Author: Codex
- Title: `theme_q4 / 603087` repeats across `B/C`, but only as another one-row baseline-style case
- Related Decision: DEC-0098
- Related Runs: theme_q4_symbol_timeline_603087_quality_b_v1, theme_q4_symbol_cycle_delta_603087_b_v1, theme_q4_nearby_cycle_bridge_603087_b_v1, theme_q4_cycle_mechanism_603087_b_v1, theme_q4_symbol_timeline_603087_quality_c_v1, theme_q4_symbol_cycle_delta_603087_c_v1, theme_q4_nearby_cycle_bridge_603087_c_v1, theme_q4_cycle_mechanism_603087_c_v1, drawdown_family_candidate_shortlist_v11
- Protocol Version: protocol_v1.1
- Hypothesis: If `theme_q4 / 603087` is on top in both `B/C`, then replaying both should tell us whether this is a richer cross-strategy pocket or just another repeated one-row avoidance case.
- What Changed: Added and ran the full `603087` replay chains for both `B` and `C`, then refreshed the queue with both rows excluded.
- Expected Impact: Either find a richer cross-strategy structure or clear another duplicated symbol out of the way.
- Observed Result: Both [theme_q4_cycle_mechanism_603087_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_b_v1.json) and [theme_q4_cycle_mechanism_603087_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_c_v1.json) contain only one `entry_suppression_avoidance` row. That confirms the symbol is cross-strategy repeatable, but only in the weakest possible sense: another single-row baseline-style example. The queue has therefore been rotated again via [drawdown_family_candidate_shortlist_v11.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/drawdown_family_candidate_shortlist_v11.json).
- Side Effects / Risks: This is another strong sign that the replay queue is entering a thinning phase where many remaining cases will add little beyond more baseline-style confirmation.
- Conclusion: `603087` does not expand the family frontier. It only reinforces the simplest baseline-style mechanism.
- Next Step: Read the refreshed v11 shortlist before deciding whether to continue replaying or to switch into a controlled stop / feature-gap audit.

### JOURNAL-0099

- Date: 2026-03-29
- Author: Codex
- Title: The specialist replay loop is now better treated as feature-limited thinning than as open-ended family discovery
- Related Decision: DEC-0099
- Related Runs: specialist_feature_gap_audit_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the replay queue is still economically healthy, then the latest high-delta pockets should keep changing the family boundary. If instead the queue is dominated by single-row baseline reuse, repeated mixed pockets, and stacked-family cases, then replay should pause and the next budget should move into feature work.
- What Changed: Added a formal audit pass over the latest replayed pockets and grouped them by dataset/slice/symbol instead of continuing directly to another queue replay.
- Expected Impact: Turn a fuzzy intuition about "high-quality dead-loop risk" into a formal phase signal that can control the next research step.
- Observed Result: [specialist_feature_gap_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_feature_gap_audit_v1.json) confirms the intuition. Across `9` recent pockets, the distribution is:
  - `mixed_existing_families = 4`
  - `single_row_baseline_reuse = 4`
  - `stacked_family_pocket = 1`
  - `feature_gap_suspect_count = 2`
  - `thinning_signal = true`
  The two clearest feature-gap suspects are:
  - `theme_research_v4 / 2024_q4 / 002902` as a `cross_strategy_mixed_repeat`
  - `theme_research_v4 / 2024_q2 / 002466` as a `stacked_known_families` case
  This means the next marginal research dollar is more likely to be won by adding more expressive features than by replaying the next symbol on the queue.
- Side Effects / Risks: The audit does not prove that a new family is hidden behind the current feature set. It only justifies switching the search method.
- Conclusion: `V1.1` is now in a feature-limited thinning phase. The right next move is a small `feature-pack-a`, not `drawdown_family_candidate_shortlist_v12`.
- Next Step: Define and implement `feature-pack-a`, then rerun the suspect pockets as a bounded replay recheck.

### JOURNAL-0100

- Date: 2026-03-29
- Author: Codex
- Title: `feature-pack-a` is now bounded tightly enough to be a real test rather than a new open loop
- Related Decision: DEC-0100
- Related Runs: specialist_feature_gap_audit_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If feature expansion is the right next move, then it should be possible to define a very small first pack that directly attacks the current suspects without reopening a broad feature-design phase.
- What Changed: Wrote [27_FEATURE_PACK_A_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/27_FEATURE_PACK_A_PLAN.md) to constrain the next cycle.
- Expected Impact: Convert "we probably need more features" into a falsifiable experiment with explicit suspects, explicit feature groups, and an explicit exit rule.
- Observed Result: The next cycle is now well-bounded. `feature-pack-a` targets only:
  - `theme_q4 / 002902`
  - `theme_q2 / 002466`
  and only four narrow feature groups:
  - theme/concept support
  - hierarchy intermediate margins
  - approval-edge state
  - short cycle context
  This means the next result can now be judged cleanly: boundary changes, or it does not.
- Side Effects / Risks: A small pack may underfit the true missing structure. But if a larger pack is needed, that should be justified after this bounded attempt fails, not before.
- Conclusion: `feature-pack-a` is now a controlled recheck cycle, not an excuse to keep expanding the research surface.
- Next Step: Implement the pack and rerun the two suspect pockets before revisiting the replay queue.

### JOURNAL-0101

- Date: 2026-03-29
- Author: Codex
- Title: `feature-pack-a` v1 confirms that the two main suspects are real threshold-edge pockets, not random leftovers
- Related Decision: DEC-0101
- Related Runs: theme_research_derived_data_v5, feature_pack_a_recheck_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the replay loop really entered a feature-limited thinning phase, then adding a small number of richer snapshot fields should make the current suspects look more like explicit edge cases and less like unexplained mixed noise.
- What Changed: Extended `theme_research_stock_snapshots_v5.csv` with concept-support and hierarchy-intermediate fields, then reran the two suspect pockets through [feature_pack_a_recheck_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_recheck_v1.json).
- Expected Impact: Replace vague "maybe we need more features" reasoning with a concrete answer about whether the current suspects actually sit on visible threshold edges.
- Observed Result: The answer is yes. All `8` rechecked mechanism rows sit on at least one explicit edge.
  - `theme_q4 / 002902 / B` is mainly a hierarchy/approval-edge case with `0` concept support on all trigger rows. The recurring signal is that `late_mover_quality` often clears the incumbent threshold but not the challenger one, and some rows also straddle `non_junk_composite`.
  - `theme_q2 / 002466 / C` is more feature-rich. It has stable concept support (`0.51` to `0.57`), positive concept counts, and repeated hierarchy-edge straddles, especially on `late_mover_quality` and sometimes on `non_junk_composite`.
  In other words, the two suspects are not the same kind of problem. `002902` looks more like a hierarchy/approval boundary with weak concept coverage; `002466` looks like a concept-supported hierarchy boundary.
- Side Effects / Risks: The recheck still does not prove that a strategy change is justified. It only proves that the current feature set was indeed hiding meaningful edge structure.
- Conclusion: `feature-pack-a` v1 succeeded as a diagnostic cycle. The replay queue should stay paused.
- Next Step: Split the next refinement step into:
  - hierarchy/approval-focused follow-up for `002902`
  - concept-supported hierarchy follow-up for `002466`

### JOURNAL-0102

- Date: 2026-03-29
- Author: Codex
- Title: The post-`feature-pack-a` next step is now a sequential two-track `feature-pack-b`, not a blended feature expansion
- Related Decision: DEC-0102
- Related Runs: feature_pack_a_triage_v1, feature_pack_b_readiness_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the current suspect pockets are genuinely different edge types, then the next feature-expansion cycle should become simpler after triage, not broader.
- What Changed: Added a formal triage layer and then a readiness layer on top of the existing recheck output.
- Expected Impact: Convert "we probably need more features" into "we know which feature lane should go first and why."
- Observed Result: The split is now explicit and actionable.
  - [feature_pack_a_triage_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_triage_v1.json) shows that `002902` is a `hierarchy_approval_edge`, while `002466` is a `concept_supported_hierarchy_edge`.
  - [feature_pack_b_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_readiness_v1.json) orders them cleanly:
    1. `theme_q4 / 002902 / B`
    2. `theme_q2 / 002466 / C`
  The reason is simple: `002902` is the cleaner non-concept edge and therefore the cheapest falsifiable first target.
- Side Effects / Risks: This does not yet prove that track A will change the family boundary. It only proves that the next phase now has a disciplined execution order.
- Conclusion: `feature-pack-b` should be sequential, beginning with hierarchy/approval refinement for `002902`.
- Next Step: Implement `feature_pack_b_hierarchy_approval` before touching the concept-supported lane.

### JOURNAL-0103

- Date: 2026-03-29
- Author: Codex
- Title: `002902` is now instrumented enough to treat track A as a coupled hierarchy-plus-approval edge
- Related Decision: DEC-0103
- Related Runs: feature_pack_a_recheck_v1, feature_pack_b_hierarchy_approval_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If `theme_q4 / 002902 / B` is the cleanest first `feature-pack-b` target, then a focused read should reduce the ambiguity from "some hierarchy/approval issue" to a small number of dominant coupled edges.
- What Changed: Extended the recheck output with `challenger_margin_gap`, `fallback_reason_score`, and `margin_straddle`, then ran [feature_pack_b_hierarchy_approval_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_v1.json) on `theme_q4 / 002902 / B`.
- Expected Impact: Turn track A from a category label into a concrete refinement lane with the smallest plausible set of useful features.
- Observed Result: The pocket is now much clearer.
  - `late_quality_straddles = 3`
  - `non_junk_straddles = 2`
  - `margin_straddles = 2`
  - `permission_split_rows = 2`
  - `avg_fallback_reason_score = 0.022103`
  - `avg_challenger_late_quality_margin = -0.105935`
  This means the first track is not just "approval." It is a coupled edge where `late_mover_quality` is the dominant hierarchy bottleneck and `score-margin threshold` is the dominant approval bottleneck.
- Side Effects / Risks: The pocket may still fail to change the family boundary even after better instrumentation. That would be a legitimate negative result rather than a reason to broaden the track.
- Conclusion: `theme_q4 / 002902 / B` is now ready for a real track-A refinement pass.
- Next Step: Keep queue replay paused and continue with the `hierarchy/approval` lane before the concept-supported hierarchy lane.

### JOURNAL-0104

- Date: 2026-03-29
- Author: Codex
- Title: `002902` turned into a useful negative result: the pocket is explainable, but not cheaply fixable
- Related Decision: DEC-0104
- Related Runs: feature_pack_b_hierarchy_approval_v1, feature_pack_b_hierarchy_approval_sweep_v1, feature_pack_b_hierarchy_approval_sweep_v2
- Protocol Version: protocol_v1.1
- Hypothesis: If `002902` is the cleanest first `feature-pack-b` target, then a narrow local sweep should reveal whether the pocket has a cheap hierarchy/approval repair or only an explanatory edge.
- What Changed: Ran two pocket-local sweeps instead of jumping to branch-level edits.
- Expected Impact: Force an answer on whether track A is a true refinement path or just a well-understood blocker.
- Observed Result: The answer is the latter.
  - [feature_pack_b_hierarchy_approval_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_v1.json) showed the pocket is a coupled edge:
    - hierarchy bottleneck: `late_mover_quality`
    - approval bottleneck: `score_margin_threshold`
  - [feature_pack_b_hierarchy_approval_sweep_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v1.json) showed that `non_junk` relief repairs assignment-side triggers, while a mild margin relief does nothing.
  - [feature_pack_b_hierarchy_approval_sweep_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v2.json) showed that stronger margin relief repairs the approval side, but the pocket-level PnL gets worse as repairs increase.
  In other words: the edge is real, but the cheap repair thesis failed.
- Side Effects / Risks: This negative result is still local to `002902`. It should not be generalized into "hierarchy/approval refinement never works."
- Conclusion: Track A should now be treated as closed for this cycle: explanatory success, refinement failure.
- Next Step: Shift the next feature budget to the concept-supported hierarchy lane on `002466`.

### JOURNAL-0105

- Date: 2026-03-29
- Author: Codex
- Title: `002466` narrows the concept-supported lane to a concept-to-late-mover bridge, not a broad concept hierarchy rewrite
- Related Decision: DEC-0105
- Related Runs: feature_pack_b_concept_supported_hierarchy_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If `002466` is the right second `feature-pack-b` target, then the first useful question is not "how do we use concept support everywhere," but "which hierarchy boundary concept support is most plausibly supposed to bridge."
- What Changed: Ran [feature_pack_b_concept_supported_hierarchy_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_supported_hierarchy_v1.json) against the `feature-pack-a` recheck rows for `theme_q2 / 002466 / C`.
- Expected Impact: Collapse the concept-supported lane from a broad feature idea into one dominant bridge hypothesis.
- Observed Result: The pocket is not symmetric enough to justify a blended concept pack.
  - `concept_supported_late_rows = 2`
  - `concept_supported_non_junk_rows = 2`
  - `avg_challenger_late_quality_margin = -0.073479`
  - `avg_challenger_non_junk_margin = 0.029458`
  So the meaningful negative edge is on the late-quality side. That makes `concept_to_late_mover` the dominant bridge.
- Side Effects / Risks: This still does not prove that the bridge is strategy-worthy. It only identifies the most plausible narrow lane for the next feature-aware refinement.
- Conclusion: Track B should now be opened as a `concept_to_late_mover` refinement, not as a general concept hierarchy pass.
- Next Step: Keep the replay queue paused and design the next concept-aware step around late-mover admission only.

### JOURNAL-0106

- Date: 2026-03-29
- Author: Codex
- Title: `002466` concept-to-late variants repaired one bridge row but collapsed most of the specialist alpha
- Related Decision: DEC-0106
- Related Runs: concept_to_late_bridge_analysis_v1, feature_pack_b_concept_late_validation_v1, theme_q2_symbol_timeline_002466_quality_c_v1, theme_q2_symbol_timeline_002466_quality_c_v2, theme_q2_symbol_timeline_002466_quality_c_v3
- Protocol Version: protocol_v1.1
- Hypothesis: If `002466` is truly a useful concept-to-late bridge, then at least one narrow concept-aware variant should preserve a meaningful share of the challenger alpha while also repairing the targeted bridge rows.
- What Changed: Built a formal track-B acceptance layer instead of trying more widening variants first.
- Expected Impact: Replace "maybe one more concept tweak" with a hard decision on whether the lane still deserves budget.
- Observed Result: The lane is now much clearer, and mostly in the negative direction.
  - [concept_to_late_bridge_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/concept_to_late_bridge_analysis_v1.json) already showed only two bridge rows mattered: `2024-05-09` and `2024-06-26`.
  - [theme_q2_symbol_timeline_002466_quality_c_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_symbol_timeline_002466_quality_c_v2.json) repaired `2024-05-09`, but challenger pnl delta fell from `536.724` to `94.049`.
  - [theme_q2_symbol_timeline_002466_quality_c_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_symbol_timeline_002466_quality_c_v3.json) stayed slightly narrower, but still only repaired the same one row and fell to `71.049`.
  - [feature_pack_b_concept_late_validation_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_late_validation_v1.json) therefore closes the lane with:
    - `best_variant_alpha_retention_ratio = 0.175228`
    - `best_variant_repair_completion_ratio = 0.5`
    - `acceptance_posture = close_track_b_as_negative_informative`
- Side Effects / Risks: This is still a statement about the current feature pack, not a universal statement about concept-aware late-mover support.
- Conclusion: Track B has now become an explanatory success but a refinement failure, similar in spirit to track A.
- Next Step: Do not reopen broad concept-to-late tuning. Any future revisit should come from a new feature pack, not from another local band/boost search.

### JOURNAL-0107

- Date: 2026-03-29
- Author: Codex
- Title: `feature-pack-c` is now the correct next stage, and replay queue restart is explicitly disallowed
- Related Decision: DEC-0107
- Related Runs: specialist_feature_gap_audit_v1, feature_pack_b_hierarchy_approval_v1, feature_pack_b_hierarchy_approval_sweep_v2, feature_pack_b_concept_supported_hierarchy_v1, feature_pack_b_concept_late_validation_v1, feature_pack_c_readiness_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once both `feature-pack-b` tracks are closed as negative-but-informative, the next healthy move should be a small local-causal feature pack rather than another queue expansion.
- What Changed: Added a readiness layer and a dedicated phase-definition file for `feature-pack-c`.
- Expected Impact: Turn "we probably need more features" into a bounded next phase with an explicit no-replay default.
- Observed Result: [feature_pack_c_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_readiness_v1.json) now makes the phase transition explicit:
  - `feature_gap_suspect_count = 2`
  - `thinning_signal = true`
  - `track_a_closed = true`
  - `track_b_closed = true`
  - `recommended_next_phase = feature_pack_c_local_causal_edges`
  - `do_restart_replay_queue = false`
  [29_FEATURE_PACK_C_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/29_FEATURE_PACK_C_PLAN.md) then constrains the first four feature groups to:
  - `fallback_reason_decomposition`
  - `late_quality_residual_components`
  - `approval_threshold_history`
  - `concept_support_excess_to_late_threshold`
- Side Effects / Risks: This does not yet prove that `feature-pack-c` will unlock a new family. It only proves that continuing replay now would be the wrong phase behavior.
- Conclusion: The specialist line is still healthy, but only if the next cycle is treated as local-causal feature expansion rather than more queue work.
- Next Step: Begin implementing the first `feature-pack-c` feature group, not another replay candidate.

### JOURNAL-0108

- Date: 2026-03-29
- Author: Codex
- Title: Unsupervised work is now allowed only as a bounded sidecar, not as a new mainline branch
- Related Decision: DEC-0108
- Related Runs: feature_pack_c_readiness_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Some current pockets may fail to form clean families because the existing feature geometry is too weak, but that does not justify introducing an unconstrained ML branch.
- What Changed: Added [30_UNSUPERVISED_FEATURE_RELATION_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/30_UNSUPERVISED_FEATURE_RELATION_PLAN.md) and bounded unsupervised work to a report-only sidecar.
- Expected Impact: Keep the option to study hidden feature structure without letting unsupervised outputs become hidden signals.
- Observed Result: The sidecar is now constrained to:
  - redundancy / correlation analysis
  - `numpy`-level PCA or axis summaries
  - small pocket clustering
  and explicitly disallows direct signal-chain use.
- Side Effects / Risks: The current local environment shows `numpy` import is fine, but `pandas` / `sklearn` trigger compatibility warnings under `NumPy 2.x`, so the first pass should avoid heavy dependency expansion.
- Conclusion: Unsupervised analysis may help, but only if it stays a lightweight geometry sidecar and only if it changes a real feature-pack decision.
- Next Step: Keep the mainline on `feature-pack-c`; if unsupervised work begins, limit it to `U1 lightweight geometry`.

### JOURNAL-0109

- Date: 2026-03-29
- Author: Codex
- Title: Pack-C starts as a late-quality-led causal feature cycle, not a concept-first cycle
- Related Decision: DEC-0109
- Related Runs: feature_pack_c_fallback_reason_analysis_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the two current suspect pockets are really feature-limited, the first pack-C pass should tell us whether the dominant hidden cause is late-quality, approval edge, or concept support.
- What Changed: Added a first pack-C analysis layer that decomposes fallback rows into local deficit types rather than immediately adding more derived fields.
- Expected Impact: Replace "we should add several local-causal features" with an ordered first implementation sequence.
- Observed Result: [feature_pack_c_fallback_reason_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_fallback_reason_analysis_v1.json) now shows:
  - `8` relevant rows across the two suspect pockets
  - `6` are late-quality-dominant
  - only `2` are score-margin-dominant
  - concept support is present on the `002466` rows, but not dominant enough to lead the pack
  So the correct pack-C opening is:
  1. fallback decomposition
  2. late-quality residual components
  3. only then approval-threshold history / concept-support excess
- Side Effects / Risks: This is still a first decomposition pass. It improves ordering, not yet the pockets themselves.
- Conclusion: Pack-C has now started with a real prioritization rule instead of a generic feature wish list.
- Next Step: Implement the first local-causal feature group around late-quality residual structure.

### JOURNAL-0110

- Date: 2026-03-29
- Author: Codex
- Title: The first late-quality residual read keeps pack-C inside the raw hierarchy stack
- Related Decision: DEC-0110
- Related Runs: theme_research_derived_data_v5, feature_pack_c_late_quality_residuals_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once the raw late-quality contributors become visible, the current suspect pockets may turn out to be primarily concept-driven, approval-driven, or genuinely raw late-quality-driven.
- What Changed: Added raw late-quality component fields to `StockSnapshot`, regenerated `theme_research_v5` derived tables, and added a dedicated pack-C residual analysis report.
- Expected Impact: Replace the single scalar `late_mover_quality` bottleneck with a small set of observable contributors so the next pack-C step can target the weakest local stack rather than another threshold.
- Observed Result: [feature_pack_c_late_quality_residuals_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_late_quality_residuals_v1.json) now shows:
  - all `8` suspect rows remain below the challenger late threshold in raw form
  - concept boost is active on only `1` row
  - the dominant contributors are split across `stability`, `liquidity`, and `sector_strength`
  - the report recommends `late_quality_stability_liquidity_context` as the next pack-C read, because concept support is not carrying the deficit
- Side Effects / Risks: The residual ranking is still local to `002902` and `002466`; it should not be overgeneralized into a global feature order.
- Conclusion: Pack-C should continue by explaining the raw late-quality stack, led by `stability/liquidity`, not by widening concept bridges or restarting approval tuning.
- Next Step: Add local context around `stability/liquidity` before opening any unsupervised geometry sidecar.

### JOURNAL-0111

- Date: 2026-03-29
- Author: Codex
- Title: The first stability/liquidity context read points to turnover-share, not volatility
- Related Decision: DEC-0111
- Related Runs: theme_research_derived_data_v5, feature_pack_c_late_quality_residuals_v1, feature_pack_c_stability_liquidity_context_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once the raw late-quality residuals are visible, the next useful split inside the suspect rows should be either volatility-led or turnover-led.
- What Changed: Added local context fields around stability/liquidity (`stability_volatility`, `liquidity_turnover_share`, `liquidity_turnover_rank`) and a dedicated pack-C context analysis report.
- Expected Impact: Replace the broad `stability/liquidity` label with a smaller decision about which local-causal branch is worth instrumenting next.
- Observed Result: [feature_pack_c_stability_liquidity_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_stability_liquidity_context_v1.json) now shows:
  - `row_count = 6`
  - `local_context_counts = {turnover_share_led: 3, mixed_stability_liquidity: 3}`
  - `volatility_led = 0`
  - `recommended_third_feature_group = late_quality_turnover_share_context`
- Side Effects / Risks: The result is still local to the current suspect pockets. It narrows the next branch, but it does not prove that volatility is globally unimportant.
- Conclusion: Pack-C should now move into turnover-share context rather than opening a volatility-first branch.
- Next Step: Add a turnover-share-led local-causal read before any unsupervised geometry work.

### JOURNAL-0112

- Date: 2026-03-29
- Author: Codex
- Title: Turnover-share does not collapse to one clean attention story
- Related Decision: DEC-0112
- Related Runs: theme_research_derived_data_v5, feature_pack_c_stability_liquidity_context_v1, feature_pack_c_turnover_share_context_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once the current suspect rows were reduced to turnover-share context, the next likely split would be either sector-peer dominance or broad-attention deficit.
- What Changed: Added sector-local turnover-share context fields and a dedicated pack-C turnover-share analysis report.
- Expected Impact: Replace the generic liquidity story with a smaller, more honest description of how turnover weakness actually appears inside the current pockets.
- Observed Result: [feature_pack_c_turnover_share_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_turnover_share_context_v1.json) now shows:
  - `row_count = 3`
  - `local_turnover_context_counts = {sector_peer_dominance: 1, balanced_share_weakness: 2}`
  - `broad_attention_deficit = 0`
  - `recommended_fourth_feature_group = late_quality_balanced_turnover_context`
  This means the lane stays split: one clean sector-peer row (`002466`) and two balanced-share weakness rows (`002902`).
- Side Effects / Risks: The turnover lane is now more realistic but less clean. It narrows false stories, but it does not yet produce a cheap next repair.
- Conclusion: Pack-C should keep turnover-share as a descriptive local-causal lane, not a simple global attention branch.
- Next Step: If refinement continues, start from balanced turnover weakness instead of broad attention.

### JOURNAL-0113

- Date: 2026-03-29
- Author: Codex
- Title: `feature-pack-c` has now closed as explanatory rather than promotable
- Related Decision: DEC-0113
- Related Runs: theme_research_derived_data_v5, feature_pack_c_balanced_turnover_weakness_v1, feature_pack_c_acceptance_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the turnover-share lane still contained a real reusable feature, the two `002902` rows should survive a deeper balanced-turnover read as something more than sector masking.
- What Changed: Added a balanced-turnover weakness analyzer and then a pack-C acceptance layer that aggregates the fallback, residual, stability/liquidity, turnover-share, and balanced-turnover reads.
- Expected Impact: Replace "maybe one more turnover feature" with a formal answer about whether pack-C should continue or close.
- Observed Result: The turnover-share lane is now effectively exhausted under the current suspects.
  - [feature_pack_c_balanced_turnover_weakness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_balanced_turnover_weakness_v1.json) shows both `002902` rows are `singleton_sector_masking`, not true balanced weakness.
  - [feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json) then concludes:
    - `acceptance_posture = close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar`
    - `do_continue_pack_c_turnover_branch = false`
    - `ready_for_u1_lightweight_geometry = true`
- Side Effects / Risks: This is a phase-closing result, not a claim that future data can never surface a reusable balanced-turnover feature.
- Conclusion: Pack-C has succeeded by clarifying the current pockets rather than by finding a cheap new repair path. The correct next move is a bounded sidecar, not more turnover-lane refinement.
- Next Step: Keep replay queue paused and open only `U1 lightweight geometry` if we continue specialist refinement.

### JOURNAL-0114

- Date: 2026-03-29
- Author: Codex
- Title: The first U1 geometry read justified itself by separating the two suspect pockets
- Related Decision: DEC-0114
- Related Runs: feature_pack_c_acceptance_v1, u1_lightweight_geometry_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If `U1 lightweight geometry` is worth running at all, it should change a real interpretation boundary rather than just restate the same labels with prettier math.
- What Changed: Added a `numpy`-only geometry sidecar and ran it against the `feature-pack-a` suspect rows using the current local-causal fields.
- Expected Impact: Test whether the two remaining suspect pockets are still one blended feature problem or already separable enough that a shared next-stage branch would be wasteful.
- Observed Result: [u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json) shows:
  - `case_centroid_distance = 4.080383`
  - `separation_reading = cases_geometrically_separable`
  - `pc1` dominated by concept-support geometry
  - `pc2` dominated by late-quality / resonance geometry
  - strongest redundancy pairs:
    - `challenger_margin_gap <-> top_score_gap`
    - `primary_concept_weight <-> concept_concentration_ratio`
- Side Effects / Risks: This is a small-sample geometry read. It should guide next-stage branching, not be mistaken for tradable latent factors.
- Conclusion: U1 succeeded because it changed the decision boundary: `002902` and `002466` should no longer be treated as one combined next-stage feature problem.
- Next Step: Keep unsupervised work bounded and do not open a blended `feature-pack-d` unless a new, larger suspect set emerges.

### JOURNAL-0115

- Date: 2026-03-29
- Author: Codex
- Title: U2 clustering is now formally parked rather than implicitly deferred
- Related Decision: DEC-0115
- Related Runs: specialist_feature_gap_audit_v1, feature_pack_c_acceptance_v1, u1_lightweight_geometry_v1, u2_pocket_clustering_readiness_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If U1 already cleanly separates the current suspect pockets, then opening U2 clustering immediately would add process, not decision value.
- What Changed: Added a U2 readiness gate on top of the feature-gap audit, pack-C acceptance, and U1 geometry outputs.
- Expected Impact: Replace "maybe clustering next" with a hard answer about whether clustering is actually warranted right now.
- Observed Result: [u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json) shows:
  - `suspect_count = 2`
  - `thinning_signal = true`
  - `u1_cases_geometrically_separable = true`
  - `u2_ready = false`
  - `recommended_next_phase = hold_u2_and_wait_for_larger_or_less_separable_suspect_set`
- Side Effects / Risks: This parks U2 under the current suspect set; it does not prove clustering can never be useful later.
- Conclusion: The sidecar now has a proper stop rule. U1 changed the interpretation boundary, and that is enough for now.
- Next Step: Keep replay queue paused, keep U2 parked, and wait for a larger or less separable suspect batch before reopening specialist refinement.

### JOURNAL-0116

- Date: 2026-03-29
- Author: Codex
- Title: `market_research_v1` is now a real broad substrate instead of just the next planned pack
- Related Decision: DEC-0116
- Related Runs: market_research_v1_free_data_bootstrap, market_research_v1_sector_mapping, market_research_concept_mapping_v1, market_research_derived_data_v1, market_research_data_audit_v1, 20260329T111733Z_3e700662
- Protocol Version: protocol_v1.1
- Hypothesis: Once specialist refinement was intentionally parked, the next healthy move was to finish a broader pack that could later yield a larger suspect batch without jumping straight to a full-market workflow.
- What Changed: Completed the entire `market_research_v1` chain:
  - bootstrapped raw market-research v1 bars and reference tables
  - generated concept mapping
  - generated derived tables
  - audited the pack
  - ran the full strategy suite
- Expected Impact: Replace "planned broader substrate" with an actually runnable and auditable mixed-market pack that can later feed a new suspect set.
- Observed Result:
  - [market_research_data_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v1.json) shows:
    - `canonical_ready_count = 6`
    - `canonical_partial_count = 0`
    - `derived_ready_count = 3`
    - `baseline_ready = true`
  - [20260329T111733Z_3e700662_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T111733Z_3e700662_comparison.json) shows:
    - `mainline_trend_c` best total return and capture
    - `mainline_trend_a` lowest drawdown
    - `mainline_trend_b` stays in the middle as a cleaner mixed-market compromise
- Side Effects / Risks: The free-data path still emits the known `NumPy 2.x` compatibility warnings through the AKShare/pandas chain. The pack completed successfully, but the environment issue remains intentionally unmanaged inside the main research environment.
- Conclusion: `market_research_v1` is now operational and can serve as the next broader suspect substrate, but it should not be silently upgraded into a new default-validation pack.
- Next Step: Leave replay queue paused and wait for the next real suspect batch before considering whether `U2` or a new specialist loop should reopen.

### JOURNAL-0117

- Date: 2026-03-29
- Author: Codex
- Title: `market_research_v1` already changes specialist opportunity geography even though it does not change the broad freeze
- Related Decision: DEC-0117
- Related Runs: 20260329T112015Z_d5db1be9, specialist_alpha_analysis_v2
- Protocol Version: protocol_v1.1
- Hypothesis: If `market_research_v1` is worth keeping as the next broad substrate, it should start producing new specialist pockets even if the broad-anchor ordering remains stable.
- What Changed: Re-ran time-slice validation with `baseline_research_v1 + theme_research_v4 + market_research_v1`, then re-ran specialist analysis on that validation report.
- Expected Impact: Distinguish "larger but redundant pack" from "larger pack that actually changes where future specialist work should start."
- Observed Result:
  - [20260329T112015Z_d5db1be9_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T112015Z_d5db1be9_comparison.json) shows the broad ranking stays healthy and familiar:
    - `buffer_only_012` remains the broad stability leader
    - `theme_strict_quality_branch` still leads drawdown-specialist rows by count
  - [specialist_alpha_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v2.json) shows genuine new pocket geography:
    - strongest new drawdown pocket:
      `market_research_v1 / 2024_q3 / mainline_trend_c`
    - strongest new capture pockets:
      `market_research_v1 / 2024_q2 / mainline_trend_a|b|c`
- Side Effects / Risks: These are still suspect pockets, not yet new family assets. The result justifies reopening specialist work later on `market_research_v1`, not bypassing replay discipline.
- Conclusion: `market_research_v1` is already doing useful work. It is not a new default-validation pack, but it is now the right first substrate when specialist refinement reopens.
- Next Step: Keep replay queue paused for now, but when the next suspect batch is intentionally reopened, start from the new `market_research_v1` pockets rather than from `market_research_v0`.

### JOURNAL-0118

- Date: 2026-03-29
- Author: Codex
- Title: The first `market_research_v1` drawdown pocket is a clean reuse of the baseline-style family
- Related Decision: DEC-0118
- Related Runs: market_v1_q3_trade_divergence_quality_c_v1, market_v1_q3_symbol_timeline_300308_quality_c_v1, market_v1_q3_symbol_cycle_delta_300308_c_v1, market_v1_q3_nearby_cycle_bridge_300308_c_v1, market_v1_q3_cycle_mechanism_300308_c_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If `market_research_v1` is the right next suspect substrate, its first strong drawdown pocket should either reveal a new family or give us a clean reuse case that confirms the broader pack remains interpretable.
- What Changed: Replayed the strongest positive symbol from `market_research_v1 / 2024_q3 / mainline_trend_c` through timeline, cycle-delta, nearby-bridge, and cycle-mechanism layers.
- Expected Impact: Distinguish "bigger pack, same interpretable family" from "bigger pack, new unclassified mechanism."
- Observed Result:
  - [market_v1_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_c_v1.json) shows `300308` is the dominant positive symbol with `pnl_delta = 1781.321`
  - [market_v1_q3_cycle_mechanism_300308_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_c_v1.json) resolves the pocket into:
    - `2` x `entry_suppression_avoidance`
    - `1` x `earlier_exit_loss_reduction`
    - `0` worsened mechanisms
- Side Effects / Risks: This is a strong interpretability result, but it also means the first new market-v1 pocket did not expand the family frontier.
- Conclusion: `market_research_v1` is producing a clean and reusable suspect pocket, but the first one lands inside the existing baseline-style drawdown family rather than generating a new non-baseline asset.
- Next Step: Continue using `market_research_v1` as the first future suspect source, but evaluate new pockets against the current family inventory before opening any new family branch.

### JOURNAL-0119

- Date: 2026-03-29
- Author: Codex
- Title: The first `market_research_v1` q2 capture pocket is a persistence edge, not another opening edge
- Related Decision: DEC-0119
- Related Runs: market_v1_q2_trade_divergence_capture_c_v1, market_v1_q2_symbol_timeline_300502_capture_c_v1, market_v1_q2_specialist_window_persistence_300502_v1
- Protocol Version: protocol_v1.1
- Hypothesis: The strongest new q2 capture pocket might still turn out to be an opening-family replay, but it could also be a different specialist mechanism if the branch and anchors entered together and only diverged on holding behavior.
- What Changed: Replayed `market_research_v1 / 2024_q2 / mainline_trend_c / 300502` across `shared_default`, `buffer_only_012`, and `baseline_expansion_branch`, then ran a targeted persistence classification over the final profitable window.
- Expected Impact: Determine whether the first market-v1 q2 capture pocket expands the capture-side mechanism map beyond opening-only stories.
- Observed Result:
  - [market_v1_q2_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_trade_divergence_capture_c_v1.json) shows `300502` is the dominant positive symbol with `pnl_delta = 467.532`
  - [market_v1_q2_specialist_window_persistence_300502_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_persistence_300502_v1.json) shows:
    - specialist still holds on `2024-06-17`
    - both anchors emit `sell`
    - both anchors have `assignment_became_junk`
    - specialist remains `late_mover` and `structure_intact`
- Side Effects / Risks: This clarifies the dominant symbol but does not yet classify every q2 capture symbol in the slice.
- Conclusion: The first `market_research_v1` q2 capture pocket is a persistence-driven specialist edge, not merely another early-opening edge.
- Next Step: If q2 replay continues, compare later symbols against this persistence interpretation first instead of assuming they must belong to the opening family.

### JOURNAL-0120

- Date: 2026-03-29
- Author: Codex
- Title: `market_research_v1` now has enough evidence to justify a formal V1.1 stage review
- Related Decision: DEC-0120
- Related Runs: market_research_data_audit_v1, 20260329T111733Z_3e700662, 20260329T112015Z_d5db1be9, specialist_alpha_analysis_v2, market_v1_q3_cycle_mechanism_300308_c_v1, market_v1_q2_specialist_window_persistence_300502_v1
- Protocol Version: protocol_v1.1
- Hypothesis: After the first few `market_research_v1` pockets were replayed, the most valuable next step was no longer another symbol-level case, but a clean stage-boundary clarification.
- What Changed: Added a dedicated stage review document instead of letting the latest meaning stay scattered across logs, pack plans, and pocket reports.
- Expected Impact: Lock in the current phase definition before specialist continuation resumes:
  - `market_research_v1` has changed role
  - broad freeze has not changed
  - specialist geography has changed
  - continuation is allowed only as narrow mechanism-first replay
- Observed Result: [32_V11_STAGE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/32_V11_STAGE_REVIEW.md) now fixes the current phase boundary and stop conditions in one place.
- Side Effects / Risks: A later replay may still strengthen or revise the current boundary, but that should now happen explicitly against the stage review rather than by drift.
- Conclusion: This stage is now properly named and bounded. The repo no longer needs to infer its own position from the latest few reports.
- Next Step: If specialist replay continues, it should continue against the stage-review rules rather than as open-ended queue momentum.

### JOURNAL-0121

- Date: 2026-03-29
- Author: Codex
- Title: The q2 market-v1 capture slice is now explicitly mixed, not persistence-only
- Related Decision: DEC-0121
- Related Runs: market_v1_q2_trade_divergence_capture_c_v1, market_v1_q2_symbol_timeline_300502_capture_c_v1, market_v1_q2_specialist_window_persistence_300502_v1, market_v1_q2_symbol_timeline_002371_capture_c_v1, market_v1_q2_specialist_window_opening_002371_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the next strongest q2 capture symbol also collapsed into persistence, then the current q2 read could stay narrow. If it instead opened a separate extra window, the slice would need to be re-described as mixed.
- What Changed: Replayed `002371` after `300502` and classified the new specialist-only window through the opening analyzer.
- Expected Impact: Test whether the q2 capture slice changes the stage boundary or merely adds another case note.
- Observed Result:
  - [market_v1_q2_symbol_timeline_002371_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_symbol_timeline_002371_capture_c_v1.json) shows an extra specialist-only trade on `2024-06-06 -> 2024-06-07`
  - [market_v1_q2_specialist_window_opening_002371_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_opening_002371_v1.json) shows the edge is not persistence:
    - permission and filters are already aligned
    - both anchors stay `junk`
    - specialist upgrades the symbol to `late_mover` and opens the extra window
- Side Effects / Risks: The q2 slice is now less simple, but more honest. Further q2 replay should be judged against whether it changes this new mixed reading.
- Conclusion: `market_research_v1 / 2024_q2 / mainline_trend_c` is now best described as a mixed capture slice: one clean persistence edge and one clean opening edge.
- Next Step: Continue q2 replay only if another symbol is likely to add a third mechanism or materially rebalance the current mixed reading.

### JOURNAL-0122

- Date: 2026-03-29
- Author: Codex
- Title: The q2 market-v1 capture slice now has an explicit stop gate
- Related Decision: DEC-0122
- Related Runs: market_v1_q2_trade_divergence_capture_c_v1, market_v1_q2_specialist_window_persistence_300502_v1, market_v1_q2_specialist_window_opening_002371_v1, market_v1_q2_capture_slice_acceptance_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once q2 already contained one clean persistence edge and one clean opening edge, the next healthy step was to ask whether replay continuation would still change the slice verdict.
- What Changed: Added a dedicated q2 slice acceptance layer instead of continuing directly to the next q2 symbol.
- Expected Impact: Replace "maybe one more q2 replay" with an explicit answer about whether the slice is still open.
- Observed Result: [market_v1_q2_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_capture_slice_acceptance_v1.json) concludes:
  - `acceptance_posture = close_market_q2_capture_slice_as_mixed_opening_plus_persistence`
  - `top_positive_symbols = [300502, 002371, 603259]`
  - `mixed_mechanism_confirmed = true`
  - `do_continue_q2_capture_replay = false`
- Side Effects / Risks: This closes the slice under current evidence, not forever. Reopening q2 later would now need an explicit reason.
- Conclusion: The q2 market-v1 capture slice is no longer just "promising"; it is a bounded mixed slice with a formal stop condition.
- Next Step: Move any future specialist continuation to a different market-v1 pocket unless q2 produces a specific reopening trigger.

### JOURNAL-0123

- Date: 2026-03-29
- Author: Codex
- Title: The q3 market-v1 drawdown slice is now closed as a cross-strategy baseline-style reuse pocket
- Related Decision: DEC-0123
- Related Runs: market_v1_q3_trade_divergence_quality_b_v1, market_v1_q3_symbol_timeline_300308_quality_b_v1, market_v1_q3_symbol_cycle_delta_300308_b_v1, market_v1_q3_nearby_cycle_bridge_300308_b_v1, market_v1_q3_cycle_mechanism_300308_b_v1, market_v1_q3_cross_strategy_cycle_consistency_v1, market_v1_q3_drawdown_slice_acceptance_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If q3/B reproduced the same positive driver and same negative-cycle map already seen in q3/C, then q3 no longer needed symbol-by-symbol continuation.
- What Changed: Replayed `market_research_v1 / 2024_q3 / mainline_trend_b / 300308` through the full cycle chain and then added a dedicated q3 drawdown slice acceptance layer.
- Expected Impact: Replace "maybe q3 still has more to teach us" with an explicit answer about whether the slice remains open.
- Observed Result:
  - [market_v1_q3_trade_divergence_quality_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_b_v1.json) again shows `300308` is the dominant positive symbol with `pnl_delta = 1781.321`
  - [market_v1_q3_cycle_mechanism_300308_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_b_v1.json) resolves into the same three negative rows as q3/C:
    - `2` x `entry_suppression_avoidance`
    - `1` x `earlier_exit_loss_reduction`
  - [market_v1_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cross_strategy_cycle_consistency_v1.json) confirms:
    - `identical_negative_cycle_map = true`
    - `shared_negative_mechanism_count = 3`
  - [market_v1_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_drawdown_slice_acceptance_v1.json) concludes:
    - `close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse`
    - `do_continue_q3_drawdown_replay = false`
- Side Effects / Risks: This strengthens the current family inventory but does not add a new family frontier.
- Conclusion: q3 is now a closed cross-strategy-stable drawdown slice, not an open replay lane.
- Next Step: Continue specialist work only on other market-v1 slices that still have the potential to change the current phase boundary.

### JOURNAL-0124

- Date: 2026-03-29
- Author: Codex
- Title: The first q4 market-v1 drawdown replay lowers novelty rather than widening the family frontier
- Related Decision: DEC-0124
- Related Runs: market_v1_q4_trade_divergence_quality_c_v1, market_v1_q4_symbol_timeline_002371_quality_c_v1, market_v1_q4_symbol_cycle_delta_002371_c_v1, market_v1_q4_nearby_cycle_bridge_002371_c_v1, market_v1_q4_cycle_mechanism_002371_c_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the top q4/C driver opened a cleaner or less familiar drawdown pattern, q4 could become the next slice most likely to change the current stage boundary.
- What Changed: Replayed only the dominant q4/C symbol `002371` through the standard timeline -> cycle delta -> nearby bridge -> mechanism chain.
- Expected Impact: Use a single strong q4 probe to decide whether q4 still deserves continuation as a potentially novel slice.
- Observed Result:
  - [market_v1_q4_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_trade_divergence_quality_c_v1.json) shows `002371` is the dominant positive q4/C symbol with `pnl_delta = 1509.5429`
  - [market_v1_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_002371_c_v1.json) reduces the edge to a single-row `entry_suppression_avoidance`
- Side Effects / Risks: This lowers the novelty expectation for q4, but does not justify closing q4 entirely because only one q4 symbol has been replayed.
- Conclusion: The first q4 read reinforces baseline-style avoidance rather than introducing a new family. q4 stays open, but with lower novelty prior.
- Next Step: Continue q4 only if the next candidate still has plausible power to change the current stage conclusion.

### JOURNAL-0125

- Date: 2026-03-29
- Author: Codex
- Title: The q4 market-v1 drawdown slice is now closed as a mixed avoidance-plus-reduced-loss pocket
- Related Decision: DEC-0125
- Related Runs: market_v1_q4_trade_divergence_quality_c_v1, market_v1_q4_cycle_mechanism_002371_c_v1, market_v1_q4_symbol_timeline_000977_quality_c_v1, market_v1_q4_symbol_cycle_delta_000977_c_v1, market_v1_q4_nearby_cycle_bridge_000977_c_v1, market_v1_q4_cycle_mechanism_000977_c_v1, market_v1_q4_drawdown_slice_acceptance_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the second q4 symbol widened the slice beyond pure avoidance, q4 could be closed as a mixed drawdown slice without replaying a long tail of more symbols.
- What Changed: Replayed `000977` through the full cycle chain and then added a dedicated q4 drawdown slice acceptance gate.
- Expected Impact: Decide whether q4 remains an open frontier or has already become a bounded mixed slice.
- Observed Result:
  - [market_v1_q4_cycle_mechanism_000977_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_000977_c_v1.json) adds:
    - `preemptive_loss_avoidance_shift`
    - `earlier_exit_loss_reduction`
  - [market_v1_q4_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_drawdown_slice_acceptance_v1.json) concludes:
    - `close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix`
    - `do_continue_q4_drawdown_replay = false`
- Side Effects / Risks: This closes q4 under current evidence, not forever. Reopening q4 later would now need explicit reason.
- Conclusion: q4 is no longer just “open but low novelty�? It is now a bounded mixed drawdown slice: one clean avoidance driver and one reduced-loss driver.
- Next Step: Continue specialist work only on other slices unless a q4 candidate is expected to break the current mixed-slice verdict.

### JOURNAL-0126

- Date: 2026-03-29
- Author: Codex
- Title: Market-v1 specialist slices separate first by theme load and turnover concentration
- Related Decision: DEC-0126
- Related Runs: sector_theme_context_audit_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once `market_research_v1` q2/q3/q4 were all closed, the next healthy question was whether specialist continuation now needed per-sector models or a narrower conditional-context layer.
- What Changed: Added a report-only sector/theme context audit over the already-closed `market_research_v1` slices.
- Expected Impact: Replace the vague intuition that boards behave differently with an explicit next conditional feature order.
- Observed Result: [sector_theme_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/sector_theme_context_audit_v1.json) shows:
  - q2 = `theme_loaded + concentrated_turnover`
  - q3 = `hot_sector + broad_sector + balanced_turnover`
  - q4 = `theme_light + concentrated_turnover`
  - `recommended_first_conditional_feature_group = theme_load_plus_turnover_concentration_context`
  - `recommended_second_conditional_feature_group = sector_state_heat_breadth_context`
  - `do_sector_specific_training_now = false`
- Side Effects / Risks: This is still a slice-level context read, not proof that a later grouped model should be trained separately by sector.
- Conclusion: The next refinement branch should condition on sector/theme state before even considering board-specific training.
- Next Step: Start with theme load plus turnover concentration, then add heat/breadth only if needed.

### JOURNAL-0127

- Date: 2026-03-29
- Author: Codex
- Title: The first explicit context branch is now theme-turnover conditioned late-quality
- Related Decision: DEC-0127
- Related Runs: context_feature_pack_a_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the first context audit was real signal rather than a nice narrative, then explicit context fields should still separate the closed `market_research_v1` slices strongly enough to justify one narrow branch.
- What Changed: Added explicit context fields into `StockSnapshot`:
  - `context_theme_density`
  - `context_turnover_concentration`
  - `context_theme_turnover_interaction`
  - `context_sector_heat`
  - `context_sector_breadth`
  Then ran a dedicated validation report over the closed q2/q3/q4 market-v1 slices.
- Expected Impact: Turn the sector/theme context conclusion into a reusable next-branch decision instead of leaving it as review-only prose.
- Observed Result: [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json) shows:
  - `bucket_counts = {interaction_high: 1, sector_heat_led: 1, turnover_led_theme_light: 1}`
  - `interaction_spread = 0.179943`
  - `heat_spread = 0.126929`
  - `breadth_spread = 0.005463`
  - `recommended_next_feature_branch = conditioned_late_quality_on_theme_turnover_context`
  - `defer_sector_heat_branch = true`
- Side Effects / Risks: This still does not justify per-sector training and does not yet prove the next conditioned branch will improve specialist outcomes.
- Conclusion: The first context-conditioned branch is now explicit and should be treated as the next narrow refinement target.
- Next Step: Start `conditioned_late_quality_on_theme_turnover_context`; keep the heat/breadth branch deferred.

### JOURNAL-0128

- Date: 2026-03-29
- Author: Codex
- Title: Theme-turnover conditioned late-quality is real as context, but not strong enough as a kept hierarchy rule
- Related Decision: DEC-0128
- Related Runs: context_feature_pack_a_conditioned_late_quality_v1, 20260329T122538Z_a98eb978, 20260329T122501Z_40f2a08a, context_feature_pack_a_conditioned_late_quality_acceptance_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the first context branch was genuinely actionable, then a small default-off late-quality relief in `mid/high` theme-turnover interaction buckets should improve at least part of the `market_research_v1` suite materially rather than just move a few signals.
- What Changed: Added a bounded hierarchy experiment with context-conditioned late-quality relief and compared it directly against a fresh current-control `market_research_v1` suite.
- Expected Impact: Either confirm that theme-turnover context should become a retained hierarchy rule, or close this branch cleanly before it grows into another tuning loop.
- Observed Result:
  - [context_feature_pack_a_conditioned_late_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_v1.json) shows `17` candidate rows, all in `interaction_high` or `interaction_mid`, concentrated in `q2/q4`
  - the bounded hierarchy experiment only changed the suite marginally:
    - `mainline_trend_a` unchanged
    - `mainline_trend_b` improved only trivially
    - `mainline_trend_c` worsened
  - [context_feature_pack_a_conditioned_late_quality_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_acceptance_v1.json) closes the branch as `non_material`
- Side Effects / Risks: This does not invalidate the context axis itself. It only means the current simple late-quality relief implementation is not strong enough to justify retention.
- Conclusion: Theme-turnover context is still useful as explanation and suspect triage, but not yet as a kept hierarchy rule.
- Next Step: Keep sector/theme conditioning at the analysis layer and only reopen rule-level work if a later suspect batch makes this axis materially more decisive.

### JOURNAL-0129

- Date: 2026-03-29
- Author: Codex
- Title: Sector heat and breadth remain explanatory, but the current branch is too sparse to continue
- Related Decision: DEC-0129
- Related Runs: context_feature_pack_b_sector_heat_breadth_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If sector heat / breadth were the next meaningful conditional branch, then near-threshold non-junk misses with intact late-quality and resonance should recur across more than one closed `market_research_v1` slice.
- What Changed: Added a bounded report-only audit for `sector_state_heat_breadth_context` over the already-closed q2/q3/q4 market-v1 slices.
- Expected Impact: Either confirm that the deferred second context branch deserves one narrow experiment, or close it quickly before it turns into a sparse exploratory loop.
- Observed Result:
  - [context_feature_pack_b_sector_heat_breadth_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_b_sector_heat_breadth_v1.json) shows only `1` surviving candidate row
  - that candidate appears only in `2024_q4`
  - the row is `000977` on `2024-10-24`, with:
    - `non_junk_gap_to_threshold = 0.024282`
    - `late_mover_quality = 0.550817`
    - `resonance = 0.546532`
    - `context_sector_heat = 0.807045`
    - `context_sector_breadth = 0.6`
  - the final posture is:
    - `recommended_posture = close_sector_heat_breadth_context_branch_as_sparse`
    - `do_continue_context_feature_pack_b = false`
- Side Effects / Risks: This does not prove sector heat / breadth are globally useless; it only shows the current suspect batch is too sparse to justify a retained branch.
- Conclusion: The second context branch should stop at explanation. Current evidence still does not support per-sector training or a new kept hierarchy rule.
- Next Step: Keep context at the analysis layer and reopen heat/breadth only when a later suspect batch provides multi-slice support.

### JOURNAL-0130

- Date: 2026-03-29
- Author: Codex
- Title: The current specialist loop is closed; the next move is a new suspect batch
- Related Decision: DEC-0130
- Related Runs: v11_continuation_readiness_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If the current `V1.1` batch still had a justified continuation lane, at least one of these should remain open:
  - an active market-v1 slice replay lane
  - an active context-conditioned branch
  - or a ready next unsupervised sidecar step
- What Changed: Added an explicit continuation readiness gate over the current closed market-v1 slices, both context branches, U2 readiness, and the current specialist opportunity surface.
- Expected Impact: Replace momentum-driven continuation with a hard stage-exit signal.
- Observed Result:
  - [v11_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v11_continuation_readiness_v1.json) shows:
    - `all_market_v1_slices_closed = true`
    - `all_context_branches_closed = true`
    - `u2_ready = false`
    - `specialist_opportunity_count = 19`
    - `recommended_next_phase = pause_specialist_refinement_and_prepare_new_suspect_batch`
- Side Effects / Risks: The repo still has specialist opportunities in principle, but they no longer justify more local replay inside this same batch. Future work should not confuse "pause this loop" with "retire specialist alpha research."
- Conclusion: The current V1.1 specialist loop should stop here. The next productive move is a materially new suspect batch.
- Next Step: Do not reopen q2/q3/q4 replay or context rule tuning. Prepare the next suspect-generating substrate instead.

### JOURNAL-0131

- Date: 2026-03-29
- Author: Codex
- Title: The next suspect batch should target missing context archetypes
- Related Decision: DEC-0131
- Related Runs: next_suspect_batch_design_v1
- Protocol Version: protocol_v1.1
- Hypothesis: Once the current loop is paused, the next batch should not simply be "larger"; it should target context environments that are currently missing from the closed-slice geography.
- What Changed: Added a bounded batch-design report on top of the current context audit and continuation gate.
- Expected Impact: Turn “prepare a new suspect batch�?into a concrete, auditable design rule.
- Observed Result:
  - [next_suspect_batch_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_design_v1.json) shows:
    - `current_loop_paused = true`
    - `observed_closed_slice_count = 3`
    - `specialist_opportunity_count = 19`
    - `recommended_next_batch_name = market_research_v2_seed`
    - `recommended_batch_posture = expand_by_missing_context_archetypes`
  - the first missing archetypes are:
    - `theme_loaded + balanced_turnover + broad_sector`
    - `theme_loaded + balanced_turnover + narrow_sector`
    - `theme_light + concentrated_turnover + broad_sector`
- Side Effects / Risks: The archetype grid is still simple and may need revision once a real v2 seed is assembled.
- Conclusion: The next batch should be designed, not just enlarged. Current evidence supports a context-targeted `market_research_v2_seed`.
- Next Step: Define a conservative seed universe and tie each new symbol to one intended missing archetype.

### JOURNAL-0132

- Date: 2026-03-29
- Author: Codex
- Title: The first market_research_v2_seed manifest is clean enough to bootstrap
- Related Decision: DEC-0132
- Related Runs: next_suspect_batch_manifest_v1
- Protocol Version: protocol_v1.1
- Hypothesis: A next-batch seed should only move forward if it adds new symbols, covers the targeted missing archetypes, and does not overlap the current `market_research_v1` substrate.
- What Changed: Added a concrete v2-seed universe, manifest, bootstrap config, and a manifest audit.
- Expected Impact: Convert the abstract “prepare a new suspect batch�?decision into a concrete, auditable next data step.
- Observed Result:
  - [next_suspect_batch_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v1.json) shows:
    - `seed_universe_count = 9`
    - `new_symbol_count = 9`
    - `overlap_with_market_v1_count = 0`
    - `missing_archetype_count = 0`
    - `ready_to_bootstrap_market_research_v2_seed = true`
- Side Effects / Risks: The archetype assignments are still design-time intentions rather than verified realized slice labels.
- Conclusion: The repo now has a concrete, conservative `market_research_v2_seed` and does not need another design loop before bootstrap.
- Next Step: Use the prepared seed as the next controlled free-data expansion batch.
### JOURNAL-0133

- Date: 2026-03-29
- Author: Codex
- Title: Market research v2 seed is now runnable and enters specialist geography
- Related Decision: DEC-0133
- Related Runs: 20260329T130402Z_0e1d8809, 20260329T130537Z_f0a9da05, specialist_alpha_analysis_v3
- Protocol Version: protocol_v1.1
- Hypothesis: A context-targeted `market_research_v2_seed` should be useful only if it becomes a real runnable pack and begins to change the specialist map without overturning the broad freeze.
- What Changed: Completed the first derived/audit/suite cycle for `market_research_v2_seed` and integrated it into a four-pack time-slice validation plus specialist-alpha read.
- Expected Impact: Convert `v2_seed` from design artifact into a real next-stage suspect substrate.
- Observed Result:
  - [market_research_data_audit_v2_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_seed.json) shows:
    - `canonical_ready_count = 6`
    - `canonical_partial_count = 0`
    - `derived_ready_count = 3`
    - `baseline_ready = true`
  - [20260329T130402Z_0e1d8809_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130402Z_0e1d8809_comparison.json) shows:
    - `mainline_trend_c` best total return and capture
    - `mainline_trend_b` lowest drawdown
  - [20260329T130537Z_f0a9da05_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130537Z_f0a9da05_comparison.json) keeps `buffer_only_012` as the broad stability leader.
  - [specialist_alpha_analysis_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v3.json) shows `market_research_v2_seed` now contributes narrow capture and drawdown specialist pockets.
- Side Effects / Risks: `v2_seed` may still be too small and archetype-focused to justify promotion above `market_research_v1`; it should be treated as a secondary suspect substrate until more evidence accumulates.
- Conclusion: `market_research_v2_seed` is now a real and useful pack, but it currently extends specialist geography without changing the current broad or stage hierarchy.
- Next Step: Use `v2_seed` only as a controlled secondary specialist substrate, not as a reason to reopen wide replay or rewrite the current stage map.

### JOURNAL-0134

- Date: 2026-03-29
- Author: Codex
- Title: The first v2-seed q4 capture replay is real but mixed
- Related Decision: DEC-0134
- Related Runs: market_v2_seed_q4_trade_divergence_capture_c_v1, market_v2_seed_q4_symbol_timeline_603986_capture_c_v1, market_v2_seed_q4_specialist_window_opening_603986_v1
- Protocol Version: protocol_v1.1
- Hypothesis: If `market_research_v2_seed` is a useful new suspect substrate, its first strong q4/C capture symbol should either provide a clean opening/persistence read or expose why the read is still mixed.
- What Changed: Replayed the dominant q4/C capture symbol inside `market_research_v2_seed`.
- Expected Impact: Determine whether the first `v2_seed` capture pocket changes the family boundary or only adds a qualified next-stage case.
- Observed Result:
  - [market_v2_seed_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_trade_divergence_capture_c_v1.json) identifies `603986` as the dominant q4/C positive symbol.
  - [market_v2_seed_q4_specialist_window_opening_603986_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_specialist_window_opening_603986_v1.json) confirms a clean specialist-only opening edge on `2024-12-12`.
  - [market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json) also shows a positive trade carried in from `2024-09-27`.
- Side Effects / Risks: The pocket is real, but the carry-in component makes it too noisy to count as a clean new family signal.
- Conclusion: The first `v2_seed` q4/C replay strengthens the case that `v2_seed` is productive, but the current read is mixed opening-plus-carry rather than a clean new family boundary.
- Next Step: Continue using `v2_seed` only where the next replay can materially clean or overturn this mixed read.

- Acceptance Update:
  - [market_v2_seed_q4_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_capture_slice_acceptance_v1.json)
    now closes the slice:
    - `acceptance_posture = close_market_v2_seed_q4_capture_slice_as_opening_plus_carry`
    - `do_continue_q4_capture_replay = false`

### JOURNAL-0135

- Date: 2026-03-29
- Author: Codex
- Title: The first v2-seed q3/C drawdown replay is real but mixed
- Related Decision: DEC-0135
- Hypothesis: If `market_research_v2_seed` is a useful secondary drawdown substrate, its first q3/C lane should either produce a clean new-family boundary or show clearly why the lane is still mixed.
- What Changed: Replayed `603986` inside `market_research_v2_seed / 2024_q3 / mainline_trend_c`, then added a q3/C slice-acceptance gate.
- Expected Impact: Turn the first q3/C read into a phase boundary instead of another open replay lane.
- Observed Result:
  - [market_v2_seed_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_trade_divergence_quality_c_v1.json) identifies `603986` as the dominant q3/C drawdown symbol.
  - [market_v2_seed_q3_cycle_mechanism_603986_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_cycle_mechanism_603986_c_v1.json) shows:
    - negative side: `entry_suppression_avoidance`
    - positive side: `entry_suppression_opportunity_cost`
  - [market_v2_seed_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_drawdown_slice_acceptance_v1.json) closes the lane:
    - `acceptance_posture = close_market_v2_seed_q3_drawdown_slice_as_avoidance_plus_opportunity_cost`
    - `do_continue_q3_drawdown_replay = false`
- Side Effects / Risks: The q3/C lane is now interpretable and bounded, but it does not supply a clean new drawdown family.
- Conclusion: `v2_seed` q3/C should now be treated as a useful but mixed drawdown slice, not as a frontier lane that deserves more local replay.
- Next Step: Keep `v2_seed` slice-gated and only reopen if a later lane can plausibly overturn the current mixed read.

### JOURNAL-0136

- Date: 2026-03-29
- Author: Codex
- Title: v2-seed is now useful, real, and bounded
- Related Decision: DEC-0136
- Hypothesis: Once `market_research_v2_seed` is baseline-ready and has two closed local lanes, the correct next posture is to hold it as a secondary substrate rather than force a third replay lane.
- What Changed: Added a dedicated continuation gate for `market_research_v2_seed`.
- Expected Impact: Prevent `v2_seed` from turning into another open-ended replay loop while keeping it available as a future suspect substrate.
- Observed Result:
  - [market_v2_seed_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_continuation_readiness_v1.json) concludes:
    - `all_open_v2_seed_lanes_closed = true`
    - `v2_seed_baseline_ready = true`
    - `v2_seed_contributes_specialist_pockets = true`
    - `recommended_next_phase = hold_market_v2_seed_as_secondary_substrate_and_wait_for_next_batch_refresh`
    - `do_continue_current_v2_seed_replay = false`
- Side Effects / Risks: `v2_seed` may still contain future useful lanes, but under the current evidence a third lane would be momentum-driven rather than decision-boundary-driven.
- Conclusion: `v2_seed` has graduated from seed manifest to bounded secondary substrate.
- Next Step: Wait for a later suspect refresh or a materially different `v2_seed` lane rather than opening a third local replay by inertia.

### JOURNAL-0137

- Date: 2026-03-29
- Author: Codex
- Title: The next post-v2 refresh is now explicitly gated
- Related Decision: DEC-0137
- Hypothesis: Once both the main `V1.1` loop and the current `v2_seed` loop are paused, the repo should not open another refresh until a real trigger appears.
- What Changed: Added an explicit next-refresh readiness gate and policy file.
- Expected Impact: Prevent `market_research_v2_refresh` from becoming another default continuation path.
- Observed Result:
  - [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json) concludes:
    - `v11_current_loop_paused = true`
    - `v2_seed_local_loop_paused = true`
    - `v2_seed_secondary_substrate_status = true`
    - `recommended_next_phase = wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh`
    - `do_open_market_research_v2_refresh_now = false`
- Side Effects / Risks: This makes the repo more conservative, but that is intentional; the next refresh should be trigger-driven, not momentum-driven.
- Conclusion: The repo now has an explicit stop-rule between `v2_seed` and any later refresh.
- Next Step: Wait for a new archetype gap or materially different suspect geography before opening the next batch design cycle.

### JOURNAL-0138

- Date: 2026-03-29
- Author: Codex
- Title: The repo is now in an explicit no-trigger waiting state
- Related Decision: DEC-0138
- Hypothesis: Once the next refresh is gated, the repo should also expose whether any trigger is currently active rather than leave the wait state implicit.
- What Changed: Added an operational refresh trigger monitor.
- Expected Impact: Make the post-`v2_seed` wait state auditable and machine-checkable.
- Observed Result:
  - [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json) shows:
    - `active_trigger_count = 0`
    - `archetype_gap_trigger = false`
    - `specialist_geography_trigger = false`
    - `clean_frontier_trigger = false`
    - `secondary_status_break_trigger = false`
    - `recommended_posture = maintain_waiting_state_until_new_trigger`
- Side Effects / Risks: The repo becomes more conservative, but that is intentional; phase reopening now needs a concrete trigger.
- Conclusion: The current status is now stronger than a pause. It is an explicit no-trigger wait state.
- Next Step: Do not open `market_research_v2_refresh` or resume local replay until at least one trigger changes.

### JOURNAL-0139

- Date: 2026-03-29
- Author: Codex
- Title: The no-trigger wait state now has its own operator checklist
- Related Decision: DEC-0139
- Hypothesis: Once the repo is in a no-trigger waiting state, the safest next improvement is not another strategy branch but an explicit operator checklist.
- What Changed: Added a refresh-trigger action-plan report and runbook.
- Expected Impact: Remove ambiguity about what to do while idle and what to do first when a trigger flips.
- Observed Result:
  - [refresh_trigger_action_plan_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_action_plan_v1.json) shows:
    - `action_mode = idle_wait_state`
    - `action_count = 3`
    - `recommended_next_phase = wait_for_new_archetype_gap_signal_before_opening_market_research_v2_refresh`
- Side Effects / Risks: This adds more governance scaffolding, but it is lightweight and helps keep future refresh work trigger-driven.
- Conclusion: The post-`v2_seed` waiting state is now fully operationalized.
- Next Step: Wait for a trigger flip rather than inventing another refinement lane.

### JOURNAL-0140

- Date: 2026-03-29
- Author: Codex
- Title: The repo now has a one-page phase status snapshot
- Related Decision: DEC-0140
- Hypothesis: Once the current phase is fully gated, the highest-value improvement is a one-page snapshot that says whether anything new should happen right now.
- What Changed: Added a phase-status snapshot over the current gate stack.
- Expected Impact: Make the current phase state readable from one report instead of five aligned reports.
- Observed Result:
  - [phase_status_snapshot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/phase_status_snapshot_v1.json) shows:
    - `current_mode = explicit_no_trigger_wait`
    - `all_gates_aligned = true`
    - `active_trigger_count = 0`
    - `recommended_operator_posture = idle_wait_state`
- Side Effects / Risks: Very low; this is a read-only compression layer.
- Conclusion: The current repo state is now easy to inspect and less likely to drift into accidental work.
- Next Step: Use the snapshot as the first check before any future replay or refresh action.

### JOURNAL-0141

- Date: 2026-03-29
- Author: Codex
- Title: The current waiting-state stack is now refreshable in one command
- Related Decision: DEC-0141
- Hypothesis: Once the repo has a gated waiting state, the next useful improvement is a single refresh chain that regenerates the whole stack in the right order.
- What Changed: Added `run_phase_status_refresh.py` and the corresponding runbook.
- Expected Impact: Reduce operator friction and avoid partial refresh of the status stack.
- Observed Result:
  - `python scripts/run_phase_status_refresh.py` successfully regenerated:
    - `next_batch_refresh_readiness_v1.json`
    - `refresh_trigger_monitor_v1.json`
    - `refresh_trigger_action_plan_v1.json`
    - `phase_status_snapshot_v1.json`
  - final snapshot still reads:
    - `current_mode = explicit_no_trigger_wait`
    - `all_gates_aligned = true`
    - `active_trigger_count = 0`
- Side Effects / Risks: Very low; this only refreshes read-only gate artifacts.
- Conclusion: The repo can now recheck its current waiting state in one command.
- Next Step: Use the refresh chain when new data or suspect signals appear, not as permission to reopen replay by itself.

### JOURNAL-0142

- Date: 2026-03-29
- Author: Codex
- Title: The current wait state now has a one-command console entry
- Related Decision: DEC-0142
- Hypothesis: After adding a refresh chain, the next useful refinement is a shorter operator-facing console read.
- What Changed: Added `run_phase_status_console.py`.
- Expected Impact: Make the current no-trigger wait state readable without opening JSON or markdown.
- Observed Result:
  - `python scripts/run_phase_status_console.py` prints:
    - `PHASE STATUS: explicit no-trigger wait`
    - `active triggers: 0`
    - the first three next actions
- Side Effects / Risks: Very low; this is a read-only console surface over existing reports.
- Conclusion: The current wait state is now both machine-refreshable and human-readable from a single command.
- Next Step: Keep using the console only as a read surface, not as permission to reopen work.

### JOURNAL-0143

- Date: 2026-03-29
- Author: Codex
- Title: The current wait state now has a one-command guarded entry
- Related Decision: DEC-0143
- Hypothesis: After adding refresh and console entrypoints, the next useful refinement is a single guarded command that refreshes first and then prints the final operator read.
- What Changed: Added `run_phase_guard.py` and the corresponding runbook.
- Expected Impact: Reduce operator friction further and remove any need to remember whether refresh should happen before console inspection.
- Observed Result:
  - `python scripts/run_phase_guard.py` successfully:
    - regenerated `next_batch_refresh_readiness_v1.json`
    - regenerated `refresh_trigger_monitor_v1.json`
    - regenerated `refresh_trigger_action_plan_v1.json`
    - regenerated `phase_status_snapshot_v1.json`
    - printed `PHASE STATUS: explicit no-trigger wait`
  - final read remained:
    - `active triggers: 0`
    - `all gates aligned: true`
    - `operator posture: idle_wait_state`
- Side Effects / Risks: Very low; this is still a read-only operational layer and does not authorize new research by itself.
- Conclusion: The no-trigger wait state is now refreshable, inspectable, and enforceable from one shortest safe command.
- Next Step: Use the guard when the only question is whether anything new is now allowed.

### JOURNAL-0144

- Date: 2026-03-29
- Author: Codex
- Title: The waiting state now has a canonical intake step for future trigger signals
- Related Decision: DEC-0144
- Hypothesis: Once the repo has a stable waiting-state gate stack, the next useful refinement is a standard intake artifact for genuinely new signals.
- What Changed: Added `run_refresh_trigger_intake.py`, the corresponding strategy helper, test, and runbook.
- Expected Impact: Future trigger candidates can be recorded consistently before rerunning the guard stack.
- Observed Result:
  - `python scripts/run_refresh_trigger_intake.py --trigger-name new_archetype_gap --trigger-type archetype_gap --source manual_review --rationale "Found a materially different suspect geography." --dataset market_research_v1 --dataset market_research_v2_seed --symbol 603986 --slice 2024_q4`
    successfully wrote:
    - [refresh_trigger_intake_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_intake_v1.json)
  - the intake summary recorded:
    - `dataset_count = 2`
    - `symbol_count = 1`
    - `slice_count = 1`
    - `recommended_next_step = rerun_phase_guard_after_persisting_new_signal`
- Side Effects / Risks: Very low; this records trigger candidates but still does not open refresh by itself.
- Conclusion: The repo now has a standard first step for future trigger handling: intake first, guard second.
- Next Step: Use intake only for genuinely new signals, then rerun `python scripts/run_phase_guard.py`.

### JOURNAL-0145

- Date: 2026-03-29
- Author: Codex
- Title: Refresh-trigger intake now enforces a canonical trigger taxonomy
- Related Decision: DEC-0145
- Hypothesis: Once intake exists, the next low-risk improvement is to constrain trigger labels to a small canonical set.
- What Changed: Added explicit trigger-type validation to `refresh_trigger_intake.py` and documented the allowed labels in the intake runbook.
- Expected Impact: Prevent future trigger candidates from drifting into incomparable free-form labels.
- Observed Result:
  - the intake CLI now validates canonical trigger types
  - the canonical set is:
    - `archetype_gap`
    - `new_suspect`
    - `specialist_geography_shift`
    - `clean_frontier_break`
    - `secondary_status_break`
    - `policy_override`
- Side Effects / Risks: Very low; this only narrows future intake labels.
- Conclusion: The waiting-state exit path is now not only standardized, but also typed.
- Next Step: Keep future intake records inside this canonical taxonomy unless the phase policy itself changes.

### JOURNAL-0146

- Date: 2026-03-29
- Author: Codex
- Title: The repo commission assumption now matches the owner's A-share contract
- Related Decision: DEC-0146
- Hypothesis: Once the owner provides a real broker commission contract, the repo should align the broker-commission assumption without simultaneously guessing unrelated statutory fees.
- What Changed: Updated the default `CostModel` commission from `3.0 bps` to `1.2 bps` and aligned the base config plus explicit config defaults to the same value.
- Expected Impact: Future backtests and strategy comparisons should better match the owner's actual broker-side commission drag.
- Observed Result:
  - `commission_bps` default is now `1.2`
  - `min_commission` remains `5.0`
  - statutory stock-tax and transfer-fee assumptions are now handled under DEC-0147 / JOURNAL-0147
- Side Effects / Risks: Historical reports remain based on the old commission assumption until rerun; this change only affects future runs.
- Conclusion: The repo is now closer to the owner's real trading cost on the broker-commission dimension, but not yet fully customized for all statutory fees.
- Next Step: Reuse the new commission default in future runs and only revisit stamp-tax / exchange fees when a separate fee table is explicitly confirmed.

### JOURNAL-0147

- Date: 2026-03-29
- Author: Codex
- Title: The repo now separates broker commission from the full public A-share stock fee stack
- Related Decision: DEC-0147
- Hypothesis: Once the owner's broker commission is aligned, the next necessary correction is to separately align the public statutory and exchange-collected stock charges instead of folding them into the commission line.
- What Changed: Updated the default A-share stock-fee assumptions to `stamp_tax_bps = 5.0` on sells and `transfer_fee_bps = 0.1`, `exchange_handling_bps = 0.341`, and `regulatory_fee_bps = 0.2`, and bulk-aligned the explicit YAML config defaults to the same sell-tax value.
- Expected Impact: Future backtests should better reflect the current practical cost stack for A-share stock trades, especially on sell-side exits and smaller notional orders.
- Observed Result:
  - `commission_bps = 1.2`
  - `min_commission = 5.0`
  - `stamp_tax_bps = 5.0`
  - `transfer_fee_bps = 0.1`
    - `exchange_handling_bps = 0.341`
    - `regulatory_fee_bps = 0.2`
  - explicit config files no longer retain the old `stamp_tax_bps = 10.0` assumption
- Side Effects / Risks: Historical reports still reflect the older fee stack until rerun, and the current model still excludes any broker-specific miscellaneous line items beyond the public stock-fee schedule.
- Conclusion: The repo now reflects the owner's live broker commission and the current public A-share stock fee stack as separate assumptions.
- Next Step: Reuse this fee stack in future reruns and only add separate exchange-handling lines if the owner later wants the model pushed closer to a full broker statement breakdown.

### JOURNAL-0148

- Date: 2026-03-29
- Author: Codex
- Title: The repo has now opened V1.2 instead of trying to keep pushing the paused specialist loop
- Related Decision: DEC-0148
- Hypothesis: Once the current specialist loop has correctly entered an explicit waiting state, the next high-value move is not another replay but a clean phase switch.
- What Changed: Added a dedicated `V1.2 Data Expansion And Factorization Prep` phase definition.
- Expected Impact: Prevent the repo from reopening low-value replay momentum and redirect work toward new inputs plus formalized feature assets.
- Observed Result:
  - the new phase purpose is documented
  - `market_research_v2_refresh` is now the intended next data-expansion target
  - feature/factor preparation is now explicitly a first-class phase objective
- Side Effects / Risks: Very low; this is a phase-definition change, not a replay restart.
- Conclusion: The repo now has a clean post-`V1.1` direction instead of a vague ��keep going�� posture.
- Next Step: Finalize data-source policy and then open the first `V1.2` data-refresh design.

### JOURNAL-0149

- Date: 2026-03-29
- Author: Codex
- Title: The repo now has an explicit V1.2 data-source policy
- Related Decision: DEC-0149
- Hypothesis: Before opening `market_research_v2_refresh`, the repo should explicitly separate primary batch-ingestion sources from official truth sources.
- What Changed: Added a data-source inventory that treats AkShare as the default batch-ingestion layer, Eastmoney-like board/theme data as usable through current wrappers, and official sites as the preferred fee/rule truth layer.
- Expected Impact: Reduce future source drift and keep the next expansion phase auditable.
- Observed Result:
  - `AkShare` remains the primary structured collection layer
  - official sites remain the preferred fee/rule truth layer
  - Tonghuashun-like public data is now explicitly secondary rather than an assumed backbone
- Side Effects / Risks: Point-in-time cleanliness risks remain and still need repo-side discipline during future batch refresh work.
- Conclusion: The repo now has a source-of-truth policy suitable for opening `V1.2`.
- Next Step: Start `market_research_v2_refresh` design on top of this source policy rather than reopening old replay loops.

### JOURNAL-0148

- Date: 2026-03-29
- Author: Codex
- Title: The repo has now opened V1.2 instead of trying to keep pushing the paused specialist loop
- Related Decision: DEC-0148
- Hypothesis: Once the current specialist loop has correctly entered an explicit waiting state, the next high-value move is not another replay but a clean phase switch.
- What Changed: Added a dedicated `V1.2 Data Expansion And Factorization Prep` phase definition.
- Expected Impact: Prevent the repo from reopening low-value replay momentum and redirect work toward new inputs plus formalized feature assets.
- Observed Result:
  - the new phase purpose is documented
  - `market_research_v2_refresh` is now the intended next data-expansion target
  - feature/factor preparation is now explicitly a first-class phase objective
- Side Effects / Risks: Very low; this is a phase-definition change, not a replay restart.
- Conclusion: The repo now has a clean post-`V1.1` direction instead of a vague ��keep going�� posture.
- Next Step: Finalize data-source policy and then open the first `V1.2` data-refresh design.

### JOURNAL-0149

- Date: 2026-03-29
- Author: Codex
- Title: The repo now has an explicit V1.2 data-source policy
- Related Decision: DEC-0149
- Hypothesis: Before opening `market_research_v2_refresh`, the repo should explicitly separate primary batch-ingestion sources from official truth sources.
- What Changed: Added a data-source inventory that treats AkShare as the default batch-ingestion layer, Eastmoney-like board/theme data as usable through current wrappers, and official sites as the preferred fee/rule truth layer.
- Expected Impact: Reduce future source drift and keep the next expansion phase auditable.
- Observed Result:
  - `AkShare` remains the primary structured collection layer
  - official sites remain the preferred fee/rule truth layer
  - Tonghuashun-like public data is now explicitly secondary rather than an assumed backbone
- Side Effects / Risks: Point-in-time cleanliness risks remain and still need repo-side discipline during future batch refresh work.
- Conclusion: The repo now has a source-of-truth policy suitable for opening `V1.2`.
- Next Step: Start `market_research_v2_refresh` design on top of this source policy rather than reopening old replay loops.

### JOURNAL-0150

- Date: 2026-03-29
- Author: Codex
- Title: The first V1.2 refresh batch is now prepared as a runnable pack skeleton
- Related Decision: DEC-0150
- Hypothesis: Once `V1.2` is opened, the next useful move is to convert the phase into a concrete refresh batch rather than leave it at plan level.
- What Changed: Added `market_research_v2_refresh` plan, merged reference base, refresh universe, manifest, bootstrap config, sector mapping, concept mapping, derived-data config, data-audit config, and suite config.
- Expected Impact: The next expansion phase can now move directly into data bootstrap instead of first rebuilding config scaffolding.
- Observed Result:
  - `next_suspect_batch_manifest_v2_refresh.json` now reports `new_symbol_count = 9`
  - `overlap_with_market_v1_count = 0`
  - `missing_archetype_count = 0`
  - `ready_to_bootstrap_next_batch = true`
- Side Effects / Risks: The archetype assignments remain design hypotheses until the refresh pack is actually bootstrapped and validated.
- Conclusion: `market_research_v2_refresh` is now a real next batch, not only a future idea.
- Next Step: Run the free-data bootstrap and first audit for `market_research_v2_refresh`.

### JOURNAL-0151

- Date: 2026-03-29
- Author: Codex
- Title: The repo now has its first formal feature/factor registry artifact
- Related Decision: DEC-0151
- Hypothesis: Once `V1.2` has a runnable refreshed pack and closed first refreshed slice, the next useful move is to classify the repo's current research assets explicitly.
- What Changed: Added `feature_factor_registry_v1` and split current assets into retained features, explanatory-only features, and candidate factors.
- Expected Impact: Prevent the next phase from treating every useful mechanism as the same kind of asset and create a clean handoff into factor-evaluation work.
- Observed Result:
  - `registry_entry_count = 10`
  - `retained_feature_count = 4`
  - `explanatory_only_feature_count = 3`
  - `candidate_factor_count = 3`
  - `ready_for_factor_evaluation_protocol = true`
- Side Effects / Risks: The first registry still relies on current evidence depth; some candidate factors may later be downgraded after protocol-level evaluation.
- Conclusion: `V1.2` now has a formal asset layer instead of only a set of reports and family notes.
- Next Step: Define `factor_evaluation_protocol_v1` and test the current candidate-factor bucket.

### JOURNAL-0152

- Date: 2026-03-29
- Author: Codex
- Title: The first candidate-factor bucket now has a formal protocol-level split
- Related Decision: DEC-0152
- Hypothesis: Once the first registry exists, the clean next move is to classify candidate factors by evaluation readiness rather than reopen replay or add more registry rows first.
- What Changed: Added `factor_evaluation_protocol_v1` and applied it to the current candidate-factor bucket using registry plus family-inventory evidence.
- Expected Impact: Create the first bounded handoff from asset classification into actual factor work while keeping weak or penalty-heavy factors out of the clean first-pass lane.
- Observed Result:
  - `evaluate_now_count = 1`
  - `evaluate_with_penalty_count = 1`
  - `hold_for_more_sample_count = 1`
  - `first_pass_shortlist = ['carry_in_basis_advantage']`
- Side Effects / Risks: `preemptive_loss_avoidance_shift` remains promising but still carries toxic companion-pocket baggage; `delayed_entry_basis_advantage` remains too thin for first-pass evaluation.
- Conclusion: `V1.2` has now moved past registry construction and into its first protocol-level factor readiness layer.
- Next Step: Open the first bounded factor workstream starting with the `evaluate_now` bucket.

### JOURNAL-0153

- Date: 2026-03-29
- Author: Codex
- Title: The first bounded factor lane now opens on carry-in-basis advantage
- Related Decision: DEC-0153
- Hypothesis: Once the protocol isolates one clean `evaluate_now` factor, the repo should open a narrow first-pass factor lane instead of widening factor work immediately.
- What Changed: Added `carry_in_basis_first_pass_v1` and confirmed that `carry_in_basis_advantage` is ready for bounded factor design while still staying below retained-feature promotion.
- Expected Impact: Give `V1.2` its first real factor workstream without losing the discipline gained from the registry and protocol layers.
- Observed Result:
  - `acceptance_posture = open_carry_in_basis_first_pass_as_bounded_factor_candidate`
  - `do_open_bounded_carry_factor_lane = true`
  - `promote_to_retained_feature_now = false`
- Side Effects / Risks: The factor is still concentrated in the current theme-q4 evidence base, so the lane should remain bounded and should not be mistaken for broad retained-feature closure.
- Conclusion: `V1.2` now has a clean first-pass factor entry point.
- Next Step: Design the first bounded carry factor workstream itself rather than reopening replay or touching penalty-track factors.

### JOURNAL-0154

- Date: 2026-03-29
- Author: Codex
- Title: The first carry factor lane is now explicitly row-isolated
- Related Decision: DEC-0154
- Hypothesis: Once carry is admitted into a bounded factor lane, the next real risk is over-widening it by treating a mixed pocket as one factor.
- What Changed: Added `carry_factor_design_v1` and restricted the first carry lane to row-isolated negative-cycle basis design.
- Expected Impact: Let `V1.2` keep moving into factor work without accidentally conflating carry with broader mixed-pocket specialist behavior.
- Observed Result:
  - `design_posture = open_row_isolated_carry_factor_design`
  - `mixed_with_earlier_exit = true`
  - `row_isolation_required = true`
  - `allow_broad_factor_scoring_now = false`
- Side Effects / Risks: The lane is now intentionally narrow; if later evidence shows clean carry-only pockets elsewhere, the design boundary may need to widen.
- Conclusion: The first bounded factor workstream now has a real design boundary instead of only an admission gate.
- Next Step: Define the carry-specific observable schema inside this row-isolated boundary.

### JOURNAL-0155

- Date: 2026-03-29
- Author: Codex
- Title: The first carry factor lane now has an explicit row-level observable schema
- Related Decision: DEC-0155
- Hypothesis: Once carry is admitted into a bounded, row-isolated factor lane, the next correct move is to define the minimal observable schema before scoring design.
- What Changed: Added `carry_observable_schema_v1` and extracted explicit row-level fields for the carry lane from the shared `theme_q4 / 300750 / B,C` evidence base.
- Expected Impact: Move the carry lane from narrative design into field-level design while keeping the lane narrow and auditable.
- Observed Result:
  - `schema_posture = open_carry_observable_schema_v1`
  - `observable_mode = negative_cycle_basis_row`
  - `required_fields = [basis_advantage_abs, basis_advantage_bps, challenger_carry_days, same_exit_date, pnl_delta_vs_closest]`
  - `allow_scoring_design_next = true`
- Side Effects / Risks: The schema is still grounded in the current `theme_q4 / 300750` evidence base, so later slices may force schema widening or field adjustment.
- Conclusion: The first bounded factor lane is now field-defined rather than only report-defined.
- Next Step: Open the first bounded carry scoring design on top of this observable schema.

### JOURNAL-0156

- Date: 2026-03-29
- Author: Codex
- Title: The first bounded carry factor lane now has an explicit score
- Related Decision: DEC-0156
- Hypothesis: Once the carry lane has a row-isolated observable schema, the next useful move is to define a bounded score before any factor pilot or strategy integration is discussed.
- What Changed: Added `carry_scoring_design_v1` and scored the current `carry` rows using a bounded formula over basis advantage, same-exit alignment, carry duration, and realized confirmation.
- Expected Impact: Move the carry lane from field definition into a real factor pilot posture while keeping the lane narrow.
- Observed Result:
  - `design_posture = open_carry_scoring_design_v1`
  - `score_field_name = carry_score_v1`
  - `allow_factor_pilot_next = true`
  - current B/C row scores are identical at `1.0`, which reflects current evidence isomorphism rather than a scoring bug
- Side Effects / Risks: The current score cannot yet discriminate across rows because the available B/C carry evidence is fully symmetric; later pockets may require recalibration or normalization changes.
- Conclusion: `V1.2` now has a real bounded carry factor score, not only a conceptual factor lane.
- Next Step: Open the first carry factor pilot evaluation while keeping strategy integration and retained-feature promotion off.

### JOURNAL-0157

- Date: 2026-03-29
- Author: Codex
- Title: The first carry factor pilot is now open, but only as a report-only micro-pilot
- Related Decision: DEC-0157
- Hypothesis: Once the carry lane has a bounded score, the correct next step is to open a pilot posture without pretending current evidence is already rankable.
- What Changed: Added `carry_factor_pilot_v1` and classified the current carry lane as a report-only micro-pilot.
- Expected Impact: Keep `V1.2` moving while preserving honesty about the current sample limits.
- Observed Result:
  - `pilot_mode = report_only_micro_pilot`
  - `distinct_score_count = 1`
  - `score_dispersion_present = false`
  - `allow_rankable_pilot_now = false`
- Side Effects / Risks: The pilot is now explicitly narrow; until more diverse carry rows appear, this lane will help documentation and future factor design more than immediate ranking behavior.
- Conclusion: The first factor pilot is open, but the repo still does not have enough diversity to treat carry as a rankable factor candidate.
- Next Step: Wait for later batches or new pockets to add carry-row diversity before widening the pilot.

### JOURNAL-0158

- Date: 2026-03-29
- Author: Codex
- Title: The first V1.2 factorization cycle is now closed as a bounded success
- Related Decision: DEC-0158
- Hypothesis: Once one clean factor has moved all the way from registry to pilot, the repo should review whether that is enough to count as a representative factorization result before opening a second lane.
- What Changed: Added `v12_factorization_review_v1` and used it to review the first carry-based factorization cycle.
- Expected Impact: Prevent the repo from widening factor work too early while still recognizing that `V1.2` has already produced a real factorization milestone.
- Observed Result:
  - `acceptance_posture = close_first_v12_factorization_cycle_as_representative_but_bounded`
  - `v12_factorization_milestone_reached = true`
  - `do_open_second_factor_lane_now = false`
  - `recommended_next_posture = hold_second_lane_until_more_diverse_rows_or_new_refresh_batch`
- Side Effects / Risks: The second factor lane remains intentionally closed, so future progress now depends on better row diversity or later refreshed evidence rather than more work on the current carry lane.
- Conclusion: `V1.2` has already crossed its first real factorization milestone without losing bounded-discipline.
- Next Step: Hold the second lane closed until later batches or new row diversity justify widening factor work.

### JOURNAL-0159

- Date: 2026-03-29
- Author: Codex
- Title: V1.2 stays open because factor row diversity is still missing
- Related Decision: DEC-0159
- Hypothesis: After the first bounded factorization cycle closes successfully, the repo still needs one more readiness check to decide whether to close the whole phase or wait for more diverse factor evidence.
- What Changed: Added `v12_phase_readiness_v1` and used it to determine whether `V1.2` should close now.
- Expected Impact: Prevent premature phase closure while also preventing premature opening of a second factor lane.
- Observed Result:
  - `acceptance_posture = keep_v12_open_and_wait_for_new_refresh_batch_or_row_diversity`
  - `ready_to_close_v12_now = false`
  - `do_open_new_refresh_batch_now = true`
  - `recommended_next_posture = prepare_later_refresh_batch_to_add_factor_row_diversity`
- Side Effects / Risks: `V1.2` remains active longer, but the extension is now focused on a very specific bottleneck rather than open-ended factor expansion.
- Conclusion: The first factorization cycle is enough to prove the phase works, but not enough to close the phase.
- Next Step: Design the next refresh batch around factor-row diversity rather than immediately opening a second factor lane.

### JOURNAL-0160

- Date: 2026-03-29
- Author: Codex
- Title: The next refresh is now defined by factor-row diversity rather than generic sample hunger
- Related Decision: DEC-0160
- Hypothesis: Once `V1.2` identifies factor row diversity as the next bottleneck, the next refresh should be designed explicitly against that gap instead of being justified by generic sample growth.
- What Changed: Added `v12_next_refresh_factor_diversity_design_v1` and defined four explicit target diversity dimensions for the next refresh batch.
- Expected Impact: Make the next refresh batch materially more useful for factor work, because it will target the exact row-level gaps currently blocking a rankable carry pilot.
- Observed Result:
  - `design_posture = prepare_refresh_batch_for_factor_row_diversity`
  - `target_count = 4`
  - `row_diversity_gap_confirmed = true`
  - `recommended_next_batch_name = market_research_v3_factor_diversity_seed`
- Side Effects / Risks: The next refresh is now more constrained and may be harder to populate with liquid symbols, but that is preferable to another blind expansion batch.
- Conclusion: The main line has now cleanly transitioned from factorization review into next-refresh targeting.
- Next Step: Prepare the manifest for `market_research_v3_factor_diversity_seed`.

## JOURNAL-0161 market_research_v3_factor_diversity_seed manifest turned green
- I converted the next refresh step from a design note into an executable manifest gate.
- The new seed adds 8 symbols, all new versus the combined `v1 + v2_seed + v2_refresh` base.
- Coverage is now explicit across the four carry-row diversity targets:
  - `basis_spread_diversity`
  - `carry_duration_diversity`
  - `exit_alignment_diversity`
  - `cross_dataset_carry_reuse`
- Result: `reports/analysis/market_research_v3_factor_diversity_seed_manifest_v1.json` now reads `ready_to_bootstrap_market_research_v3_factor_diversity_seed = true`.

## JOURNAL-0162 market_research_v3_factor_diversity_seed became baseline-ready
- I turned the v3 factor-diversity seed into a runnable pack instead of leaving it at manifest status.
- The first parallel attempt exposed a sequencing problem: derived and audit must be rerun after mapping completion for a small seed pack.
- After rerunning in the correct order, the pack audited as `baseline_ready = true`.
- The first suite run now exists in `reports/20260330T005408Z_70e5fe8c_comparison.json`.

## JOURNAL-0163 market_research_v3_factor_diversity_seed entered the specialist map
- After bootstrap and ordered rebuild, the pack audited as `baseline_ready = true`.
- The first suite run showed `mainline_trend_a` as best return/drawdown and `mainline_trend_c` as best capture.
- Six-pack validation kept `buffer_only_012` as the broad stability leader.
- The first new v3 specialist lane is now `2024_q4 / mainline_trend_c`, and `002049` is the top positive capture driver with `pnl_delta = 871.897588` versus `buffer_only_012`.

## JOURNAL-0164: v3 q4 002049 structural check
Date: 2026-03-30

- Reused the existing specialist opening/persistence analyzers instead of creating a new lane-specific acceptance tool.
- `market_v3_factor_diversity_q4_specialist_window_opening_002049_v1.json` confirms a clean specialist-only opening on `2024-11-05`.
- `market_v3_factor_diversity_q4_specialist_window_persistence_002049_v1.json` returns no clean persistence edge in the checked late window.
- Additional staggered openings also appear on `2024-11-27` and `2024-12-18`, but the lane is still best read as opening-led rather than persistence-led.
- This keeps the main risk under control: do not over-interpret `002049` as a carry breakthrough and do not widen the `v3` replay map yet.

## JOURNAL-0165: first v3 lane acceptance
Date: 2026-03-30

- Added a dedicated first-lane acceptance gate for `market_research_v3_factor_diversity_seed / 2024_q4 / mainline_trend_c`.
- `market_v3_q4_first_lane_acceptance_v1.json` confirms that the lane closes as `opening-led not carry breakthrough`.
- This preserves the main V1.2 risk control: `v3` is a factor-row-diversity substrate, but its first active lane does not yet justify widening replay or upgrading the carry lane.

## JOURNAL-0166: bottleneck check after first v3 lane
Date: 2026-03-30

- Added a short phase-level bottleneck check to avoid overreacting to the first `v3` lane.
- `v12_bottleneck_check_v1.json` confirms that the first lane does not change the carry reading and does not reopen lane expansion.
- The right current reading is: `v3` is a live factor-row-diversity substrate, but the primary V1.2 bottleneck still remains missing carry row diversity.

## JOURNAL-0167: V1.2 next-refresh entry
Date: 2026-03-30

- Added a criteria-first next-refresh entry layer after the first `v3` lane closed as opening-led.
- `v12_next_refresh_entry_v1.json` confirms that the next healthy move is to prepare `market_research_v4_carry_row_diversity_refresh`, but not to write a new manifest yet.
- This keeps replay closed while the next refresh rule set is being narrowed.

## JOURNAL-0168: v4 refresh criteria freeze
Date: 2026-03-30

- Added a dedicated criteria layer before writing the `v4` manifest.
- `v12_v4_refresh_criteria_v1.json` keeps the next refresh focused on carry-row diversity and blocks drift into generic sample growth or pure opening-led clone expansion.
- This means the next healthy move is manifest drafting, not more replay.

## JOURNAL-0169: v4 manifest ready
Date: 2026-03-30

- Drafted and audited the first `market_research_v4_carry_row_diversity_refresh` manifest.
- The gate now passes both target coverage and the stricter criteria layer.
- This moves the main line from `v4 criteria-ready` to `v4 manifest-ready`.

## JOURNAL-0170: v4 entered the live research map
Date: 2026-03-30

- Completed the full `v4` bootstrap chain and corrected the earlier path/order issue by rerunning audit and suite sequentially.
- `v4` now audits as `baseline_ready` and has its first suite run.
- After seven-pack validation and `specialist_alpha_analysis_v6`, `v4` is no longer just manifest-ready or bootstrap-ready; it is an active substrate with at least one visible specialist pocket.
- The first visible `v4` pocket is `2024_q2 / mainline_trend_a` under `baseline_expansion_branch`, but replay remains closed for now.
## JOURNAL-0171 2026-03-30
- Replayed `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 601919` and reduced the first active `v4` lane to a single structure question.
- The decisive edge was a clean specialist-only opening into the 2024-05-27 to 2024-05-30 trade; the checked late window did not show persistence.
- This confirms that `v4` is active, but the first visible lane still does not change the current carry-row-diversity bottleneck reading.
## JOURNAL-0172 2026-03-30
- Converted the policy/news catalyst idea into a bounded research method rather than a loose explanation.
- The new branch tests whether catalyst persistence, board pulse breadth, retrace shape, and reacceleration separate opening-led lanes from carry-row-present lanes.
- It is intentionally deferred until it can change a later factor decision rather than becoming a narrative side path.
## JOURNAL-0173 2026-03-30
- Converted the catalyst-persistence idea into a concrete registry schema rather than a loose note.
- The resulting schema now distinguishes source authority, execution strength, rumor risk, reinforcement, consolidation days, and reacceleration shape.
- This gives the repo a bounded way to test whether opening-led lanes fail to become carry-led because the catalyst context itself is too weak or too short-lived.
## JOURNAL-0174 2026-03-30
- Ran the first bounded training pilot using only frozen lane artifacts rather than raw prices or raw messages.
- The leave-one-out nearest-centroid pilot perfectly separated the three current lane classes, which suggests the existing artifact layer already contains usable structure for later bounded ML work.
- This still does not justify promoting ML into strategy integration; it only shows that the current structured lane vocabulary is internally separable.
## JOURNAL-0175 2026-03-30
- Ran a readiness check immediately after the first bounded training pilot to avoid over-reading the perfect micro accuracy.
- The result is useful but disciplined: structure is separable, yet the branch is still too small and too carry-thin to justify a larger model step.
- This preserves the distinction between `can train something bounded` and `should scale the training branch now`.
## JOURNAL-0176 2026-03-30
- Converted the training readiness result into an explicit sample-expansion design and then into a bounded manifest.
- The branch now has a frozen request: keep opening rows flat, add only clean persistence rows, and treat true carry rows as the primary expansion target.
- This prevents the micro pilot from being inflated by relabelling neighboring factor families into the carry class just to make the training branch look richer.
## JOURNAL-0177 2026-03-30
- Turned the new training manifest into an operational binding gate rather than leaving it as a static request list.
- The immediate effect is disciplined: the first `v3` and `v4` opening-led lanes remain structurally useful but are not allowed to enlarge the training sample.
- This keeps the branch focused on the real shortages: clean persistence rows and true carry rows.
## JOURNAL-0178 2026-03-30
- Converted the training manifest and binding gate into a per-lane operational check.
- The immediate result is disciplined: both currently closed first lanes from `v3` and `v4` stay outside the training branch because they are opening-led.
- This leaves the branch in the correct posture: wait for a future clean persistence lane or a future true carry row before expanding the sample.
## JOURNAL-0179 2026-03-30
- Moved the catalyst-persistence branch from schema-only into its first real sample set.
- The branch now has six seeded rows spanning opening, persistence, and carry outcomes, which is enough to begin manual or semi-manual event filling without losing auditability.
- This keeps the catalyst work aligned with the mainline: explain why some lanes stay opening-led before deciding whether catalyst persistence deserves factor relevance.
## JOURNAL-0179 2026-03-30
- Moved the catalyst-persistence branch from schema-only into its first real sample set.
- The branch now has six seeded rows spanning opening, persistence, and carry outcomes, which is enough to begin manual or semi-manual event filling without losing auditability.
- This keeps the catalyst work aligned with the mainline: explain why some lanes stay opening-led before deciding whether catalyst persistence deserves factor relevance.
## JOURNAL-0180 2026-03-30
- Ran the first catalyst event fill without forcing a premature news-ingestion pipeline.
- All six seeded rows now have a bounded market-context layer, which is enough to distinguish theme-scoped versus sector-scoped cases before touching official source provenance.
- This keeps the branch moving while preserving the key boundary: source authority still needs a later manual or semi-manual fill pass.
## JOURNAL-0181 2026-03-30
- Added the first source-level layer to the catalyst branch without forcing fake certainty onto every lane.
- Five rows now carry official or high-trust industry references, while one row stays openly unresolved; this is the right tradeoff for a bounded, auditable branch.
- The catalyst branch is now ready for its first bounded context audit because it has schema, seed, market-context fill, and partial source fill in place.
## JOURNAL-0182 2026-03-30
- Ran the first bounded catalyst-context audit after building the schema, seed, market-context fill, and partial source layer.
- Even with only six rows, the branch now shows a meaningful directional pattern: opening maps to single-pulse context, persistence to multi-day reinforcement, and carry to followthrough context.
- The result is useful but still bounded; it justifies keeping the catalyst branch active, not promoting it.
## JOURNAL-0182 2026-03-30
- Ran the first bounded catalyst-context audit after building the schema, seed, market-context fill, and partial source layer.
- Even with only six rows, the branch now shows a meaningful directional pattern: opening maps to single-pulse context, persistence to multi-day reinforcement, and carry to followthrough context.
- The result is useful but still bounded; it justifies keeping the catalyst branch active, not promoting it.

## JOURNAL-0183 2026-03-30
- Immediately phase-checked the catalyst branch so it would not become a new open-ended refinement loop.
- The branch now has a clear role: contextual support for why opening-led lanes surface before carry-led ones, not a replacement for the main carry-row-diversity work.
- This preserves a clean V1.2 posture while still keeping the catalyst work alive for later decisions.
## JOURNAL-0184 2026-03-30
- Converted the carry-row bottleneck into an explicit hunting strategy rather than leaving the next symbol choice implicit.
- The branch now has a disciplined next move: stay inside `v4`, avoid broad replay, and check a basis-spread candidate before touching more exit-alignment names.
- This is the cleanest way to keep the mainline pointed at true carry-row diversity rather than drifting into another opening-led loop.
### JOURNAL-0185 V1.2 000725 carry-row hunt check
Date: 2026-03-30

Work completed:
- Added a generic `market_v4_q2_symbol_hunt_acceptance` analyzer and runner.
- Replayed `000725` over `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a`.
- Ran full-slice opening and persistence checks for the symbol.
- Wrote `PROJECT_LIMITATION/76_V12_CARRY_ROW_HUNT_000725_V1.md`.

Result:
- `000725` closes as `no_active_structural_lane`.
- The symbol shows zero pnl divergence, no specialist-only opening edge, and no clean persistence edge.
- This means the basis-spread hunt stays inside the current v4 refresh but moves to the next candidate symbol rather than widening replay.

Artifacts:
- `reports/analysis/market_v4_q2_symbol_timeline_000725_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_000725_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_000725_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_000725_v1.json`
### JOURNAL-0186 V1.2 600703 carry-row hunt check
Date: 2026-03-30

Work completed:
- Replayed `600703` over `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a`.
- Ran full-slice opening and persistence checks for the symbol.
- Reused the generic `market_v4_q2_symbol_hunt_acceptance` analyzer with excluded-symbol handling.
- Wrote `PROJECT_LIMITATION/77_V12_CARRY_ROW_HUNT_600703_V1.md`.

Result:
- `600703` closes as `no_active_structural_lane`.
- The symbol shows zero pnl divergence, no specialist-only opening edge, and no clean persistence edge.
- Basis-spread targets are now exhausted inside the current bounded hunt order, so the next symbol should come from `carry_duration_diversity`.

Artifacts:
- `reports/analysis/market_v4_q2_symbol_timeline_600703_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_600703_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_600703_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_600703_v1.json`
### JOURNAL-0187 V1.2 600150 carry-row hunt check
Date: 2026-03-30

Work completed:
- Replayed `600150` over `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a`.
- Ran full-slice opening and persistence checks for the symbol.
- Reused the generic `market_v4_q2_symbol_hunt_acceptance` analyzer with excluded-symbol handling.
- Wrote `PROJECT_LIMITATION/78_V12_CARRY_ROW_HUNT_600150_V1.md`.

Result:
- `600150` closes as `no_active_structural_lane`.
- The symbol shows zero pnl divergence, no specialist-only opening edge, and no clean persistence edge.
- The bounded hunt now shifts to the second `carry_duration_diversity` target, `601127`.

Artifacts:
- `reports/analysis/market_v4_q2_symbol_timeline_600150_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_600150_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_600150_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_600150_v1.json`
### JOURNAL-0188 V1.2 601127 carry-row hunt check
Date: 2026-03-30

Work completed:
- Replayed `601127` over `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a`.
- Ran full-slice opening and persistence checks for the symbol.
- Reused the generic `market_v4_q2_symbol_hunt_acceptance` analyzer with excluded-symbol handling.
- Wrote `PROJECT_LIMITATION/79_V12_CARRY_ROW_HUNT_601127_V1.md`.

Result:
- `601127` closes as `no_active_structural_lane`.
- The symbol shows zero pnl divergence, no specialist-only opening edge, and no clean persistence edge.
- High-priority v4 hunt targets are now exhausted without yielding an active carry-supporting lane, so the next action should be a phase-level check.

Artifacts:
- `reports/analysis/market_v4_q2_symbol_timeline_601127_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_601127_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_601127_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_601127_v1.json`
### JOURNAL-0189 V1.2 v4 q2/A hunt phase check
Date: 2026-03-30

Work completed:
- Added a dedicated `v12_v4_hunt_phase_check_v1` analyzer, runner, config, and test.
- Aggregated the four completed single-symbol hunt acceptances inside `v4 / q2 / A`.
- Wrote `PROJECT_LIMITATION/80_V12_V4_HUNT_PHASE_CHECK_V1.md`.

Result:
- The checked high-priority `basis_spread_diversity` and `carry_duration_diversity` targets are exhausted.
- All checked high-priority hunts closed inactive.
- The correct next posture is to pause before lower-priority tracks and reassess the current v4 hunt posture.

Artifacts:
- `reports/analysis/v12_v4_hunt_phase_check_v1.json`
### JOURNAL-0190 V1.2 v4 reassessment
Date: 2026-03-30

Work completed:
- Added a dedicated `v12_v4_reassessment_v1` analyzer, runner, config, and test.
- Combined the local `v4` hunt phase check with the broader specialist map and existing bottleneck reading.
- Wrote `PROJECT_LIMITATION/81_V12_V4_REASSESSMENT_V1.md`.

Result:
- `v4` remains active as a substrate in the broader specialist map.
- The checked `v4 / q2 / A` high-priority hunt region is locally exhausted.
- The correct next action is no longer local v4 replay, but a higher-level V1.2 batch/substrate decision.

Artifacts:
- `reports/analysis/v12_v4_reassessment_v1.json`
### JOURNAL-0191 V1.2 batch/substrate decision
Date: 2026-03-30

Work completed:
- Added a dedicated `v12_batch_substrate_decision_v1` analyzer, runner, config, and test.
- Combined the phase readiness gate, the `v4` reassessment, and the broader specialist map.
- Wrote `PROJECT_LIMITATION/82_V12_BATCH_SUBSTRATE_DECISION_V1.md`.

Result:
- The next correct V1.2 move is to prepare the next refresh batch.
- The current decision explicitly rejects reopening local `v3` or `v4` replay.
- The mainline returns to refresh preparation because the bottleneck is still carry row diversity.

Artifacts:
- `reports/analysis/v12_batch_substrate_decision_v1.json`
### JOURNAL-0192 V1.2 next refresh entry v2
Date: 2026-03-30

Work completed:
- Added a dedicated `v12_next_refresh_entry_v2` analyzer, runner, config, and test.
- Combined the batch/substrate decision, the training sample manifest, and the catalyst branch phase check.
- Wrote `PROJECT_LIMITATION/83_V12_NEXT_REFRESH_ENTRY_V2.md`.

Result:
- The next executable batch entry is now `market_research_v5_carry_row_diversity_refresh`.
- The next batch posture is fixed as `criteria_first_true_carry_plus_clean_persistence_refresh`.
- Local `v3` and `v4` replay stays closed while the new batch is translated into criteria and a manifest.

Artifacts:
- `reports/analysis/v12_next_refresh_entry_v2.json`
### JOURNAL-0193 V1.2 v5 refresh criteria
Date: 2026-03-30

Work completed:
- Added a dedicated `v12_v5_refresh_criteria_v1` analyzer, runner, config, and test.
- Combined the v5 entry posture, the training sample manifest, and the carry schema.
- Wrote `PROJECT_LIMITATION/84_V12_V5_REFRESH_CRITERIA_V1.md`.

Result:
- `v5` criteria are now frozen.
- The batch is explicitly training-gap-aware rather than a generic carry refresh.
- The next step should be manifest drafting, not more local replay.

Artifacts:
- `reports/analysis/v12_v5_refresh_criteria_v1.json`
### JOURNAL-0194 V1.2 v5 refresh manifest v1
Date: 2026-03-30

Work completed:
- Added a dedicated `v12_v5_refresh_manifest_v1` analyzer, runner, and test.
- Created the combined `v5` reference base file and the new `v5` seed universe file.
- Wrote `PROJECT_LIMITATION/85_MARKET_RESEARCH_V5_CARRY_ROW_DIVERSITY_REFRESH_PLAN.md`.

Result:
- `v5` manifest is ready to bootstrap.
- It stays narrow with `4` new symbols and covers both required training gaps.
- The next healthy move is data bootstrap, not more criteria work.

Artifacts:
- `reports/analysis/market_research_v5_carry_row_diversity_refresh_manifest_v1.json`
- 2026-03-30: Completed the `v5` pack bootstrap chain and moved `market_research_v5_carry_row_diversity_refresh` into the active validation map. The pack is `baseline_ready`, appears in the eight-pack validation report, and enters the specialist geography without yet changing the main `V1.2` bottleneck reading.
- 2026-03-30: Formalized long-horizon autonomy with charter, stop, waiting-state, and cross-phase rules in `PROJECT_LIMITATION/86_LONG_HORIZON_AUTONOMY_POLICY.md`.
- 2026-03-30: `v5` produced its first active lane on `002273 / q2 / B`, but the lane closed as opening-led rather than carry-supporting. `V1.2` therefore stays constrained by the same carry-row-diversity bottleneck.
- 2026-03-30: `v5` exhausted its remaining bounded lanes without producing an acceptance-grade clean persistence row or true carry row. The final probe `000099 / q2 / B` closed as opening-led, and `v12_v5_exhaustion_phase_check_v1.json` fixed `v5` as a bounded-but-non-repairing refresh.
- 2026-03-30: After the exhaustion check, I initialized only the next legal entry: `v12_next_refresh_entry_v3.json` freezes `market_research_v6_catalyst_supported_carry_persistence_refresh` as the next criteria-first batch. Catalyst context is allowed to support symbol selection, but not to replace the carry-row-diversity objective.- 2026-03-30: After `v5` exhausted, I froze `v6` criteria rather than reopening old replay. The new batch keeps training-gap repair primary and uses catalyst context only as bounded support.
- 2026-03-30: `market_research_v6_catalyst_supported_carry_persistence_refresh` is now manifest-ready with `4` new symbols and a clean `2 true carry + 2 clean persistence` split.
- 2026-03-30: The first bounded v6 lane (`600118 / q3 / C`) produced a clean opening edge on 2024-07-22 but no persistence. Follow-on gate work showed no acceptance-grade remaining local v6 candidate, so v6 stays active while local second-lane expansion is held.

- 2026-03-30: `V1.2` now sits in explicit waiting state. The active `v6` substrate did not justify a second local lane, and policy-based review prevented forced branch expansion into `v7`.

- 2026-03-30: `V1.3` opened as bounded catalyst/concept infrastructure rather than as direct signal work. The first concept-focused cycle stayed replay-independent and showed usable context separation with full resolved source coverage on the bounded theme-scope seed.

- 2026-03-30: Concept stock handling in `V1.3` now has explicit confidence rules. Cross-industry concept mappings are no longer treated as flat tags; they are stratified by link mode, source quality, and market confirmation before they can enter bounded context.

- 2026-03-30: `V1.3` now has a consumable concept registry. The important guardrail held: resolved concept rows are usable for bounded context, but still stay provisional until manual symbol-link mode assignment confirms whether they are primary-business, investment-holding, supply-chain, or weaker mappings.

- 2026-03-30: Completed bounded manual symbol-link assignment for the four current concept rows, then reclassified the concept registry. The registry is now proof-backed instead of fully provisional: 3 rows are core_confirmed and 1 row remains market_confirmed_indirect.
- 2026-03-30: Froze bounded concept-registry usage rules. The key boundary held: even proof-backed concept rows stay infrastructure only and cannot integrate into the strategy mainline.
- 2026-03-30: Ran v13_phase_closure_check_v1 and closed V1.3 as bounded context infrastructure success. The phase now enters explicit waiting state rather than widening ingestion or inventing a follow-on branch.
- 2026-03-30: V1.4 is now open. The first lawful move was not a model or replay action, but a context-consumption protocol freeze built on top of V1.3 usage rules and the bounded catalyst audit.
- 2026-03-30: The current V1.4 branch remains replay-independent and report-only. It can now proceed to schema-level context feature work, but it still cannot integrate into the strategy mainline.
- 2026-03-30: V1.4 now has a concrete report-only context feature schema instead of only a protocol. The work is still replay-independent, and the next bounded step is discrimination review rather than model expansion.
- 2026-03-30: V1.4 completed its first full cycle: charter, protocol, report-only context feature schema, bounded discrimination review, phase check, and closure check.
- 2026-03-30: The important result is not promotion, but bounded consumption proof. V1.4 showed that the frozen concept/catalyst infrastructure can be consumed as report-only context with stable directional discrimination, then closed cleanly into waiting state.
- 2026-03-30: `V1.5` is now open. The first lawful move was a candidacy protocol freeze rather than promotion. This keeps the branch aligned with the evidence chain from `V1.4` without skipping straight into retained-feature decisions.
- 2026-03-30: The current `V1.5` branch is review-only. It can now proceed to per-feature admissibility judgments, but it still cannot promote features into the strategy mainline.
- 2026-03-30: `V1.5` completed its first full cycle: charter, candidacy protocol, per-feature admissibility review, phase check, and closure check.
- 2026-03-30: The key result is bounded candidacy sorting rather than promotion. Four context features remain inside provisional candidacy review; one indirectness feature stays on hold for more evidence. The phase closes cleanly into waiting state.
- 2026-03-30: `V1.6` is now open. The first lawful move was a bounded stability-review protocol freeze built on the provisional candidacy outputs of `V1.5`.
- 2026-03-30: The current `V1.6` branch is still review-only. It can now proceed to per-feature stability judgments, but it still cannot promote features or open local-model work.
- 2026-03-30: `V1.6` completed its first full cycle: charter, stability protocol, per-feature stability review, phase check, and closure check.
- 2026-03-30: The important result is bounded stability confirmation rather than promotion. All four provisional candidacy features remain alive under bounded review, and the phase closes cleanly into waiting state.- 2026-03-30: `V1.7 Promotion-Evidence Generation` opened as the first lawful phase after `V1.6` stability review. The branch is explicitly not a promotion phase; it exists to state what evidence is still missing.
- 2026-03-30: Froze `v17_promotion_evidence_protocol_v1.json`. The current bounded protocol tracks four promotion-evidence gaps: sample breadth, cross-pocket or cross-regime support, non-redundancy stress, and safe consumption beyond report-only use.
- 2026-03-30: `V1.7` completed its first full cycle: charter, promotion-evidence protocol, per-feature promotion-gap review, phase check, and closure check.
- 2026-03-30: The key result is explicit promotion shortfall mapping rather than advancement. All four provisional features remain alive, but each still lacks bounded evidence required to change promotion judgment.
- 2026-03-30: `V1.8A` opened as the highest-leverage next phase after `V1.7` because two provisional features share the same primary shortfall: `sample_breadth_gap`.
- 2026-03-30: The first bounded protocol now freezes `single_pulse_support` and `policy_followthrough_support` as the only lawful sample-breadth targets. This keeps the phase narrow and prevents it from sliding into generic replay growth.
- 2026-03-30: `V1.8A` completed its first full cycle: charter, sample-breadth protocol, breadth-entry design, phase check, and closure check.
- 2026-03-30: The key result is lawful breadth-entry specification rather than sample acquisition. Both breadth-target features now have bounded candidate source pools and sample limits, but no sample collection was authorized inside this phase.
- 2026-03-30: `V1.8B` completed its first full cycle: charter, sample admission protocol, per-feature admission gate review, phase check, and closure check.
- 2026-03-30: The key result is bounded admission readiness rather than collection. Both breadth-target features now have explicit lawful gates for future screened collection, but no samples were collected in this phase.
- 2026-03-30: `V1.8C` completed its first full cycle: charter, screened collection protocol, actual screened bounded collection, phase check, and closure check.
- 2026-03-30: This is the first phase in the promotion-evidence branch that produced real new breadth evidence instead of only design or gate artifacts. The collection stayed within frozen pools and sample limits, and still did not trigger promotion.
- 2026-03-30: `V1.9` completed a bounded breadth-evidence re-review cycle.
- 2026-03-30: The important result is not promotion but shortfall refresh. `single_pulse_support` now looks less breadth-starved and more blocked by non-redundancy; `policy_followthrough_support` still needs broader evidence beyond one symbol-family.
- 2026-03-30: `V1.9` therefore closes as bounded breadth-evidence re-review success and now sits in explicit waiting state.
- 2026-03-30: `V1.10A` completed a single cross-family breadth probe for `policy_followthrough_support`.
- 2026-03-30: The important result is a hard negative conclusion rather than a new case: under the current bounded pool, no policy-followthrough candidate survives the cross-family non-redundancy gate beyond the existing `300750` family.
- 2026-03-30: `V1.10A` therefore closes as successful negative probe and now sits in explicit waiting state, with no automatic `V1.10B+`.
- 2026-03-30: Governance was loosened only where it needed to be loosened. The project now explicitly allows exploration-layer outputs that change the future decision basis, while keeping admission, promotion, and strategy-mainline standards tight.
- 2026-03-30: Added a stronger anti-loop governance layer. Future autonomy now must stop if it is only restating the same evidence-pool conclusion under new micro-phase names, and repeated waiting-state outcomes now force a `Solution Shift Memo` instead of more review churn.
- 2026-03-30: `V1.11` completed the first real solution-shift away from same-pool review loops.
- 2026-03-30: The important result is not a new case but a new upstream capability: the project now has a frozen acquisition basis for sustained catalyst evidence instead of relying on ad hoc case scavenging.
- 2026-03-30: `V1.11` therefore closes as sustained acquisition infrastructure success and now sits in explicit waiting state pending owner review of the bounded first pilot.
- 2026-03-30: `V1.11A` completed the first real bounded execution on top of the new acquisition basis.
- 2026-03-30: The important distinction is that the pilot validated the acquisition path without pretending to fix the original feature bottleneck. Two non-anchor candidates were admitted under frozen rules, but direct `policy_followthrough_support` breadth still did not expand beyond the old anchor family.
- 2026-03-30: `V1.11A` therefore closes as bounded first acquisition pilot success and now sits in explicit waiting state. The system has moved from ad hoc case scavenging to reusable acquisition plus one lawful execution cycle.
- 2026-03-30: `V1.12` deliberately changes the unit of progress from “more cases” to “one clean training experiment.”
- 2026-03-30: The important result is not a trained model yet, but a frozen pilot grammar: one carry family, one cycle archetype, one sample unit, one label set, and one validation discipline. This should reduce the chance that later scaling turns into uncontrolled object sprawl.
- 2026-03-30: `V1.12` therefore closes as single price-cycle training definition success and now sits in explicit waiting state pending owner review of bounded pilot data assembly.
- 2026-03-30: `V1.12A` turns that frozen grammar into the first human-correctable pilot sheet instead of jumping straight into fitting.
- 2026-03-30: The important result is a bounded collaboration surface: a small object pool, draft role guesses, empty cycle-window slots, and explicit owner correction fields for missing objects or wrong labels.
- 2026-03-30: `V1.12A` therefore closes as owner-correction-ready pilot data assembly success and now sits in explicit waiting state pending owner edits before any training starts.
- 2026-03-30: The first owner correction has now been absorbed without reopening the whole phase chain.
- 2026-03-30: `300308` now has a concrete multi-stage cycle sketch (first rise, long consolidation, major markup, pullback, rebound), which makes it the first partially resolved benchmark row in the pilot dataset draft.
- 2026-03-30: This confirms the collaboration pattern is working: the system can present a bounded draft, the owner can inject market-grounded corrections, and the draft can evolve without pretending that unresolved rows are already clean enough for training.
- 2026-03-30: The next high-value move after the first owner anchor was not more protocol work, but a price-structure pass on the unresolved symbols.
- 2026-03-30: `300502` and `300394` now have coarse cycle drafts inferred from daily bars and aggregated weekly/monthly structure. They are intentionally calibration-grade, so the owner can correct windows instead of starting from blank rows.
- 2026-03-30: The owner then asked to remove the special handling on `300308` and let it be inferred under the same method as the other two names.
- 2026-03-30: `V1.12A` now has a fully unified calibration draft: all three optical-link symbols carry price-inferred cycle windows, while the old manual `300308` window is preserved only as a comparison baseline.
- 2026-03-30: The owner then accepted the unified draft, so the optical-link pilot crossed from calibration into execution.
- 2026-03-30: `V1.12B` now gives the project its first frozen trainable pilot dataset and first report-only time-split baseline readout. The important change is not the raw score itself, but that the single-cycle training chain is now executable end to end instead of stopping at schemas and review sheets.
- 2026-03-30: The first baseline is intentionally simple and bounded: `2238` daily samples, `carry_constructive / watch_constructive / failed` as the first three carry-outcome classes, and `0.4509` test accuracy from a nearest-centroid readout. This is enough to review labeling, stage boundaries, and training grammar quality without pretending that the system is ready for live deployment.
- 2026-03-30: `V1.12C` turns the first baseline from a score into a diagnosis. The current baseline does not fail uniformly; it is specifically too optimistic in late `major_markup` and `high_level_consolidation`.
- 2026-03-30: This matters because the next black-box comparison now has a precise target. We are no longer asking whether a sidecar model is generically "better"; we are asking whether it reduces optimistic false positives in the exact stages where the first bounded baseline is weak.
- 2026-03-30: The first sidecar protocol is therefore frozen on the same dataset, same labels, and same time split. This keeps the next comparison honest by preventing data-scope drift from masquerading as model improvement.
- 2026-03-30: `V1.12D` then turned that protocol into a real model comparison instead of another planning artifact.
- 2026-03-30: The important result is not merely that a black-box model scored higher. The key signal is that the best sidecar (`hist_gradient_boosting_classifier`) materially reduced the exact optimistic false-positive zones that `V1.12C` highlighted, especially in `high_level_consolidation`.
- 2026-03-30: This is the first place where the project has evidence that a non-linear sidecar may be capturing structure the simple interpretable baseline misses. But it is still only a sidecar result on one bounded pilot dataset, so the correct posture remains review, not deployment.
- 2026-03-30: `V1.12E` then asked the next non-cosmetic question: why did the first sidecar help? The answer is now explicit at block level.
- 2026-03-30: `catalyst_state` is the current main contributor to hotspot control. Removing it does not worsen `major_markup` false positives, but it destroys `high_level_consolidation` control (`1 -> 53` false positives), which means the current sidecar gain is tightly linked to how catalyst-state features interact with late-stage structure.
- 2026-03-30: This changes the next research basis. The project does not most urgently need a larger model family; it more likely needs feature or label refinement around late-stage catalyst persistence and high-level consolidation semantics.
- 2026-03-30: `V1.12F` then forced the next question into one primary cause instead of leaving everything blurred together.
- 2026-03-30: The current answer is now explicit: the immediate bottleneck is not missing samples inside the frozen pilot, and not a simple catalyst-weight problem. It is a `feature_definition_or_non_redundancy_gap`.
- 2026-03-30: The current best refinement path is to enrich `catalyst_state` with freshness, cross-day persistence, and breadth-confirmation semantics before doing any broad label rewrite or new model escalation.
- 2026-03-30: `V1.12G` executed that bounded refinement path instead of jumping to label surgery. Three semantic catalyst-state features were added and the same frozen pilot was rerun end to end.
- 2026-03-30: The important result is not only a small metric lift. The meaningful delta is concentrated in `high_level_consolidation`: even the simple baseline cut optimistic carry false positives from `46` to `34`, while GBDT removed the last remaining one (`1 -> 0`).
- 2026-03-30: This means the project is now isolating a real semantic asset: late-stage catalyst freshness/persistence/breadth context. The next question is no longer whether semantics matter, but whether this delta should stay feature-side only or motivate a bounded label split inside `high_level_consolidation`.
- 2026-03-30: The current subagent question is now narrowed enough to answer precisely. There are lawful repetitive tasks, but only a few, and they must stay additive rather than directive.
- 2026-03-30: The current ready-now subagent work is not "train until something useful appears." It is bounded support exploration: hotspot bucketization and semantic-field ablation on the same frozen pilot.
- 2026-03-30: This is an important governance distinction. Mainline remains the convergence layer; subagents, if used later, will act only as low-cost exploratory bandwidth for repetitive evidence formatting and filtering.
- 2026-03-30: The subagent role was then sharpened further. Exploration alone is too narrow a frame; what the project actually needs is low-governance candidate-structure generation.
- 2026-03-30: The updated posture now distinguishes four lawful subagent task types: exploration, drafting, structuring, and execution. This matters because candidate label-split discovery sits in drafting/structuring, not in formal governance.
- 2026-03-30: A hard review cadence is now frozen alongside this role split. Subagents may produce one bounded batch, then mainline must review before any further batch can begin. This prevents a quiet slide into infinite low-quality experimentation.
- 2026-03-30: That review cadence then needed one more correction: not all batches are alike. Repetitive pipeline work and candidate-structure drafting should not be reviewed on the same rhythm.
- 2026-03-30: The updated rule now distinguishes cadence by task type. `structuring` / `execution` can accumulate to a bounded task-count or time window; `drafting` / `exploration` still require review at a bounded thematic stage. This should preserve throughput without weakening governance.
- 2026-03-30: `V1.12I` then froze the missing review standard. The project now has a fixed rule for deciding whether candidate bucket structures are strong enough to justify bounded label refinement.
- 2026-03-30: This matters because the first subagent structuring output did arrive cleanly. `v112h_hotspot_bucketization_v1.json` shows that the current hotspot misreads can be organized into eight reviewable buckets rather than one undifferentiated error cloud.
- 2026-03-30: The next judgment is therefore sharper: not "should we invent new labels," but "do these candidate structures clear the review gates strongly enough to warrant a bounded label-refinement phase?"
- 2026-03-30: `V1.12J` answered that question with a bounded review judgment rather than a schema change.
- 2026-03-30: The answer is asymmetric. `high_level_consolidation` does show enough structured semantic/error differentiation to justify bounded drafting follow-up. `major_markup` does not; it remains too mixed and should stay on the feature side for now.
- 2026-03-30: This is a good narrowing move. The project does not need to debate generic label refinement anymore. It now only needs to decide whether to open one bounded drafting follow-up inside `high_level_consolidation`.
- 2026-03-30: `V1.12K` then executed that narrow drafting follow-up instead of jumping into formal labels.
- 2026-03-30: The draft now has two directly reviewable candidate substates plus one large mixed stall cluster that still needs inner drafting. This is the right shape: not too abstract, not prematurely formal.
- 2026-03-30: The project now has a concrete review object for `high_level_consolidation`, while still keeping the governance boundary intact. The next decision is no longer whether to split labels broadly; it is whether the mixed stall cluster deserves one more bounded inner-drafting pass.
- 2026-03-30: The first bounded structuring subagent task has now run: hotspot bucketization on `high_level_consolidation` and `major_markup`.
- 2026-03-30: The important outcome is that the hotspot rows are not random noise. They collapse into `8` reviewable buckets, with `4` semantic buckets per stage. This is a usable draft for owner review, not a formal label split.
- 2026-03-30: This validates the subagent role split in practice: repetitive structuring work can be delegated safely, then reviewed in one bounded pass, without letting the subagent decide any formal schema or phase direction.
- 2026-03-30: `V1.12L` then performed the owner-level preserve/reject review on top of the `V1.12K` draft instead of diving straight into inner splitting.
- 2026-03-30: The result is cleaner than the original draft: two candidate substates survive as review-only assets, while the mixed stall cluster is explicitly downgraded to an optional future inner-drafting target.
- 2026-03-30: This is the right stopping point for now. The system is no longer asking whether `high_level_consolidation` deserves any substate structure at all; it now knows exactly which parts are preservable and which part remains mixed.
- 2026-03-30: The owner then explicitly reopened only that mixed stall target, so `V1.12M` ran one bounded inner-drafting pass instead of widening the whole label-refinement problem again.
- 2026-03-30: That pass was useful. The mixed stall cluster is not irreducible noise: it now separates into a recoverable quiet-contraction pocket, a residual-breadth exhaustion pocket, and one still-unresolved residue.
- 2026-03-30: This is another good narrowing step. We now know the unresolved area is smaller than the original mixed cluster, while the two clearer inner candidates can remain frozen as review-only assets.
- 2026-03-30: `V1.12N` then answered the natural next question: do these inner-draft pieces actually improve the frozen pilot if treated as shadow features?
- 2026-03-30: The answer is no. The rerun is flat for both the simple baseline and GBDT. That is a strong negative result, not a disappointment: it means the current inner draft is more useful for understanding than for immediate predictive lift.
- 2026-03-30: This prevents a common mistake. We now know not to over-read the inner draft as a feature promotion candidate just because it looks semantically meaningful.
- 2026-03-30: That negative result justified a clean resource shift instead of more sunk-cost pocket refinement.
- 2026-03-30: `V1.13` therefore reopens the project at a higher-leverage layer: `theme_diffusion_carry` is now the selected next carry family, with three bounded seed archetypes and a schema-first posture.
- 2026-03-30: This is the right reset. The project is no longer asking how to squeeze one more local gain out of `high_level_consolidation`; it is asking how to formalize the A-share carry grammar that likely matters most.
- 2026-03-30: `V1.13A` then freezes the first usable grammar for that line. The project now separates theme-diffusion carry into state, role, strength, and driver layers instead of treating "mainline strength" as one mixed intuition bucket.
- 2026-03-30: This phase also records an important governance distinction: many strong-mainline drivers are still only partially known. They should be searched and drafted as `review-only candidate drivers`, often via subagents, but they should not be legislated into formal schema variables before review.
- 2026-03-30: The first preserved review-only candidates include policy strength, industrial advantage, market tailwind, event resonance, leader height, mid-core confirmation, cross-day breadth diffusion, absorption quality / A-kill suppression, catalyst freshness / reinforcement, and mapping clarity. These now exist as structured review memory instead of loose owner intuition.
- 2026-03-30: `V1.13B` then performs the first narrowing pass on those candidates. This is important because the project no longer needs to carry all ten unknowns as equal hypotheses.
- 2026-03-30: The strongest bounded next-step set is now reduced to four drivers: policy backing, industrial advantage, market regime tailwind, and event resonance. These are the best current explanation layer for why some themes become true mainlines instead of short spikes.
- 2026-03-30: The remaining five candidates still matter, but they now have a lower and cleaner status: review-only support drivers rather than immediate schema-budget claimants. `mapping_clarity_and_tradeable_story` remains preserved but explicitly deferred as a noisy borderline idea.
- 2026-03-30: `V1.13C` then answers the next governance question: how may the strongest driver quartet actually be used?
- 2026-03-30: The answer is deliberately narrow. They may now enter theme-diffusion work only as schema-review context, not as model features, execution variables, or strategy signals. This is the right intermediate layer because it lets the project start using driver language without pretending those drivers are already quantified alpha inputs.
- 2026-03-30: The project is now materially closer to usable archetype review. It has state, role, strength, high-priority drivers, and lawful usage boundaries for those drivers. The next bounded move can therefore shift from "what are the drivers?" to "how do these drivers illuminate specific archetypes?"
- 2026-03-30: `V1.13D` then tests exactly that. The result is positive but not uniform: the grammar is archetype-usable, which is the threshold we needed to clear, but only one seed (`commercial_space_mainline`) is currently clean enough to act as a strong core review asset.
- 2026-03-30: This is a good result. It means the grammar is real, not decorative, but it also means the project should resist the temptation to treat every seed theme as equally mature. `stablecoin_theme_cycle` and `low_altitude_economy_cycle` still carry more driver/role mixing and should remain bounded review assets.
- 2026-03-30: The correct posture after `V1.13D` is therefore discipline, not escalation: preserve the archetype review assets, keep model and execution lines closed, and only reopen if a later owner decision wants to deepen the template line further.
- 2026-03-30: `V1.13E` then opens the first lawful downstream pilot entry for the `theme_diffusion_carry` line.
- 2026-03-30: The project does not jump into training broadly. It chooses the cleanest current seed (`commercial_space_mainline`) and freezes a single-archetype, report-only pilot basis with four label blocks: state, role, strength, and driver-presence review flags.
- 2026-03-30: This is the right bridge toward the ultimate quant goal. The line is no longer only a review grammar; it now has a lawful path into bounded pilot labeling and training, while still keeping execution, signal, and automatic archetype expansion closed.
- 2026-03-30: `V1.13F` then turns that pilot basis into a real draft object pool. This is an important shift because the line is no longer just describable; it is now inspectable. The first commercial-space pool is intentionally tiny and asymmetric: one dense local leader seed, plus two weaker owner-correctable draft objects.
- 2026-03-30: That asymmetry is exactly what we want at this stage. It means the project is not pretending to have a clean truth universe where it does not. The draft is lawful, useful, and still honest about uncertainty.
- 2026-03-30: The correct next move after `V1.13F` is owner correction, not auto-labeling and not training. This keeps the first theme-diffusion pilot anchored in review discipline before it touches downstream fitting.
- 2026-03-30: The owner then clarified something more important than a few object edits: commercial-space should be treated as a major archetype study because it compresses many A-share behaviors into one line. That changes the problem from "which three pilot objects do we freeze?" to "what is the lawful deep-study boundary for this archetype?"
- 2026-03-30: `V1.13G` freezes exactly that boundary. The project now records commercial-space as a multi-wave, hierarchy-rich, decay-and-revival archetype with explicit study dimensions and a split between validated local seeds and broader owner-named candidates.
- 2026-03-30: This is the right intermediate posture. The line becomes deeper without pretending that every named object is already validated or ready for training. The project keeps governance intact while preserving a much richer study surface.
- 2026-03-30: I then lowered the friction on the still-open `V1.13F` owner work by freezing a compact owner review guide. That matters because otherwise the draft object pool remains technically correct but operationally annoying. The guide now says, in plain Chinese terms, what each of the three first pilot objects currently is and what the owner actually needs to correct.
- 2026-03-30: The owner then reprioritized again: commercial-space remains valuable, but `CPO / optical-link` should be eaten through first. The correct response was not to reopen the exhausted `high_level_consolidation` pocket. Instead, the line was lifted from a finished three-symbol pilot into `V1.12O Optical-Link Deep Archetype Scope`.
- 2026-03-30: `V1.12O` preserves the original three trainable anchors (`300308 / 300502 / 300394`) while recording a bounded adjacent review-only cohort (`002281 / 603083 / 688205 / 301205 / 300620 / 300548`). This is the right altitude change: stop burning time inside an exhausted pocket, but keep CPO as the current high-value earnings-transmission mainline.
- 2026-03-30: The next frontier for the CPO line is now explicit and above-board: not more stall splitting, but lawful adjacent-candidate validation or bounded cohort-widening review.
- 2026-03-30: `V1.12P` then widened the CPO line from a deep-study archetype scope into a true full-cycle information registry. The project now preserves `20` names across core, direct-related, extension, and mixed-relevance tiers, plus `6` distinct information layers covering catalysts, earnings, technology chain, price structure, liquidity/sentiment, and spillover noise.
- 2026-03-30: This is intentionally not a purity move. It is an omission-control move: some weak or noisy rows are preserved on purpose so later factor work can test whether they matter, instead of losing them before review.
- 2026-03-30: The next discussion now has a clean basis. The registry already shows where the line is still thin: full daily concept-index turnover history, official-report anchors for the whole adjacent cohort, a normalized future-catalyst calendar, and truth-checking on mixed-relevance spillover rows.

## 2026-03-30 V1.12Q CPO registry schema hardening
- Built a harder CPO information-registry schema because omission risk was becoming more important than incremental object discovery.
- The schema now starts before the visible markup window via `pre_ignition_watch` and keeps separate layers for technical path, catalysts, earnings, price/technical structure, role/cohort, branch extension, liquidity, noise, and stage attachment.
- First bounded parallel collection drafts were preserved as review-only memory instead of being left in conversational context.

## 2026-03-30 V1.12R adjacent cohort validation
- The CPO adjacent pool is now less ambiguous: some rows are clean enough to preserve as review assets, while several others are clearly blocked by role-coarseness rather than pure lack of information.
- This pass confirmed that object-pool cleaning should precede chronology normalization and spillover truth-check.

## 2026-03-30 V1.12S CPO chronology normalization
- The chronology layer is no longer a flat list of conferences and earnings dates.
- It now explicitly separates pre-event watch, event window, post-event follow-through, quiet dead zones, pre-earnings drift, post-earnings reset, and the main lag structures that matter for CPO cycle reading.

## 2026-03-30 V1.12T CPO spillover truth-check
- The CPO line now has a cleaner answer to the hardest omission-control question: noisy spillover rows are not being deleted, but they are no longer mixed with cleaner adjacent assets.
- This matters because some of these rows may later become A-share-specific spillover factors, while others are better remembered as weaker board-follow or name-bonus phenomena.
- With adjacent validation, chronology normalization, and spillover truth-check now all completed, the CPO foundation is much closer to research-ready than to training-ready.

## 2026-03-30 V1.12U CPO foundation completeness and research-readiness review
- The project now has an explicit readiness boundary for the CPO line instead of an intuitive one.
- The right reading is not that the information foundation is complete in some absolute sense; the right reading is that it is structured enough for bounded research and still below the threshold for formal training.
- This matters because future work can now move forward without pretending that registry completeness automatically implies trainability.

## 2026-03-30 V1.12V CPO daily board chronology operationalization
- The board chronology gap is no longer only a sentence in a readiness review.
- The project now has a concrete operational target for what a day-level board chronology table should look like, how missingness should be recorded, and which source classes should be trusted first.
- This is still not a full data backfill, but it sharply reduces ambiguity around what the next collection layer should build.

## 2026-03-30 V1.12W CPO future catalyst calendar operationalization
- The future catalyst gap is no longer just a pile of useful dates and source links.
- The project now has a recurring calendar target with cadence buckets, forward window fields, confidence tiers, and explicit missingness handling.
- This still does not create trigger logic, but it makes later forward-timing review much less ambiguous.

## 2026-03-30 V1.12X CPO spillover sidecar probe
- The spillover layer is no longer trapped between two bad options: either treat it as meaningless noise or over-promote it into formal factors.
- A bounded sidecar-style probe is the right altitude here. It keeps two rows alive as A-share-specific factor candidates while explicitly leaving one row as weak memory only.
- This sharpens the residual ambiguity in the CPO foundation without pretending that sidecar evidence equals trainable truth.

## 2026-03-30 V1.12Y CPO adjacent role-split sidecar probe
- The adjacent unresolved bucket is now much less blunt. Instead of nine rows all being equally pending, most of them now carry explicit review-only split suggestions.
- This is exactly where a bounded sidecar helps: it reduces structural ambiguity without pretending to create final truth.
- The remaining ambiguity is now concentrated in a small residual set rather than spread across the whole adjacent layer.

## 2026-03-30 V1.12Z CPO bounded cycle reconstruction entry
- The CPO line has now crossed from “foundation hardening” into “bounded experiment setup.”
- This is the right place to move. Further desk cleaning would have produced diminishing returns, while the remaining high-value questions now require reconstruction-style exposure.
- The key guardrail is preserved: the experiment is ambiguity-preserving and still does not open training.
## 2026-03-30 CPO process-record consolidation
- I consolidated the whole `V1.12P -> V1.12Z` CPO chain into one reusable process record for paper writing and later sector transfer.
- The record explicitly preserves the ordering of:
  - registry construction
  - schema hardening
  - adjacent / chronology / spillover cleaning
  - readiness boundary freezing
  - operational gap reduction
  - sidecar disambiguation
  - subagent challenge
  - lawful experiment entry
- This should reduce the chance that future sector studies skip omission control and jump too early from partial information into training.

## 2026-03-30 V1.12Z operational charter hardening
- I froze an operational charter on top of `V1.12Z` so the next work is judged by the right success criteria.
- The key shift is that cycle absorption is now the primary objective, not early factor neatness.
- The execution stack is now explicit:
  - black-box discovers
  - white-box constrains
  - narrative validates
- This should prevent the line from sliding into one of two bad regimes:
  - over-cleaned but under-absorbed research
  - strong black-box fit without owner-facing understanding

## 2026-03-30 V1.12Z report-only model payoff probe
- I ran the first payoff-oriented comparison on the frozen optical-link pilot instead of relying only on classification accuracy.
- The important result is not just that the primary black-box (`GBDT`) scored higher. It also showed better bounded trade-quality characteristics than the guardrail baseline:
  - higher hit rate
  - shallower average drawdown
  - much stronger profit factor
- This strengthens the working hypothesis that black-box discovery should lead the next cycle-absorption work, while white-box remains the audit rail.

## 2026-03-30 V1.12Z bounded cycle reconstruction pass
- This was the first point where the cleaned CPO information layers became a full owner-facing cycle narrative rather than only a registry plus a few probes.
- The reconstruction makes the cycle readable as multiple waves with explicit role transitions:
  - leader / high-beta core / upstream platform
  - adjacent challengers and domestic optics bridges
  - branch extensions
  - late-cycle spillover and weak name-bonus memory
- The most important negative discipline is intact: I did not delete the remaining ambiguity just to make the cycle look cleaner. The pending adjacent rows and operational gaps remain visible.
- This is a meaningful threshold: the line is now explainable enough for bounded downstream review, but still not clean enough to claim automatic training rights.

## 2026-03-30 V1.12AA CPO bounded cohort map
- This phase turns the reconstruction narrative into a downstream-safe skeleton.
- The most valuable part is not the count of rows; it is the fact that each object now has:
  - a cohort layer
  - a role family
  - bounded stage windows
  - evidence axes
  - a current posture
- That should reduce the biggest downstream risk: writing mixed or spillover objects into formal labels too early.
- The map also confirms that not all non-core rows should be treated equally:
  - some are secondary review assets
  - some are branch or maturity assets
  - some are spillover overlays
  - some still need to remain pending

## 2026-03-30 V1.12AB CPO bounded labeling review
- This phase turns cohort structure into label-surface discipline without pretending labels are already final.
- The most important result is not the counts; it is the explicit separation between:
  - rows that may later carry label truth
  - rows that may only support review
  - rows that should stay as overlay signals
  - rows that still must remain excluded
- That should make the eventual label-draft step much safer and should reduce the chance that spillover or unresolved rows leak into formal truth.

## 2026-03-30 V1.12AC CPO unsupervised role-challenge probe
- This phase was deliberately not allowed to become a replacement for the cohort map.
- The useful result is exactly the tension we wanted:
  - part of the manual role grammar is supported by latent structure
  - part of it is challenged
- The strongest supportive finding is the quiet-window pending pocket:
  - `300620 / 300548 / 000988`
- The strongest challenging findings are:
  - late-cycle extension vs spillover mixing
  - core rows vs advanced-component branch rows mixing during strong markup windows
- That means the current manual map is not fake, but it is also not the last word.
- The correct use of this phase is:
  - keep the manual map as governed truth
  - keep the challenger output as review-only candidate structure

## 2026-03-30 V1.12AD CPO dynamic role-transition feature review
- This phase upgrades the role language from static classification to stage-conditioned migration.
- The most important gain is not count inflation; it is that the system can now represent:
  - role persistence
  - challenger activation
  - role demotion
  - route-depth upgrade
  - requalification after quiet windows
  - late spillover saturation
  - residual core vs spillover collapse
- This is the right response to a real market fact:
  - the same row can be leader-like in one window and much less important in another
  - the same row can be branch or spillover in one window and gain strategic relevance in another
- These dynamic features remain review-only, which is correct at this stage.

## 2026-03-30 V1.12AE CPO feature-brainstorm integration
- I used a bounded first batch of explorer-style brainstorms instead of letting “more feature ideas” stay as loose chat content.
- The integrated shortlist clearly points at three under-built regions:
  - chronology time geometry
  - role handoff and vacancy
  - weak-cohort migration / late-cycle false diffusion
- The strongest new candidates are not generic “better alpha factors”; they are structural missing pieces in the current CPO grammar.
- The batch also surfaced real blind spots that should stay explicit:
  - breadth formula is still not frozen
  - turnover normalization is still not frozen
  - name/alias/concept-tag structure is still missing
  - some A-share microstructure layer is still missing

## 2026-03-30 V1.12AF CPO feature-family design review
- This phase turns a brainstorm list into a governed design layer.
- The most important gain is not more feature names. The gain is that the strongest candidates now have:
  - point-in-time definitions
  - allowed input bundles
  - duplicate guards
  - anti-leakage rules
  - explicit allowed surfaces
- The current family layout is already informative:
  - chronology geometry
  - catalyst sequence
  - dynamic role handoff
  - board concentration divergence
  - spillover maturity
  - overlay boundary
- This should make the next label-draft step materially safer because the system no longer needs to consume raw brainstorm nouns.

## 2026-03-30 V1.12AG CPO bounded label-draft assembly
- The key move here is not "writing labels faster." It is checking whether label language is actually supportable by the current cohort, role, chronology, and feature-family structure.
- The most valuable outputs are:
  - the family-support matrix
  - the anti-leakage posture review
  - the ambiguity-preservation layer
- The draft is intentionally uneven in places:
  - some labels are supportable now
  - some need provisional vs confirmed posture
  - some remain review-only
- This is a good sign because it means the draft is preserving uncertainty instead of hiding it.

## 2026-03-30 V1.12AH factor candidate preservation rule
- This rule exists because the current danger is no longer "too few ideas." The danger is "cleaning away weak-looking ideas before bounded experiments have a chance to test them."
- The important distinction is:
  - not every candidate deserves promotion
  - but many candidates still deserve memory, archive, or later re-check status
- This should protect A-share specific structures that first appear as noisy spillover, late-cycle overlays, weak board-follow, or awkward adjacent roles.

## 2026-03-30 V1.12AI CPO label-draft integrity owner review
- This pass is useful because it translates the integrity draft into a bounded owner disposition map instead of leaving the next step ambiguous.
- The strongest result is not that some labels are ready. The strongest result is that nothing useful had to be thrown away to get a workable downstream subset.
- The downstream lesson is clear:
- use the ready and guarded labels next
- keep branch-upgrade and residual-collapse language out of ex-ante dataset truth

## 2026-03-30 V1.12AJ CPO bounded label-draft dataset assembly
- This pass is the first point where the label language becomes dataset-shaped without pretending it is trainable truth.
- The most important split is not row count. It is:
  - truth-candidate rows
  - context-only rows
- That split keeps support, overlay, and pending structure alive without letting them contaminate the truth layer.

## 2026-03-30 V1.12AK CPO bounded feature binding review
- This pass matters because global label admission can create a false sense of readiness.
- The key discovery is that the current truth-candidate geometry is still narrower than the globally admitted label bundle.
- That is a good result, not a bad one. It means row-level usability is now explicit before any training-readiness claim.

## 2026-03-30 V1.12AL CPO bounded training readiness review
- This phase is valuable because it stops two failure modes at once:
  - endless pre-pilot auditing
  - premature training optimism
- The important split is now explicit:
  - a tiny core-skeleton pilot may be lawful
  - broader representative training is still not lawful
- The current limiting factor is not the existence of labels alone.
- The main bottleneck is implementation maturity:
  - board-series operational rules are not fully frozen
  - recurring catalyst-calendar rules are not fully frozen
- Row geometry is the next bottleneck because quiet-window and spillover truth surfaces are still outside the current truth set.

## 2026-03-30 V1.12AM CPO extremely small core-skeleton training pilot
- This phase is important because it converts the readiness conclusion into bounded failure exposure instead of one more audit layer.
- The strongest result is not just that the pilot ran. The strongest result is that `GBDT` learned the current skeleton materially better than the guardrail:
  - `phase_progression_label`: `0.6265 -> 1.0000`
  - `role_state_label`: `0.4784 -> 0.7377`
  - `catalyst_sequence_label`: `0.6265 -> 1.0000`
- The phase model also improved the small constructive-stage payoff side reading:
  - guardrail predicted constructive phase avg forward return: `0.0626`
  - `GBDT`: `0.0891`
- This still does **not** imply broad training readiness.
- The right interpretation is narrower:
  - the current core skeleton is learnable
  - the project now has real experimental evidence
  - broader representativeness and implementation maturity are still open questions

## 2026-03-30 V1.12AN CPO core-skeleton pilot result review
- This phase matters because it stops the team from over-celebrating the first tiny pilot.
- The main finding is sharp:
  - `phase_progression_label` and `catalyst_sequence_label` are being learned mostly through the current `catalyst_presence_proxy`
  - they are not yet proving that chronology geometry is fully doing the heavy lifting
- That is not a failure, but it is a warning:
  - the tiny pilot currently learns more from an explicit stage-aligned catalyst proxy than from richer timing geometry
- `role_state_label` remains the hardest layer, and the confusion is concentrated in the secondary high-beta extension cluster:
  - `603083`
  - `688205`
  - `301205`
- This indicates the next real choice is not "more generic review." It is:
  - widen the pilot carefully
  - or patch the role layer before widening

## 2026-03-30 V1.12AO CPO role-layer patch pilot
- This phase matters because it answers the most immediate post-pilot question with an experiment instead of another audit layer.
- The key result is not only that `role_state` improved.
- The key result is that it improved **without widening the pilot geometry**.
- The strongest patch signal comes from:
  - market microstructure
  - limit-regime differences
  - short-horizon behavior signatures
- This is a useful warning as well as a win:
  - the current role layer is partly an A-share structure problem, not just a pure business-role problem
- That means later widening should test whether this gain survives beyond the current tiny row set.

## 2026-03-30 V1.12AP CPO bounded secondary widen pilot
- This phase matters because it tests whether the patched core skeleton survives one lawful widen step before any broader training claim.
- The widen is intentionally narrow:
  - same `7` truth rows
  - same core targets
  - only `3` guarded targets added on lawful subsets
- The strongest result is that the widen did **not** collapse the core layer.
- All guarded targets were learnable, and `role_transition_label` produced the largest gain.
- That is useful, but still not the same as broad readiness.
- The next real question shifts back to:
  - is the main bottleneck now feature implementation,
  - or is row geometry already the limiting factor for the next widen?

## 2026-03-30 V1.12AQ CPO feature implementation patch review
- This phase matters because it prevents the project from widening geometry just because the first guarded widen survived.
- The strongest result is not the number of gaps. The strongest result is the ordering:
  - implementation remains the narrowest lawful aperture
  - geometry remains important, but should wait
- That is useful because it keeps the next experiment interpretable:
  - if the project widens rows too early, it will not know whether later failures come from geometry or from unfinished implementation rules

## 2026-03-30 V1.12AR CPO feature implementation patch spec freeze
- This phase matters because it turns implementation ambiguity into a bounded and auditable patch set.
- The strongest result is not "more documentation." The strongest result is that the project now has a concrete next move:
  - bounded implementation backfill on the current truth rows
- This keeps the workflow out of two traps at once:
  - infinite readiness review
  - premature row-geometry widen

## 2026-03-30 V1.12AS CPO bounded implementation backfill
- This phase matters because it converts the frozen patch rules into explicit sample-level fields on the current truth rows.
- The strongest result is not the sample count. The strongest result is that implementation ambiguity is no longer an abstract excuse on the current row set.
- After this phase, if a rerun still fails or plateaus, the project can attribute that more confidently to geometry or mechanism limits rather than unfinished board/calendar implementation.

## 2026-03-30 V1.12AT CPO post-patch rerun
- This phase matters because it refuses to assume that explicit implementation backfill automatically creates model gains.
- The strongest result is actually the absence of new `GBDT` gain on the current tiny row set.
- That absence is informative:
  - implementation is no longer the hidden reason to avoid the next step
  - the next live uncertainty is now row geometry, not unfinished board/calendar rules
- This is exactly the kind of bounded experiment that prevents infinite audit drift.

## 2026-03-30 V1.12AU CPO bounded row-geometry widen pilot
- This phase matters because it converts row geometry from a theory question into a real failure-exposure question.
- The strongest result is not that the widen "mostly worked."
- The strongest result is that branch-row admission broke `role_state_label` while leaving the guarded layer intact.
- That is useful because it localizes the next problem:
  - not implementation
  - not generic training readiness
  - specifically branch-role geometry
- This is the right kind of failure: narrow, interpretable, and actionable.

## 2026-03-30 V1.12AV CPO branch role geometry patch pilot
- This phase matters because it tests whether the `V1.12AU` branch-row failure was a dead end or a patchable geometry issue.
- The strongest result is not just that `role_state` improved again.
- The strongest result is that widened geometry recovered without reopening the whole system.
- That means the branch layer is not globally untrainable; it was missing a local geometry description.

## 2026-03-30 V1.12AW CPO branch guarded admission review
- This phase matters because it converts a successful local patch into an explicit admissibility split.
- The strongest result is not that branch rows are now "all fixed."
- The strongest result is that the project can admit some branch rows into guarded context while keeping the mixed connector/MPO branch out.
- That keeps the next experiment narrower and more interpretable than a blunt all-branch widen.

## 2026-03-30 V1.12AX CPO guarded branch-admitted pilot
- This phase matters because it tests the `V1.12AW` admissibility decision under real bounded pilot conditions.
- The strongest result is not the extra row count.
- The strongest result is that the admitted branch subset can be tested without recreating the earlier branch-role collapse.
- That means branch admission can now be discussed at the next bounded layer without pretending the whole branch space is solved.

## 2026-03-30 V1.12AY CPO guarded branch training-layer review
- This phase matters because it separates "can be tested in a bounded pilot" from "can enter the next training-facing layer."
- The strongest result is that the same three branch rows survive this second cut without reopening the mixed connector/MPO branch.
- That keeps the next move narrow and lawful instead of turning into a generic branch expansion.

## 2026-03-30 V1.12AZ CPO bounded training layer extension
- This phase matters because it turns the branch training-layer review into a concrete training-layer asset.
- The strongest result is not just a bigger row count.
- The strongest result is that the project now has a single 10-row bounded layer instead of juggling a 7-row baseline plus separate guarded branch notes.
- That makes the next readiness question sharper: can this 10-row layer replace the old 7-row baseline for the next bounded pilot?

## 2026-03-30 V1.12BA CPO 10-row layer replacement review
- This phase matters because it eliminates a lingering fork in the workflow.
- The strongest result is that the project now has one explicit default bounded layer for the next pilot instead of two competing baselines.
- That removes a large source of future ambiguity without opening formal training.

## 2026-03-30 V1.12BB CPO default 10-row guarded-layer pilot
- This phase matters because it converts the new default layer from a governance decision into a real experimental baseline.
- The strongest result is not a new jump in score.
- The strongest result is that the `10`-row guarded layer now behaves as a stable default baseline against both:
  - the old `7`-row core baseline
  - the earlier guarded-branch pilot
- That means later widen decisions can be judged against one bounded baseline instead of a forked setup.

## 2026-03-30 V1.12BC CPO portfolio objective protocol
- This phase matters because the project is now close enough to portfolio experimentation that objective leakage would become a real risk.
- The strongest result is not more model freedom.
- The strongest result is the hard separation between:
  - hindsight upper-bound benchmarking
  - no-leak aggressive experimentation
  - no-leak neutral/selective experimentation
- That separation protects later portfolio tests from quietly inheriting oracle logic.

## 2026-03-30 V1.12BD market regime overlay feature review
- This phase matters because broad-market and board-style context clearly matter, but they should not overwrite stock-level cycle truth.
- The strongest result is not the feature count.
- The strongest result is that the project now has a lawful overlay family that can amplify or suppress interpretation without flattening the CPO grammar into market beta.

## 2026-03-30 V1.12BE CPO oracle upper-bound benchmark
- This phase matters because it converts the frozen portfolio protocol into the first real portfolio line.
- The strongest result is not the giant hindsight return by itself.
- The strongest result is that the project now has an explicit upper-bound benchmark built on the same lawful 10-row CPO layer that later no-leak tracks will use.
- That makes future portfolio comparison much cleaner than comparing no-leak models against an undefined idea of "what could have happened."

## 2026-03-30 V1.12BF CPO aggressive no-leak black-box portfolio pilot
- This phase matters because it converts the portfolio protocol from a benchmark-only setup into a real no-leak comparison.
- The strongest result is not that the aggressive line already looks good enough.
- The strongest result is that the project now has a measurable no-leak gap:
  - return gap versus oracle
  - drawdown gap versus oracle
- That means later work can stop arguing abstractly about missing factors and start asking which missing mechanisms explain the specific gap.

## 2026-03-30 V1.12BG CPO oracle-vs-no-leak gap review
- This phase matters because the project now has two explicit portfolio lines, so the next improvement should come from bottleneck attribution rather than generic model expansion.
- The strongest result is that the current gap is now framed as:
  - risk-control failure
  - stage-maturity filtering failure
  - not just missing factor coverage
- That lets the next track change objective posture instead of simply chasing more aggressive fitting.

## 2026-03-30 V1.12BH CPO neutral selective no-leak portfolio pilot
- This phase matters because it proves the project can build a second no-leak line with a different objective without violating the same lawful layer.
- The strongest result is not only lower drawdown.
- The strongest result is that the neutral line improves:
  - total return
  - max drawdown
  - profit factor
  relative to the first aggressive track, while holding cash most of the time.
- That means the research system is beginning to translate cycle understanding into distinct portfolio behaviors rather than a single monolithic predictor.

## 2026-03-30 V1.12BI CPO cross-sectional ranker pilot
- This phase matters because it tests whether the portfolio problem is better framed as direct cross-sectional ordering than as classifier-style winner detection.
- The strongest result is not that ranking beats everything.
- The strongest result is that ranking improves versus the aggressive no-leak line while still failing to beat the current neutral selective line.
- That means target-function alignment matters, but participation discipline still matters more than switching from classification to ranking alone.

## 2026-03-30 V1.12BJ CPO neutral teacher gate pilot
- This phase matters because the current strongest no-leak line is the neutral selective track, so it is tempting to assume that its discipline can simply be learned as a second-layer gate.
- The strongest result is not any return number.
- The strongest result is that the naive teacher-gate imitation collapses to all-cash behavior.
- That means the neutral line's edge is more structured and sparse than a straightforward top-candidate gate imitation can recover.

## 2026-03-30 V1.12BK CPO tree/ranker search
- This phase matters because it tests whether a cheap tree/ranker model zoo can beat the current neutral selective baseline without reopening leak or deployment risk.
- The strongest result is not that random forest makes more money.
- The strongest result is that the best tree variant improves return but still fails the drawdown guard relative to the neutral selective line.
- That means the neutral line remains the best current no-leak behavior, even though tree/ranker search is now a useful comparison branch.

## 2026-03-31 V1.12CH packaging mainline template freeze
- This phase matters because the project finally has one control template that is no longer merely exploratory.
- The strongest result is not just that `packaging_process_enabler` worked on one realized path.
- The strongest result is that three different checks now agree:
  - realized-path improvement
  - broader family validation improvement
  - no path distortion after refinement
- That makes `packaging_process_enabler` the first cluster mainline refined template asset rather than another temporary successful branch.

### JOURNAL-0195 Board-level world model plus execution feedback becomes the new main learning posture

- Date: 2026-04-01
- Author: Codex
- Title: Stop treating structure research and execution replay as separate universes
- Related Decision: DEC-0195
- Related Runs: V113I, V113J, V113K, V113L, V113M, V113N, V113V
- Protocol Version: protocol_v1.13
- Hypothesis: The project had reached the point where more structure-only refinement would add less value than wiring board-level structure into a replay environment that can impose actual action consequences.
- What Changed: Formalized the split of responsibilities: owner labels the board truth, assistant labels internal structure, early batch board research becomes a world-model prior layer, and execution replay becomes the place where research language must pay cost and prove usefulness.
- Expected Impact: Reduce drift toward elegant but consequence-free research loops and keep the system learning from board structure without collapsing into single-symbol overfit.
- Observed Result: The architecture now has the right layers to support this posture: no-leak board schema, CPO world-model mapping, populated board episodes, execution main feed, and full-board replay.
- Side Effects / Risks: Board-level labels remain powerful and can still create narrative comfort if they stop being audited by replay and future out-of-regime checks.
- Conclusion: The project should continue learning mainly at the board-state level, but it should no longer let execution remain a downstream afterthought.
- Next Step: Use replay to judge which structure improvements actually change expression, add/reduce behavior, or risk containment.

### JOURNAL-0196 Under-exposure diagnosis reframes the next phase from “better structure” to “better expression”

- Date: 2026-04-01
- Author: Codex
- Title: The first real replay showed that the main bottleneck is under-exposure, not primary stock selection failure
- Related Decision: DEC-0196
- Related Runs: V113W, V113X, V113Y, V113Z, V114A, V114B, V114C, V114D
- Protocol Version: protocol_v1.13
- Hypothesis: If the system’s main weakness is low expression rather than poor object choice, then upgrading sizing, add, and reduce behavior should improve curve capture more directly than adding yet another stock-logic branch.
- What Changed: Replaced the old “gate everything harder” posture with a new stack:
  - hard veto only for truly invalid states
  - soft sizing for valid-but-uncertain states
  - probability/expectancy before risk caps
  - constrained add/reduce learning instead of binary exposure changes
  - structural batch search instead of random parameter probing
- Expected Impact: Improve board capture without reopening already-frozen selection logic or pretending the system needs a brand-new stock picker.
- Observed Result: The local frontier now exists. Stable-zone representatives consistently beat the original replay baseline, and the `expectancy_max_injection` representative became the default candidate:
  - baseline: `1.8401 / 0.1347`
  - default stable-zone candidate: `2.3083 / 0.1853`
- Side Effects / Risks: The stronger expression layer raises drawdown and therefore must keep respecting hard-veto semantics and future cross-environment audits.
- Conclusion: The project has now moved from “can it identify the right structure?” to “can it express that structure with enough size without becoming reckless?”
- Next Step: Promote the default stable-zone sizing candidate into the next replay phase and then audit it across longer windows and harsher environments instead of endlessly re-searching the same local neighborhood.

### JOURNAL-0197 Unsupervised discovery is upgraded from cluster hunting to candidate-state auditing for expression settlement

- Date: 2026-04-01
- Author: Codex
- Title: Keep the vector line, but stop letting attractive discovery drift into half-legislated action structure
- Related Decision: DEC-0197
- Related Runs: V113X, V113Y, V113Z, V114A, V114B, V114C, V114D
- Protocol Version: protocol_v1.13
- Hypothesis: Unsupervised vectors are still useful, but only if the project stops treating high-dimensional discovery as inherently actionable. The next useful role for unsupervised work is to surface candidate states that can materially improve sizing, add, reduce, and under-exposure correction.
- What Changed: Reframed the vector lane around five active target objects:
  - market-voice states
  - strategy-position joint states
  - board-internal relative structure
  - interference / false-signal structure
  - state transitions
  Also preserved one optional follow-on extension:
  - benchmark-relative residual states
  State-transition vectors were moved into the active set because expression upgrades after V113X/V114C now depend heavily on whether the system can identify accelerating, exhausting, or rolling-over states rather than only classify static conditions.
  At the same time, added four mandatory audit gates before any discovered structure may influence action:
  - stability
  - action relevance
  - boundary clarity
  - incremental value
  Also made one methodological correction explicit: this lane must allow continuous bands and transition manifolds, not just hard clusters.
- Expected Impact: Increase the chance that unsupervised work produces real expression improvements instead of only more elegant descriptions.
- Observed Result: The project now has a much clearer standard for what counts as a valuable unsupervised output: not “interesting geometry,” but candidate state information that survives audit and changes replay behavior for the better.
- Side Effects / Risks: Promotion will slow down because more discoveries will remain candidate-only for longer. This is desirable at the current stage because CPO is structurally rich but not repeatable enough to tolerate casual over-promotion.
- Conclusion: The vector lane remains valuable, but only as a disciplined discovery-and-audit tool for expression settlement, not as a parallel truth system.
- Next Step: Start with the five active vector families, and treat state-transition vectors as a first-class candidate-state lane for add/reduce and high-expression timing. Only benchmark-residual vectors remain as a secondary extension.

### JOURNAL-0198 Default sizing promotion freezes the first replay-worthy expression surface

- Date: 2026-04-01
- Author: Codex
- Title: Stop re-searching the same local neighborhood and promote the replay-validated stable-zone winner
- Related Decision: DEC-0198
- Related Runs: V114A, V114B, V114C, V114D, V114E
- Protocol Version: protocol_v1.13
- Hypothesis: The project had already learned enough about the CPO sizing frontier to stop treating every good point as temporary. The next useful step was not more local search, but freezing the best replay-validated stable-zone representative as the default expression surface.
- What Changed: Promoted `expectancy_max_injection` from a candidate stable-zone representative into the default probability-expectancy sizing candidate. The promoted default is:
  - `strong_board_uplift = 0.04`
  - `under_exposure_floor = 0.25`
  - `de-risk_keep_fraction = 0.50`
  This keeps hard-veto semantics intact and only changes the expression layer.
- Expected Impact: Replace chronic under-exposure with a lawful stronger default posture, while giving the replay stack a stable sizing reference for future audits.
- Observed Result: The promoted default remains the strongest replay-validated candidate from the stable zone:
  - baseline: `1.8401 / 0.1347`
  - promoted default: `2.3083 / 0.1853`
  It increases curve and capture materially while keeping drawdown below the soft 0.20 guardrail.
- Side Effects / Risks: Promotion may create a false sense of completion if the project skips the next stage of judgement. The right next move is not another local search loop but longer-window and harsher-environment replay audit.
- Conclusion: The sizing line has crossed from exploration into a first frozen default posture. The project should now test this posture, not keep searching the same narrow neighborhood.
- Next Step: Run the promoted default as the new replay baseline and start judging where it still under- or over-expresses outside the current CPO-rich environment.

### JOURNAL-0199 The board method is now formalized enough to become a bounded autonomous queue instead of a manually reissued ritual

- Date: 2026-04-01
- Author: Codex
- Title: Convert the board-research ritual into a one-shot queue protocol with explicit stops
- Related Decision: DEC-0199
- Related Runs: V114F, V114G
- Protocol Version: protocol_v1.14
- Hypothesis: The project no longer needs the user to restate orchestration intent every phase. The board workflow has become structured enough to run as a queue-driven bounded worker as long as stop conditions and promotion gates remain explicit.
- What Changed: Added a formal autonomous orchestrator protocol and seeded the first queue. The worker no longer asks for a new prompt between board phases; it runs until terminal board status or hard stop. The fixed phase stack is:
  - board world model
  - role grammar
  - control extraction
  - paper replay
  - bottleneck diagnosis
  - sizing upgrade
  - unsupervised candidate-state audit
  - promotion gate
- Expected Impact: Reduce orchestration friction while keeping research bounded, auditable, and anti-overfit.
- Observed Result: The protocol now exists as a first-class project asset, and the first queue seed is ready with `CPO` as the head board. This means the user no longer needs to keep saying “继续编排” for every board phase.
- Side Effects / Risks: Autonomy can drift into over-refinement if the worker keeps running after incremental value disappears. The stop rules therefore matter as much as the phase stack.
- Conclusion: The project has moved from manual phase prompting to a bounded autonomous board-worker posture.
- Next Step: Start the first queue head under the new protocol, then expand the queue board by board only after the runner and logs stay stable.

### JOURNAL-0200 Existing daily information still has real headroom for add/reduce learning, but only if it is replay-audited as a candidate overlay

- Date: 2026-04-01
- Author: Codex
- Title: Turn market-voice persistence and state-transition prototypes into a candidate add-band replay audit
- Related Decision: DEC-0200
- Related Runs: V114H, V114I, V114J, V114K
- Protocol Version: protocol_v1.14
- Hypothesis: The remaining under-expressed strong CPO days are not purely an intraday problem yet. Existing daily board information should still contain enough structure to improve add/reduce settlement through market-voice persistence and state-transition prototypes.
- What Changed: Built a candidate-only replay layer that computes online market-voice and state-transition scores from existing daily board context and uses them only to strengthen adds on already-mature holdings. Hard vetoes, de-risk semantics, and symbol admission logic remain unchanged.
- Expected Impact: Reduce the remaining under-expressed strong-board days without secretly turning new vector scores into direct policy law.
- Observed Result: The candidate overlay materially reduced the count of remaining under-expressed strong days:
  - promoted default remaining under-expressed strong days: `14`
  - candidate overlay remaining under-expressed strong days: `6`
  Replay curve also improved:
  - promoted default: `2.3083 / 0.1853`
  - candidate overlay: `3.0841 / 0.2862`
  But drawdown expanded sharply, which means this is not promotion-ready law.
- Side Effects / Risks: The gain is real but too expensive to ignore. The overlay improved capture by adding more aggressively into a few strong windows, but current thresholds and uplift sizing are still too hot for default promotion.
- Conclusion: Existing daily information still contains meaningful add/reduce signal. However, the right status for market-voice and state-transition scores is still candidate-only until thresholds and guardrails are refined or later validated by richer data.
- Next Step: Compare the newly improved dates to the drawdown expansion, then decide whether to refine candidate thresholds, soften the extra uplift, or escalate the need for intraday confirmation on same-day expression upgrades.

### JOURNAL-0201 CPO now has a retained multi-posture sizing registry instead of a single frozen future truth

- Date: 2026-04-01
- Author: Codex
- Title: Keep multiple CPO sizing postures alive for later board judgement
- Related Decision: DEC-0201
- Related Runs: V114D, V114E, V114K, V114L
- Protocol Version: protocol_v1.14
- Hypothesis: CPO is too idiosyncratic to justify collapsing future board research onto a single local sizing winner. A retained registry of distinct postures will better support later cross-board judgement.
- What Changed: Built a parallel posture registry with one promoted default and multiple retained alternates:
  - `default_expectancy_mainline`
  - `conservative_guardrail`
  - `balanced_shadow`
  - `vector_overlay_experimental`
- Expected Impact: Preserve optionality for later boards while keeping current CPO governance explicit.
- Observed Result: The posture registry is now a first-class project asset instead of an implied memory spread across V114D, V114E, and V114K.
- Side Effects / Risks: Registry sprawl becomes a risk if too many variants are retained without clear status labels.
- Conclusion: CPO should now be treated as a board that produced a small posture family, not a board that already discovered one final universal sizing truth.
- Next Step: Use this registry when future boards arrive, and compare posture behavior before deciding whether any one posture deserves broader promotion.

### JOURNAL-0202 Segment leadership inside one board is useful evidence, but still not enough for promotion

- Date: 2026-04-01
- Author: Codex
- Title: Compare CPO posture family across strong and weak environment slices
- Related Decision: DEC-0202
- Related Runs: V114L, V114M
- Protocol Version: protocol_v1.14
- Hypothesis: The retained CPO posture family should not be judged only by full-curve totals. Segment splits inside the same board can reveal whether an aggressive posture is merely lucky or genuinely better at expressing strong-board conditions.
- What Changed: Replayed the retained posture family and compared:
  - `default_expectancy_mainline`
  - `conservative_guardrail`
  - `balanced_shadow`
  - `vector_overlay_experimental`
  across:
  - `all_strong`
  - `high_readiness_strong`
  - `ordinary_strong`
  - `euphoric_strong`
  - `weak_or_mixed`
- Expected Impact: Separate "high return because of one lucky patch" from "high return because the posture systematically expresses strong-board conditions better."
- Observed Result: `vector_overlay_experimental` led every strong segment inside CPO, not just one isolated patch. However, total replay drawdown remained too high for promotion.
- Side Effects / Risks: Internal segment dominance can create false confidence if it is mistaken for cross-board robustness.
- Conclusion: Segment leadership is real evidence, but still not enough to turn the overlay into law.
- Next Step: Refine the overlay locally, trim heat if possible, and keep it candidate-only until harsher judgement arrives.

### JOURNAL-0203 Local vector-overlay refinement found a cleaner experimental variant, but not a new promoted default

- Date: 2026-04-01
- Author: Codex
- Title: Trim vector-overlay heat without pretending CPO has discovered a universal sizing winner
- Related Decision: DEC-0203
- Related Runs: V114N
- Protocol Version: protocol_v1.14
- Hypothesis: A bounded local refinement around the experimental vector overlay may reduce drawdown without destroying its strong-segment advantage.
- What Changed: Searched a small structured neighborhood across:
  - `candidate_add_threshold`
  - `candidate_extra_uplift`
  - `candidate_floor`
  while keeping symbol admission, hard vetoes, and the promoted default base fixed.
- Expected Impact: Find a risk-trimmed overlay candidate that is easier to carry forward for later board transfer tests.
- Observed Result: Lowering `candidate_extra_uplift` from `0.02` to `0.01` produced the best risk-trimmed candidate:
  - hot overlay: `3.0841 / 0.2862`
  - refined overlay: `2.9771 / 0.2800`
  The refined version still beat the default posture in the key strong segments, but did not justify replacing the promoted default.
- Side Effects / Risks: The gain remains CPO-specific until other boards or harsher windows say otherwise.
- Conclusion: The overlay line survives, but only as an experimental family with a cleaner preferred variant.
- Next Step: Carry the refined overlay alongside the default and conservative postures, then judge them outside CPO before any broader promotion.

### JOURNAL-0204 Current CPO execution-axis search says the overlay heat is a confirmation problem, not a cap problem

- Date: 2026-04-01
- Author: Codex
- Title: Test whether cleaner overlay behavior comes from smaller caps or from requiring better add confirmation
- Related Decision: DEC-0204
- Related Runs: V114O
- Protocol Version: protocol_v1.14
- Hypothesis: After threshold/uplift/floor refinement, the remaining overlay heat might be reduced either by smaller expression caps, tighter daily add caps, or by making adds require stronger confirmation.
- What Changed: Ran a bounded local search over:
  - `max_expression_weight`
  - `max_order_notional`
  - `add_confirmation_offset`
  while holding the refined overlay discovery layer fixed.
- Expected Impact: Separate structural heat from pure execution heat and identify the next execution axis worth refining.
- Observed Result: Only `add_confirmation_offset` changed replay behavior in the current CPO window. The tested `max_expression_weight` and daily add-cap ranges were effectively inactive. The cleanest execution-trimmed candidate became:
  - `mx_0.12_cap_200k_confirm_0.00`
  with:
  - `2.5705 / 0.2309`
  versus the refined overlay baseline:
  - `2.9771 / 0.2800`
  This means cleaner behavior is achievable, but at the cost of giving back a meaningful amount of curve.
- Side Effects / Risks: The inactive-cap conclusion may be local to current CPO because the board did not generate enough dense add traffic for those caps to bind.
- Conclusion: If CPO keeps refining, the next real lever is confirmation design, not more local cap tuning.
- Next Step: Either refine confirmation logic from existing daily information, or defer further execution tuning until intraday confirmation can be added.

### JOURNAL-0205 Daily confirmation logic has now been pushed about as far as current CPO information can credibly take it

- Date: 2026-04-01
- Author: Codex
- Title: Test conditional daily confirmation modes against the execution-trimmed overlay reference
- Related Decision: DEC-0205
- Related Runs: V114O, V114P
- Protocol Version: protocol_v1.14
- Hypothesis: Existing daily information might still support a smarter confirmation layer than a blunt constant offset, especially using persistence, market voice, thin coverage, and simple staged confirmation.
- What Changed: Built and replayed six daily-only confirmation candidates:
  - `constant_offset_0.03`
  - `persistence_relaxed`
  - `voice_relaxed`
  - `thin_coverage_relaxed`
  - `two_stage_confirmation`
  - `execution_trimmed_reference`
- Expected Impact: Recover some of the hot overlay's curve while preserving the drawdown reduction gained by adding confirmation.
- Observed Result: None of the conditional daily confirmation modes materially beat the simpler execution-trimmed reference. The cleanest candidate remained:
  - `execution_trimmed_reference`
  - `2.5705 / 0.2309`
  while the hot overlay stayed:
  - `3.0841 / 0.2862`
  This means the project has likely extracted most of the credible confirmation value available from current daily inputs.
- Side Effects / Risks: Continuing to invent more local daily confirmation branches now looks more like overfitting than genuine model improvement.
- Conclusion: Daily-only confirmation is locally exhausted for CPO. If cleaner confirmation is still required, the project should move to a narrow intraday confirmation layer rather than continue daily micro-heuristic search.
- Next Step: Keep current CPO posture family intact and, if further refinement is needed, add intraday confirmation only for the mature symbols and action names instead of broadening the whole board.

### JOURNAL-0206 Three-way critique forced the intraday layer to become a board-state audit and expectancy-label problem, not just a finer confirmation problem

- Date: 2026-04-01
- Author: Codex
- Title: Expand CPO intraday work beyond single-name confirmation after parallel attack review
- Related Decision: DEC-0206
- Related Runs: V114Q, V114R, V114S
- Protocol Version: protocol_v1.14
- Hypothesis: The initial intraday plan was directionally correct, but may still be too narrow if the real goal is to maximize capture of diffusion-style main-uptrend boards while controlling unnecessary drawdown.
- What Changed: Three independent critiques attacked the plan from:
  - goal coverage
  - data sufficiency
  - action semantics / trainability
  Their shared outcome forced a revision:
  - add board-level intraday state layers for diffusion authenticity, persistence, board decay risk, and role migration
  - promote several field groups from optional to must-have
  - define action-outcome label families so `add / reduce / close` can later be trained as expectancy revisions
- Expected Impact: Prevent the project from using richer intraday data merely to re-express 'structure looks stronger' and instead push it toward conditional probability / expectancy supervision.
- Observed Result: The revised protocol now treats:
  - board-state audit
  - single-name confirmation
  - action-outcome labeling
  as one connected layer. This is a stricter and more expensive design, but much closer to the stated objective.
- Side Effects / Risks: The revised layer is no longer runnable from current repository inputs alone because several promoted must-have fields and the action-outcome label table do not yet exist.
- Conclusion: The earlier intraday plan was useful as a narrow prototype, but not yet complete enough for serious learning. The revised version is a better foundation even though it raises the build burden.
- Next Step: Collect the revised narrow-symbol intraday dataset and define the first action-outcome label table before attempting any intraday learning run.

### JOURNAL-0207 CPO replay integrity had to be repaired before the project could credibly continue promoting sizing and overlay results

- Date: 2026-04-01
- Author: Codex
- Title: Replace optimistic same-day-close replay assumptions with next-day-open costed execution
- Related Decision: DEC-0207
- Related Runs: V113V, V114T
- Protocol Version: protocol_v1.14
- Hypothesis: The largest execution realism bug was not in the research ideas themselves, but in the replay surface: same-day close execution and zero transaction costs were making CPO results look better than a realistic paper implementation.
- What Changed: Built `V114T` as an integrity-repaired replay with:
  - signal generated on day `T` close
  - execution moved to day `T+1` open
  - explicit commission, stamp tax, and slippage
  - stricter pretrade checks for cash usage, turnover, and ADV share
- Expected Impact: Lower the optimism bias in all later CPO judgement layers and create a replay surface worth reusing for further promotion decisions.
- Observed Result: The repaired replay now clearly shows delayed execution and non-zero costs. Example: the first `300502` buy signal from `2023-04-28` executes on `2023-05-04` open at `68.02`, not on the signal-day close, and incurs explicit transaction cost. Final equity also drops from the older optimistic replay surface.
- Side Effects / Risks: A large slice of later CPO sizing and overlay work was built on `V113V`, so those reports are now directionally useful but no longer the final truth surface.
- Conclusion: This repair does not invalidate the whole CPO line, but it does mean future promotion claims must migrate to `V114T` or a later repaired replay instead of resting on the optimistic baseline.
- Next Step: Quantify the delta between `V113V` and `V114T`, then rerun the most decision-relevant CPO posture and under-exposure analyses on the repaired replay.

### JOURNAL-0208 Intraday work now needs second-level event visibility discipline, not just better market bars

- Date: 2026-04-01
- Author: Codex
- Title: Treat news and catalyst timing as a first-class legality problem for future intraday replay
- Related Decision: DEC-0208
- Related Runs: V114U
- Protocol Version: protocol_v1.14
- Hypothesis: Once the project introduces intraday decisions, market bars alone are not enough; external information timing can create a new forward-leak channel unless event visibility is recorded precisely.
- What Changed: Defined a new timestamp discipline requiring second-level timing for external information that may alter intraday actions, including:
  - `event_occurred_time`
  - `public_release_time`
  - `system_visible_time`
  - explicit timezone and source identifier
- Expected Impact: Make future intraday training and replay legally point-in-time instead of merely bar-aligned.
- Observed Result: The protocol now distinguishes between what happened in the world, what became public, and what the system could actually see. This sharply reduces the chance of smuggling later-known news into earlier intraday decisions.
- Side Effects / Risks: Some data sources will become unusable or downgraded until they provide adequate timestamp fidelity.
- Conclusion: If intraday work is going to be credible, event visibility timing must be treated as seriously as price timing.
- Next Step: Enforce this timestamp discipline in future intraday news/event collection before minute-level learning begins.

### JOURNAL-0209 Benchmark repair materially changed the narrative: CPO still under-expresses, but not nearly as badly as the old board-equal comparison implied

- Date: 2026-04-01
- Author: Codex
- Title: Separate opportunity ceiling from fairer sparse-action comparison after replay repair
- Related Decision: DEC-0209
- Related Runs: V114T, V114V
- Protocol Version: protocol_v1.14
- Hypothesis: Once replay integrity is repaired, the old full-board equal-weight comparison may still be directionally useful but is likely overstating practical underperformance for a sparse-action strategy.
- What Changed: Built `V114V` to distinguish:
  - repaired strategy curve
  - full-board equal-weight opportunity curve
  - action-coverage proxy curve
- Expected Impact: A clearer benchmark hierarchy for future CPO decisions.
- Observed Result: The repaired strategy finished near `1.7665`, while the action-coverage proxy was `1.8301` and the board equal-weight opportunity curve stayed `4.2093`. This means the old board-relative shortfall was real in spirit but badly overstated in magnitude.
- Side Effects / Risks: The proxy benchmark is still imperfect and should not be mistaken for a final institutional benchmark.
- Conclusion: CPO underperformance versus the full board was too loose as the primary story; the fairer story is that the strategy still lags its action-coverage opportunity set, but by a much smaller amount.
- Next Step: Use the repaired benchmark stack for all later under-exposure and sizing judgements.

### JOURNAL-0210 Under-exposure survived replay repair, which means the sizing problem is real rather than a replay artifact

- Date: 2026-04-01
- Author: Codex
- Title: Re-run the under-exposure diagnosis on the repaired replay and benchmark surfaces
- Related Decision: DEC-0210
- Related Runs: V114T, V114V, V114W
- Protocol Version: protocol_v1.14
- Hypothesis: If the earlier under-exposure diagnosis was mostly a replay artifact, it should weaken sharply once same-day execution optimism and zero-cost accounting are removed.
- What Changed: Rebuilt the under-exposure attribution on top of `V114T` and the repaired benchmark hierarchy in `V114V`.
- Expected Impact: Either invalidate the under-exposure story or confirm it on a cleaner surface.
- Observed Result: Under-exposure remains, but the scale is different:
  - repaired strategy curve: `1.7665`
  - action-coverage proxy: `1.8301`
  - gap: `-0.0636`
  Strong-board low-expression misses still appear, but the core message becomes more disciplined: CPO is still too timid, not catastrophically broken.
- Side Effects / Risks: This is still one board and one replay family, so the conclusion is not yet a universal law.
- Conclusion: The under-exposure problem is real, but the old narrative was too dramatic because it leaned on an unfair benchmark and optimistic replay assumptions.
- Next Step: Rebuild the sizing grammar on this repaired surface instead of carrying forward the old one.

### JOURNAL-0211 The CPO sizing grammar survives replay repair, but with slightly lower exposure floors

- Date: 2026-04-01
- Author: Codex
- Title: Reissue probability/expectancy sizing after replay realism repair
- Related Decision: DEC-0211
- Related Runs: V114T, V114W, V114X
- Protocol Version: protocol_v1.14
- Hypothesis: The logic behind the old sizing grammar may still hold after replay repair, but the exact exposure floors should likely soften once next-day execution and transaction costs are recognized.
- What Changed: Built `V114X` as the repaired successor to the old CPO sizing grammar.
- Expected Impact: Preserve the main insight about timid expression without overreacting to the older optimistic replay surface.
- Observed Result: The repaired grammar still calls for stronger expression in real board strength, but trims the floors slightly:
  - one-line strong board floor: `0.30`
  - two-line strong board floor: `0.45`
  This is lower than the older optimistic surface, but still materially above the replay's current realized exposure in many strong windows.
- Side Effects / Risks: The grammar is cleaner than before, but it remains daily-layer sizing and still awaits intraday confirmation and action-outcome supervision.
- Conclusion: The project can move forward, but only if future CPO posture work uses the repaired sizing grammar rather than the old optimistic one.
- Next Step: Treat `V114X` as the valid CPO daily sizing base until intraday learning is ready.

### JOURNAL-0212 The market-cap bug is now split cleanly into “current truth fixed” versus “historical truth still missing”

- Date: 2026-04-01
- Author: Codex
- Title: Collect a real current free-float snapshot for the entire CPO cohort
- Related Decision: DEC-0212
- Related Runs: V114Y
- Protocol Version: protocol_v1.14
- Hypothesis: Even if a historical float time series is still missing, the project should stop pretending that a market-cap proxy is the best currently available truth for all use cases.
- What Changed: Built `V114Y` to collect current `float_shares` and `free_float_market_cap` snapshots for all `20` CPO cohort symbols and wrote them to a dedicated reference layer.
- Expected Impact: Replace fake precision with explicit current-truth fields wherever the workflow only needs present-day float context.
- Observed Result: Coverage is `20/20`, with no collection failures. This fixes the old “we only have proxy market cap” statement for current-state work, while keeping the boundary explicit: historical float series are still absent.
- Side Effects / Risks: The new snapshot is useful, but dangerous if anyone later treats it as historical point-in-time truth.
- Conclusion: The right posture is no longer “we only have a proxy” but “we have current float truth and still lack historical float truth.”
- Next Step: Keep historical turnover-rate work blocked on time-varying float data, but start using the snapshot where current-state normalization is enough.

### JOURNAL-0213 The intraday gap is no longer abstract: we now know exactly which CPO windows we need and that the current provider does not yet deliver them

- Date: 2026-04-01
- Author: Codex
- Title: Freeze the four-symbol intraday backlog and audit current provider failure explicitly
- Related Decision: DEC-0213
- Related Runs: V114Z
- Protocol Version: protocol_v1.14
- Hypothesis: A narrow, concrete key-window manifest would be more useful than another round of generic “we need intraday” discussion.
- What Changed: Built `V114Z`, which maps the four mature CPO action symbols to `19` concrete historical key windows and attempts provider access for those windows.
- Expected Impact: Convert the intraday requirement from a vague dependency into an auditable acquisition backlog.
- Observed Result: The backlog is now explicit, but current readiness is `false`: all attempted historical windows failed, so the project cannot honestly claim intraday replay readiness yet.
- Side Effects / Risks: This pushes the next bottleneck into data sourcing rather than modeling, which may feel slower but is much cleaner.
- Conclusion: The project has crossed from “knowing intraday is needed” to “knowing exactly what to collect and admitting current access is insufficient.”
- Next Step: Treat the `V114Z` manifest as the only valid narrow-scope intraday backlog for CPO until real minute files begin landing.

### JOURNAL-0214 The intraday story is now properly split: rolling 1-minute collection exists, and historical mid-frequency backfill is already partially solved

- Date: 2026-04-01
- Author: Codex
- Title: Validate Baostock as the first historical mid-frequency backfill rail for CPO
- Related Decision: DEC-0214
- Related Runs: V115A
- Protocol Version: protocol_v1.15
- Hypothesis: The right intraday plan is not “all or nothing”; rolling 1-minute collection and historical backfill can be solved with different providers.
- What Changed: Added `V115A` to audit Baostock against the frozen CPO key-window manifest from `V114Z`.
- Expected Impact: Clarify whether historical intraday confirmation work can start before a full historical 1-minute archive is available.
- Observed Result: `73/76` requests returned non-empty bars across `5/15/30/60min`, which is strong enough to treat Baostock as a real historical confirmation source. This means the project does not need to wait for perfect 1-minute archives to begin historical intraday refinement.
- Side Effects / Risks: A few requests still failed and should be handled with retry logic or provider fallback; Baostock remains a mid-frequency layer, not a replacement for true 1-minute history.
- Conclusion: The earlier statement “historical intraday is not ready” was too broad. The accurate statement is now:
  - rolling 1-minute collection: ready via Sina
  - historical mid-frequency backfill: materially ready via Baostock
  - historical 1-minute archive: still not solved
- Next Step: Use Baostock for historical `5/15/30/60min` confirmation studies on the four mature CPO action objects.

### JOURNAL-0215 Mid-frequency intraday has now crossed from "nice factor table" into "candidate action evidence" on repaired CPO miss days

- Date: 2026-04-01
- Author: Codex
- Title: Audit repaired under-exposure miss days with Baostock `30/60min` bars
- Related Decision: DEC-0215
- Related Runs: V114T, V114W, V115B, V115C
- Protocol Version: protocol_v1.15
- Hypothesis: If the repaired CPO under-exposure diagnosis is real, then at least some of the strongest miss days should already show add-like confirmation in the mid-frequency bars of the core names we were actually holding.
- What Changed: Built `V115C`, reconstructed the held-symbol set on the six repaired top-opportunity miss days, fetched `30/60min` Baostock bars for those held names, and scored them with a narrow candidate confirmation function.
- Expected Impact: Tell us whether mid-frequency intraday is merely descriptive, or whether it is already capable of producing candidate action evidence on top of the repaired replay base.
- Observed Result: The first pass is directionally strong: all `10` audited held-name miss windows cleared the current candidate confirmation threshold. That means the intraday line is no longer hypothetical. It already has action-layer signal. At the same time, the result is clearly too permissive to be promoted directly.
- Side Effects / Risks: The threshold is lenient because it is anchored on a small repaired reference set. If left unchallenged, it could silently over-promote intraday confirmation.
- Conclusion: Mid-frequency intraday is now useful for CPO action research, but only as candidate evidence. The next task is not to celebrate the `10/10`, but to harden the threshold on a broader repaired sample before letting it influence default replay behavior.
- Next Step: Expand the repaired intraday audit window set beyond the six top misses and retest the confirmation threshold before any promotion.

### JOURNAL-0216 The intraday line now has a real supervised training table, not just factor rows and miss-day audits

- Date: 2026-04-01
- Author: Codex
- Title: Align Baostock mid-frequency windows with repaired replay timing and action contexts
- Related Decision: DEC-0216
- Related Runs: V114T, V115B, V115C, V115D
- Protocol Version: protocol_v1.15
- Hypothesis: Once mid-frequency bars are aligned to repaired `T-close -> T+1-open` execution timing and paired with forward path labels, they should become trainable action-timepoint samples rather than static descriptive windows.
- What Changed: Built `V115D`, which merges the original `V115B` window factors with the repaired replay state from `V114T`, adds miss-window coverage from `V115C`, and emits an action-context table with four contexts: `entry_vs_skip`, `add_vs_hold`, `reduce_vs_hold`, and `close_vs_hold`.
- Expected Impact: Give the project a lawful first dataset for candidate supervised intraday learning on top of the repaired replay base.
- Observed Result: The first table contains `29` rows, including `10` repaired miss-window rows. It now exposes forward-return, favorable-excursion, adverse-excursion, and expectancy-proxy labels at `1d/3d/5d` horizons. This is enough to begin harder thresholding work, but not enough to claim fully mature action-expectancy supervision.
- Side Effects / Risks: The current action labels are still proxy labels, and the repaired miss windows are overrepresented inside `add_vs_hold`, so the table remains candidate-only.
- Conclusion: CPO mid-frequency research has crossed a real threshold: it is no longer just “we have intraday data”; it is now “we have a first repaired, action-aligned intraday training table.”
- Next Step: Expand the repaired window set and rebuild the labels toward the full `V114S` conditional-expectancy family before any promotion into default replay behavior.


### JOURNAL-0217 The Baostock confirmation line now has a harder candidate gate calibrated on the broader repaired action table

- Date: 2026-04-01
- Author: Codex
- Title: Replace the narrow miss-day threshold with a broader repaired threshold calibration
- Related Decision: DEC-0217
- Related Runs: V115C, V115D, V115E
- Protocol Version: protocol_v1.15
- Hypothesis: If the intraday line is real, it should survive a harder calibration regime built on the broader repaired action-timepoint table rather than only the six top miss days.
- What Changed: Built `V115E`, which recalibrates the `30/60min` confirmation thresholds on the broader repaired action table from `V115D` instead of the narrow miss-day slice from `V115C`.
- Expected Impact: Move the Baostock line from ?everything on miss days looks confirmatory? toward a stricter candidate gate that can actually reject weaker windows.
- Observed Result: The harder calibration settled around:
  - `f30_best_threshold = 0.60`
  - `f60_best_threshold = 0.60`
  with `9` of the `10` repaired miss-window rows still passing. That is materially stricter than the earlier permissive posture and still leaves the line useful.
- Side Effects / Risks: The broader table still relies on proxy action-outcome labels and small negative-reference counts, so this remains candidate-only.
- Conclusion: The mid-frequency line has now crossed from a permissive miss-day explainer into a harder candidate overlay gate grounded in the repaired action table.
- Next Step: Keep `V115E` as the current intraday candidate baseline and expand the action-outcome label family before any replay promotion.


### JOURNAL-0218 The Baostock action table is no longer add-only, but the first negative enrichment pass overshot and created a new imbalance

- Date: 2026-04-01
- Author: Codex
- Title: Thicken reduce/close supervision with repaired replay risk days
- Related Decision: DEC-0218
- Related Runs: V114T, V115D, V115F
- Protocol Version: protocol_v1.15
- Hypothesis: The next meaningful quality jump for intraday learning would come not from more positive confirmation windows, but from thickening the weak negative side: reduce and close.
- What Changed: Built `V115F`, which scans repaired replay risk days with open positions and converts them into candidate `reduce_vs_hold` and `close_vs_hold` samples, adding first-pass proxy labels such as:
  - `P_reduce_avoided_drawdown_proxy_3d`
  - `reduce_payoff_decay_vs_hold_proxy_3d`
  - `P_close_invalidation_realized_proxy_3d`
  - `P_close_opportunity_cost_proxy_3d`
- Expected Impact: Make the intraday table less add-biased and more usable for actual action-value learning.
- Observed Result: The action table expanded from `29` rows to `450`, with the negative side now dominating:
  - `reduce_vs_hold = 340`
  - `close_vs_hold = 85`
  - `add_vs_hold = 17`
  This is useful because the weak side is no longer empty, but it also means the raw enriched table is now too negative-heavy to use naively.
- Side Effects / Risks: The project has moved from one imbalance to another. Future training must rebalance or weight contexts instead of learning directly from the raw row counts.
- Conclusion: The main defect in the intraday table has changed. It is no longer ?not enough negative supervision?; it is now ?negative supervision exists, but must be reweighted before it can train anything sensible.?
- Next Step: Build a balanced training view on top of `V115F` before re-running any intraday overlay calibration or promotion tests.


### JOURNAL-0219 The right intraday discovery base is not the 4 manual vectors, but a de-redundant high-dimensional table

- Date: 2026-04-01
- Author: Codex
- Title: Replace manual semantic compression with a higher-dimensional discovery substrate before unsupervised learning
- Related Decision: DEC-0219
- Related Runs: V115F, V115G, V115H
- Protocol Version: protocol_v1.15
- Hypothesis: If the project wants more objective intraday discovery, it should delay semantic naming and instead preserve more raw state directions while stripping out pseudo-dimensions and identity leakage.
- What Changed: Built `V115H`, a high-dimensional intraday feature base table that:
  - keeps `30/60min` main-state fields,
  - keeps `5/15min` only as differential support features,
  - applies robust-standardization-ready columns,
  - and explicitly moves identity, action labels, and outcome labels out of the discovery distance space.
- Expected Impact: Make the next unsupervised pass less definition-heavy than `V115G` while avoiding a naive raw-field dump that would be dominated by frequency duplication and price-scale noise.
- Observed Result: The base table now contains:
  - `450` actionable rows
  - `25` discoverable features
  - `15` audit-only fields
  - `19` dropped fields
  and fixes the discovery posture as `high_dimensional_base_table_before_unsupervised_discovery`.
- Side Effects / Risks: This is still not a promotable learning set. The sample is path-dependent and the downstream action labels remain partly proxy-based, so unsupervised outputs must still be audited as candidate-only.
- Conclusion: The intraday line should no longer treat the manually precompressed 4-vector view as its objective substrate. `V115H` is the new base table for discovery; naming comes later.
- Next Step: Run PCA/sparse-PCA and band-oriented unsupervised discovery on `V115H`, then audit whether any discovered state directions truly improve `add/reduce/close` expectancy judgments.


### JOURNAL-0220 The V115H intraday base table already supports a guarded candidate training view, but not promotion

- Date: 2026-04-01
- Author: Codex
- Title: Build the first weighted action-learning pilot on the high-dimensional intraday base table
- Related Decision: DEC-0220
- Related Runs: V115H, V115I
- Protocol Version: protocol_v1.15
- Hypothesis: If `V115H` is a useful substrate, a guarded training view built on top of it should at least recover some candidate action-separation signal before unsupervised discovery is run.
- What Changed: Built `V115I`, which:
  - derives coarse action-expression labels,
  - constructs a weighted balanced training view,
  - screens features on the train split only,
  - and compares a weighted nearest-centroid guardrail against a weighted ridge multiclass candidate.
- Expected Impact: Sanity-check whether the high-dimensional base table has genuine action-learning value instead of being only a discovery substrate.
- Observed Result: `V115I` selected `12` top features dominated by:
  - `high_time_ratio`
  - `close_location`
  - `breakout_efficiency`
  - `afternoon_volume_share`
  - `last_bar_volume_share`
  The weighted ridge candidate improved over the nearest-centroid guardrail on macro recall, but the smallest train class remained only `5`, so the whole result remains candidate-only.
- Side Effects / Risks: The training table still inherits repaired-replay path dependence and the increase-expression class is extremely thin; the pilot can validate learnability, but not justify policy promotion.
- Conclusion: `V115H` is not just a discovery table; it already supports a guarded candidate training view. But it is still far from a promotable action learner.
- Next Step: Keep `V115I` as a supervised sanity check and move on to PCA/sparse-PCA plus continuous-band unsupervised discovery on `V115H`.


### JOURNAL-0221 The current intraday discovery space behaves more like a continuous band than a natural cluster family

- Date: 2026-04-01
- Author: Codex
- Title: Use PCA band audit to narrow strict add zones before any replay overlay
- Related Decision: DEC-0221
- Related Runs: V115J, V115K, V115L
- Protocol Version: protocol_v1.15
- Hypothesis: If the intraday discovery space is genuinely smooth rather than discretely clustered, a PCA band audit should reveal that broad positive-looking regions need to be narrowed before they can be used in any add-overlay test.
- What Changed: Built:
  - `V115J`, which runs PCA and continuous-band audit on the `V115H` base table,
  - `V115K`, which maps those bands into candidate add/reduce semantics,
  - `V115L`, which then tightens the add-band set into a strict subset.
- Expected Impact: Prevent the project from leaking all positive-looking states into the next overlay and instead force a stricter band selection before any replay-facing test.
- Observed Result: The PCA result is heavily dominated by `PC1` (`~93%` explained ratio), supporting a band-first reading. `V115K` initially marked `3` add-looking bands, but `V115L` trimmed that down to `2` strict add bands:
  - `pc1_low__pc2_low`
  - `pc1_high__pc2_low`
  while leaving `pc1_low__pc2_high` as a softer review-only region.
- Side Effects / Risks: The state-band map is still candidate-only and still inherits the repaired CPO sample bias. It is useful for the next overlay audit, not for direct law extraction.
- Conclusion: The intraday line should currently be treated as a continuous-band problem with a strict add-band subset, not as a mature clustering problem.
- Next Step: Run the next candidate overlay audit using only the strict add bands and keep all weaker positive-looking regions out of the first replay-facing test.


### JOURNAL-0222 The strict add-band overlay is cleaner than the permissive band map, but too leaky to become admission law

- Date: 2026-04-01
- Author: Codex
- Title: Audit strict intraday add bands only against repaired miss days before any replay binding
- Related Decision: DEC-0222
- Related Runs: V115M
- Protocol Version: protocol_v1.15
- Hypothesis: If `V115L` really isolated the cleanest add-looking intraday bands, then auditing only those bands against repaired miss days should produce better expectancy/adverse quality than the broader top-miss set, while still revealing whether they are safe enough to become a replay-facing overlay.
- What Changed: Built `V115M` to audit only:
  - `pc1_low__pc2_low`
  - `pc1_high__pc2_low`
  against repaired miss-day rows, and compared their hit quality, miss-day coverage, and context leakage against the broader top-miss pool.
- Expected Impact: Determine whether the strict band subset is clean enough for the next replay-facing overlay test without accidentally turning intraday discovery into a new-entry law.
- Observed Result: The strict bands improved average miss-row quality:
  - `strict_hit_expectancy_mean = 0.101147`
  - vs `all_top_miss_expectancy_mean = 0.075894`
  and improved adverse-path quality:
  - `strict_hit_adverse_mean = -0.043511`
  - vs `all_top_miss_adverse_mean = -0.056003`
  but they only covered `2/6` repaired top miss days and still leaked heavily into `entry_vs_skip` (`0.875` rate).
- Side Effects / Risks: The strict overlay is cleaner but sparse, and the admission leakage is far too high to let these bands open fresh names. This remains a candidate-only held-position overlay idea.
- Conclusion: The strict bands are useful enough to survive narrowing, but only as a constrained overlay on already-held mature names. They are not safe enough to become a generic intraday add/admission law.
- Next Step: If a replay-facing test is run next, keep it narrow: held-position overlay only, no soft band, no fresh admissions.


### JOURNAL-0223 Wick features can be added cleanly, but the current mid-frequency sample is too coarse for them to matter yet

- Date: 2026-04-01
- Author: Codex
- Title: Add explicit upper/lower shadow structure to the intraday base table and check whether current CPO windows actually use it
- Related Decision: DEC-0223
- Related Runs: V115B, V115H, V115I, V115J, V115K, V115L, V115M
- Protocol Version: protocol_v1.15
- Hypothesis: If wick/shadow structure really carries useful confirmation information, then explicitly adding it to the intraday base table should either change the selected training features, alter the PCA/band map, or improve the downstream strict-band action audit.
- What Changed: Added explicit shadow-derived features into the factor extraction and high-dimensional base table:
  - `upper_shadow_ratio`
  - `lower_shadow_ratio`
  - `body_ratio`
  - `last_bar_upper_shadow_ratio`
  - `last_bar_lower_shadow_ratio`
  and corresponding cross-frequency differential fields. Then reran the downstream chain from `V115H` through `V115M`.
- Expected Impact: Either the new features would surface as meaningful structure in the current `Baostock 30/60min` sample, or they would prove that the current intraday bar granularity is too coarse for wick-style microstructure to contribute.
- Observed Result: The schema expanded successfully and all downstream tests still passed, but the current sample showed little to no useful variation in the new shadow fields. The selected feature set in `V115I` did not change materially, the PCA structure in `V115J` remained dominated by the same primary direction, and the strict-band conclusions in `V115L/V115M` were effectively unchanged.
- Side Effects / Risks: This means the feature family is structurally correct but presently low-value. If the team overreads it now, it will create false confidence rather than real action gain.
- Conclusion: Wick/shadow structure belongs in the discovery substrate, but the present `Baostock 30/60min` windows are too coarse for it to become a meaningful confirmation driver. The likely path to real value is later `1min` or richer intraday data.
- Next Step: Keep wick features in the base table, stop trying to promote them on current mid-frequency evidence, and revisit them after `1min` supplementation or a richer intraday sample arrives.


### JOURNAL-0224 The strict intraday add-band line now has replay-facing incremental value, but only in a very narrow held-position setting

- Date: 2026-04-01
- Author: Codex
- Title: Bind strict add bands into repaired replay and check whether the candidate line survives contact with actual PnL
- Related Decision: DEC-0224
- Related Runs: V115N
- Protocol Version: protocol_v1.15
- Hypothesis: If the strict bands from `V115L/V115M` really carry action value rather than only descriptive structure, then a narrow held-position overlay on the repaired replay should show some incremental equity gain without needing to become a new-entry law.
- What Changed: Built `V115N`, which replays a strict held-position overlay on top of `V114T` using:
  - only already-held mature names,
  - only strict add-band hits on repaired miss days,
  - and `T` signal / `T+1 open` execution with costs intact.
- Expected Impact: Reveal whether the strict intraday line has any real replay-facing upside while preserving the rule that intraday discovery cannot open fresh names or override baseline sell-side controls.
- Observed Result: The narrow overlay generated `4` add orders across `2` repaired miss days and lifted repaired final equity from `1.7665M` to `2.1544M`, while max drawdown rose from `0.1343` to `0.1734`.
- Side Effects / Risks: The uplift is real, but the sample is extremely thin and still path-dependent. This is enough to prove candidate value, not enough to declare a new law.
- Conclusion: The strict intraday band line has crossed the threshold from “pure audit object” into “candidate replay overlay,” but only in a narrow held-position setting. It remains candidate-only and must not be generalized into admission or generic intraday add logic.
- Next Step: Keep the line narrow, expand repaired-window revalidation, and test whether similar overlay behavior survives outside `CPO` before any promotion.
### JOURNAL-0225 The repaired replay was materially understating strict intraday add-band value by forcing same-session signals into next-day execution

- Date: 2026-04-01
- Author: Codex
- Title: Audit intraday signal visibility and rerun strict held-position overlay with same-session next-bar execution
- Related Decision: DEC-0225
- Related Runs: V115O, V115P
- Protocol Version: protocol_v1.15
- Hypothesis: If strict intraday add-band hits are already visible during the same session, then `V115N` is materially understating the line by forcing those signals into `T+1 open` execution.
- What Changed: Built `V115O` to reconstruct historical intraday prefixes and identify the earliest legal checkpoint for each strict hit, then built `V115P` to execute intraday-visible strict hits at the same-session next `30min` bar open instead of `T+1 open`.
- Expected Impact: Clarify how much of the previously observed under-exposure came from timing semantics rather than from the add-band logic itself.
- Observed Result: All `4` strict overlay hits were already visible by `10:30`, with no late-session or post-close cases. Replaying them with same-session next-bar execution lifted repaired final equity from `1.7665M` to `2.4276M`, versus `2.1544M` under `V115N`. Max drawdown rose from `0.1343` to `0.1925`.
- Side Effects / Risks: The signal-timing conclusion is clean for this narrow sample, but the sample remains small and path-dependent. This proves semantic relevance, not promotion readiness.
- Conclusion: Strict intraday add-bands should no longer be described as generic `T+1` overlays. Their natural candidate semantics are timing-aware:
  - same-session next-bar execution for intraday-visible hits,
  - while still preserving held-position-only scope and all baseline sell-side controls.
- Next Step: Keep the line candidate-only, expand repaired-window coverage, and verify whether timing-aware same-session execution survives outside the current narrow `CPO` sample.


### JOURNAL-0226 Widening the strict intraday add-context sample confirms that timing-aware execution survives, but raw expansion is too loose

- Date: 2026-04-01
- Author: Codex
- Title: Expand strict add-band timing audit beyond top-miss days and compare broader timing-aware overlay filters
- Related Decision: DEC-0226
- Related Runs: V115Q, V115R
- Protocol Version: protocol_v1.15
- Hypothesis: If timing-aware intraday execution is a real semantic improvement rather than a top-miss artifact, then it should still show value once the sample widens to all strict `add_vs_hold` rows.
- What Changed: Built `V115Q` to widen timing audit from the repaired top-miss subset to all strict `add_vs_hold` rows, then built `V115R` to compare four timing-aware held-position overlay filters on top of the repaired replay:
  - all strict rows
  - positive expectancy only
  - action-favored only
  - positive and favored
- Expected Impact: Distinguish whether broader timing-aware semantics remain useful once negative and marginal strict hits are allowed back into the sample.
- Observed Result: All `9` strict `add_vs_hold` rows were already intraday-visible by `10:30`. On replay, the raw broader expansion (`all_strict_add_context`) produced the highest equity (`2.5200M`) but also admitted negative-expectancy adds. The cleaner broader posture was `positive_expectancy_only`, which executed `3` overlay orders, lifted equity to `2.2776M`, and produced the best drawdown among the broader variants (`0.1569`).
- Side Effects / Risks: The broader raw variant looks strongest on equity, but it is too permissive because it includes known negative-expectancy strict hits. That makes it unsuitable as a clean promotion candidate.
- Conclusion: Timing-aware execution survives sample widening, but raw strict-add expansion is too loose. The cleaner broader reference should now be `positive_expectancy_only`, retained in parallel rather than promoted.
- Next Step: Keep broader timing-aware variants parallel and candidate-only. Use `positive_expectancy_only` as the next cleaner reference posture when expanding repaired-window validation or testing outside `CPO`.


### JOURNAL-0227 Visible-only checkpoint-score filtering survives the first no-future-label repair, but the cleanest candidate sits in a narrow middle band rather than at either extreme

- Date: 2026-04-01
- Author: Codex
- Title: Rebuild intraday timing-aware filters from point-in-time-visible checkpoint scores and refine the visible-only threshold family
- Related Decision: DEC-0227
- Related Runs: V116C, V116D
- Protocol Version: protocol_v1.16
- Hypothesis: If the strict intraday overlay line contains real signal rather than only post-hoc label leakage, then a visible-only rebuild using `10:30` checkpoint `pc1/pc2` scores should still produce executing candidate variants with meaningful uplift.
- What Changed: Built `V116C` to remove all future labels from filter definitions and rebuild the intraday overlay using only visible checkpoint scores, then built `V116D` to sweep low-threshold variants across `pc1/pc2` quantiles and compare the resulting timing-aware held-position overlays.
- Expected Impact: Preserve the timing-aware intraday line after leakage repair and identify whether a cleaner visible-only candidate exists between the broad all-pass posture and no-trade sparsity.
- Observed Result: The broad visible-only ceiling (`all_intraday_strict_visible`) still executed `9` overlay orders and lifted repaired equity to `3.1247M`, but it remained too loose. The cleanest executing visible-only candidate was `pc1_only_q_0p2`, which executed `2` overlay orders, lifted equity to `2.0839M`, and kept max drawdown at `0.1571`. A more expressive middle candidate, `pc1_or_pc2_q_0p25`, executed `6` orders and reached `2.6079M` with `0.1765` drawdown.
- Side Effects / Risks: The line now avoids future-label leakage, but all variants still sit on the same narrow `CPO` timing-aware sample. The strongest broad variant is still likely too permissive, while the cleaner variants may be too thin to generalize.
- Conclusion: The strict intraday overlay line survives the first no-future-label repair. The real information now appears to live in a narrow band of visible checkpoint-score thresholds, not in either the raw all-pass variant or the no-trade extreme filters.
- Next Step: Carry the visible-only executing variants forward, add two more runs on this line, and then subject the repaired family to the next mandatory three-run adversarial review.


### JOURNAL-0228 The first visible-only three-run review demoted the apparent clean winner and forced a time-split rebuild

- Date: 2026-04-01
- Author: Codex
- Title: Triage the first visible-only three-run block and rebuild threshold logic across time splits
- Related Decision: DEC-0228
- Related Runs: V116F, V116G
- Protocol Version: protocol_v1.16
- Hypothesis: If the visible-only family still contains real signal after leakage repair, then a three-run adversarial review plus a simple time split should separate coherent candidates from same-sample lucky bands.
- What Changed: Formalized the first adversarial triage for `V116C/V116D/V116E`, then rebuilt threshold logic across an early/late time split instead of calibrating and judging on the same `9` windows.
- Expected Impact: Reduce the risk that visible-only candidates are merely a carved threshold family on the same tiny sample.
- Observed Result: The triage demoted `pc1_only_q_0p2` because replay cleanliness and audit coherence diverged after the `V116E` repair. The retained visible-only candidates became:
  - `pc2_only_q_0p25` as the cleaner coherent candidate
  - `pc1_or_pc2_q_0p25` as the expressive shadow candidate
  while `all_intraday_strict_visible` was retained only as an audit ceiling. The time-split rebuild then showed that the family still has signal, but the “winner” depends materially on which side of the split is used for calibration.
- Side Effects / Risks: The time-split audit improves methodology, but the sample remains only `9` rows (`5` early, `4` late). This is still too thin for promotion, and checkpoint-to-fill timing semantics remain the next execution-level repair.
- Conclusion: The visible-only line survives its first adversarial review, but only as a candidate family. The biggest gain from this block was not a new winner; it was forcing the line off same-sample threshold carving and onto time-split scrutiny.
- Next Step: Keep the visible-only family candidate-only, use time-split rows as the main anti-overfit guardrail, and next repair checkpoint-to-fill alignment before any broader replay expansion.


### JOURNAL-0229 The cleaner narrow visible-only candidate failed wider repaired-window revalidation, while the expressive shadow candidate retained partial explanatory power

- Date: 2026-04-01
- Author: Codex
- Title: Revalidate retained visible-only candidates on a wider repaired under-exposure window
- Related Decision: DEC-0229
- Related Runs: V116I
- Protocol Version: protocol_v1.16
- Hypothesis: If a retained visible-only candidate is genuinely useful for under-exposure correction, then it should touch a broader set of repaired strong-day misses rather than only the original strict sample.
- What Changed: Built `V116I` to apply the retained visible-only candidates from the first triage against the wider repaired under-exposed window extracted from `V114H`, using only `add_vs_hold` rows on those repaired miss days.
- Expected Impact: Distinguish whether the cleaner narrow candidate or the more expressive shadow candidate is the more relevant next replay-facing object.
- Observed Result: `pc2_only_q_0p25` hit none of the wider repaired under-exposed rows. By contrast, `pc1_or_pc2_q_0p25` hit `7` rows across `4` repaired miss days, with `0.714286` positive-expectancy hit rate and `0.128348` average expectancy proxy, though it still included the known weak `2023-12-08` pair.
- Side Effects / Risks: The wider-window result improves prioritization, but it also confirms that the expressive candidate remains mixed rather than clean. This still does not justify promotion.
- Conclusion: The wider-window audit shifted the visible-only ranking. The narrow clean candidate is no longer the right next expansion target; the broader expressive candidate is the one that actually reaches repaired under-exposure, even if it remains candidate-only.
- Next Step: Carry `pc1_or_pc2_q_0p25` forward as the next broader replay-facing shadow candidate and keep `pc2_only_q_0p25` only as a narrow clean reference, not as the main expansion line.


### JOURNAL-0230 The wider visible-only shadow replay only became meaningful after reconnecting it to the repaired miss surface

- Date: 2026-04-01
- Author: Codex
- Title: Rebuild the broader visible-only shadow replay on repaired under-exposure days and repaired sizing floors
- Related Decision: DEC-0230
- Related Runs: V116J
- Protocol Version: protocol_v1.16
- Hypothesis: If `pc1_or_pc2_q_0p25` is the only visible-only candidate that still explains wider repaired under-exposure, then a checkpoint-aware shadow replay on the repaired miss surface should show whether that explanatory power survives once it is translated back into execution.
- What Changed: Replaced the stale `V114H` miss surface with repaired `V114W` miss days and repaired `V114X` sizing floors, rebuilt candidate timing from visible checkpoint scores, and replayed only the broader visible-only candidate with held-position-only same-session next-bar adds.
- Expected Impact: Convert the broader visible-only line from an audit-only explanation layer into a replay-facing shadow candidate that still respects repaired execution semantics.
- Observed Result: The rebuilt shadow replay produced a large delta over baseline, but the resulting line is too hot to promote. This means the replay is useful as a shadow stress line, not as a new default rule.
- Side Effects / Risks: The main risk shifted from “does the candidate do anything at all?” to “does this candidate now over-express too aggressively on repaired miss days?” That is a better place to be methodologically, but still far from promotable.
- Conclusion: The broader shadow replay only started to matter once it was rebuilt on the repaired miss surface. That validates the direction, but it also confirms that the expressive visible-only candidate should remain shadow-only.
- Next Step: Keep `pc1_or_pc2_q_0p25` as the wider shadow replay line, accumulate two more runs, and force the next mandatory three-run adversarial review before any further replay-facing expansion.


### JOURNAL-0231 The second visible-only three-run review caught the project trying to retain the hottest replay line as the cooled winner

- Date: 2026-04-02
- Author: Codex
- Title: Triage `V116J/V116K/V116L` and overrule the mistaken cooled-shadow retention
- Related Decision: DEC-0231
- Related Runs: V116J, V116K, V116L, V116M
- Protocol Version: protocol_v1.16
- Hypothesis: If the second visible-only three-run block is reviewed adversarially, then it should be possible to distinguish the genuinely cooled candidate from the hottest replay reference rather than silently retaining the latter.
- What Changed: Ran the second mandatory three-run adversarial review over `V116J/V116K/V116L` and formalized the result in `V116M`.
- Expected Impact: Prevent the visible-only line from drifting into a naming trap where the hottest replay is relabeled as the cooled retained object.
- Observed Result: The review concluded that `V116L` was methodologically wrong: it retained `earliest_visible_reference`, even though `V116K` already showed that the cleanest cooled variant was `double_confirm_late_quarter`. The triage therefore overruled `V116L`, demoted `earliest_visible_reference` to a hot upper-bound audit line, and selected `double_confirm_late_quarter` as the only corrected cooled-shadow retained candidate.
- Side Effects / Risks: The corrected retained object is cleaner, but still sits on the same visible-only candidate family and cannot be promoted. The main gain here is methodological integrity, not immediate tradability.
- Conclusion: The three-run cadence did exactly what it was supposed to do: it caught a drift back toward hot replay worship and forced the retained object back into alignment with the stated cooling objective.
- Next Step: Freeze the corrected retained object explicitly and continue future visible-only work from that corrected reference rather than from `V116L`.


### JOURNAL-0232 The corrected cooled-shadow retained object restores consistency between the heat-trim family and the carried-forward candidate

- Date: 2026-04-02
- Author: Codex
- Title: Replace the mistaken V116L retained object with a corrected cooled visible-only shadow reference
- Related Decision: DEC-0232
- Related Runs: V116N
- Protocol Version: protocol_v1.16
- Hypothesis: If the adversarial triage is accepted, then the project should immediately carry forward the corrected cooled retained object rather than leaving the mistaken `V116L` result in place.
- What Changed: Built `V116N` to freeze `double_confirm_late_quarter` as the corrected cooled-shadow retained candidate and explicitly separate it from the hot upper-bound `earliest_visible_reference`.
- Expected Impact: Give the visible-only family a coherent retained object that can be reused in later candidate-only validations without confusing it with the hottest replay line.
- Observed Result: The corrected retained object is materially less hot than the previous retained line, while still preserving a substantial replay delta over the repaired baseline.
- Side Effects / Risks: This does not solve the deeper sample-fragility problem; it only fixes the immediate retention inconsistency.
- Conclusion: `V116N` should be treated as the authoritative carried-forward cooled visible-only shadow reference, while `V116L` becomes part of the audit trail rather than the current retained truth.
- Next Step: Use `V116N` instead of `V116L` whenever the project refers to the retained cooled visible-only shadow candidate.


### JOURNAL-0233 The corrected retained object survived wider repaired-window revalidation, but only as a thinner candidate-only survivor

- Date: 2026-04-02
- Author: Codex
- Title: Revalidate the corrected cooled visible-only shadow candidate on the wider repaired under-exposure window
- Related Decision: DEC-0233
- Related Runs: V116O, V116P
- Protocol Version: protocol_v1.16
- Hypothesis: If `double_confirm_late_quarter` is truly the right retained cooled-shadow object, then it should retain some repaired-window explanatory power even after the V116M/V116N correction.
- What Changed: Built `V116O` to compare the corrected cooled retained object against the hot upper-bound reference on the wider repaired under-exposure window, then formalized the next triage in `V116P`.
- Expected Impact: Determine whether the corrected retained object deserves replay-facing expansion or merely continued candidate-only survival.
- Observed Result: The corrected retained object remained cleaner than the hot upper bound, but only hit `3/6` repaired days and `6` rows total. This was enough to keep it alive, but not enough to justify new replay-facing expansion.
- Side Effects / Risks: The main risk shifted from retention incoherence to thin repaired-window evidence. The line is now methodologically cleaner but still too narrow.
- Conclusion: `double_confirm_late_quarter` survives as the only retained visible-only candidate, but it survives as a thinner candidate-only object, not as a replay-ready winner.
- Next Step: Expand the repaired-window sample before doing anything else replay-facing on this visible-only family.


### JOURNAL-0234 The project widened the repaired-window audit surface so visible-only work stops circling the same 6-day family

- Date: 2026-04-02
- Author: Codex
- Title: Freeze an expanded repaired-window manifest for the next visible-only candidate audits
- Related Decision: DEC-0234
- Related Runs: V116Q
- Protocol Version: protocol_v1.16
- Hypothesis: If the current blocker is repaired-window thinness rather than retention coherence, then the next step should widen the audit surface before replay expansion.
- What Changed: Built `V116Q` to freeze an expanded repaired-window manifest that contains all `10` remaining under-exposed strong days from `V114H`, while marking which `6` rows came from the original repaired top-miss family.
- Expected Impact: Break the visible-only line out of the same small repaired-window orbit without pretending that replay expansion has already been justified.
- Observed Result: The audit surface widened from `6` to `10` days, adding `4` new repaired under-exposed strong days for future candidate-only validation.
- Side Effects / Risks: This widens the CPO audit surface, but it is still inside the same family and therefore still not cross-family evidence.
- Conclusion: The visible-only line now has a wider repaired-window surface available for the next validation step, which is the correct move before any further replay-facing expansion.
- Next Step: Use the expanded 10-day manifest as the next visible-only candidate revalidation surface.


### JOURNAL-0235 The Q/R/S three-run review flipped the visible-only problem statement from signal death to candidate-base blindness

- Date: 2026-04-02
- Author: Codex
- Title: Freeze the Q/R/S triage and stop blaming zero new-day hits on the corrected cooled candidate alone
- Related Decision: DEC-0235
- Related Runs: V116Q, V116R, V116S, V116T
- Protocol Version: protocol_v1.16
- Hypothesis: If the widened repaired-window validation is failing because the intraday candidate base never generated rows for the new days, then further visible-only replay or threshold tuning would be methodologically misplaced.
- What Changed: Formalized the Q/R/S triage into `V116T` and elevated the candidate-base coverage gap to the authoritative current blocker.
- Expected Impact: Redirect effort away from replay-facing visible-only experiments and back onto the intraday table-construction layer.
- Observed Result: The triage showed that the corrected cooled candidate still deserves candidate-only survival, but the zero new-day hit result in `V116R` cannot be read cleanly until the three true gap days have add-vs-hold rows.
- Side Effects / Risks: Progress temporarily looks slower because the project is backfilling infrastructure rather than chasing a new replay delta.
- Conclusion: The visible-only line was not ready for another replay-facing argument; it first needed a candidate-base repair.
- Next Step: Rebuild the expanded-window add-vs-hold action-timepoint rows for the three true gap days.


### JOURNAL-0236 The project repaired the expanded-window intraday candidate base by appending six new add-vs-hold rows

- Date: 2026-04-02
- Author: Codex
- Title: Rebuild add-vs-hold intraday action-timepoint rows for the three true expanded-window gap days
- Related Decision: DEC-0236
- Related Runs: V116U
- Protocol Version: protocol_v1.16
- Hypothesis: If the blind spot is table-construction rather than signal failure, then rebuilding the three true gap days should append new candidate rows without changing the original PCA geometry.
- What Changed: Queried fresh Baostock 5/15/30/60-minute bars for `300308` and `300502` on `2023-11-07`, `2024-01-18`, and `2024-01-23`, rebuilt the feature rows, projected them into the existing PCA space, and merged the resulting six add-vs-hold rows back into an expanded-window PCA band table.
- Expected Impact: Close the candidate-base blind spot while preserving comparability with all earlier visible-only PCA work.
- Observed Result: The rebuild appended `6` new rows across `3` days and grew the merged expanded-window PCA table to `456` rows.
- Side Effects / Risks: The new rows include both clearly positive and mixed/soft outcomes, so the rebuild removes the coverage excuse but may expose the visible-only line to harsher validation.
- Conclusion: The data-layer blind spot is no longer hypothetical; it has been concretely repaired.
- Next Step: Re-run the expanded-window coverage audit on the merged PCA band table.


### JOURNAL-0237 The post-rebuild re-audit confirmed that all true held-mature coverage gaps are closed

- Date: 2026-04-02
- Author: Codex
- Title: Verify that the expanded-window action-timepoint rebuild actually removed the three true candidate-base blind spots
- Related Decision: DEC-0237
- Related Runs: V116V
- Protocol Version: protocol_v1.16
- Hypothesis: If the V116U rebuild succeeded, then the widened repaired-window surface should no longer contain any held-mature days without add-vs-hold candidate rows.
- What Changed: Re-ran the `V116S`-style coverage audit on the merged PCA band table produced by `V116U`.
- Expected Impact: Establish a clean precondition for the next corrected cooled visible-only validation pass.
- Observed Result: The re-audit showed `days_with_add_candidate_rows = 9`, `days_with_held_mature_symbols = 9`, and `true_coverage_gap_day_count_after_rebuild = 0`. The only remaining day without add candidates is `2023-04-28`, which has no held mature symbols and therefore is not an add-space miss.
- Side Effects / Risks: The project no longer gets to explain weak expanded-window validation by blaming candidate-base coverage; the next validation must stand or fail on actual signal quality.
- Conclusion: The widened repaired-window candidate base is now structurally complete enough for another visible-only candidate validation pass.
- Next Step: Re-run corrected cooled-shadow expanded-window validation on the rebuilt candidate base and read the line again from there.


### JOURNAL-0238 The rebuilt-base expanded-window validation finally produced a real new-day hit for the corrected cooled candidate

- Date: 2026-04-02
- Author: Codex
- Title: Re-run corrected cooled visible-only validation on the rebuilt expanded-window candidate base
- Related Decision: DEC-0238
- Related Runs: V116W
- Protocol Version: protocol_v1.16
- Hypothesis: If the visible-only line looked dead on new expanded-window days mainly because the candidate base was missing rows, then the corrected cooled candidate should begin to hit at least some new days once the coverage repair is in place.
- What Changed: Re-ran the `V116R`-style expanded-window validation using the merged rebuilt PCA band table from `V116U` instead of the original thin base.
- Expected Impact: Distinguish between true signal death and candidate-base blindness on the newly added repaired-window days.
- Observed Result: The corrected cooled candidate moved from `new_hit_day_count = 0` to `new_hit_day_count = 1`, while the hot upper bound expanded to `new_hit_day_count = 3`. The corrected cooled line now hits `8` rows across `4` days with `positive_expectancy_hit_rate = 0.75` and `avg_expectancy_proxy_3d = 0.098337`, which is cleaner than the hot upper bound but still materially thinner.
- Side Effects / Risks: The new-day hit only appears on `2024-01-18`, not across all rebuilt days, so the visible-only line is not broadly revived; it is only partially rescued by the coverage repair.
- Conclusion: The coverage repair mattered. The corrected cooled candidate was not simply dead on the expanded window, but its external extension remains narrow and candidate-only.
- Next Step: Keep the line candidate-only, preserve future labels as audit-only, and use the next three-run adversarial review to decide whether this partial rescue justifies any further visible-only work.


### JOURNAL-0239 The rebuilt-day contrast closed the coverage chapter and exposed the remaining quality gate

- Date: 2026-04-02
- Author: Codex
- Title: Compare the three rebuilt expanded-window days side by side after the coverage repair
- Related Decision: DEC-0239
- Related Runs: V116X
- Protocol Version: protocol_v1.16
- Hypothesis: If the corrected cooled visible-only line only converts one rebuilt new day after coverage repair, then the remaining difference should be explained by signal quality rather than by missing rows or broken timing.
- What Changed: Built `V116X` to compare `2023-11-07`, `2024-01-18`, and `2024-01-23` directly on rebuilt rows plus rebuilt-base validation hits, using only the repaired data surface.
- Expected Impact: Force the project to stop re-litigating coverage and timing when the remaining issue is actually the cooled gate's quality discriminator.
- Observed Result: `2024-01-18` became the only rebuilt new day that converts into a corrected cooled hit. `2023-11-07` stayed positive but late-only, while `2024-01-23` stayed late-only and weak. Coverage is no longer the live blocker.
- Side Effects / Risks: The contrast is still same-family and narrow. It clarifies the current problem, but it does not create promotable evidence by itself.
- Conclusion: The visible-only family's current problem is now quality discrimination after coverage repair, not timing repair and not missing rows.
- Next Step: Keep the line candidate-only and make the next visible-only step quality-facing rather than timing-facing.


### JOURNAL-0240 The U/V/W adversarial review froze the visible-only line at the quality-discrimination stage

- Date: 2026-04-02
- Author: Codex
- Title: Use the next three-run review to stop replay-facing expansion after the rebuilt-base validation
- Related Decision: DEC-0240
- Related Runs: V116U, V116V, V116W, V116Y
- Protocol Version: protocol_v1.16
- Hypothesis: If the three-run cadence is doing its job, then the review after `V116U/V116V/V116W` should distinguish a partially rescued candidate line from a replay-ready law.
- What Changed: Built `V116Y` to freeze the U/V/W triage using the repaired-base validation plus the rebuilt-day contrast, and incorporated the convergent views of the three adversarial reviewers.
- Expected Impact: Keep the visible-only line from drifting back into replay-first expansion immediately after the coverage repair succeeded.
- Observed Result: The review accepted that coverage is fixed and that the corrected cooled candidate was partially rescued, but still blocked promotion and replay-facing expansion. The line remains candidate-only, with quality discrimination now defined as the current main problem.
- Side Effects / Risks: The line now looks slower-moving because the next step is quality-side work rather than another replay delta. That is a methodological constraint, not a sign that the line is dead.
- Conclusion: The three-run cadence worked again: it kept a fragile same-family candidate alive without letting it harden into a replay-facing law.
- Next Step: Keep rebuilt-row future labels audit-only and only continue visible-only work if the next step directly targets quality-side discrimination.


### JOURNAL-0241 The first quality-side cooled refinement showed that the visible-only family is effectively PC1-driven

- Date: 2026-04-02
- Author: Codex
- Title: Sweep visible-score quality thresholds while keeping the cooled timing structure fixed
- Related Decision: DEC-0241
- Related Runs: V116Z
- Protocol Version: protocol_v1.16
- Hypothesis: If the current blocker is quality discrimination rather than timing or coverage, then holding the cooled timing structure fixed and sweeping only visible-score quantiles should reveal whether a cleaner quality-side variant exists.
- What Changed: Built `V116Z` to re-run the corrected cooled visible-only line on the rebuilt expanded-window base while changing only the visible-score quality gate (`q=0.20`, `0.25`, `0.33`, `0.40`) and explicitly auditing whether PC2 is ever a real active axis.
- Expected Impact: Distinguish whether the next visible-only step should still be framed as a two-dimensional `pc1/pc2` family or whether it has effectively collapsed into one PC1-driven line.
- Observed Result: `q=0.25` and `q=0.33` were effectively identical, `q=0.20` became narrower and weaker, `q=0.40` became hotter and noisier, and the retained family never meaningfully activated PC2. The cooled line is therefore effectively PC1-driven at this stage.
- Side Effects / Risks: This is still same-board same-family evidence. The main value is methodological narrowing, not a new promotion candidate.
- Conclusion: The quality-side cooled refinement did not create a new winner; it proved that the current visible-only family has already collapsed to a narrow PC1-driven plateau.
- Next Step: Freeze the current quality-side reference and stop regrinding the same quantile family.


### JOURNAL-0242 The quality-side cooled retention closed the current quantile loop instead of chasing another local optimum

- Date: 2026-04-02
- Author: Codex
- Title: Freeze `cooled_q_0p25` as the quality-side cooled reference and demote the rest to shadow or rejection status
- Related Decision: DEC-0242
- Related Runs: V117A
- Protocol Version: protocol_v1.16
- Hypothesis: If the first quality-side refinement pass only produces a plateau, then the correct move is to freeze a reference variant and stop same-family quantile carving.
- What Changed: Built `V117A` to freeze the retention result from `V116Z`, keeping `cooled_q_0p25` as the retained quality-side cooled reference, `cooled_q_0p33` as an equivalent shadow, and rejecting the hotter or narrower neighbors.
- Expected Impact: Prevent the visible-only line from slipping back into endless threshold tuning without actually adding new information.
- Observed Result: The retained variant stayed `cooled_q_0p25`, `cooled_q_0p33` was formally recognized as equivalent rather than better, and the family was frozen as effectively PC1-driven.
- Side Effects / Risks: Progress now looks flatter because the project deliberately ended a local same-family search rather than squeezing one more replay delta out of it.
- Conclusion: The current quantile loop is closed. Any further visible-only work now needs a genuinely new discriminator, not another pass over the same thresholds.
- Next Step: If this line continues, the next step should be either a new quality-side discriminator or the next three-run adversarial review, not more quantile grinding.


### JOURNAL-0243 The cooled_q_0p25 contrast made the current visible-only boundary explicit

- Date: 2026-04-02
- Author: Codex
- Title: Turn the rebuilt-new-day separation into a retained-variant-specific quality contrast
- Related Decision: DEC-0243
- Related Runs: V117B
- Protocol Version: protocol_v1.16
- Hypothesis: Once `cooled_q_0p25` is frozen as the retained quality-side reference, the project should explicitly state what this retained line accepts and rejects instead of leaving that boundary implicit.
- What Changed: Built `V117B` to compare the three rebuilt new days against the retained `cooled_q_0p25` quality standard using a small set of explicit quality axes plus the rebuilt-day contrast already frozen in `V116X`.
- Expected Impact: Make the visible-only boundary easier to reason about and easier to preserve without sliding back into replay-first improvisation.
- Observed Result: `2024-01-18` remained the only rebuilt new day that satisfies the retained standard. `2023-11-07` now reads as the clearest example of a late-only but otherwise decent day, while `2024-01-23` reads as late and materially weak.
- Side Effects / Risks: This clarifies the current same-family boundary, but it does not solve the deeper generalization problem.
- Conclusion: The current visible-only line is no longer just “a narrow candidate”; it now has an explicit retained boundary that can be referred to without re-deriving it every time.
- Next Step: If this line continues, the next move should be a genuinely new quality-side discriminator rather than another pass over timing, coverage, or quantile tuning.


### JOURNAL-0244 The continuation-integrity score added quality information but failed the standalone-law test

- Date: 2026-04-02
- Author: Codex
- Title: Audit the new visible-only quality score and demote it to a component instead of a law
- Related Decision: DEC-0244
- Related Runs: V117C, V117D
- Protocol Version: protocol_v1.17
- Hypothesis: A new score can be worth keeping even if it is not strong enough to replace the retained cooled boundary, as long as it carries visible-only quality information that later audits can reuse.
- What Changed: Built `V117D` to test whether the `continuation_integrity_score_candidate` from `V117C` could stand alone against the current `cooled_q_0p25` retained line and the hot-only set.
- Expected Impact: Distinguish between a score that is merely descriptive and a score that is already strong enough to become a replay-facing discriminator.
- Observed Result: The score clearly separated retained hits from hot-only rows on average, but its best standalone threshold was too strict to preserve the retained rebuilt day `2024-01-18`. Lowering the threshold enough to keep that day would introduce materially more hot-only leakage.
- Side Effects / Risks: This slows down visible-only promotion because the new score is useful but not decisive.
- Conclusion: The continuation-integrity score is real, but only as a quality component. It should help later audits, not replace the retained cooled boundary or timing gate.
- Next Step: Keep the score candidate-only and only combine it with already-retained visible-only structure if later work still justifies continuing this line.


### JOURNAL-0245 The three-run adversarial review formally ended the continuation-integrity branch as a mainline candidate

- Date: 2026-04-02
- Author: Codex
- Title: Use the three-run review cadence to demote a promising descriptive score before it silently turns into policy
- Related Decision: DEC-0245
- Related Runs: V117C, V117D, V117E, V117F
- Protocol Version: protocol_v1.17
- Hypothesis: A three-run adversarial review should be able to stop a branch that looks attractive descriptively but fails the stronger tests of standalone usability and retained-set refinement.
- What Changed: After `V117C` discovered the score and `V117D/V117E` tested it, `V117F` froze the three-agent review outcome: the score has explanatory value but not enough robust decision value to remain a mainline candidate.
- Expected Impact: Prevent the project from sliding back into same-family refinement on a branch that no longer deserves replay-facing resources.
- Observed Result: All three reviewers converged on the same answer: the continuation-integrity score does not justify further mainline investment. It survives only as an explanatory audit field.
- Side Effects / Risks: This deliberately narrows the visible-only line and forces the next step to be a genuinely new discriminator rather than another extension of the same branch.
- Conclusion: The three-run cadence worked. It stopped a branch that could easily have looked “promising enough” if we had kept staring only at descriptive gaps.
- Next Step: Move on to a genuinely new quality-side discriminator and keep the continuation-integrity score only as a supporting explanatory field.


### JOURNAL-0246 The breakout-damage branch survived the three-run review and replaced continuation-integrity as the active candidate line

- Date: 2026-04-02
- Author: Codex
- Title: Open a new quality-side branch around breakout efficiency and damage containment, then keep it alive only after retained-set refinement and adversarial review
- Related Decision: DEC-0246
- Related Runs: V117G, V117H, V117I, V117J
- Protocol Version: protocol_v1.17
- Hypothesis: A genuinely new quality-side branch should look different from the old continuation line and should still separate positive vs weak rows inside the retained family before it deserves further attention.
- What Changed: Built `V117G` to discover a new breakout-damage score, `V117H` to audit it against `q25_hit` vs `hot_only`, `V117I` to test retained-set refinement, and `V117J` to run the scheduled three-agent adversarial review.
- Expected Impact: Replace the demoted continuation-integrity branch with a stronger candidate line if and only if the new branch survives both external and retained-set scrutiny.
- Observed Result: The new branch survived. It separated `q25_hit` from `hot_only`, still separated positive vs weak retained rows, and all three reviewers agreed it is stronger than the old branch. They also agreed the sample is too small for promotion.
- Side Effects / Risks: The branch now becomes the new focus, which risks over-investment unless the project remembers it is still based on a small retained sample.
- Conclusion: The breakout-damage branch is the new active candidate quality-side line. It is alive, but still candidate-only.
- Next Step: Continue only through wider external audit or larger-sample validation, not replay-facing promotion.


### JOURNAL-0247 The three-run review killed the reverse/heuristic side branch before it could distract the CPO mainline

- Date: 2026-04-02
- Author: Codex
- Title: Use the K/L/M review cadence to demote a broad reverse-signal branch and keep heuristic pattern ideas in protocol space only
- Related Decision: DEC-0247
- Related Runs: V117K, V117L, V117M, V117N
- Protocol Version: protocol_v1.17
- Hypothesis: A reverse branch that looks acceptable in a broad pool but fails once conditioned into the actual main-uptrend held-position problem should be demoted before it starts competing with the stronger quality-side mainline.
- What Changed: Built `V117K` to discover a broad reverse-signal score, `V117L` to formalize human heuristic quantization as objective proxy families, `V117M` to condition the reverse branch into the true problem setting, and `V117N` to freeze the three-agent review outcome.
- Expected Impact: Prevent the project from drifting into weak downside-story branches just because they sound intuitive or psychologically appealing.
- Observed Result: The reverse branch weakened materially once conditioned into the actual use case, and the heuristic quantization layer remained protocol-level only. All three reviewers converged that both should be demoted out of the mainline.
- Side Effects / Risks: The current project will stay more asymmetric, with much more energy invested in the positive-side quality branch than in explicit reverse-signal modeling.
- Conclusion: The three-run cadence worked again. It stopped an intuitive but weak side branch before it could absorb disproportionate research effort.
- Next Step: Keep reverse/heurstic ideas only as low-priority auxiliary material and continue the mainline on the stronger breakout-damage candidate branch.


### JOURNAL-0248 The broader external-pool and time-split audits broke the breakout-damage mainline, so the project deliberately stopped before replay-facing drift

- Date: 2026-04-02
- Author: Codex
- Title: Let the O/P/Q review cycle kill the strongest visible-only candidate once it stops surviving wider external scrutiny
- Related Decision: DEC-0248
- Related Runs: V117O, V117P, V117Q, V117R
- Protocol Version: protocol_v1.17
- Hypothesis: A branch that survives retained-set refinement may still deserve demotion if it fails on a broader `add_vs_hold` pool and becomes unstable under time-split validation.
- What Changed: Built `V117O` to move breakout-damage onto a wider add-pool, `V117P` to test chronological stability, `V117Q` to inspect whether reverse/human layers explain its false positives, and `V117R` to freeze the three-agent adversarial outcome.
- Expected Impact: Stop the project from confusing a neat visible-only candidate with a robust replay-facing add discriminator once broader validation contradicts the earlier retained-set story.
- Observed Result: The branch failed the broader test surface. External-pool mean separation turned negative, time-split stability fell to weak levels, and the reverse/human layers helped explain false positives without rescuing the branch's mainline status.
- Side Effects / Risks: This removes the current best positive-side candidate and forces the project to reopen discovery, which may feel like losing progress.
- Conclusion: The cadence worked again. It prevented the project from promoting a candidate that looked strongest only on a narrow retained surface.
- Next Step: Keep breakout-damage only as an explanatory component and reopen a fresh quality-side search rather than continuing same-family replay-facing refinement.


### JOURNAL-0249 Reopening from the broader add pool produced a better branch than breakout-damage, but not one that deserves replay-facing status yet

- Date: 2026-04-02
- Author: Codex
- Title: Let the S/T/U cycle keep a new candidate alive only because it survives the broader pool better, not because it is already stable
- Related Decision: DEC-0249
- Related Runs: V117S, V117T, V117U, V117V
- Protocol Version: protocol_v1.17
- Hypothesis: A new branch discovered directly from the broader `add_vs_hold` pool should be treated as more trustworthy than one grown inside a tiny retained family, but it still must survive crude time-split validation before it deserves stronger investment.
- What Changed: Built `V117S` for discovery, `V117T` for broader external audit, `V117U` for time-split validation, and `V117V` for the scheduled three-agent review.
- Expected Impact: Replace the post-breakout vacuum with a candidate line that is at least externally cleaner than the degraded branch, without pretending that this makes the new line replay-ready.
- Observed Result: The cooling-reacceleration branch kept a positive broader external-pool gap and materially stronger balanced accuracy than breakout-damage, but still failed the stricter stability test with `min_test_balanced_accuracy = 0.375`.
- Side Effects / Risks: The project now has a new live candidate, but also a strong temptation to over-interpret its external-pool success and ignore the time-split weakness.
- Conclusion: The branch deserves one more non-replay audit cycle, but nothing more. The cadence again blocked replay-facing drift before the evidence justified it.
- Next Step: Use the next cycle only to test false-positive control and temporal robustness; if it still fails, cut it quickly.


### JOURNAL-0250 The false-positive-control refinement materially improved the cooling-reacceleration branch, but not enough to loosen the replay ban

- Date: 2026-04-02
- Author: Codex
- Title: Let the W/X/Y cycle harden the candidate without pretending it is already replay-ready
- Related Decision: DEC-0250
- Related Runs: V117W, V117X, V117Y, V117Z
- Protocol Version: protocol_v1.17
- Hypothesis: A narrow visible-only overheat-control layer can improve a fragile quality-side candidate by reducing false positives, and if the improvement survives crude time splits the branch may deserve continued candidate investment without yet becoming replay-facing.
- What Changed: Built `V117W` to add an overheat-control layer, `V117X` to test whether the controlled score improved broader external-pool discrimination, `V117Y` to test whether that improvement held across year splits, and `V117Z` to freeze the scheduled three-agent review outcome.
- Expected Impact: Convert the cooling-reacceleration line from a shaky one-more-cycle candidate into a more disciplined candidate that is worth continued auditing, while still blocking premature replay expansion.
- Observed Result: The branch improved materially on both external-pool and time-split metrics. The three reviewers converged that this was a real refinement, not noise, but also converged that the branch still lacks enough negative rejection strength and sample breadth to justify shadow replay.
- Side Effects / Risks: Because the sample remains small, the branch may still fail later under a wider or dirtier surface despite the apparent improvement.
- Conclusion: The cadence worked again. It allowed the project to keep a genuinely improved candidate alive while still refusing replay-facing drift.
- Next Step: Continue only with candidate-only out-of-set false-positive-control work; do not loosen the replay ban yet.


### JOURNAL-0251 The add-vs-entry branch attacks the right contamination mode, but chronology still flips its threshold behavior

- Date: 2026-04-02
- Author: Codex
- Title: Let the B/C/D cycle confirm the right problem and still block replay because chronology remains unstable
- Related Decision: DEC-0251
- Related Runs: V118A, V118B, V118C, V118D, V118E
- Protocol Version: protocol_v1.18
- Hypothesis: Once the retained cooling-reacceleration branch is shown to leak mainly into strong entry, a dedicated add-vs-entry discriminator should be more useful than another generic false-positive filter.
- What Changed: Built `V118A` to prove the current contamination mode is add-vs-entry, `V118B` to discover a dedicated separation score, `V118C` to audit that score on the full positive-add versus all-entry surface, `V118D` to test chronology stability, and `V118E` to freeze the three-agent review outcome.
- Expected Impact: Move the project away from generic heat control toward a more problem-specific discriminator that can eventually tell when a move should be treated as add rather than just a strong new entry.
- Observed Result: The branch is directionally right and externally meaningful, but chronology still flips how the threshold fails: some splits pass all add and reject no entry, while another rejects entry better but loses add recall.
- Side Effects / Risks: This creates a tempting new branch that looks more semantically correct than the old one, yet may still collapse under broader chronology or out-of-set pressure.
- Conclusion: The cadence worked again. It kept the branch alive because the problem framing improved, but still blocked replay-facing drift because time-split behavior is not trustworthy yet.
- Next Step: Continue one more non-replay adversarial cycle focused on chronology-hardening or out-of-set challenge; do not relax the replay ban.


### JOURNAL-0252 The strengthened add-vs-entry branch still failed once role holdouts exposed that chronology weakness was really role-year entanglement

- Date: 2026-04-02
- Author: Codex
- Title: Let the F/G/H cycle kill a semantically correct branch once its object-shift failure becomes undeniable
- Related Decision: DEC-0252
- Related Runs: V118F, V118G, V118H, V118I
- Protocol Version: protocol_v1.18
- Hypothesis: If the add-vs-entry branch truly captures an action distinction rather than a sample pocket, it should remain viable even after narrowing the entry surface to strong entries and then challenging the branch under role-family holdouts.
- What Changed: Built `V118F` to audit only against strong entry lookalikes, `V118G` to hold out role families, `V118H` to explain chronology failure through role-year entanglement, and `V118I` to freeze the three-agent review outcome.
- Expected Impact: Distinguish between a branch that merely needed a stronger adversarial surface and one that still collapses once the surface is widened in the correct dimension.
- Observed Result: The branch remained strong on the narrowed strong-entry surface, but role-family holdouts broke it badly and showed that chronology failure was partly object-shift: entry rows are concentrated in a late role-year pocket, while positive adds live elsewhere.
- Side Effects / Risks: This removes another branch that felt more semantically correct than earlier lines, increasing pressure on the next discovery attempt.
- Conclusion: The cadence worked again. It stopped the project from mistaking a conceptually correct branch for a stable branch.
- Next Step: Keep this branch only as an explanatory role-year entanglement layer and reopen discovery on a fresh line instead of continuing same-family training.


### JOURNAL-0253 Reclassifying degraded branches under expectancy logic rescued exactly one branch above pure explanation: breakout-damage

- Date: 2026-04-02
- Author: Codex
- Title: Let the expectancy lens distinguish between truly dead branches and branches that still deserve to survive as soft components
- Related Decision: DEC-0253
- Related Runs: V117F, V117N, V117R, V118I, V118J
- Protocol Version: protocol_v1.18
- Hypothesis: The older candidate-vs-explanatory framing may throw away branches that no longer deserve hard-law status but still contain useful expectancy information for soft penalty or correction layers.
- What Changed: Asked all three reviewers to revisit the degraded legacy branches under a richer taxonomy and then froze the reclassification in `V118J`.
- Expected Impact: Reduce waste from previous demotions without reopening weak branches as active candidates, and make the branch graveyard more useful for future expectancy-aware stacking.
- Observed Result: All three reviewers converged that only `breakout_damage` deserves rescue above pure explanation. The other degraded lines remain explanatory only because they either never created real training gain or are dominated by object-shift artifacts.
- Side Effects / Risks: Because breakout-damage is now kept in a middle state, there is renewed risk of accidentally letting it drift back into candidate or replay-facing status.
- Conclusion: The expectancy lens changed the taxonomy, but not permissively. It rescued exactly one branch and kept the rest demoted.
- Next Step: Reuse breakout-damage only as a soft expectancy component and keep the rest in the explanatory archive.


### JOURNAL-0254 The breakout-damage rescue stayed valid, but active integration still failed, so the branch is now archived rather than active

- Date: 2026-04-02
- Author: Codex
- Title: Let the K/L/M cycle prove that a rescued soft component can survive conceptually yet still fail to earn active integration
- Related Decision: DEC-0254
- Related Runs: V118K, V118L, V118M, V118N
- Protocol Version: protocol_v1.18
- Hypothesis: A branch can deserve rescue as a soft expectancy component without necessarily improving the live candidate when actively integrated.
- What Changed: Built `V118K` to test integration weights, `V118L` to re-audit the best integrated variant, `V118M` to compare chronology behavior, and `V118N` to freeze the reviewer consensus.
- Expected Impact: Separate “preserve this idea in the archive” from “spend active model budget integrating it now.”
- Observed Result: The best active integration weight stayed at `alpha = 0.0`, meaning no integration at all. The branch therefore kept conceptual value but earned no active role in the current line.
- Side Effects / Risks: Archiving may reduce near-term reuse of a still-interesting quality-side idea.
- Conclusion: The expectancy taxonomy held up under pressure. It did not reopen breakout-damage as an active line just because it survived demotion.
- Next Step: Leave breakout-damage archived and continue the mainline without active integration from it.
- ### JOURNAL-0255 The reclaim-absorption idea felt trader-intuitive, but the first three-run block showed it was directionally wrong
-
- Date: 2026-04-02
- Author: Codex
- Title: Use the three-run cadence to kill a plausible-sounding quality branch before it absorbs another week of attention
- Related Decision: DEC-0255
- Related Runs: V118O, V118P, V118Q, V118R
- Protocol Version: protocol_v1.18
- Hypothesis: Positive add windows in a diffusion-main-uptrend board might show better intraday absorption and reclaim quality than negative add windows.
- What Changed: Built `V118O` for discovery, `V118P` for broader external-pool audit, `V118Q` for immediate time-split validation, and `V118R` to freeze the three-agent triage.
- Expected Impact: Either discover a new quality-side branch that is genuinely different from cooling and breakout-damage, or kill the idea fast if it fails the basic external and chronology tests.
- Observed Result: The branch failed both core tests. The full-pool gap was negative, and chronology remained unstable, so all three reviewers converged on `dead`.
- Side Effects / Risks: This shrinks the active branch set again and reinforces how hard it is to find a stable quality-side discriminator on the current CPO mid-frequency surface.
- Conclusion: The cadence worked as intended. A plausible idea was not allowed to survive on intuition alone.
- Next Step: Reopen quality-side discovery on a different axis and do not revisit reclaim-absorption unless the feature basis itself changes materially.

### JOURNAL-0256 Sustained participation without chase is the first new post-reclaim branch that survived the initial three-run block

- Date: 2026-04-02
- Author: Codex
- Title: Let a live branch stay alive without letting it jump too early into replay
- Related Decision: DEC-0256
- Related Runs: V118T, V118U, V118V, V118W
- Protocol Version: protocol_v1.18
- Hypothesis: Positive add windows may be better characterized by persistent intraday occupancy and afternoon participation than by cooling or absorption language, as long as the close does not look like a late-session chase.
- What Changed: Built `V118T` for discovery, `V118U` for broader external-pool audit, `V118V` for immediate time-split validation, and `V118W` to freeze the three-agent triage.
- Expected Impact: Replace dead quality-side branches with a cleaner line that has broad-pool directionality while still obeying chronology discipline.
- Observed Result: The branch stayed positive on the broader add pool and achieved `best_balanced_accuracy = 0.727273`, but one holdout year still collapsed to `0.375`, so all reviewers converged on `candidate-only`.
- Side Effects / Risks: This line may still die in the next hardening cycle if the weak chronology bucket cannot be repaired without same-family overfitting.
- Conclusion: The branch is alive and worth one more cycle, but only because the protocol blocked premature replay-facing expansion.
- Next Step: Use the next cycle to harden false-positive control and temporal robustness, not to widen action or replay usage.

### JOURNAL-0257 The XYZ hardening cycle did not strengthen the sustained-participation branch, so the control line itself had to die

- Date: 2026-04-02
- Author: Codex
- Title: Let a live family survive while killing the hardening subline that failed to move the needle
- Related Decision: DEC-0257
- Related Runs: V118X, V118Y, V118Z, V119A
- Protocol Version: protocol_v1.19
- Hypothesis: A visible-only penalty on prior heat, late fade, and tail-volume overheat could reduce false positives enough to strengthen the sustained-participation non-chase branch without reopening replay.
- What Changed: Built `V118X` for the control discovery, `V118Y` for broader external-pool audit, `V118Z` for time-split validation, and `V119A` to freeze the three-way conclusion.
- Expected Impact: Either create a stronger non-replay hardening layer for the branch, or prove that same-family penalty tuning was not the right next move.
- Observed Result: The control changed almost nothing. External balanced accuracy stayed at `0.727273`, chronology stayed at `0.597222 / 0.375`, and `V118X` explicitly reported `control_helpful = false`.
- Side Effects / Risks: This removes the most obvious same-family hardening idea, leaving the parent branch alive but with less immediate room for simple refinement.
- Conclusion: The cadence worked again. It killed the hardening subline without overreacting and killing the parent family with it.
- Next Step: If the sustained-participation family continues, it must do so through a genuinely orthogonal hardening idea rather than more prior-heat or late-fade penalty tuning.

### JOURNAL-0258 Tushare data completion finally replaced proxy float-turnover context for the CPO cohort

- Date: 2026-04-02
- Author: Codex
- Title: Use the live token immediately and close a known data debt instead of postponing it behind more model work
- Related Decision: DEC-0258
- Related Runs: V119B, V119C
- Protocol Version: protocol_v1.19
- Hypothesis: A direct Tushare data pack for `daily_basic`, `moneyflow`, and `stk_limit` should materially improve the project's data basis because several later branches were still leaning on proxy float-share and turnover context.
- What Changed: Added a private-token Tushare client, bootstrapped the full bounded `CPO` cohort, wrote the three datasets into canonical repo data paths, and audited critical-field coverage.
- Expected Impact: Make later CPO training and replay work less dependent on proxy float/turnover assumptions and give the project a cleaner daily data surface before further branch discovery.
- Observed Result: The bootstrap completed with:
  - `daily_basic_rows = 15665`
  - `moneyflow_rows = 15665`
  - `stk_limit_rows = 15700`
  and the coverage audit confirmed the critical `daily_basic` and `stk_limit` fields are ready.
- Side Effects / Risks: This still does not provide minute-level Tushare data, so intraday add/reduce confirmation remains a separate problem.
- Conclusion: This was the right interruption. The project now has a harder daily data base for CPO instead of continuing to argue on proxy fields.
- Next Step: Treat the Tushare daily pack as the default float/turnover/limit reference in the next CPO data-facing steps.

### JOURNAL-0259 The first Tushare-backed orthogonal hardening line is the strongest new candidate since the replay repair, but one year bucket still blocks promotion

- Date: 2026-04-02
- Author: Codex
- Title: Let new daily data produce a materially better branch without immediately repeating the promotion mistake
- Related Decision: DEC-0259
- Related Runs: V119D, V119E, V119F, V119G
- Protocol Version: protocol_v1.19
- Hypothesis: Direct daily turnover, free-float, and moneyflow context from Tushare may supply the orthogonal hardening signal that the intraday-only quality branches could not stably produce.
- What Changed: Built `V119D` for discovery on add rows, `V119E` for broader external-pool audit, `V119F` for immediate year-split validation, and `V119G` to freeze the three-way adversarial conclusion.
- Expected Impact: Either create the first genuinely stronger post-replay hardening line, or prove that even better data still does not solve the branch instability problem.
- Observed Result: The branch materially outperformed the recent quality-side lines:
  - `V119E best_balanced_accuracy = 0.863636`
  - `V119F mean_test_balanced_accuracy = 0.75`
  - `V119F min_test_balanced_accuracy = 0.5`
  but `holdout_2024` still had `test_positive_recall = 0.0`, which blocked early promotion.
- Side Effects / Risks: Because this is the first branch in a while that looks genuinely strong, there is renewed risk of promoting too early out of relief rather than discipline.
- Conclusion: This is the strongest new orthogonal hardening line so far, but the protocol stayed disciplined and kept it at candidate-only.
- Next Step: Use the next cycle to understand the 2024 holdout failure surface before permitting any replay-facing use.

### JOURNAL-0260 The first combo branch finally improved both external ordering and chronology, but the protocol still refused replay until the weakest year bucket looks less fragile

- Date: 2026-04-02
- Author: Codex
- Title: Recognize the first actually stronger combo line without repeating the promotion error
- Related Decision: DEC-0260
- Related Runs: V119H, V119I, V119J, V119K
- Protocol Version: protocol_v1.19
- Hypothesis: Combining one live intraday participation signal with one new Tushare-backed turnover discipline signal may repair chronology weakness that neither branch can fully solve alone.
- What Changed: Built the minimal `participation_turnover_combo_score_candidate`, audited it on the broad add pool, validated it under year holdouts, and then froze the three-run adversarial conclusion.
- Expected Impact: Either produce the first clearly superior live combo branch, or prove that even careful orthogonal stacking still fails chronology and should be abandoned.
- Observed Result: The combo did improve both broad-pool ordering and chronology:
  - `V119I best_balanced_accuracy = 0.863636`
  - `V119J mean_test_balanced_accuracy = 0.791667`
  - `V119J min_test_balanced_accuracy = 0.666667`
  but the `holdout_2024` bucket still only reached `test_positive_recall = 0.333333`, so promotion stayed blocked.
- Side Effects / Risks: This branch now creates the strongest temptation yet to relax the replay gate too early, especially because it genuinely beats the single-family lines.
- Conclusion: The combo branch is alive and materially stronger, but the protocol correctly kept it at `candidate-only`.
- Next Step: Spend one more non-replay cycle on the remaining 2024 weakness before deciding whether the combo deserves a harder label.

### JOURNAL-0261 The first branch finally earned hard-candidate language, but only after a new daily capital-flow support term materially improved the weakest chronology bucket

- Date: 2026-04-02
- Author: Codex
- Title: Use one more orthogonal ELG-flow term to turn the strongest combo candidate into the first non-replay hard candidate
- Related Decision: DEC-0261
- Related Runs: V119L, V119M, V119N, V119O
- Protocol Version: protocol_v1.19
- Hypothesis: A narrow extra-large-order buy-sell support term may add exactly the missing daily capital-flow information that the participation-turnover combo still lacked in the 2024 holdout bucket.
- What Changed: Added `0.25 * z(elg_buy_sell_ratio)` to the existing participation-turnover combo, audited the new line on the external add pool, validated it under year holdouts, and then froze the three-run adversarial conclusion with explicit disagreement recorded.
- Expected Impact: Either prove that one more orthogonal capital-flow term can harden the best live branch into a real hard candidate, or show that the project is still overfitting the same small add pool geometry.
- Observed Result: The ELG-supported combo materially improved the live surface:
  - `V119M best_balanced_accuracy = 0.909091`
  - `V119N mean_test_balanced_accuracy = 0.875`
  - `V119N min_test_balanced_accuracy = 0.833333`
  - `holdout_2024 test_positive_recall = 0.666667`
  This was strong enough for two of three adversarial reviewers to upgrade it to hard-candidate language.
- Side Effects / Risks: Because the branch is now the first non-replay hard candidate, there is renewed risk of letting success itself weaken replay discipline.
- Conclusion: The project finally has a hard candidate, but only in non-replay form.
- Next Step: Spend exactly one more non-replay audit cycle on this line before allowing any discussion of replay-facing use.

### JOURNAL-0262 The first hard candidate did not survive the next adversarial cycle, which is exactly why the protocol needed that extra non-replay checkpoint

- Date: 2026-04-02
- Author: Codex
- Title: Let the object-shift and leakage surfaces overrule the excitement from the first hard-candidate promotion
- Related Decision: DEC-0262
- Related Runs: V119P, V119Q, V119R, V119S
- Protocol Version: protocol_v1.19
- Hypothesis: If the ELG-supported combo really deserved hard-candidate language, it should survive one more cycle of symbol holdout, role-family holdout, and out-of-set leakage review.
- What Changed: Ran the next non-replay adversarial block on the newly promoted branch and forced the protocol to reconsider its strongest current line under harder object-shift and leakage conditions.
- Expected Impact: Either confirm the branch as a true hard candidate, or prove that the promotion happened one cycle too early.
- Observed Result: The harder surfaces broke the branch:
  - symbol holdout `mean/min = 0.4375 / 0.375`
  - role holdout `mean/min = 0.440476 / 0.333333`
  - `entry leakage = 0.375`
  - `close leakage = 0.666667`
  This was enough to revoke the hard-candidate label.
- Side Effects / Risks: The project now has to admit that even its strongest recent branch still carries meaningful object and context entanglement.
- Conclusion: The hard-candidate promotion was useful precisely because the next cycle could falsify it; the branch is still alive, but only as candidate-only.
- Next Step: If the family continues, it must do so through de-entangling symbol/role geometry or cleaning leakage, not through replay expansion.

### JOURNAL-0263 The limit-band discipline idea improved the story more than it improved the model

- Date: 2026-04-02
- Author: Codex
- Title: Preserve the non-chase explanation, but stop pretending it is a live candidate branch
- Related Decision: DEC-0263
- Related Runs: V119V, V119W, V119X, V119Y
- Protocol Version: protocol_v1.19
- Hypothesis: A narrow daily limit-band discipline term might orthogonally repair the ELG-supported combo by rewarding add contexts that stay away from pure up-limit chase behavior.
- What Changed: Built a compact branch using `up_gap`, `close_to_up_band`, and `high_to_up_band`, then pushed it through discovery, broad external audit, chronology validation, and a scheduled three-reviewer triage.
- Expected Impact: Either uncover a real non-chase hardening term or prove that the idea is more explanatory than operational.
- Observed Result: The branch slightly improved the discovery gap, tied the parent externally, and then weakened chronology:
  - discovery gap `1.863218` vs parent `1.810537`
  - external `0.909091` vs parent `0.909091`
  - time-split mean/min `0.819445 / 0.666667` vs parent `0.875 / 0.833333`
  Two reviewers called it `explanatory_only`; one allowed only a very weak candidate interpretation.
- Side Effects / Risks: The project now has one more attractive-looking but budget-unworthy branch, which is useful as a reminder that intuitive market stories do not automatically deserve candidate status.
- Conclusion: The limit-band discipline line explains part of the non-chase intuition but does not improve the parent where it matters, so it should live only as explanation.
- Next Step: Stop touching this branch and move on to a genuinely new orthogonal discovery idea.

### JOURNAL-0264 The daily Tushare plane now looks locally exhausted, which is useful because it closes a whole class of tempting but weak next steps

- Date: 2026-04-02
- Author: Codex
- Title: Scan the remaining obvious daily-field variations once, then declare a stopline instead of opening endless micro-branches
- Related Decision: DEC-0264
- Related Runs: V119Z
- Protocol Version: protocol_v1.19
- Hypothesis: Even after the ELG-supported combo weakened, there might still be one last narrow orthogonal repair hidden inside the current Tushare daily field family.
- What Changed: Ran a consolidated stopline scan across the remaining obvious daily-data directions:
  - float/free-float and cap structure
  - medium-flow support
  - net-flow scaling
  - retail crowding
  - limit-band discipline
- Expected Impact: Either reveal one more viable narrow branch or prove that the current Tushare daily plane should be treated as locally exhausted.
- Observed Result: No scanned direction cleared the parent on both broad external and chronology surfaces:
  - `scan_candidate_count = 9`
  - `viable_increment_candidate_count = 0`
  - several tied the parent externally, but none improved chronology
- Side Effects / Risks: This closes off a psychologically comfortable area of work; future progress will require a harder shift to a new data plane rather than nicer variations on the same inputs.
- Conclusion: The daily Tushare field family is no longer the right place to keep searching for another narrow fix.
- Next Step: Move the next discovery cycle onto a different data plane instead of reopening daily-field micro-tuning.

### JOURNAL-0265 Reduce-side finally has a formal branch, which matters even if it is not yet promotable

- Date: 2026-04-03
- Author: Codex
- Title: Replace the stalled close-only refinement loop with a broader `reduce_vs_hold` board risk-off branch
- Related Decision: DEC-0265
- Related Runs: V121I, V121J, V121K
- Protocol Version: protocol_v1.21
- Hypothesis: The right next risk-side step is not another narrow close gate but a broader board risk-off signal that can tell us when to reduce before the system is forced into full close behavior.
- What Changed: Opened a new `reduce_vs_hold` branch using the enriched action table joined to Tushare daily context:
  - lower `board_avg_return`
  - lower `board_breadth`
  - higher `turnover_rate_f`
  - higher `volume_ratio`
  were treated as early de-risk structure rather than close-only collapse.
- Expected Impact: If valid, this would become the first genuinely broader downside candidate and would move the project from "soft close priors" toward a usable reduce-side grammar.
- Observed Result:
  - discovery mean gap `1.31783`
  - external best balanced accuracy `0.687336`
  - time-split mean/min `0.615348 / 0.525`
  - stability posture: `candidate_stable_enough_for_next_adversarial_review`
- Side Effects / Risks: The branch may still be too broad and may be capturing generic stress episodes rather than precise reduce semantics, so it must survive adversarial review before any stronger claim is made.
- Conclusion: This is the first risk-side line in a while that looks alive beyond soft-component status, which is a meaningful shift even though it is still far from replay-facing.
- Next Step: Run the next three-run adversarial review on `V121I/J/K` and decide whether the branch stays `candidate-only`, downgrades to soft-component, or dies.

### JOURNAL-0266 The first reduce-side branch survived adversarial review, which matters more than whether it feels glamorous

- Date: 2026-04-03
- Author: Codex
- Title: Keep the board risk-off reduce branch alive, but refuse to confuse survival with readiness
- Related Decision: DEC-0266
- Related Runs: V121I, V121J, V121K, V121L
- Protocol Version: protocol_v1.21
- Hypothesis: If the first formal reduce-side branch survived both broad external ranking and crude chronology, adversarial review would likely keep it alive rather than kill it.
- What Changed: Sent `V121I/J/K` through the three-reviewer adversarial cadence.
- Expected Impact: Either prove the branch is still too soft to matter, or validate that the project finally has a live downside candidate worth further narrowing.
- Observed Result:
  - `candidate_only` votes: `2`
  - `soft_component` votes: `1`
  - replay-facing remained unanimously blocked
  - the key numbers survived the review:
    - discovery gap `1.31783`
    - external best BA `0.687336`
    - time-split mean/min `0.615348 / 0.525`
- Side Effects / Risks: Keeping the branch alive may tempt premature execution use, especially because the project has been starved for downside progress; this is exactly why replay-facing remains blocked.
- Conclusion: The line is alive and deserves more narrowing budget, but not more trust than the evidence supports.
- Next Step: Continue only with non-replay reduce-side narrowing and reject any attempt to smuggle this branch into execution too early.

### JOURNAL-0267 The first reduce-side branch passed symbol holdout but failed the harsher question: does it really mean reduce?

- Date: 2026-04-03
- Author: Codex
- Title: Symbol generalization was not the bottleneck; cross-action specificity was
- Related Decision: DEC-0267
- Related Runs: V121L, V121M, V121N, V121O
- Protocol Version: protocol_v1.21
- Hypothesis: If the new reduce-side branch survived symbol holdout, the next likely bottleneck would be whether it stayed specific to reduce context rather than turning into a generic risk prior.
- What Changed:
  - `V121M` added a symbol-holdout audit.
  - `V121N` added an out-of-set false-positive audit across `add`, `entry`, and `close` contexts.
  - `V121O` froze the second adversarial verdict for the branch.
- Expected Impact: Either prove the branch is becoming a real reduce-side candidate or reveal that it is still too broad to distinguish reduce from general stress.
- Observed Result:
  - symbol holdout mean/min BA `0.631365 / 0.580508`
  - symbol generalization survives
  - but leakage is total at the current threshold:
    - `reduce_pass_rate = 1.0`
    - `add_leakage_rate = 1.0`
    - `entry_leakage_rate = 1.0`
    - `close_leakage_rate = 1.0`
- Side Effects / Risks: The branch is now psychologically dangerous because "survives symbol holdout" sounds stronger than it is; in reality, it still behaves like a broad risk prior rather than a discrete action selector.
- Conclusion: The reduce-side branch is alive, but the real next job is not more generalization checks; it is action-context separation.
- Next Step: Continue only with non-replay reduce-side narrowing aimed at separating reduce from add/entry/close contexts.

### JOURNAL-0268 The recent `1min` downside line survived, but the bridge did not

- Date: 2026-04-03
- Author: Codex
- Title: Keep the `1min` downside soft component isolated until the data can support a real bridge
- Related Decision: DEC-0268
- Related Runs: V122R, V122S, V122T, V122U, V122V
- Protocol Version: protocol_v1.22
- Hypothesis: If the recent `1min` downside soft component contained genuinely transferable risk information, either the historical bridge would have some legal overlap or the recent same-plane stack would beat the standalone score across both discovery and transfer.
- What Changed:
  - `V122S` audited the date overlap between the old historical reduce surface and the recent `1min` plane.
  - `V122T` tested a minimal same-plane stack that combined the standalone downside failure score with broad board-micro risk context.
  - `V122U` froze the attachment stopline.
  - `V122V` sent the bridge question through the three-reviewer adversarial cadence.
- Expected Impact: Either justify attaching the `1min` downside component into the broader downside stack or force the project to keep it isolated.
- Observed Result:
  - historical overlap day count: `0`
  - same-plane stack improved discovery gap `0.08154386 -> 0.10833396`
  - but did **not** improve the transfer metrics enough to matter:
    - q75 balanced accuracy `0.5206375 -> 0.51908727`
    - time-split mean `0.52515907 -> 0.52230714`
    - symbol-holdout mean `0.51487065 -> 0.51482082`
  - all three reviewers converged on the same posture: keep the standalone soft component, block attachment
- Side Effects / Risks: This freezes one tempting integration path and may feel slow, but it also prevents a recent-only component from quietly contaminating the broader downside stack.
- Conclusion: The `1min` downside line is alive, but only in isolation; the bridge is not.
- Next Step: Keep `V122R` as a standalone `soft_component` and wait for either historical `1min` coverage or a genuinely stronger same-plane increment before reopening attachment.
## JOURNAL-0269 V123A-D Orthogonal 1min Downside
- We explicitly stopped tuning the old recent `1min downside_failure` family and scanned for low-correlation alternatives instead.
- Three orthogonal candidates were tested on the same recent `1min` proxy label plane:
  - `churn_rejection_score`
  - `vwap_rejection_imbalance_score`
  - `gap_exhaustion_stall_score`
- The winner was `gap_exhaustion_stall_score`:
  - discovery gap `0.10445157`
  - q75 BA `0.54544126`
  - corr vs old `downside_failure` only `0.46646728`
- It survives both chronology and symbol holdout a bit above random:
  - time-split mean/min `0.54016402 / 0.5242303`
  - symbol-holdout mean/min `0.53970323 / 0.52670002`
- Pauli and Tesla both classified it as `soft_component`; James classified it as `candidate_only`.
- We froze the branch as `soft_component` by majority.
- The branch is worth preserving because it adds a different recent `1min` downside angle, but it is still too weak to drive execution directly.
## JOURNAL-0270 V123E-G Same-Plane Blend Stopline
- We tested whether the new orthogonal recent `1min` downside branch (`gap_exhaustion_stall_score`) should be attached to the older `downside_failure_score` in the same recent label plane.
- Simple blends did create larger pooled gap values, but that was not enough.
- The best blend was `orthogonal_heavy_blend_score`, yet it did not improve q75 BA at all relative to the best standalone branch and it made symbol minimum robustness worse.
- All three reviewers agreed that same-plane attachment should stay blocked.
- Outcome:
  - `downside_failure_score` stays as detached recent `1min downside soft_component`
  - `gap_exhaustion_stall_score` stays as detached orthogonal recent `1min downside soft_component`
  - no replay-facing move
  - no more same-plane blend tuning
## JOURNAL-0271 V123H-K Regime Overlay Result
- We tested whether top-level regime variables could explain the large research-baseline drawdown windows:
  - broad index returns
  - index turnover contraction
  - CPO board turnover contraction
- `liquidity_drought_regime_score` won the pooled scan.
- It looked useful in discovery, but the moment we forced chronology, the branch became unstable.
- We also discovered a hard data boundary:
  - the current index bootstrap only covers one year
  - so genuine cross-year regime transfer cannot be tested yet
- Final posture:
  - keep as `explanatory_only`
  - useful for understanding why drawdowns cluster
  - not usable as candidate execution logic yet
## JOURNAL-0272 Heat Guardrail Interval Truth
- We finally compared the uncapped research line and the main heat-capped variants on the exact same three drawdown windows.
- This clarified something important:
  - heat guardrails are not cosmetic
  - they really do shrink the two largest later drawdowns by carrying much less `300308` and `300502`
- But they do not explain everything:
  - the earlier `2023-06-20 -> 2023-11-01` drawdown does not improve at all
  - in that interval the guardrails never actually reduced carry, so the path stays identical
- This means:
  - heat is a real first-order problem
  - but it is not the only one
  - the remaining unresolved pain still points back toward true downside / reduce-side action logic
## JOURNAL-0273 Residual Downside After Heat Caps
- We isolated the one large drawdown family that heat guardrails did not improve:
  - the third drawdown `2023-06-20 -> 2023-11-01`
  - within the research line while still holding both `300308` and `300502`
  - and still carrying more than `60%` cash, so this is not just an overheated leverage story
- Inside that narrow subset, `held_pair_deterioration_score` emerged as the strongest residual downside branch.
- It does not collapse under chronology, and it does not light up equally across the pre/post boundary negatives.
- That makes it more than explanation-only.
- But it is still tightly tied to a specific carry structure:
  - `300308 + 300502`
  - high-cash residual downside
- Final posture:
  - keep as `candidate_only`
  - do not attach to replay
  - do not pretend it is a general downside rule
## JOURNAL-0274 Residual Branch Is Not a Single Threshold Artifact
- We sanity-checked the new residual downside branch against adjacent high-cash floors.
- The important result is that the branch is effectively unchanged at:
  - `cash_ratio > 0.55`
  - `cash_ratio > 0.60`
  - `cash_ratio > 0.65`
- That matters because it means the signal is tied to the held-pair residual downside geometry itself, not just a lucky cutoff at `60%`.
- The branch only starts to degrade once the subset becomes materially narrower at `cash_ratio > 0.70`.
- So the right reading is:
  - narrow, yes
  - context-specific, yes
  - but not a trivial threshold artifact
## JOURNAL-0275 Residual Branch Fails the Core-Focus Test
- We pushed one step harder on the residual branch:
  - not just “does it separate the interval”
  - but “does it actually light up the deepest stress core inside the interval”
- The answer was no.
- Inside the positive residual interval, the branch scores the fringe slightly **higher** than the core:
  - core mean `0.33515`
  - fringe mean `0.545276`
- The granular boundary view tells the same story:
  - core pass rate `0.466667`
  - fringe pass rate `0.5`
  - both still above pre/post negatives, but not ordered the way a real core trigger should be
- This is why the branch was demoted:
  - not dead
  - not fake
  - but too diffuse to stay `candidate_only`
## JOURNAL-0276 Drawdown Control Layers Are Now Ordered
- We finally collapsed the recent risk work into a single attribution matrix instead of a pile of separate branches.
- That matrix says:
  - drawdowns 1 and 2 are mainly heat problems
  - drawdown 3 is mainly a non-overheated held-pair deterioration problem
- The consequence is practical:
  - the next control work should not start from macro regime or new family discovery
  - it should start from the ordered stack:
    1. heat
    2. broad reduce prior
    3. narrow residual soft penalty
    4. regime explanation
- This is the first time the risk-side work has a clean priority order tied directly to the actual big drawdowns.
## JOURNAL-0277 Broad Risk-Off Is Too Blunt for Execution
- We finally attached the ordered risk stack to the research line and the answer was cleaner than expected:
  - heat works
  - broad risk-off, in execution form, is too blunt
- The `balanced/strict heat` references still look like actual research-trading controls:
  - they give back less than the uncapped line
  - but they do not annihilate the curve
- The moment we let `board_risk_off_reduce_prior` fire as real de-risking at next open, the line becomes over-defensive:
  - drawdown compresses sharply
  - final equity collapses with it
- So the right reading is not that risk-off is useless.
- It is that current `board_risk_off_reduce_prior` is still too wide to be an execution layer.
- That is a valuable stopline:
  - keep heat as the only live execution control
  - push broad risk-off back to non-replay narrowing and explanation
## JOURNAL-0278 Narrow Risk-Off Is Real, But Still Not Worth Promoting
- We gave risk-off one fair retry instead of killing the idea outright.
- The retry was simple:
  - only let risk-off fire when the book is already hot enough
  - and only trim partially
- That worked in one important sense:
  - the line no longer collapsed to near-baseline equity
  - so the old broad failure really was about width, not pure direction
- But it still failed the main question:
  - can it beat the plain balanced heat reference on the return/drawdown tradeoff?
- The answer stayed no.
- So the honest reading is:
  - broad risk-off was too blunt
  - narrow risk-off is not fake
  - but narrow risk-off is still only a shadow defensive variant
- That is a useful endpoint because it stops us from endlessly trying to promote a family that is now well understood.
## JOURNAL-0279 Heat Is Right, But Smaller Ladders Still Lose
- Once heat was confirmed as the only live execution control, the obvious next question was:
  - maybe the real problem is not heat itself
  - maybe we just size each add too aggressively
- We tested that directly by shrinking the add ladder under the same balanced heat budget.
- The answer came back clean:
  - yes, smaller ladders soften drawdown
  - no, they do not beat the current balanced reference
- That matters because it means the problem is no longer “we forgot to try gentler add sizing.”
- We did try it.
- The results say the current balanced heat reference is already the best point on that dimension.
- So this closes another tempting loop:
  - no more same-family ladder tuning
  - no more pretending smaller adds are a hidden missing fix
## JOURNAL-0280 Add Suppression Was Not Just Weak, It Was Absent
- We tested the mildest downside execution idea available:
  - do not sell
  - just stop adding when risk-off appears inside already-hot books
- The replay result came back perfectly flat against the heat reference, which looked suspicious.
- The overlap audit explained it immediately:
  - there were only `13` overlay add execution rows at all
  - only `1` of them even had a matching risk-off score
  - none crossed the risk-off threshold
  - none overlapped with the gross-heat gate
- That means this family is not a hidden gem we failed to tune.
- It simply has no live surface in the current CPO sample.
- This is an important closure point because it leaves much less ambiguity:
  - heat is still real
  - narrow risk-off shadow is real but not promotable
  - add suppression is not even entering the game
## JOURNAL-0281 CPO Is Frozen Enough That Queue Discipline Matters Again
- After `V124G`, the main practical state became unusually clear:
  - `CPO` still teaches us a lot
  - but its live execution stack is no longer expanding
  - it is basically `baseline + balanced_heat_reference`
- That changes the most valuable next action.
- The problem is no longer discovering one more clever CPO branch.
- The problem becomes:
  - what board should inherit the research worker next
  - and how do we keep that handoff explicit and auditable
- Re-opening the multi-board protocol showed we had never actually expanded the queue beyond `CPO`.
- So `V124H` does something simple but important:
  - it turns the next-board choice back into a real artifact
  - instead of leaving it as a conversational intention
- The current snapshot makes `商业航天` the cleanest next primary board, with `航天航空` and `军民融合` queued behind it as shadow alternates.
- That matters because once one board is frozen, progress should come from portability and comparison, not from staying emotionally attached to the first board forever.
## JOURNAL-0282 The Queue Only Matters If The Next Board Actually Starts
- Queue expansion by itself is bookkeeping unless the head of the queue immediately becomes a real worker.
- So after `V124H`, the right move was not to admire the ranking.
- The right move was to begin `商业航天` at phase 1 and force the same discipline we used on `CPO`:
  - first a world model
  - then role grammar
  - then lawful controls
- The current snapshot is enough to do that honestly.
- `002085` looks like the liquid leadership anchor.
- `000738` gives a more stable core-support shape.
- `600118` is still sparse, so it should stay an alternate rather than be over-trusted early.
- That is a healthy starting posture:
  - enough structure to begin
  - not enough certainty to pretend the board is solved in advance
## JOURNAL-0283 Broad Theme Boards Need Tier Discipline From Day One
- The user's warning about `商业航天` was right.
- This board is not just a clean direct-industry cluster.
- It has a real risk of concept sprawl:
  - direct names
  - adjacent same-engine names
  - propagation names
  - distant sympathy names
- If those layers are mixed too early, the worker will learn narration breadth instead of mechanism.
- So `V124J` does something deliberately conservative:
  - it keeps the current direct worker on a narrow tier-1 core
  - it keeps adjacent sectors as tier-2 shadow support
  - and it pushes user-noted broad concept names into a tier-3 watchlist
- This is not denying that those names move with the theme.
- It is acknowledging that they move for different reasons and therefore should not be granted the same causal status too early.
## JOURNAL-0284 Broad Theme Strength Can Come From Outside The Official Board Label
- The user corrected an important hidden assumption:
  - not every decisive mover has to sit inside the direct board label
  - some non-board names can still be real drivers of the move
- That is especially true for a board like `商业航天`, where capital can express the theme through adjacent chains, platform names, or narrative bridges.
- So the correction in `V124K` is not a softening.
- It is a better map:
  - direct board owners
  - cross-board propulsion allies
  - adjacent support sectors
  - distant sympathy noise
- This is healthier than the earlier narrow tiering because it keeps mechanism ownership and market force separated.
- The direct board still owns the internal role grammar.
- But the cross-board propulsion layer is now recognized as a real force in breadth and diffusion, not as disposable concept clutter.
## JOURNAL-0285 A-Share Theme Boards Need A Web Reality Check
- The local snapshot was not enough by itself for `商业航天`.
- The user's examples pointed to a classic A股 truth:
  - a board move is often driven by more than the official board members
  - concept linkages, equity stakes, shovel sellers, and emotion mirrors all become part of the tradeable reality
- Web sources made that visible very quickly.
- `华菱线缆` is the cleanest example:
  - easy to dismiss as concept hype if you only stare at board labels
  - much harder to dismiss once you see the actual aerospace cable and acquisition context
- `顺灏股份 / 金风科技 / 鲁信创投` show a second A股 truth:
  - capital linkage and narrative bridge names can become real market force even when they are not formal industry-core owners
- So `V124L` turns the universe into a more honest A股 map:
  - formal owners
  - concept propulsion
  - shovel sellers
  - similar-path mirrors
- That is the right base if the goal is not just industry truth, but industry truth as filtered through A股 pricing behavior.
## JOURNAL-0287 Missing Names Usually Mean The Universe Is Still Too Narrow
- The user's correction was useful because the omissions were not random.
- They exposed two recurring blind spots:
  - chip shovel-sellers that matter even without direct board-label ownership
  - materials names that have real aerospace linkage but still trade mainly as concept propulsion
- `*ST铖昌` and `臻镭科技` strengthen the shovel layer.
- `再升科技` strengthens the concept-propulsion layer.
- This is exactly the kind of A股-specific universe repair that matters more than having a theoretically neat but practically incomplete board list.
## JOURNAL-0288 Universe Repair Is Iterative On A股 Theme Boards
- The additional correction with `西测测试` and `中超控股` reinforces the same point:
  - a useful A股 theme universe is not discovered in one pass
  - it is repaired iteratively as real trading names surface
- `西测测试` strengthens the shovel layer because testing/verification is often a hidden but crucial industrial position.
- `中超控股` strengthens the concept-propulsion layer because sometimes the market chooses a high-elasticity name as a force amplifier even when the industrial purity is weaker.
## JOURNAL-0289 The Right Question Is No Longer “Is The Universe Complete?”
- Once a board reaches this breadth, the better question is:
  - not whether the list is complete
  - but whether additions are ranked honestly
- `V124N` is the first step that treats universe expansion like a graded process:
  - high-confidence additions
  - medium-confidence additions
  - pending names that still need another pass
- That is closer to real A股 board work.
- The board is allowed to stay broad.
- What is not allowed is pretending every broad name deserves identical causal weight.
## JOURNAL-0290 Breadth Success Creates A Boundary Problem
- The first three-step expansion worked in one real sense:
  - the commercial-aerospace universe now feels much closer to how A股 actually trades the theme
- But success created the next problem immediately:
  - the board is broad enough to describe
  - yet still too broad to legislate
- The adversarial review was useful because it forced a clean pause:
  - do not keep expanding
  - do not start control extraction
  - first run universe triage
- That is the right kind of slowdown.
- It does not deny the board's breadth.
- It just refuses to confuse breadth with executable authority.
## JOURNAL-0286 Breadth Only Helps If Authority Stays Layered
- Once the universe is widened, the real danger becomes obvious:
  - everything starts to matter
  - and then nothing is ranked properly
- `V124M` fixes that by making authority explicit.
- The direct board owners still own the mechanism.
- Cross-board propulsion names now have legitimate status, but only as breadth and diffusion force.
- Shovel sellers get their own confirmation layer.
- Mirror names become emotional context instead of accidental pseudo-core names.
- This is the point where the commercial-aerospace worker starts to look usable instead of just broad.
## JOURNAL-0291 The Universe Problem Has Finally Turned Into A Data Problem
- The commercial-aerospace work changed character the moment `V124R` landed.
- Before that point, every omitted-name argument still had some force because the board was trapped in a `web-only` state.
- Once local Tushare feeds existed for the merged universe, the real question changed:
  - no longer `did we forget another concept name?`
  - but `can the machine legally learn the widened universe?`
- That is a healthier problem.
## JOURNAL-0292 Full Local Support Is Necessary But Not Sufficient
- `V124S` removes a comforting excuse.
- When `51/51` names are locally supported, weak machine understanding can no longer be blamed on feed gaps.
- From this point on, bad machine triage is an authority problem, not a collection problem.
## JOURNAL-0293 A Wider Machine Surface Immediately Exposes Authority Pollution
- `V124T` proves that widening the board mechanically is dangerous.
- The machine now sees far more than the earlier three-name bottleneck.
- But once it sees more, it starts treating:
  - concept-propulsion names
  - mirror names
  - genuine internal owners
as if they belong to one causal layer.
- That is exactly the mistake the user has been guarding against.
## JOURNAL-0294 Adversarial Review Helped More Than Another Discovery Pass
- The three-subagent review did not create alpha.
- It did something more important here:
  - it blocked a premature slide into `control extraction`
  - it forced the board to admit that the refreshed machine surface was still too dirty to legislate
- This is the right kind of slowdown.
## JOURNAL-0295 A-Shares Need Breadth, But Controls Need A Much Thinner Core
- `V124V` is the first truly lawful commercial-aerospace handoff.
- The board is still broad:
  - direct formal names
  - cross-board propulsion
  - shovel sellers
  - mirror names
all remain in the research surface.
- But control authority is no longer broad.
- That asymmetry is not a weakness.
- It is how an A-share concept board stops being a theme dump and starts becoming tradable research structure.
## JOURNAL-0296 Boundary-Risk Names Still Matter Even When They Lose Authority
- `航天发展` forced a useful correction.
- It was wrong to treat it as either:
  - clean control core
  - or meaningless mirror noise
- `sentiment_watch_quarantine` is the better answer:
  - keep the name visible
  - keep its heat readable
  - but block it from polluting lawful controls
## JOURNAL-0297 Pure Structure Was Not Enough For Commercial Aerospace
- `V125G` was an important negative result.
- Even after the board was cleaned:
  - thin formal core
  - confirmation separated
  - sentiment-watch quarantined
the control surface still stayed negative on chronology.
- That means the next missing layer was not more role grammar polish.
- It was catalyst semantics.
## JOURNAL-0298 The Event Layer Finally Produced A Real Improvement
- `V125I` is the first commercial-aerospace result that clearly moved the control surface in the right direction.
- `quality_event_gate` did not just beautify the story.
- It turned the control surface from negative mean year spreads into positive mean year spreads.
- That is a real shift.
## JOURNAL-0299 The Event Layer Did Not Fix Coverage
- The improvement is real but not complete.
- `V125L` makes the remaining weakness obvious:
  - `2024` has no event coverage
  - `2026` still has a weak tail even with event conditioning
- So the next blocker is no longer whether events matter.
- The blocker is whether event-conditioned control covers enough of the board's chronology to be lawful.
## JOURNAL-0300 Decisive Events Are More Useful Than Theme Heat
- The user was right to push back against broad event collection.
- Commercial aerospace is not helped by another pile of `板块爆发` articles.
- It is helped by:
  - continuation enablers
  - turning-point warnings
  - regulation/financing-risk events
- That narrower event language is much closer to how A-share theme行情 actually turns.
## JOURNAL-0301 Calendar Years Were A Bad Language For This Board
- The year split was a useful legality check, but a bad description of the board itself.
- `V125N` is the first time commercial aerospace starts to look like a real行情 object:
  - impulse expansion
  - sentiment overdrive transition
  - weak drift / chop
  - risk-off deterioration
- That is a more truthful lens than `2024 vs 2025 vs 2026`.
## JOURNAL-0302 The Good Surprise Is That Not All Structural Heat Is Bullish
- `V125O` clarifies something important:
  - pure sentiment overdrive is bad for eligibility
  - weak drift / chop is also bad
  - the only clearly positive structural phase is impulse expansion
- This is exactly the kind of asymmetry that a theme board should reveal if the modeling is honest.
## JOURNAL-0303 BK0480 Taught A Limit, Not A System
- `BK0480` looked promising as the first transfer target because it at least had a narrow dual-core shape.
- But once the role surface, local expansion, and historical bridge were formalized, the truth became clear:
  - `000738` and `600118` are the only clean same-plane core
  - `600760` is only a historical confirmation bridge
  - everything else is timeline-only or too thin
- That is useful. It means the portability method is honest enough to say “not enough board here yet,” instead of hallucinating a replay system.
## JOURNAL-0304 Freezing Transfer Is A Positive Result
- `V130G/V130H/V130I/V130J/V130K` are not a stall; they are a governance upgrade.
- The transfer program is now explicitly frozen, with a watchlist and reopen triggers.
- That is better than pretending `BK0808` or another adjacent board is ready just because we want forward motion.
- The closest thing to readiness is `BK0808`, but “closest” is still not “ready.”
## JOURNAL-0305 BK0808 Is Nearer Than The Rest, But Still Not There
- `V130L/V130M` made the freeze more honest.
- The watchlist is no longer just ranked by closeness; it now has concrete gap-closure paths.
- `BK0808` is the only board with a plausible single-step-looking path, but even that “single step” still requires two real things to happen:
  - another `v6` same-plane symbol
  - bridge-only status to disappear
- That is exactly the kind of almost-there situation where research teams usually jump too early. This time the governance layer is doing its job.
## JOURNAL-0306 600118 Is The Interesting BK0808 Watch, Not 600760
- `V130N/V130O` gave a better answer than “just keep watching BK0808.”
- `600760` is still useful, but only as historical bridge memory.
- The genuinely interesting name is `600118`, because it already shows BK0808 timeline-native support without yet having same-plane snapshot support.
- That is the right kind of near-readiness signal:
  - useful for supervision
  - not enough for unlock
## JOURNAL-0307 A Good Watch Is A Trigger, Not A Story
- `V130P/V130Q` made the BK0808 watch sharper.
- `600118` is not just “interesting.” It is now the explicit emergence trigger:
  - if it appears in real `v6` BK0808 same-plane support,
  - and board strength remains acceptable,
  - BK0808 stops being a frozen curiosity and becomes a real reopen candidate.
- That is the right way to supervise a frozen transfer program: convert narrative closeness into concrete trigger logic.
## JOURNAL-0308 A Good Trigger Also Needs A State Machine
- `V130R/V130S/V130T/V130U` pushed the BK0808 watch one step further.
- `600118` now has real dated `near_surface_watch` windows, not just a static watch label.
- That matters because it shows the freeze is not passive:
  - the system can tell when the watch is active,
  - when it falls back to inactive,
  - and still refuse to promote BK0808 until real same-plane support exists.
- This is the kind of governance layer that keeps research honest when the temptation to reopen too early is high.
## JOURNAL-0309 Sometimes The Honest Next Step Is To Stop Recomputing
- `V130V/V130W` are a useful reminder that “continue” does not always mean “open a new worker.”
- Once the transfer freeze, triggers, watch windows, and state machine are all explicit, re-running more static analytics on the same evidence is mostly self-soothing.
- The honest posture now is:
  - keep the bundle
  - watch `600118`
  - wait for real new `v6` same-plane evidence
## JOURNAL-0310 A Freeze Is Better When It Has A Mechanical Gate
- `V130X/V130Y` close the loop.
- The transfer program is no longer frozen only by judgment; it is frozen by a concrete monitored-artifact gate.
- That matters because it turns the next restart from a debate into a check:
  - did any of the monitored source artifacts actually change?
  - if not, do not reopen
## JOURNAL-0311 A Good Freeze Also Needs A Dashboard
- `V131A` is not glamorous, but it is useful.
- Once a program is honestly frozen, people still ask the same operational questions:
  - are we still frozen?
  - who is closest?
  - what exactly would trigger a rerun?
- The status card answers those immediately:
  - frozen
  - BK0808
  - 600118
  - wait for real `v6` same-plane emergence
## JOURNAL-0312 A Frozen Program Is Stronger When Restart Is Already Scripted
- `V131C` adds the last useful layer.
- Once the transfer program is honestly frozen, there are only two clean states:
  - the gate is still closed, so do nothing
  - the gate opens, so rerun a pre-declared chain
- The rerun command sheet matters because it removes the temptation to improvise a restart under pressure.
- That is the right final posture for this branch:
  - frozen under unchanged artifacts
  - restart-ready under changed artifacts
## JOURNAL-0313 The Next Honest Frontier Is Intraday Governance, Not More EOD Tuning
- `V131D/V131E/V131F` close an important loop.
- The commercial-aerospace primary replay no longer needs more local threshold polishing.
- What it needed was a clean way to preserve the strongest lawful-but-wrong intraday failures without pretending they already belong inside the lawful EOD stack.
- The new supervision bundle does exactly that:
  - `2` retained override positives
  - `2` reversal watches
  - `30` clean controls
- That is enough to stop arguing abstractly about intraday collapse and start preserving concrete seed geometry for future minute-level work.
## JOURNAL-0314 A Good Intraday Idea Still Needs A Data Floor
- `V131G/V131H/V131I` add the missing operational reality check.
- The commercial-aerospace intraday override idea is now well-formed enough to supervise, but not well-supported enough to model.
- The important part is that this is no longer vague:
  - the exact missing symbols are known
  - the exact required sessions are listed
  - the exact priority order is explicit
- That is the right posture here:
  - keep the idea
  - keep the seeds
  - block the modeling
  - wait for the minute-data floor
## JOURNAL-0315 The Right Freeze For Intraday Work Looks Like A Small Change Gate
- `V131J/V131K/V131L` finish the operational packaging.
- The minute-level branch no longer lives in a fuzzy state of 鈥渨e should probably collect data later.鈥?
- It now has:
  - exact required files
  - exact missing count
  - exact high-priority symbols
  - a single status card
- That is the right final posture for this branch under current data:
  - preserve the supervision bundle
  - preserve the manifest
  - freeze the modeling
  - reopen only after the file gate is actually satisfied
## JOURNAL-0316 The Local Monthly 1min Drop Changed The Intraday Branch From Blocked To Real
- `V131O/V131P/V131Q/V131R` are the first intraday steps here that are not about governance-only waiting.
- The new local monthly archive means the branch is no longer asking:
  - do we have minute files at all
- It is now asking:
  - what is the right narrow prototype to run on the exact retained override sessions
- The important shift is not abstract data abundance.
- The important shift is that the branch no longer depends on:
  - Baostock
  - share-page downloads
  - partial provider luck
- That is a real state change:
  - the exact four retained sessions are covered
  - the exact four sessions can be resampled from `1min` to `5min`
  - the intraday branch is now materially unblocked for local prototype work
## JOURNAL-0317 The Local 5-Minute Prototype Finally Turned The Intraday Idea Into A Governed Object

Date: 2026-04-04

The local monthly one-minute archives changed the minute branch from theoretical to operational. The most important consequence was not that a full intraday model suddenly became lawful, but that the narrow commercial-aerospace override idea could finally be tested on real retained sessions instead of synthetic placeholders.

The result was clean enough to matter. The first local five-minute prototype covered both retained override positives and both reversal-watch cases while staying completely off thirty clean controls. That is the first time the commercial-aerospace intraday branch produced something with enough separation to keep.

The correct posture is still narrow. This is not a replay-facing minute model. It is a governed supervision layer that now sits alongside the lawful EOD primary, the failure library, and the time-chain governance work. The right reading is not "intraday solved"; the right reading is "the first narrow minute object is now real and worth preserving without contaminating the main replay stack."
## JOURNAL-0318 The 5-Minute Prototype Stayed Narrow When Expanded

Date: 2026-04-04

The useful part of the new local five-minute branch is not that it suddenly created an intraday execution model. The useful part is that it survived contact with the full commercial-aerospace buy surface without leaking into ordinary clean trades.

When expanded from the retained severe cases to all fifty-five buy executions, the prototype still behaved like a severe-case detector. It hit all four seed cases, touched none of the thirty clean controls, and only crossed into two ambiguous executions. That is exactly the kind of behavior a governance object should have: narrow, bounded, and explicit about what it may overreach on.

This means the minute branch now has a real supervision artifact with documented limits. The right reading is still conservative. It should not rewrite the lawful EOD replay. But it is no longer just a promising idea; it is a bounded intraday governance object with measured false-positive behavior.
## JOURNAL-0319 The Prototype’s Two “False Positives” Were Not Really False

Date: 2026-04-04

The broader five-minute audit left two residual non-override hits. At first glance they looked like the kind of leakage that should cap the prototype. But once they were isolated and judged on their own path shape, both turned out to belong in a weaker supervision tier rather than in a hard false-positive bucket.

What mattered was not their original table label but their intraday path. Both had hour-level deterioration strong enough to satisfy the mild-watch rule: sixty-minute return below roughly minus four and a half percent, sixty-minute drawdown beyond the same threshold, and a close location near the day’s low. That is not ordinary noise. It is not severe enough to rewrite the replay, but it is severe enough to deserve retention.

So the commercial-aerospace minute branch is no longer just a severe-case detector. It now has a small graded supervision stack: severe override positives, reversal watches, and mild override watches. That is still governance, not execution. But it is a better supervision object than the cruder “hit or false positive” view we had before.
## JOURNAL-0320 The Minute Branch Finally Has A Proper Registry

Date: 2026-04-04

The commercial-aerospace minute work stopped being a scattered set of examples once the supervision registry was frozen. That changed the branch from a case-study workflow into a label-governance workflow.

The important part is the tiering. Severe override positives, reversal watches, and mild override watches now live in one canonical object, which means future minute-level work can start from a clear severity hierarchy instead of trying to rediscover structure from raw cases every time. That is a real methodological improvement.

The boundary remains strict. The registry still belongs to governance, not to the lawful EOD replay. But the branch now has something it did not have before: a proper seed source for later one-minute label formalization.
## JOURNAL-0321 The Minute Branch Now Has Actual Seed Rules

Date: 2026-04-04

The commercial-aerospace intraday branch crossed another threshold once the first explicit one-minute rules were able to reproduce the frozen severity ordering on all six retained seeds. That is a stronger state than simply having a registry or having envelopes. It means the branch now has the beginnings of a real rule grammar, even if it is still narrow and still governance-bound.

The important boundary remains intact. These are seed rules, not replay rules. Their job is to preserve the hierarchy between severe override positives, reversal watches, and mild override watches on the retained seed set. They did that cleanly, which is why they deserve to remain frozen and documented.

The next question is now the right one: not whether the rules fit the seeds, but how badly they spread outside the seeds. In other words, the minute branch has finally reached the point where broader false-positive auditing matters more than additional anecdotal case discussion.
## JOURNAL-0322 The First 1-Minute Rules Stayed Clean On The Full Buy Surface

Date: 2026-04-04

The first meaningful stress test for the new one-minute rules was whether they would start firing once they were applied outside the frozen six-seed set. They did not. On the full fifty-five-row buy-execution surface, the rules preserved all six seeds and did not touch a single non-seed execution.

That matters because it upgrades the rules from "internally coherent on the seed set" to "bounded on the current replay-side surface." The branch is still governance-first; none of this makes the rules replay-ready. But the minute work is no longer just a seed grammar. It is a bounded supervision object with its first real false-positive audit behind it.

The natural next question is broader than replay. The next place these rules need pressure is on the wider local session surface for the retained symbols, not merely on the subset of sessions that happened to become buy executions in the current EOD primary.
## JOURNAL-0323 The Minute Rules Did Not Blow Up When We Left The Replay Surface

Date: 2026-04-04

The broader session expansion audit was the first real sign that the one-minute branch may be more than a fragile seed artifact. Once the rules were applied to all locally available first-hour sessions for the six retained seed symbols, they produced twenty-four hits across six hundred and twelve sessions. That is not trivial, but it is still sparse enough to stay interpretable.

The most important number was not the raw hit count. It was the shape of the expansion surface. The maximum symbol-level hit rate stayed below six percent, which means the rules did not explode into a generic weakness detector. They expanded, but they stayed narrow.

That is exactly the behavior we needed to see before taking the minute branch any further. It is still governance, not replay. But it is no longer only a hand-built seed grammar. It now has a bounded broader session surface that can be studied directly.
## JOURNAL-0324 The Minute Branch Started To Explain Bad Notional, Not Just Bad Cases

Date: 2026-04-04

The local one-minute branch crossed another threshold once the shadow-benefit audit was run on the full fifty-five-row buy-execution surface. Before this step, the branch was already bounded and temporally aligned with the board's real risk structure. What it still lacked was a direct economic justification for why it deserved a stronger place in governance.

That changed once the flagged slice was measured against later downside notional. Six flagged executions, just over ten percent of the buy surface, accounted for nearly seventy-nine percent of later negative forward notional and more than fifty-six percent of later adverse notional. That is not the profile of a generic weakness filter. It is the profile of a narrow governance layer that is pointing toward the trades that later hurt.

The boundary still matters. None of this promotes the minute branch into the lawful EOD replay. But it does change how the branch should be treated organizationally. It is no longer just bounded supervision. It has become shadow-benefit-aligned governance, which means it belongs inside the formal commercial-aerospace governance stack rather than hanging off to the side as an isolated experiment.
## JOURNAL-0325 The Minute Branch Finally Became A State Machine Extension

Date: 2026-04-04

There is a real difference between having a registry of bad cases and having an action ladder. The registry tells you that certain intraday paths matter. The action ladder tells you what those paths mean inside the system.

That is the threshold the commercial-aerospace minute work crossed once the severe, reversal, and mild tiers were translated into explicit governance actions. Severe is now the future emergency-exit shadow object. Reversal is now a panic de-risk watch. Mild is now a do-not-readd watch. None of that is replay execution, but all of it is actual system semantics.

This matters because it changes the role of minute research. It is no longer an isolated branch waiting for someday to be useful. It has become a formal extension of the governance state machine that already surrounds the frozen EOD primary. Once a lawful point-in-time intraday path exists, the system will not need to improvise from scratch. It will already know how to interpret what it sees.
## JOURNAL-0326 The Minute Branch Started To Behave Like A Real Escalation Ladder

Date: 2026-04-04

The strongest new evidence for the commercial-aerospace minute branch did not come from another false-positive count. It came from the path structure of the broader hit sessions. Once those twenty-four sessions were replayed through full-day one-minute data, the dominant pattern was not random. It was ordered escalation: neutral to mild, mild to reversal, reversal to severe.

That matters because a ladder only deserves to be called a ladder when the underlying sessions actually climb it. Here they mostly did. Four out of five severe hits had already passed through reversal first, and the most common session pattern across the broader hit surface was the full neutral-to-mild-to-reversal-to-severe progression.

That turns the minute branch into something stronger than a bounded supervision gadget. It becomes a real governance state-machine extension. The system still cannot legally trade from it yet, but it can now interpret intraday deterioration in a way that is both structured and empirically grounded. That is the right endpoint for this stage of commercial-aerospace minute work.
## JOURNAL-0327 The Minute Branch Became Something A Human Can Actually Inspect

Date: 2026-04-04

The final missing piece of the commercial-aerospace minute branch was not another threshold or another audit. It was readability. Once a branch grows into registry, rules, ladders, and escalation support, it still needs one more thing if it is going to remain trustworthy: a way for a human to inspect the canonical sessions directly.

That is what changed once the six seed sessions were packaged into a single case panel. The branch is no longer only documented in abstract reports. It can now be looked at. You can see where a mild session first weakened, where a reversal session broke, and where a severe session collapsed. That matters because supervision quality is easier to maintain when the canonical examples remain visible.

This does not change execution. It changes governance quality. The commercial-aerospace minute branch now ends this stage not as a pile of findings, but as a coherent, inspectable supervision framework that a future lawful intraday system could actually inherit.
## JOURNAL-0328 The Minute Branch Reached A Real Stopping Point

Date: 2026-04-04

The most important outcome of the final packaging step was not a new number. It was clarity about where this branch should stop. By the end, the commercial-aerospace minute work had become a full governance package: a tiered supervision registry, explicit one-minute rules, bounded false-positive behavior, shadow-benefit evidence, an action ladder, ordered escalation support, and a canonical visual case panel.

That is enough. In fact, it is the point at which continuing local minute tuning would become more dangerous than useful. Once a branch reaches that level of internal coherence, the real question is no longer how to squeeze one more board-specific refinement out of it. The real question is whether there exists a lawful execution surface that can inherit it, or a new board context that can test its portability.

So the right ending here is a governance freeze, not another local experiment. The package is ready. The execution path is not. That distinction is exactly what a disciplined research program should be able to say.
## JOURNAL-0329 The Commercial-Aerospace Minute Branch Now Knows Why It Is Still Frozen

Date: 2026-04-04

The final improvement to the commercial-aerospace minute work was not analytical. It was operational. Once the governance package had been frozen, the remaining risk was ambiguity: the branch could still attract more local experiments simply because there was no explicit statement of what was missing.

That ambiguity is gone now. The branch has an explicit intraday execution unblock protocol and a status card. The package itself is ready. What is not ready is the execution environment around it: point-in-time intraday visibility, an execution simulation surface, and a lawful replay binding lane.

That is an important stopping condition. A mature research line should not keep searching for tiny local improvements once the real blockers are infrastructural. At that point, clarity about why the line is frozen is more valuable than another round of board-specific optimization.
## JOURNAL-0330 The Intraday Branch Now Has The Same Kind Of Freeze Discipline As Transfer

Date: 2026-04-04

The last useful step for the commercial-aerospace intraday line was to stop treating its frozen state as a passive fact and turn it into an active governance object. That is what the change gate and heartbeat status finally did.

At this point the branch no longer depends on memory or taste. It has a package, a blocker list, a status card, and a change gate. That means the next continuation is no longer subjective. Either the missing infrastructure appears, or it does not. If it does not, the branch stays frozen. If it does, the branch has a lawful reason to reopen.

That is the right ending for this stage. A disciplined research program should not only know when a line is promising. It should also know when to stop touching it, and under what exact conditions it may be touched again.
## JOURNAL-0331 The Program Finally Knows That Continuing For Its Own Sake Is Wrong

Date: 2026-04-04

The most important program-level change was not analytical at all. It was the moment the different frozen lines were finally compressed into one master control surface. Before that, each branch knew its own stopping conditions, but the overall program still carried the risk of drifting into whichever line happened to feel easiest to touch next.

That risk is smaller now. The master status card makes something plain: every active line is frozen, and every legitimate continuation now depends on an explicit gate. CPO needs a specific replay-side review posture. Transfer needs same-plane emergence. Commercial-aerospace intraday needs infrastructure. None of those are hidden or subjective anymore.

That is what maturity looks like in a research program. Not constant motion, but explicit reasons for motion. Once those reasons are absent, the right action is not to invent another local refinement. It is to wait.
## JOURNAL-0332 The Program Finally Has The Tools To Wait Properly

Date: 2026-04-04

There is a difference between being frozen and being operationally ready to stay frozen. A program that is merely frozen can still drift, because nobody knows exactly what would justify a restart or what the current state is without rereading many reports.

That is what the reopen playbook and heartbeat snapshot fixed. The program now has two simple operational objects: one that says how a restart would happen, and one that says whether any restart is needed right now. That turns waiting into a governed activity instead of a vague pause.

This is a subtle but important end state. A disciplined research system should not only know how to run. It should also know how to remain still without losing clarity. That is where the program is now.

## JOURNAL-0333 The Program Can Move Again Only By Building Infrastructure, Not By Guessing

Date: 2026-04-04

A useful freeze is not the same thing as an empty stop. Once the commercial-aerospace minute branch had been packaged, the open question became whether the team actually knew how to move from governance into lawful intraday execution. That question is different from asking for more strategy ideas. It is an engineering and legality question.

The build protocol and three-subagent review answered that question cleanly. The direction itself is sound: first build a point-in-time minute state feed, then build a simulator, then bind a separate intraday replay lane. But the review also made clear that even a correct direction can still be too loose if the visibility semantics are not hardened. The two crucial constraints are now explicit: every intraday state must carry a real first-visible timestamp, and the shadow intraday lane must remain physically read-only relative to the frozen EOD primary.

That is a useful change in posture. The branch is no longer frozen because nobody knows what to do. It is frozen because the only remaining legitimate work is infrastructure buildout under hard guardrails. That is a much better kind of block.

## JOURNAL-0334 A Real Intraday Build Starts Only When Visibility Is Specified Precisely

Date: 2026-04-04

The important shift was not starting to code a simulator. It was recognizing that simulator work would still be premature until the minute-level state itself had a precise lawful shape. That is why the first implementation step became a visibility specification rather than a strategy feature search.

This matters because intraday leakage is subtle. A line can look disciplined while still cheating if day-level events are silently backfilled into minutes or if same-minute aggregates are treated as visible before the bar has actually closed. The visibility spec fixes that by forcing a concrete language: every event/state field needs a `first_visible_ts`, every lineage needs a `source_cutoff_ts`, and same-minute OHLCV belongs to the bar close, not the instant before it.

That is the right beginning for phase 1. The branch is now moving again, but only in the narrowest lawful way: define what can be seen at minute `t`, prove that the seed sessions can be reconstructed with that visibility surface, and block everything else until that proof exists.

## JOURNAL-0335 The First Real Intraday Object Is Not A Simulator But A Seed Visibility Feed

Date: 2026-04-04

The most important thing about the first implementation step is that it stayed narrow. Instead of widening immediately into all minute sessions or jumping toward replay, the build stayed on the six canonical commercial-aerospace seed sessions. That kept the scope lawful and inspectable.

This mattered because the real question was simple: can the branch produce a minute-level table where the bars are visible only at their close, the path features are computed only from prior closed bars, and every state field has explicit lineage? The answer is now yes, at least on the seed surface. Six sessions, three hundred and sixty rows, and zero missing lineage fields is a much more meaningful milestone than another generic blocker memo.

That still is not an intraday system. But it is the first object that deserves to exist before an intraday system can be attempted. The right next step is still phase 1 only, but now phase 1 has something concrete to audit rather than just a design document.

## JOURNAL-0336 Phase 1 Is Done Once The Visibility Surface Is Wider Than The Original Seeds

Date: 2026-04-04

The useful thing about phase 1 is that it stayed disciplined while still moving. It did not jump from six canonical seed sessions to an execution simulator. Instead it widened its own legal surface in steps: first the seeds, then the broader hit sessions, then the complete first-hour session surface for the six seed symbols. At each step the question stayed the same: can the branch still explain what is visible at minute `t` without backfilling the future?

By the time the all-session surface exists, phase 1 has essentially finished its job. There is no longer any ambiguity about whether a lawful point-in-time minute state surface can be built on the existing local archives. It can. The remaining work is no longer visibility. It is simulation and later replay binding, both of which are separate workstreams for a reason.

That is the right place to stop this phase. Research maturity is not just about building a thing. It is also about knowing when that thing has become complete enough that continuing in the same direction would only blur the phase boundary.

## JOURNAL-0337 A Simulator Becomes Lawful Only After Its Clock And Boundary Are Boring

Date: 2026-04-04

Once phase 1 finished, the temptation would have been to jump straight into coding a minute replay and see whether the override ladder improved outcomes. That would have been fast, but it would also have been sloppy. The useful next step is not another experiment. It is a simulator specification that makes the execution clock and the boundary conditions painfully explicit.

That is why the phase-2 work was first reduced to mundane details: when a trigger is evaluated, when a trade can fill, what price reference is allowed, what costs apply, and whether the branch is allowed to buy back later in the same session. Those details are not glamorous, but they are exactly where intraday leakage and accidental optimism tend to hide. A simulator that says “bar close only, next-bar open only, shadow-only, read-only relative to the EOD primary” is much more valuable than a more ambitious lane with fuzzy timing.

The consequence is healthy. The commercial-aerospace intraday branch is moving again, but it is moving inside a narrow seed-session lane with a boring clock and a hard wall around the frozen EOD primary. That is the correct kind of progress at this stage.

## JOURNAL-0338 The First Intraday Simulator Is Useful Precisely Because It Is Incomplete

Date: 2026-04-04

The first seed-session simulator is not important because it is broad. It is important because it finally turns the minute governance ladder into explicit sells with explicit fill timing. That means the branch has crossed a real threshold: it is no longer only naming emergency exits and panic de-risk states, it is simulating them under a lawful timing clock.

The boundedness still matters just as much as the existence. In the current canonical seed set, every retained trigger could be executed under the phase-2 timing rules using the local minute archive, so no pending outside-window fills were needed. That is still a useful result because the simulator is not relying on vague discretionary exits; it is producing next-bar fills from explicit trigger minutes under a fixed cost model.

That is why the result should be retained but not over-celebrated. The branch now has a lawful seed simulator, but it still does not have an intraday replay lane. The correct next move is still governed expansion inside phase 2, not premature promotion.

## JOURNAL-0339 A Narrow Intraday Simulator Is Only Useful If Its Time Order Is Honest

Date: 2026-04-04

The most important thing that happened after the first seed simulator existed was not a performance number. It was the discovery and correction of a chronology defect. A minute simulator that evaluates actions in tier order rather than in real minute order is not just inelegant; it is wrong in exactly the place where an intraday lane is supposed to earn trust.

Fixing that defect changed the meaning of the branch. The `601698` seed now behaves the way the minute narrative says it should: the early severe signal exits the position before the much later reversal state ever gets a chance to act. That is a small correction in code, but a large correction in research posture. It means the branch is now respecting the same temporal discipline it claims to be building.

Only after that correction does attribution become worth reading. And once it is corrected, the interesting result is that same-day damage avoidance is not concentrated only in the severe tier. A large share comes from reversal handling, and the heaviest seed contribution comes from `300342`. That is exactly the kind of directional understanding phase 2 should produce before any broader simulation or replay lane is even considered.

## JOURNAL-0340 The First Real Optimization Is Not More Heat, It Is Better Judgment About Which Tier Deserves Expansion

Date: 2026-04-04

Once a narrow intraday simulator becomes deterministic, the next temptation is obvious: widen it quickly and see whether it saves more money. That instinct is understandable, but still premature. The more useful question is not 鈥渃an phase 2 widen?鈥? It is 鈥渨hat exactly has earned the right to widen?鈥?

The answer is not symmetrical across tiers. The current seed attribution makes that clear. `reversal_watch` is carrying most of the same-day damage avoidance, while `severe_override_positive` remains important as the terminal emergency layer. `mild_override_watch`, however, still has positive forward expectancy in the shadow-benefit audit and should therefore not be treated as an early sell trigger just because it looks like part of the same ladder. That difference matters. A research branch becomes more trustworthy when it can say not only what worked, but also what should remain governed rather than promoted.

That is why the next widening step has to be narrow in two dimensions at once: narrow in surface and narrow in tier. The surface should widen only from the canonical seeds to the already-flagged broader-hit sessions, not to the full local minute universe. The tier set should widen only through `reversal_watch` and `severe_override_positive`, not through `mild_override_watch`. That is a more useful kind of progress than another uncontrolled expansion because it turns phase 2 from a loose exploration into a supervised execution research lane.

## JOURNAL-0341 A Good Widening Step Enters More Sessions Without Relaxing Its Ethics

Date: 2026-04-04

The first broader-hit widening step is useful because it expands the surface while refusing to expand the excuses. It does not claim that every minute session now deserves simulation. It does not quietly let `mild_override_watch` become a sell trigger. It does not slip into replay language. Instead it takes the already-flagged broader-hit sessions and runs them through the same disciplined intraday clock as the seed lane, using a normalized reference notional so the sessions can be compared on equal footing.

That matters because it preserves the meaning of phase 2. A phase-2 widening should answer whether the current ladder generalizes to its own nearby surface, not whether the branch can already masquerade as a finished trading engine. Keeping all-session expansion blocked and replay binding blocked is therefore not conservative theater; it is what makes the widening informative rather than self-deceptive.

## JOURNAL-0342 The First Wider Lane Is Most Useful When It Reveals What Still Should Not Be Executed

Date: 2026-04-04

The first broader-hit widening did what a good supervised expansion should do: it showed that the intraday branch is not trapped inside six hand-picked seeds. On a normalized notional basis, the wider 24-session lane still avoids a meaningful amount of same-day damage. That matters because it shows the branch has some local generalization, not just seed memorization.

But the more valuable lesson is where the drag came from. The attribution and failure review make the answer uncomfortably clear: predicted `mild_override_watch` sessions are still the weakest part of the widened lane. They are exactly the type of context that looks like part of the same escalation ladder, but still carries too much upside or ambiguity to deserve mechanical execution in the wider simulator. That is a healthy result. It means the next refinement is not 鈥渢ry more surface鈥? It is 鈥渂e stricter about who is allowed to execute inside the surface already opened.鈥?

That is the right kind of supervision outcome. A branch becomes more trustworthy when widening teaches it where not to act.

## JOURNAL-0343 The First Useful Tightening Is To Remove The Wrong Kind Of Obedience

Date: 2026-04-04

Once the wider phase-2 lane revealed that predicted mild sessions were dragging results, the right response was not to invent a new trigger. It was to stop being obedient in the wrong place. A branch that treats every later reversal print inside a predicted mild session as executable is behaving too literally. It is letting a governance signal leak into an execution privilege.

Blocking predicted mild sessions from execution is therefore a healthy refinement. It does not make the branch smarter by adding complexity. It makes the branch cleaner by restoring the intended boundary: mild is a watch state, not a sell mandate. That kind of refinement is exactly what supervision should do before any wider expansion is considered.

## JOURNAL-0344 A Research Branch Needs A Current Reference, Not A Pile Of Half-Retired Variants

Date: 2026-04-04

Once the mild-boundary refinement proved itself, the important next step was not another experiment. It was to freeze the shadow stack. Without that freeze, the branch would keep oscillating between the original wider lane and the refined wider lane, and every later discussion about performance or supervision would blur together old and new assumptions.

That is why phase 2 now needs a current narrow reference and a current wider reference. The narrow one remains the canonical seed simulator. The wider one is no longer the first broader-hit lane; it is the mild-blocked broader-hit lane. Freezing that stack does not stop progress. It creates a clean surface for the next supervision pass so the branch can judge one reference at a time instead of endlessly comparing against stale variants.

## JOURNAL-0345 Once The Reference Is Frozen, The Right Next Move Is To Study Its Shape, Not To Replace It

Date: 2026-04-04

After the shadow stack is frozen, the branch has finally earned the right to ask a more interesting question: what shape does the current wider reference actually have? That is a much better question than whether another small variant might score slightly better. A real execution research lane should know whether its benefit is coming from a few symbols, a particular month-window, or a specific failure cluster before it decides that any further change is justified.

That is why the next supervision pass stays entirely inside the current wider reference. It attributes the retained lane, identifies the strongest contributors, and clusters the remaining failures. If those failures are concentrated, the branch should supervise those local clusters rather than reopen the surface. That is how phase 2 stays disciplined: not by stopping, but by asking narrower questions after each successful freeze.

## JOURNAL-0346 The Best Sign Of Maturity Is When A Bigger Lane Fails Only In One Small Way

Date: 2026-04-04

The current wider reference passed an important test: after the mild-boundary refinement, it no longer failed in a diffuse or mysterious way. It failed in one small, intelligible way. A single reversal-predicted session in January still lost ground because the branch obeyed a severe trigger that arrived very late in the day. That is exactly the kind of failure a healthy supervised branch should want: not broad confusion, but a narrow over-execution pattern.

Once the failure looks like that, the right response is local. A late-severe block is not a new theory of the market. It is a statement that a reversal-predicted session should not automatically escalate into a terminal severe execution when that escalation only appears near the close. That kind of refinement keeps phase 2 honest. It improves the retained wider reference without pretending that the branch is ready for a bigger surface or for replay binding.

## JOURNAL-0347 A Mature Shadow Lane Eventually Stops Expanding And Starts Polishing Only Its Last Sharp Edge

Date: 2026-04-04

The most reassuring part of the latest phase-2 supervision pass is not that the numbers improved again. It is that the branch improved without changing its boundary. The wider lane did not ask for more sessions, more symbols, or another new tier. It only removed the last sharp edge inside the already-approved broader-hit surface. That is a healthier sign than another round of widening because it means the branch is beginning to converge on a stable internal logic.

Once the local late-severe refinement is promoted, the wider reference becomes simpler to reason about. Predicted mild sessions no longer leak drag into execution, and reversal-predicted sessions are no longer allowed to escalate into a terminal severe leg only because the day decays near the close. The branch still is not replay-ready, and it still should not touch all-session expansion. But it has now reached a better kind of stability: not a frozen experiment, but a refined shadow lane whose remaining decisions are increasingly local and intelligible.

## JOURNAL-0348 A Strong Sell-Ladder Result Is Useful Only If The Objective Is Named Honestly

Date: 2026-04-04

The reversal sell-fraction audit produced a result that is too strong to ignore: within the current broader-hit shadow lane, the best same-day outcome comes from treating reversal as a full first-stage exit. That makes intuitive sense for a same-day loss-avoidance objective because once a session has already entered the approved reversal state, holding half the position is often just an invitation to donate more downside to the afternoon tape.

But the important discipline is not to confuse that result with replay readiness. The branch is still optimizing a same-day shadow criterion, not a full multi-day trading objective. A full reversal exit can be the right answer for a same-day defensive lane and still be the wrong answer for a replay-bound execution system. That is why the promotion is valid inside phase 2 and still must remain blocked from replay binding. The result is valuable precisely because it sharpens the supervision ladder without pretending to solve the larger execution problem.

## JOURNAL-0349 The Right Defensive Ladder Can Still Need A Warning Label

Date: 2026-04-04

The horizon sanity pass clarified something important about the new full-reversal reference. It is not secretly a bad rule that only looks good intraday. Across the reversal sessions with available forward data, holding the sold shares would still have lost more money on aggregate over one, three, and five trading days. That means the branch is not just harvesting a cosmetic intraday mark. It is defending against real follow-through weakness in most cases.

At the same time, the branch also proved that some rebound opportunity is sacrificed. That is exactly why the result needs a warning label rather than a rollback. The right interpretation is not that full reversal should be abandoned. It is that the lane should be retained as a horizon-limited shadow reference: strong enough to keep, but still not broad enough or replay-clean enough to become an unquestioned execution truth. In a healthy research process, that kind of caveat is a feature, not a weakness.

## JOURNAL-0350 Volume-Price Is Useful Here Not Because It Solves The Ladder, But Because It Names The Misses

Date: 2026-04-04

The first volume-price supervision pass did not magically overturn the current sell ladder, and that is a good sign. If one small audit immediately rewrote the ladder, the branch would probably be overreacting to noise. What it did show is more valuable: the reversal sessions that later rebound have a higher post-reversal up-amount share than the sessions that keep deteriorating. That means the branch is finally starting to describe the miss in the right language. Some sells are not wrong because price looked better; they are wrong because the post-reversal tape starts to carry more upward participation than a true follow-through weak session should.

That is why the right posture remains supervision-only. The branch now has a concrete volume-price clue, but not a full rule. It can say, with some discipline, that rebound-cost cases look more like partial re-accumulation after reversal. It still cannot say exactly how much upward participation is enough to cancel the sell. That difference matters. Good governance names the clue first and only promotes it later if it survives more targeted supervision.

## JOURNAL-0351 A Clean Selector Can Still Be The Wrong Execution Edit

Date: 2026-04-04

The local rebound-cost veto scan did exactly what a good supervision pass should do: it found a very small, very clean selector. Two reversal sessions matched the volume-price conjunction, and both were genuine rebound-cost cases. No follow-through case slipped into that narrow bucket. That is already useful because it proves the branch is no longer guessing blindly about rebound risk.

But a clean selector is not automatically a good execution edit. Once the branch actually downgraded those two sessions from full reversal to half reversal, it recovered some five-day rebound cost but gave back too much same-day protection. That is an important maturity test. Research gets better when it can say: this clue is real, this execution change is not yet worth it. The veto now has a proper place. It is not discarded, and it is not promoted. It stays where it belongs for now: as a local supervision-side clue waiting for a better execution expression.

## JOURNAL-0352 A Better Local Expression Can Be Smaller, Not Looser

Date: 2026-04-04

The useful follow-up to the failed half-reversal experiment was not to loosen the same selector again. It was to make the execution edit smaller and more conditional. That produced a better answer. Instead of cutting the reversal sell size on both rebound-cost cases, the branch asked a more point-in-time question: was the first reversal followed by a clean neutral reclaim before any new reversal leg, and did the next reversal come back late enough to matter? That expression only touched one case, `2025-12-19 688523`, and it improved both same-day protection and five-day rebound cost.

That is exactly the kind of progress worth keeping. The branch did not need a wider surface, a new tier, or a softer ladder. It only needed a more faithful description of the tape pattern it was trying to spare. This is why local supervision matters. Sometimes the right optimization is not to do less selling in general. It is to recognize one tiny class of false-first-reversal and delay only that class. The result is still shadow-only, but it is a cleaner step toward a future sell-side grammar that respects both protection and rebound risk.

## JOURNAL-0353 The Right Time To Stop Is When A Pattern Turns From Cluster Into Residue

Date: 2026-04-04

The local deferral promotion raised an immediate follow-up question: was that one successful refinement the first example of a larger family, or was it just the last loose screw in the current ladder? The singularity audit answered that cleanly. Out of twelve reversal sessions with usable forward outcomes, only one matched the promoted local deferral expression. That means the branch has not discovered a broad new subclass of reversal mistakes. It has corrected one narrow residue.

That distinction matters because it changes the correct research posture. When a clue still covers a visible cluster, it is worth continuing the same family search. When it collapses to a single residue, more mining usually becomes expensive decoration. In this case the right move is to keep the refinement, keep the current wider reference, and stop spending more attention on the same false-first-reversal family. Good supervision is not just about finding one more improvement. It is also about knowing when a family has converged enough to leave alone.

## JOURNAL-0354 The Remaining Misses No Longer Look Like Bad Sells

Date: 2026-04-04

Once the false-first-reversal residue was isolated, the shape of the remaining misses changed. What stayed behind was not a set of sessions where the sell clearly happened too early on the same day. The remaining cases were mostly negative on day one and positive only later. That is a different problem. It says the branch may still be selling correctly in the short horizon while failing to define a governed rebuild or reentry path for the later recovery.

That is why the next orthogonal family had to shift. Continuing to mine sell-side timing would have been a category error. The right supervised move is to convert those remaining rebound-cost cases into a seed-level reentry registry. That keeps the discipline clean. The current sell-side wider reference stays frozen, and the next supervision branch starts from a separate question: not “should we have sold less,” but “what kind of later rebuild were we structurally unable to take.”

## JOURNAL-0354 The Next Useful Family Often Appears In The Cases The Last Fix Could Not Touch

Date: 2026-04-04

Once the false-first-reversal family was frozen, the remaining rebound-cost residues became much easier to read. They did not look like diluted versions of the same pattern. They looked noisier and harsher: repeated reversals, repeated severe re-entries, and many more state flips across the session. That is a different failure shape. The right conclusion is not that the old family still needs more variants. It is that the branch has reached a genuinely new orthogonal supervision family.

That matters because it preserves discipline. Research quality improves when a branch knows how to stop a converged family and open a new one with a clean reason. The new candidate, `oscillatory_breakdown_churn`, is not yet a rule and not yet a replay story. It is only a better description of the next unsolved residue. But that is enough. The work now has a new target, and it has one for the right reason: the remaining cases no longer behave like false first reversals, so the next audit should stop pretending they do.

## JOURNAL-0354 Naming The Next Family Is Not The Same As Opening It

Date: 2026-04-04

Once the false-first-reversal family reached stopline, the tempting mistake would have been to open another deep supervision line immediately just to preserve momentum. The orthogonal-family quick scan is useful precisely because it slows that impulse down. It does name a next likely direction: `early_severe_reclaim`. But it also shows that this direction is only a weak candidate, not a ready-made new branch. That is an important distinction. Research quality improves when the system can say not only what might come next, but also whether the evidence is strong enough to deserve a new local budget.

The result is healthy. The branch has not gone blank after freezing the prior family. It has a provisional map of the next territory. At the same time, it has not confused a provisional map with a permission slip. That is the right posture when the current wider reference is already stable and blocked from replay for larger reasons. A named weak candidate is enough. It preserves direction without manufacturing false urgency.

## JOURNAL-0354 The Remaining Misses Look More Like Missing Rebuilds Than Bad Exits

Date: 2026-04-04

Once the false-first-reversal family was frozen, the natural next question was whether another sell-side family was hiding in the remaining rebound-cost cases. The horizon pattern audit argues against that. After removing the one local-deferral residue, the remaining rebound-cost cases are not mostly positive immediately after the sell. Two of the three are negative on day one and only turn positive by day three. That means the sell itself still did useful work. The branch protected capital first and missed the later rebuild.

That is a different problem class. It suggests the next orthogonal supervision family should not be another intraday sell-timing refinement. It should be a post-exit reentry gap family: cases where the branch exits correctly, then fails to recognize that weakness has finished and rebuild conditions are forming. This is a healthier direction change than continuing to mine the exhausted sell-side family. It keeps the current defensive ladder intact and moves the research frontier to the next missing capability instead of over-polishing the last one.

## JOURNAL-0355 A New Family Begins Best As A Seed Registry, Not As A New Simulator

Date: 2026-04-04

Once the branch accepted that the remaining misses were reentry problems rather than sell-timing problems, the next temptation would have been to open another simulator immediately. That would have been premature. The healthier move is what the branch did instead: freeze the first post-exit reentry seed registry. Three residual cases are enough to name the new territory, but they are not enough to justify another execution lane yet.

This is an important governance pattern. A new family should start as a seed registry when the evidence is directional but still thin. That keeps the branch honest. It acknowledges that the current sell-side ladder has reached maturity, while also admitting that rebuild timing is still mostly undefined. The registry is therefore not a weak half-step. It is the correct first step. It turns the new family into something concrete enough to supervise without pretending it is already ready to trade.

## JOURNAL-0356 Delayed Rebuild Is A Timing Problem, Not A Same-Day Chase Problem

Date: 2026-04-04

Once the branch named post-exit reentry as the next missing family, the next temptation would have been to ask whether some of those cases really wanted same-day rebuilds. The timing audit argues no. None of the three seed cases are positive on day one after the exit. Two only turn positive by day three, and the remaining deep-washout case does not turn positive until day five. That means the missing capability is not "buy back faster on the same day." It is "know when delayed rebuild watch is allowed to begin."

That distinction matters. Same-day chase would collapse the separation between defensive selling and later rebuild supervision. The timing windows preserve that separation. They let the branch keep its defensive intraday ladder while still naming when a different type of supervision should wake up. In other words, this is not yet a reentry engine. It is the first clean timing grammar for when rebuild observation may legitimately start.

## JOURNAL-0357 A Reentry Ladder Is Better Than A Flat Watch Label

Date: 2026-04-04

Once the branch had timing windows for the new reentry seeds, the remaining ambiguity was whether those windows should just remain static labels. The ladder audit shows why that would be too weak. These seeds do not only differ by when rebuild watch may start. They also differ by what kind of later confirmation they need. The delayed rebound cases are not merely "watch from T+3." They are "watch from T+3, then look for persistent reclaim." The deep washout case is not merely "watch from T+5." It is "stay in base observation until the late base confirms."

That is why the ladder matters. It keeps reentry supervision aligned with the same philosophy the branch used on the sell side: states should progress, not collapse into one label. The branch still does not have enough evidence to trade this ladder, but it now has a cleaner semantic object to supervise. This is a good stopping point before any reentry simulator exists, because it preserves caution without flattening away the real structural differences between rebuild cases.

## JOURNAL-0358 Sometimes The Correct Reentry Answer Is A Board-Level No

Date: 2026-04-04

The reentry ladder was a necessary refinement, but it still lived at the seed level. That made it vulnerable to a familiar mistake: assuming every post-exit miss is fundamentally a rebuild problem. The board cooling audit pushes back on that. Once the board overlay is deeply off peak, the regime has flipped into weak drift or risk deterioration, and the next 20 to 40 trading days remain negative, the right abstraction is no longer "when do we rebuild?" It becomes "why are we still trying to rebuild inside a board that is structurally cooling?"

This is why the new lockout seed matters. It does not invalidate the reentry ladder. It places it in the correct hierarchy. A board-level cooling lockout should sit above seed-level rebuild supervision, because it changes the question entirely. The branch is no longer trying to optimize a reentry. It is trying to decide whether reentry should even be discussed. That is exactly the kind of higher-order veto a governance stack is supposed to provide.

## JOURNAL-0359 Unlocking A Cooling Board Is Mostly The Same Problem As Detecting A New Rise

Date: 2026-04-04

Once the cooling lockout existed, the next instinct might have been to invent a brand-new theory of "revival." The audit suggests that is unnecessary. Unlocking the board is mostly the same problem as identifying a board rise in the first place. What changes is not the conceptual family. What changes is the burden of proof. After a lockout, the branch must demand more breadth, more genuine full-quality participation, and less residual de-risk pressure before it even considers saying the board is alive again.

That is why the new unlock supervision is valuable. It does not ask for something exotic. It asks whether the old rise semantics have truly returned in a broad enough way to overpower the lockout. If not, the move remains a false bounce. This is a very healthy simplification. It means the branch does not need one ontology for rising and another ontology for reviving. It needs one ontology for board emergence, with stronger guards when the board is climbing out of a cooling regime.

## JOURNAL-0360 A Few Strong Names Inside A Weak Board Are Not A Contradiction

Date: 2026-04-04

One of the most dangerous moments in a cooling thematic board is not total weakness. It is partial strength. A handful of names start to rebound hard and the mind rushes to narrate revival. The local-only rebound audit is useful because it refuses that shortcut. It shows that isolated strength is not evidence against lockout. It is often evidence that the lockout needs a more explicit anti-false-bounce guard.

This matters because the board can remain structurally weak while one or two names bounce violently. That is not a paradox. It is a normal late-stage thematic behavior. Some names become temporary pressure-release valves, liquidity magnets, or short-cover targets while the broader board still lacks genuine quality participation. The right response is not to deny the local strength. It is to put it in the right semantic box: local-only rebound, not board revival.

## JOURNAL-0361 Governance Becomes Cleaner Once Board State Comes First

Date: 2026-04-04

After lockout, unlock, and seed-level reentry supervision all existed, the remaining risk was not missing another label. The remaining risk was precedence confusion. Without an explicit hierarchy, a branch can accidentally let a lower-level object override a higher-level one. That is how symbol strength starts bullying board weakness, or how a rebuild ladder starts discussing opportunities inside a board that never stopped cooling.

The new hierarchy spec fixes that. It says the order out loud. First the board may be locked. Then local-only rebound may strengthen the case that the lockout still holds. Only after a board-level unlock seed appears is the branch allowed to resume symbol-level rebuild discussion. This is a better mental model than memorizing isolated rules. It turns the branch into a layered governance system instead of a pile of disconnected audits.

## JOURNAL-0362 A Cooling Board Is Better Described By Expectancy Than By Shape

Date: 2026-04-04

There is a limit to how far shape language can carry a branch. Words such as lockout, rebound, and revival are useful, but they still leave too much room for human projection. A board can "look interesting" while still having terrible expectancy. Once that becomes true, the right next step is not to add more adjectives to the shape. It is to ask the harder and simpler question: is this board worth touching on a forward reward-risk basis?

That is why the expectancy layer matters. It reframes the board stack in harder terms. Unlock-worthy dates do not merely have a nice shape; they also carry strong forward board returns and large positive reward-risk asymmetry. False-bounce-only dates do not merely fail breadth tests; they also have poor forward expectancy. Lockout-worthy dates are worse still. This is a healthier top-level language for reduce because it pushes the branch away from aesthetic interpretation and toward consequences. A weak board is not weak because it looks ugly. It is weak because the payoff for touching it is poor.

## JOURNAL-0363 The Remaining Reduce Gap Is Not Conceptual Anymore

Date: 2026-04-04

Once the branch wrote the full closure stack down, the ambiguity finally shrank. The problem is no longer that reduce lacks structure. The branch now has a sell ladder, a board expectancy layer, a board-first lockout/unlock hierarchy, and a seed-level rebuild ladder. In other words, most of the thinking has already happened. The branch can now explain what it wants to do and why, at each layer, without reaching for vague language.

That changes the diagnosis of what remains open. The remaining gap is no longer conceptual. It is infrastructural and executional. There is still no replay-facing lane that binds these layers together into one lawful intraday system. That is a much healthier place to be stuck. Being blocked by execution infrastructure is frustrating, but it is a better problem than being blocked by semantic confusion. It means the branch has mostly finished learning what reduce should mean. It has not yet earned the right to trade it end to end.

## JOURNAL-0364 Once Execution Gaps Are Named, The Project Feels Less Vague

Date: 2026-04-04

One reason a branch can feel "unfinished" even after a lot of work is that the remaining blocker is still described too vaguely. Saying that execution binding is missing is true, but it is not useful enough. It keeps the branch emotionally open-ended. The blocker audit improves that because it names the missing surfaces one by one. Two belong to sell-side binding. Two belong to full closure. That is a much healthier diagnostic state.

This matters psychologically as well as technically. Once the branch can say "sell-side binding is waiting on point-in-time visibility and a deterministic simulator" and "full closure is waiting on a replay lane and a reentry surface," the work stops feeling like a foggy unfinished mess. It becomes an ordered backlog. That is exactly what a mature governance branch should do: reduce existential uncertainty into explicit dependencies.

## JOURNAL-0365 The Sell Side Is Less Incomplete Than It Feels

Date: 2026-04-04

After the branch spent so long building minute supervision, it was easy to keep emotionally treating sell-side execution as if it were still mostly missing. The readiness audit corrects that feeling. The branch already has a lawful all-session visibility surface. It already has a deterministic seed simulator. It already has a current wider sell shadow that acts as a frozen behavioral reference. In other words, the branch is not staring at an empty sell-side execution problem. It is staring at an integration problem.

That distinction matters. An empty problem invites more research. An integration problem invites narrower engineering. This is one of those moments where a branch becomes healthier by admitting that the semantic work is sufficiently mature for its current scope. The right next step is not to keep searching for a better sell family. The right next step is to bind the existing pieces through holdings-aware state and an isolated shadow lane. That is a smaller and more honest frontier.

## JOURNAL-0366 A Good Sell Shadow Is Not Yet A Real Inventory Surface

Date: 2026-04-04

There is a subtle but important difference between a strong shadow reference and a bindable execution surface. The wider sell shadow now behaves well enough that it is tempting to mentally promote it into "the thing we would really do." The holdings-aware audit pushes back on that temptation. Most of the current wider sessions are still sized in normalized reference quantity, not in actual frozen-primary inventory. That means the branch can describe good sell behavior without yet being able to claim that the behavior belongs to the real portfolio state.

This is a useful disappointment. It narrows the next task. The branch does not need another sell family. It needs a holdings ledger. It needs start-of-day reality. It needs a policy for what happens when a same-day EOD open, add, or reduce collides with an intraday sell trigger. Those are mundane problems, but they are the right problems. Once a branch reaches this stage, more semantic cleverness is usually a distraction. The bottleneck has become inventory truth.

## JOURNAL-0367 Inventory Truth Produces Smaller, Better Questions

Date: 2026-04-04

Once the branch stops pretending that reference quantity equals real inventory, the execution problem becomes smaller and healthier. The question is no longer "what is the best sell signal?" The question becomes "what quantity was actually carried into the day, and what should happen if an intraday sell collides with a same-day open, add, reduce, or close?" Those questions are less glamorous than signal research, but they are exactly the questions that make a shadow lane honest.

This is one of the cleaner transitions in the branch so far. The sell-side is no longer blocked by missing semantics. It is blocked by accounting. That is progress. Accounting is narrow. Accounting can be audited. Accounting does not seduce the branch into new stories. The start-of-day ledger and the same-day precedence policy are valuable precisely because they force the branch to respect inventory truth before it earns the right to claim execution realism.

## JOURNAL-0368 The First Real Binding Surface Feels Smaller Than The Old Shadow, But Truer

Date: 2026-04-04

There is a psychological shift once the branch moves from a normalized shadow to a carried-inventory lane. The new lane is smaller. It fires on fewer sessions. It refuses to sell same-day new lots. It clips later EOD reduce and close requests when the carried bucket is already gone. At first that can feel like a loss of power. In reality it is the first moment the sell-side becomes honest enough to deserve the word binding.

That honesty matters more than raw activity. A lane that only sells what actually existed at the start of the day is less dramatic, but far more trustworthy. The branch now has something it did not previously have: a real, holdings-aware sell reference. That does not solve execution closure, but it changes the tone of the remaining work. The bottleneck is no longer whether the branch can imagine good sell behavior. The bottleneck is whether that behavior remains worthwhile once measured beyond the same-day close.

## JOURNAL-0369 A Strong Same-Day Defense Can Still Hide A 3-Day Rebound Cost

Date: 2026-04-04

One of the most important discoveries in this round is that a lane can be simultaneously right and incomplete. The isolated sell-side lane clearly protects same-day outcomes. It also protects the next day on net. But the 3-day horizon flips slightly positive, which means the branch is paying a real rebound cost pocket even while the same-day defense looks excellent. That is exactly the kind of nuance that gets lost when a branch celebrates too early.

This is a healthy disappointment. It proves the branch is now asking better questions. A weaker branch would have stopped at "the sell lane works." A healthier branch now has to say something more precise: "the sell lane works as a same-day and short-horizon protection surface, but it still carries a nontrivial medium-short rebound caveat." That sentence is better than confidence. It keeps the branch disciplined and points the next work toward local attribution instead of expansion fantasy.

## JOURNAL-0370 Once The Sell Binding Surface Becomes Real, Its Problems Get Smaller And More Honest

Date: 2026-04-04

The local attribution round sharpens the emotional picture again. The first real sell binding surface is not failing everywhere. It is not collapsing under a thousand contradictory cases. Its medium-short caveat is concentrated. The dominant same-day protector and the dominant 3-day rebound residue are both mostly the same symbol. That is frustrating in one sense, but healthy in another: the branch is no longer confusing a local residue with a global invalidation.

This is usually what maturity looks like. Early in a branch, every imperfection feels like a reason to rebuild the whole thing. Later, the imperfections become smaller and more local. The task changes from "find a better worldview" to "keep the current worldview and supervise the residue honestly." That is where this sell-side binding line now sits. It is not finished in the absolute sense, but it has stopped being fundamentally uncertain. That is a meaningful closure point.

## JOURNAL-0371 Closure Often Feels Disappointing Because What Remains Is Small

Date: 2026-04-04

There is a peculiar feeling when a branch gets close to closure. The work stops producing dramatic new mechanisms. Instead it produces a short list of residues, a split between persistent and transient edge cases, and a growing confidence that broad retuning would now be mostly self-harm. That can feel anticlimactic, especially after a long period of discovery. But it is usually a sign that the branch has finally become disciplined.

That is where reduce now sits. The branch still has four rebound-residue seeds. Two persist a bit longer. Two fade quickly. None of that is nothing, but none of it justifies reopening the whole sell-side family either. This is one of the few moments where stopping broad tuning is actually progress. The branch has earned the right to say: the remaining problem is small enough to supervise locally, and that is different from being unfinished in a dangerous way.

## JOURNAL-0372 Research Completion And Execution Completion Are Not The Same Milestone

Date: 2026-04-04

One source of confusion in long branches is the tendency to think that if execution is not finished, then research must also still be open. That is not always true. Reduce now provides a cleaner example. The branch has a full governance stack, a real sell-side binding reference, a documented horizon caveat, and only four residue seeds left under local supervision. At the same time, the full execution closure still remains blocked by infrastructure. Both statements are true together.

That distinction matters because it protects the branch from endless re-entry into solved semantic questions. Once research is complete enough, the healthiest act is often to freeze it and admit that the remaining work is of a different species. In this case, what remains is no longer broad reduce reasoning. It is infrastructure and future handoff discipline. That is a better place to end a research branch than a vague sense that maybe one more pass would reveal something profound.

## JOURNAL-0373 A Good Handoff Package Is A Kind Of Ending

Date: 2026-04-04

There is a final psychological move after a branch is mostly complete: it has to stop thinking of itself as the center of the program. Packaging reduce as a handoff object forces that move. The branch now says, in effect, "I am no longer the place where the next big discovery should happen. I am the place where future work will inherit stable rules and a small residue list." That is a healthier identity than clinging to the role of active frontier forever.

This matters because it creates permission to move on later without guilt. A branch that never reaches handoff form keeps calling the program back into itself. A branch that does reach handoff form can finally say something cleaner: the mainline is frozen, the local residue list is known, the remaining execution blockers are explicit, and the next frontier can be opened intentionally rather than as a leak from unfinished business. That is about as complete an ending as a research branch usually gets.

## JOURNAL-0374 The Cleanest Next Move After Closure Is Usually A Gate, Not A New Idea

Date: 2026-04-04

Once a branch is truly frozen, the temptation is to keep producing one more clever bridge into the next frontier. That is often how drift begins. The more honest move is usually smaller and colder: write down the exact conditions under which the next frontier may open, and then stop. That is what the intraday-add opening checklist does. It is not new alpha. It is a boundary.

There is something mature about this kind of work. It accepts that good research programs do not move forward by emotional momentum alone. They move by explicit gates. Reduce is now strong enough that the main risk is no longer inside its semantics. The risk is that the next thing starts in a sloppy way and inherits authority it never earned. A checklist is an antidote to that kind of contamination.

## JOURNAL-0375 A Deferred Frontier Still Benefits From Being Easy To Read

Date: 2026-04-04

After a checklist exists, the next temptation is to keep elaborating it. That can become another form of drift. A better move is often to compress the deferred frontier into a status card that says, in one glance, what is frozen, what is next, and what is still prohibited. That is what the prelaunch card does for intraday add. It removes ambiguity without creating momentum.

This kind of artifact matters because deferred states are psychologically unstable. People treat them as half-open. A clean status card fights that impulse. It says something colder: yes, the next frontier is named; no, it is not active; yes, preparation exists; no, silent opening is allowed. That is less exciting than discovery work, but it is the kind of operational hygiene that prevents the next frontier from beginning with contamination.

## JOURNAL-0376 Once A Deferred Frontier Is Real, Program Governance Has To Say So Out Loud

Date: 2026-04-04

There is a subtle failure mode in research programs: the board-level governance becomes cleaner than the program-level governance. When that happens, the local truth is sharp but the global posture is still blurry. That blur invites accidental continuation. Refreshing the program master card to include the deferred frontier's gate count and silent-opening ban is not glamorous, but it closes that gap.

This kind of synchronization is a small sign of maturity. The program no longer relies on memory or on the researcher's mood to remember that the next frontier is deferred. It can now state that fact mechanically at both levels. When a branch has reached that point, more continuation is usually not curiosity anymore. It is just resistance to stopping.

## JOURNAL-0377 The Final Form Of A Deferred Frontier Is Operational, Not Semantic

Date: 2026-04-04

There is a moment when a deferred frontier stops benefiting from more conceptual work. The remaining useful artifacts become almost embarrassingly operational: a heartbeat that says the frontier is still not open, and a short playbook that says what to do when it finally is. Those are not glamorous objects. But they are the right ending for a branch that has already done enough thinking.

This matters because deferred frontiers often absorb anxiety. People keep adding one more specification, one more note, one more clever safeguard, as if the frontier would feel safer when it is more elaborated. Usually the opposite is true. Once the gate, status, and playbook exist, the safest thing is to stop. Anything more is often just an unwillingness to admit that the next real move now belongs to the future.

## JOURNAL-0378 Opening Add The Honest Way Means Starting With Raw Inheritance

Date: 2026-04-04

When a new frontier opens, the strongest temptation is to begin with a polished theory. Add would be especially vulnerable to that because it feels intuitively exciting and directionally positive. But the right beginning turned out to be colder: take the existing open/add surface from the frozen EOD branch, do not grant it execution authority, and turn it into a supervision registry. That is a more honest start because it forces the branch to look at what it already inherited before it starts narrating what add is supposed to mean.

This also protects the new frontier from overconfidence. A registry is not a claim that add is understood. It is a claim that add now has a canonical seed surface that can be interrogated. That distinction matters. It keeps the new branch from skipping its own apprenticeship just because reduce had already matured.

## JOURNAL-0379 The First Add Feed Changes The Program More Than It Changes The Branch

Date: 2026-04-04

The point-in-time add feed is important, but its deepest effect is not local. It changes the truth of the whole program. Once add has a lawful seed feed, the program can no longer pretend the frontier is merely deferred. The shift has happened. That required a master-status refresh, and that refresh is more than bookkeeping. It is the moment when the system admits that the new branch is now active, even if only at supervision scope.

That kind of honesty matters because research programs often linger in transitional language. They keep saying "next frontier" long after the next frontier is already being worked on. Refreshing the master card prevents that self-deception. It says something sharper: reduce is frozen, add is open, and the new work must now earn its own structure without borrowing execution authority from the old branch.

## JOURNAL-0378 The First Honest Step Of Add Is Not Confidence, It Is A Registry

Date: 2026-04-04

When add finally opens, the temptation is to make it symmetrical with reduce and jump straight into action language. That would be too fast. Add has less mature supervision than reduce did. The cleanest first step is therefore not a simulator and not a rule engine. It is a registry: what did the historical open/add surface look like, which cases now still look legitimate, which turned into obvious failures, and which would have been blocked under the current board-level veto stack.

That is a quieter beginning than people usually want from a new frontier. But it is the right one. A registry says the branch is willing to look at its raw inheritance before it starts inventing authority. It also keeps the most important asymmetry clear: add is now open, but it is open only as supervision. That distinction matters. It keeps the new branch from borrowing confidence it has not earned yet.

## JOURNAL-0380 Add Needed A Vocabulary Before It Needed A Theory

Date: 2026-04-04

The point-in-time feed made intraday add lawful enough to inspect, but it still did not say what kind of add each case was. That gap matters more than it first appears. A frontier without a vocabulary tends to hallucinate structure. It starts talking about "good adds" and "bad adds" in broad strokes, and that vagueness quickly leaks into premature execution ideas. Freezing the first tier vocabulary prevents that drift.

What emerged is not a grand theory, just a disciplined split: soft preheat probe adds, stronger preheat full adds, failed impulse-chase adds, and board-blocked adds. That sounds modest, but it is exactly the right level of truth for a young branch. It says the new frontier has differentiated its inheritance enough to start pattern mining, but not enough to pretend it already owns action authority. That is a healthier kind of progress than rushing into simulated entries with labels that still blur together.

## JOURNAL-0381 Add Archetypes Became Real Once The Blocked Cases Stopped Looking Like Near-Misses

Date: 2026-04-04

The most useful thing in the first local add envelope audit was not the distinction between probe and full. That distinction was expected. The more clarifying result was what happened to the blocked board-lockout cases. They do not look like pure collapse in the first fifteen minutes. In fact they can look briefly repaired. That matters because it explains why a naive intraday-add branch would be tempted to misclassify them as tradeable local rebounds.

Once that observation is named correctly, the hierarchy gets cleaner. A blocked add is not a near-miss allowed add. It is a board-vetoed local rebound whose temporary early repair is precisely the reason the veto must remain upstream. That is an important maturation point for the add frontier. It means the branch is no longer just distinguishing good from bad entries. It is learning that some apparently decent entries are structurally invalid because the board regime is wrong.

## JOURNAL-0382 Probe Needed To Stay Weaker Than Full Without Being Punished For Looking Weak

Date: 2026-04-04

The first add rules almost worked immediately. That is usually a warning sign, because it often means the rules are just restating the labels. But the one real mismatch cluster was instructive: several probe seeds were being thrown out simply because their fifteen-minute close location was too poor. That would have been a subtle conceptual mistake. Probe is supposed to tolerate weaker early acceptance than full. If it demanded upper-half range quality, it would stop being probe and start imitating full.

Once that unnecessary gate was removed, the rule set became cleaner, not sloppier. That is the useful kind of refinement. It did not broaden the branch into permissiveness. It restored the intended asymmetry between probe and full. That is exactly what a young frontier should learn from its first rule pass: not every weak-looking entry is invalid, only the ones that violate the semantics of their own tier.

## JOURNAL-0383 Add Hit A Real Expansion Wall The Moment It Left The Seed Surface

Date: 2026-04-04

The first broader false-positive audit for add was clarifying in the bluntest possible way. The positive rules that looked coherent on the 55-row seed surface became far too generous on the wider local session surface. That is not a subtle failure. It is a structural one. It means the branch currently knows how a historically valid add looked, but it does not yet know how to distinguish that from an ordinary early-session rebound when the historical seed context is removed.

That wall is actually useful. It prevents the branch from lying to itself. A young frontier often wants to believe that once a seed rule is internally consistent, expansion is just a matter of tuning thresholds. This audit says otherwise. The missing ingredient is context, not calibration. Until positive add permission is anchored to stronger context, broader expansion would just be a generic rebound detector wearing an add label.

## JOURNAL-0384 Slow Context Was Helpful Enough To Be Honest, But Not Strong Enough To Be Useful

Date: 2026-04-04

It was tempting to believe that one more layer of slow context would save the broader add rules. Phase windows, expectancy unlock dates, repeated full-capable symbols: all of these sound structurally meaningful, and they are. But the audit showed something more sobering. They reduce density, yes, but they do not transform the problem. Even the best combination still leaves too many non-seed positive hits relative to the number of genuine seed cases it preserves.

That is an important kind of failure because it narrows the search space. It means the add frontier does not merely need better board context. It needs a stronger permission surface that is point-in-time and nearer to the add decision itself. In other words, the next useful object is not another slow veto. It is a context layer that can explain why an early-session rebound is genuinely add-permissive on that bar for that symbol, instead of merely looking strong in isolation.

## JOURNAL-0385 The First Useful Add Permission Clue Was About Containment, Not Strength

Date: 2026-04-04

The add branch finally picked up a more realistic piece of early-session behavior: genuine add seeds are often less frantic than the broader population of shape-only positive rebounds. That is not the direction a naive momentum mind expects. It wants the best adds to look strongest immediately. But the broader audit had already hinted that the branch was overfiring on ordinary strong opens. The point-in-time quantity-price pass makes that intuition explicit. What starts separating the better add seeds is not extra explosiveness. It is early containment: less first-fifteen-minute amount consumed too quickly, less crowding into too many positive bars, less evidence of a chase.

That does not solve the frontier, but it does correct the frontier's bias. The branch was too willing to believe that stronger-looking early sessions deserved permission. The new clue says something subtler: some of the truest adds are constructive without already looking exhausted by their own first fifteen minutes. That is a meaningful conceptual step because it makes the branch more like a permission system and less like a rebound detector.

## JOURNAL-0386 Reduce Needed A Written Quantity-Price Appendix Even Though It Did Not Need A Reopen

Date: 2026-04-04

The user's nudge about quantity and price was right in an important way. Reduce had already learned useful quantity-price distinctions earlier, but the frozen handoff package still looked too price-path-centric if someone skimmed it quickly. That is risky because frozen branches tend to calcify around whatever is most visible, not necessarily around everything that actually mattered. Writing the quantity-price supplement down as an explicit governance appendix fixes that asymmetry.

Nothing new was "discovered" in reduce this round. That is precisely the point. The branch did not need reopening. It needed a cleaner memory. The strongest reversal-side separator and the local rebound-cost veto were already there; they just needed to be carried forward as official retained context instead of implicit background. That is the right kind of supplementation for a frozen branch: no new frontier, no fake progress, just a more faithful handoff.

## JOURNAL-0387 The First Good Add Permission Clue Turned Out To Be A Family, Not A Rule

Date: 2026-04-04

The encouraging part of the first quantity-price permission clue was that it did not simply reduce density. It also uncovered a real pocket of sessions that continued through the rest of the first hour. That matters because it means the clue is not just a compression artifact. It is seeing something structurally closer to true permission than the raw shape-only branch could see. But that result immediately came with an equally important limitation: the same narrow clue still captures fragile and outright failed sessions.

That is exactly the kind of mixed result that should change the branch's mental model. A weaker branch would try to turn the clue into a single rule and then spend three more rounds pretending the remaining misses are just parameter noise. A stronger branch admits what the clue really is: a family generator. It surfaces a meaningful local continuation family, but it also surfaces nearby counterfactuals. That means the next object to build is not permission authority. It is family supervision. The branch is learning structure, but not yet enough structure to claim execution rights.

## JOURNAL-0388 Add Finally Produced A Confirmation Layer That Looks Like Confirmation

Date: 2026-04-04

Most of the add frontier so far has been about learning what not to overclaim. That discipline mattered, but it also created a risk: the branch could become so cautious that every improvement still sounds like another way of saying "not ready." This round is different. The persistent-permission family now has a simple local confirmation gate that is genuinely clean. Within that narrow family surface, asking for a decent hour-close and positive continuation from minute fifteen to minute sixty separates nine persistent candidates with no fragile or failed contamination.

That does not mean the frontier is ready for execution. It means something subtler and more useful: the branch has finally produced a confirmation object that behaves like confirmation instead of behaving like a denser or looser proxy. That is a qualitative change. The add frontier still cannot promote broad positive permission, but it no longer lacks a believable local confirmation layer. That is exactly the kind of progress that makes a young branch worth continuing, because it is now learning structure that can survive contact with counterfactuals rather than just surviving inside seed labels.

## JOURNAL-0389 Persistent Permission Needed A Quality Ladder Once It Became Real

Date: 2026-04-04

As soon as the persistent-permission family gained a clean continuation gate, it stopped being useful to speak about it as a single object. That is a good problem to have. Weak branches stay vague forever. Stronger branches eventually discover that the thing they finally trust also contains internal asymmetry. Here that asymmetry is intuitive once named: some persistent cases really do look like full-quality permission, some are still probe-quality, and a small bridge tier sits uncomfortably in the middle.

That bridge tier is especially valuable because it prevents the frontier from overlearning. If the branch only had full-quality and probe-quality pockets, it would be tempting to claim a neat dichotomy. But the mixed middle is a reminder that local permission is not a finished ontology. It is a developing one. The right response is not to force certainty. It is to encode the bridge explicitly and keep it as an upgrade watch. That preserves nuance without surrendering structure.

## JOURNAL-0390 The Strongest Add Tier Turned Out To Be Surprisingly Simple

Date: 2026-04-04

After several rounds of family-building, continuation checks, and quality layering, the strongest local add tier finally collapsed into something simple: if the first fifteen minutes finish high enough in their own range, the full-quality persistent cases separate cleanly. That kind of simplification is valuable precisely because it arrives late. Early simplifications are usually fake. Late simplifications often mean the branch has earned the right to compress what it learned.

What matters here is not that `close_loc_15m` is some magical universal feature. It is that, inside the already narrow and highly supervised local ladder, it became a faithful anchor for the strongest tier without leaking bridge or probe cases back in. That is the kind of archetype a branch can carry forward safely: not as permission authority, but as a readable anchor that keeps the strongest local object legible.

## JOURNAL-0391 The Frontier Learned Something Important By Failing To Port Its Best Object

Date: 2026-04-04

One of the easiest mistakes at this stage would be to confuse a clean local object with a portable one. The strongest add archetype is now very readable inside the persistent-permission ladder, and that kind of success naturally invites ambition. But the portability audit was valuable precisely because it refused to indulge that ambition. Even after combining the archetype with the best slow context and burst moderation, the branch still retained too many non-seed cases relative to the tiny number of seed cases it preserved.

That failure is clarifying. It says the add frontier has already learned one of the hardest research lessons: local truth and portable truth are not the same thing. The branch now owns a genuinely useful local archetype, but it also knows exactly where that ownership stops. That is progress of the right kind, because it makes the frontier more bounded rather than merely more complicated.

## JOURNAL-0392 The Remaining Add Portability Misses Turned Out To Be Counterfactuals, Not Noise

Date: 2026-04-04

The next useful question after a portability failure is whether the residue is random or structured. If the remaining non-seed hits are random, then the branch probably still lacks a real object. If they are structured, then the object may be real but blocked by a different layer. That is what this round clarified. The three residual non-seed hits under the strongest portable-looking add scenario did not look like generic false positives. They clustered into two much more specific families: one displaced same-day alternative and two no-order-day late echoes on symbols that had already produced earlier allowed-add seeds.

That matters because it changes what the branch should work on next. There is little value in pretending more local shape tweaking will solve a problem that is no longer local. The active blocker has moved upward. The frontier now has enough evidence to say that its strongest local add object is not failing because the archetype is fake. It is failing because broader promotion needs a day-level selection authority the branch does not yet own. That is a much better kind of blocker to discover than another vague "needs more data" excuse, because it narrows the next supervision question without overstating present capability.

## JOURNAL-0393 The Add Frontier Finally Found Its Daily Choice Problem

Date: 2026-04-04

Once the residual non-seed hits were shown to be structured, the obvious next question was whether the structure lived at the symbol level or at the daily decision level. This round answered that cleanly. Under the strongest portable-looking add scenario, the frontier does not see a large messy surface. It sees four days, and those four days already separate into three interpretable daily families: one aligned day where the strong candidates and the real open/add decisions match, one displaced day where a strong candidate exists but another symbol gets chosen instead, and two post-wave echo days where the local shape survives after the add wave has already passed.

That is a useful narrowing because it means the branch should stop negotiating with local shape. Local shape has already done its job. The next missing layer is a daily authority for selection: why a day with multiple plausible objects resolves to one actual choice, and why an apparently strong local echo should still stay dormant on a no-order day. In other words, the add frontier is no longer primarily blocked by not understanding the candle. It is blocked by not yet understanding the day.

## JOURNAL-0394 The Daily Add Problem Split Again, And That Is Good News

Date: 2026-04-04

The moment the frontier found a daily authority problem, it still faced a risk of overgeneralizing. "Day-level selection" can become another vague bucket if it is not split quickly. This round did the useful next cut. The four key candidate days under the strongest portable-looking add scenario do not all represent the same unresolved issue. Two of them are already much easier than the others: they are post-wave echo days, where no new add wave is active and the local shape is simply arriving too late. Those can be filtered with a cheap recent-order-flow state. That is not a complete solution, but it is a real simplification.

What remains after that simplification is the harder and more interesting part: active-wave selection. That is where the branch must explain why a live add wave resolves into one actual symbol choice instead of another equally plausible local candidate. This is progress because it makes the frontier smaller and sharper. The branch no longer needs to solve a generic portability mystery. It now needs to solve a specific ranking problem inside live add waves, while keeping a separate veto for post-wave echoes.

## JOURNAL-0395 The First Same-Wave Add Selection Clue Is Small But Real

Date: 2026-04-04

After carving away the easy post-wave echo days, the frontier was left with a much smaller and more honest problem: what happens inside an actually live add wave. That is where overfitting becomes tempting, because the sample is tiny and the urge to declare a full ranker arrives early. The right move was narrower. Instead of inventing a whole ranking model, the branch asked whether the displaced candidate differed in one simple and interpretable way from the selected ones. The answer was yes. The displaced candidate sat inside recent symbol-level reduce residue, while the selected ones fell into either same-symbol continuation or clean-reset states.

This is not execution authority. It is not even a complete daily ranker. But it is the right kind of progress. The frontier now has a first same-wave state split that explains something real about why one local candidate was not chosen. That means the active-wave problem is no longer an abstract "needs more daily context" complaint. It has started to grow concrete internal states. Those states can now be supervised further without pretending the branch has earned broader promotion yet.

## JOURNAL-0396 The First Same-Wave Exclusion Clue Passed The Smallest Honest Test

Date: 2026-04-04

Once the active-wave state split existed, the next honest question was whether the negative state was merely descriptive or already useful. The smallest fair test was simple: if recent reduce residue is treated as a local exclusion clue, does it remove the displaced candidate without mistakenly removing the selected ones? On the current surface, the answer is yes. That matters less because the numbers are large—they are not—and more because the branch resisted the temptation to ask for more than the sample can support. It asked a tiny question and got a clean answer.

That answer should still be handled carefully. A clean local exclusion clue is not a daily ranker, and it is certainly not execution authority. But it is a meaningful step because it shows the active-wave selection problem is no longer just a mystery about "why this one and not that one." It has started to admit explicit exclusion logic. That makes the next supervision layer clearer: not broader promotion, but a more structured local daily-choice language built around exclusion and continuation rather than raw shape alone.

## JOURNAL-0397 The Branch Learned To Exclude Before It Learned To Rank

Date: 2026-04-04

After finding a clean local exclusion clue, the natural temptation would be to search for its mirror image: a positive daily ranker that tells the branch which remaining same-wave candidate should win. This round showed why that temptation must be resisted. The two retained selected states still do not behave like a single positive archetype. One has stronger early push, the other has stronger close-location and hour-end continuation. That is not a failure. It is a useful boundary. The branch now knows it has learned exclusion faster than ranking.

That asymmetry is healthy. Good frontiers rarely learn everything at once. Here the add branch has earned one clean negative clue but not a promotable positive ranker. That means the correct next step is not to blur the distinction and pretend the branch already has a full same-wave selection engine. The correct next step is to preserve the asymmetry explicitly: keep the exclusion logic, block positive-ranker promotion, and continue treating the remaining selected states as supervision structure rather than execution truth.

## JOURNAL-0398 The Frontier Does Not Need A Single Winner If The Local States Are Complementary

Date: 2026-04-04

Once the branch admitted it did not yet own a positive daily ranker, the next useful question was whether ranking was even the right problem. That is where this round helped. The two retained same-wave states do not merely fail to collapse into one winner. They also look complementary in a way that makes a dual-slot interpretation more natural. One slot carries continuation: reuse an already live symbol that is still behaving well. The other carries reset: allow a clean new participant without inheriting fresh residue. That is a different framing from ranking, and in this case it is the more honest one.

This matters because it changes the tone of the frontier. A branch that cannot rank often sounds incomplete. A branch that can already define parallel permission slots sounds more structurally mature. It still does not have execution authority, and it still should not promote itself into a broader module. But it no longer needs to apologize for not producing a single winner when the local evidence still favors differentiated risk-sharing states. That is not a weakness. It is a better reading of the object the branch currently owns.

## JOURNAL-0399 The First Risk-Sharing Add Archetype Turned Out To Be Tiered

Date: 2026-04-04

Once the frontier accepted a dual-slot reading, the natural next question was whether those slots should be treated equally or asymmetrically. The local answer was not neutral. On the only day where both slots were simultaneously live, the clean reset slot carried roughly twice the participation of the continuation slot. That is a useful finding because it makes the risk-sharing story more concrete. The branch is not just saying "both can exist." It is saying the two slots can exist with different responsibilities: the reset slot as the primary fresh exposure and the continuation slot as the smaller reinforcing layer.

This still is not execution authority. One local day is not enough to declare a real allocation policy. But it is enough to keep the frontier honest about what kind of object it currently owns. It owns a tiered local allocation archetype, not a flat two-slot symmetry and not a deployable sizing engine. That is a stronger and more usable statement than either overclaiming execution readiness or pretending the branch has learned nothing about add-side risk sharing.

## JOURNAL-0400 A Dual-Slot View Does Not Mean Dual Slots Are Always Available

Date: 2026-04-04

The next trap after discovering a dual-slot structure is to start treating it as the default topology of the branch. That would be premature. This round showed why. On the current strict active-wave surface, dual-slot coexistence only appears on one local day. The other active-wave day does not degrade into a neat single-slot case on the same surface; it actually collapses below retained-slot capacity altogether after the current local filters and exclusions are applied. That is a useful warning. A dual-slot view can be correct without being universally available.

This is an important distinction for the branch's discipline. The add frontier now owns a conditional capacity object, not a default one. That means the right next step is not to operationalize "always open both slots." It is to preserve the logic that dual-slot coexistence is contingent, local, and currently rare. That keeps the branch grounded in the actual structure of the sample instead of letting a good local archetype inflate into a universal operating assumption.

## JOURNAL-0401 Exclusion First, Capacity Second

Date: 2026-04-04

This round clarified that the add branch should not think about slot capacity as a sizing question first. It is a hierarchy question. The current strict active-wave surface resolves in two stages. First, same-wave exclusion is applied. Second, whatever remains may support either zero-slot or dual-slot capacity. That ordering matters because it explains why one active-wave day does not become a clean single-slot example. The branch is not failing to allocate; it is correctly collapsing into no retained slot after exclusion.

This is a stronger reading than simply saying dual-slot is rare. It means capacity itself is downstream of governance. The observed dual-slot day remains valuable because it gives a local tiered pattern: reset primary, continuation secondary. But the absence of a single-slot day means we still do not have a portable fallback allocation rule. The branch should therefore preserve zero-slot veto and tiered dual-slot as the two currently valid local capacity states, while keeping broader promotion and execution blocked.

## JOURNAL-0402 No Single-Slot Template Yet

Date: 2026-04-04

It is tempting to assume that once an add branch learns zero-slot veto and dual-slot coexistence, the missing middle must be a single-slot fallback. This round showed that the sample does not justify that shortcut. On the current strict active-wave surface, no true single-slot day exists. The branch resolves into either full exclusion or a local tiered dual-slot pattern. That absence matters because it prevents us from inventing an allocation template the data has not earned.

The only honest concession is a weak local surrogate: if a forced one-slot reading is needed on the lone dual-slot day, the reset slot has the stronger provisional claim. But that is not the same thing as observing a real portable single-slot state. The branch therefore now has a sharper topology. It knows how to veto, it knows how to hold a local two-slot structure, and it knows that the one-slot middle is still missing. That missing middle is itself informative because it marks the current stopline for add-capacity promotion.

## JOURNAL-0403 Forced Collapse Is Not Observation

Date: 2026-04-04

This round closed an important loophole. Once the branch admits that no true single-slot fallback has been observed, the next temptation is to treat the stronger slot on the lone dual-slot day as if it had already earned the missing template. That shortcut would overstate the evidence. What we actually learned is narrower. If the local two-slot structure is forcibly collapsed into one slot, reset survives more naturally than continuation. It wins on more quality dimensions and already carries the larger local weight. But that is still a forced-collapse reading, not a naturally observed single-slot state.

This distinction matters because it prevents the branch from smuggling a portable allocation rule through a local asymmetry. The reset slot can now be described more precisely: not as the branch's single-slot fallback, but as the only plausible local surrogate under explicit forced collapse. That keeps the supervision branch honest and preserves the real stopline: a portable one-slot template is still missing.

## JOURNAL-0404 Add Has Reached Its Supervision Stopline

Date: 2026-04-04

The add branch now looks much more like a completed supervision program than an open frontier. It has a stable registry, seed rules that recover the frozen surface, a local permission hierarchy, a local confirmation layer, and a local slot-capacity hierarchy. What it does not have is equally clear: portable positive promotion, an observed single-slot fallback, or execution authority. That distinction matters because it marks a genuine stopline. At this point, asking the branch for more broad local tuning would mostly mean forcing portable answers out of a sample that has only earned local ones.

This is structurally similar to where the reduce branch ended up before handoff. The research layer becomes complete enough before the execution layer becomes legal or portable. For add, the honest state is now the same: the supervision mainline is rich enough to freeze, while the missing pieces remain explicitly blocked. Future work should therefore narrow rather than widen. Unless a real portability unlock appears, the branch should move from open exploration into local residue maintenance.

## JOURNAL-0405 The Missing Middle Becomes The New Frontier

Date: 2026-04-05

Both major branches had reached the same structural stopline. Reduce had become research-complete enough but still lacked full execution authority. Add had also become supervision-complete enough but still lacked portability and execution authority. That symmetry changes the question. The next frontier should not be another local clue inside either branch. It should be the missing middle that connects them.

This round therefore promotes a different kind of frontier: not a new alpha family, but a unifying shadow replay lane. The lane is explicitly protocol-only and read-only. That matters because it prevents the project from pretending that frozen supervision stacks are already lawful execution modules. The first useful build inside that lane is the reentry/unlock bridge. It already has enough frozen material to be specified cleanly: reduce exit as source, board lockout and unlock as upper gates, reentry timing and confirmation as the middle state machine, and only then add supervision as a downstream permission consult. The lane can now move forward without re-opening either frozen branch or claiming execution authority it still has not earned.

## JOURNAL-0406 The Bridge Stops Being Abstract

Date: 2026-04-05

The new frontier needed to pass a simple test before it could become useful: it had to stop being purely procedural language. This round is the first point where that happened. The reentry/unlock bridge now has a concrete state surface. That matters because it turns a sequence of governance ideas into an enumerable object. Each current seed can now be placed inside board-gate state, same-day chase block, observation window, rebuild-watch timing, later confirmation shape, and add-handoff readiness.

The surface also clarified something important: none of the current seeds are actually ready to hand off into add permission. One seed sits before the formal lockout start, two sit inside the lockout window, and all three remain blocked from same-day chase. That is a healthy result because it prevents the bridge from smuggling reentry optimism into add consultation before board unlock has genuinely occurred. The bridge now has a real table, but still no execution authority. That is exactly the right asymmetry at this stage.

## JOURNAL-0407 The Bridge Blocker Is Now Concrete, Not Intuitive

Date: 2026-04-05

The handoff blocker between reentry and add is no longer a vague feeling that the timing is not ready. It is now explicit and two-layered. Every current seed fails the bridge for the same pair of reasons. First, the rebuild-watch date still sits inside the board-level cooling lockout. Second, there is no later unlock seed after that rebuild-watch date. This matters because it changes the mental model of the bridge. The blockage is not caused by missing minute nuance or weak symbol confirmation alone. It is caused by the absence of a lawful board-level reopening context.

That is a useful tightening of the frontier. It means the bridge has already learned something important without simulating a single trade. A seed can look better on its own timetable and still remain non-handoffable because the board never reopens. That keeps the project from confusing local symbol recovery with a valid transition back into add permission. The bridge is now doing the right kind of work: converting intuition about timing and regime mismatch into explicit blocked states.

## JOURNAL-0408 Post-Lockout Vacancy Is Not The Same As Weakness

Date: 2026-04-05

The next blocker turned out to be narrower and more structural than another round of symbol interpretation. After lockout end, local raw intraday dates still exist. The raw calendar continues through late March and early April. But the derived board-state surface stops exactly at the lockout boundary. That matters because it changes how the vacancy should be read. The project is not merely waiting for a better unlock-looking day inside an already-modeled board regime. It is missing the post-lockout regime surface itself.

This distinction is useful because it keeps the shadow replay lane honest. If post-lockout dates existed nowhere, the blocker would be a plain data absence. If post-lockout board states existed and all looked weak, the blocker would be a negative board judgment. What exists here is different: raw local dates continue, but the board-level derivation has not yet been extended across them. That means the bridge still cannot lawfully reopen into add consultation. The missing object is not another local clue. It is the post-lockout board surface on which unlock context could even be tested.

## JOURNAL-0409 The Gap Is Synchronized, Not Accidental

Date: 2026-04-05

This round tightened the blocker again. The earlier vacancy audit already showed that post-lockout raw dates continue. The next useful question was whether one derived surface had merely gone stale while another still extended forward. The answer is no. Both board-level surfaces stop on the same date: the lockout end itself. Daily state stops there, and phase geometry stops there too. Raw intraday data continues for ten more trading days, but the two derived board surfaces do not. That makes the blocker structurally cleaner than a generic missing-update story.

This matters because it changes the kind of future work that is justified. The shadow replay lane is not yet asking for a subtler unlock classifier. It is asking for the board-state derivation boundary to move. Until that happens, any discussion of post-lockout unlock quality remains premature. The bridge is not blocked by a weak candidate living inside an already-modeled reopening regime. It is blocked because the reopening regime surface has not yet been extended at all.

## JOURNAL-0410 The Boundary Matches Lockout, Not Last Trade

Date: 2026-04-05

The next useful distinction was whether the derivation gap should be blamed on missing raw data, on the end of trading activity, or on a deliberate analytical boundary. The answer is now much cleaner. Execution history ends on 2026-02-27. But the derived board surfaces continue well past that date and stop only on 2026-03-20, exactly where board lockout ends. Raw daily bars and raw intraday data both continue through 2026-04-03. That combination rules out the two lazier explanations. The stop is not driven by raw-data absence, and it is not simply inherited from the last execution day.

What remains is the more structural reading: the current bridge is blocked by a lockout-aligned derivation boundary. This matters because it changes the next honest question. The project is no longer deciding whether post-lockout days look good enough. It is deciding whether the board-state derivation boundary itself should remain frozen at lockout end or be explicitly extended beyond it. Until that policy changes, the bridge cannot legally reopen, regardless of how many raw post-lockout dates already exist underneath it.

## JOURNAL-0411 Existing Raw Coverage Does Not Authorize Silent Extension

Date: 2026-04-05

Once the boundary was classified, the next temptation was obvious: if raw daily and raw intraday data already continue beyond lockout end, why not just let the derived board surfaces continue automatically too? This round closes that shortcut. The presence of raw coverage does not by itself authorize a new derived board regime. That would silently convert a frozen lockout-aligned boundary into an open extension policy without ever naming the policy change. For a shadow replay lane that is still read-only and still blocked from execution, that would be the wrong kind of progress.

The cleaner framing is now explicit. There are two different future paths, and only one is currently active. The active path is to retain the boundary and keep the bridge blocked. The inactive but legitimate future path is to open an explicit shadow-only extension program. That distinction matters because it preserves governance order. The project should not start judging post-lockout unlock quality until it has first admitted that the derivation boundary itself is being extended on purpose.

## JOURNAL-0412 Preparation Stops Short Of Opening

Date: 2026-04-05

The boundary question has now reached the same kind of stopline that other frontiers hit earlier. Once it became clear that silent extension was the wrong move, the remaining useful task was procedural rather than analytical: define how a future extension would have to open if the project ever chose to do it. That is what the new checklist does. It names the gates without crossing them. Policy shift must be explicit. Extension must remain shadow-only. Daily-state and phase-geometry surfaces must extend together. Unlock-quality debate still comes later, not now.

That matters because it keeps the lane from drifting into accidental implementation. The project now has enough structure to extend the boundary later without confusion, but it has not actually extended it. This is the right stopping point for the current blocker. The bridge remains blocked, not because the next step is unknown, but because the next step is now clearly a future opening decision rather than a present analytical obligation.

## JOURNAL-0413 The Deferred Option Is Now Fully Formed

Date: 2026-04-05

There is a useful difference between an undefined future option and a fully formed deferred one. After the checklist was added, one more compact object was worth creating: a prelaunch status card. That card does not add new research signal. It simply makes the current posture explicit and stable. Boundary extension now has a name, a state, a gate count, and a prohibition on silent opening. That means the line has reached the same kind of management stopline other frozen branches reached earlier.

This matters because it closes the temptation to continue polishing the deferred branch as if more paperwork were equivalent to forward progress. It is not. Once the option is fully formed and explicitly deferred, the honest next step is to stop. The branch should remain frozen until an explicit frontier shift is made. Anything else would be governance drift dressed up as diligence.

## JOURNAL-0414 Strong Symbols Can Still Be Negative Labels

Date: 2026-04-05

The next useful step was to stop treating all post-lockout strength as one thing. Named symbols like 天银机电, 再升科技, 神剑股份, 航天发展, and 西测测试 do not all tell the same story. Some rebound weakly and never get close to prior highs. Some approach prior highs only after lockout end, inside a raw-only zone where board context does not legally exist. One of them, 天银机电, even manages to break its prior peak inside the lockout window itself. That is exactly why these symbols are useful negative labels. They show that symbol strength and board restart are separable.

What matters is not just whether they bounce, but where and under what context they bounce. A breakout inside lockout is not a board unlock. A breakout after lockout end, when only raw prices exist but no derived board state does, is not a legal reopening signal either. This gives the project a more mature way to learn from discretionary intuition: strong names can be genuinely strong and still be the wrong reason to re-enter a board.

## JOURNAL-0415 Crowded Shelter Rebound Is Not The Same As Weak Repair

Date: 2026-04-05

One of the more valuable distinctions to emerge is between ordinary weak repair and what looks more like symbol-level crowding. 再升科技 and 神剑股份 do not merely rebound a little more than weak peers. They recover much closer to prior highs and do so with substantially heavier turnover. That is not enough to make them healthy board signals. In fact, it is useful precisely because it shows how a locked board can still host concentrated strength in a few liquid, attention-rich names.

This distinction matters because otherwise the model learns the wrong lesson. If all failed restart attempts are lumped together, it misses the specific danger of crowded shelter names: they look cleaner, stronger, and more persistent than ordinary weak repairs, yet they still fail the board-level restart test. The right interpretation is not that crowding is bullish. It is that crowding is a separate negative-label family that deserves to be learned on its own terms.

## JOURNAL-0416 The Right Next Step Is To Learn Role Separation Before Action

Date: 2026-04-05

Once the local negative-label families were clean enough, the temptation was to jump straight into another action layer. That would have been premature. The more honest reading is that the project still confuses three things that discretionary traders often separate intuitively: the stock that catches heat, the stock that absorbs crowded attention, and the stock that money actually keeps choosing. Those are not the same object, especially in A-share thematic bursts. A hot name can be an attention anchor without being the best trading vehicle. A very strong name can still be evidence of concentration inside a weak board rather than evidence of board restart.

That is why the new route freezes action authority and instead promotes environment semantics and event-attention-capital divergence. The next gain is not another local minute pattern. It is a cleaner language for distorted attention, capital misalignment with the board, and fragile divergence. Only after that language exists should the system try to learn true selection or followthrough leadership. This is also why manifold learning stays late and optional: representation is not the current bottleneck. Label discipline is.

## JOURNAL-0417 Incomplete Information Should Produce Explicitly Incomplete Semantics

Date: 2026-04-05

One risk in moving upward from local negative labels to environment interpretation is false completeness. It would be easy to smuggle in policy pressure, macro weakness, or external board competition as if they were already formalized, simply because they feel directionally true. The better move is to make the current layer explicitly incomplete. That is what the new negative environment registry does. It promotes three semantically useful states—attention distortion, capital misalignment with the board, and fragile divergence—but keeps them board-local on purpose.

This matters because it preserves honesty about what the system actually knows. The current layer is strong enough to say that local strength can coexist with weak board conditions, and that concentrated symbol leadership does not equal healthy board restart. It is not yet strong enough to claim a full external-causality model. Policy and news context therefore belong in the next event-attention layer, not hidden inside the current one. That keeps bias visible instead of turning it into unexamined structure.

## JOURNAL-0418 The First Attention Case Should Be A Hard One, Not A Pretty One

Date: 2026-04-05

The first event-attention layer should not begin with a broad and flattering taxonomy. It should begin with a hard case that forces the distinction between heat and restart. 航天发展 is exactly that kind of case. The turning-point source explicitly names it as a high-recognition emotional axis when the board is overheating, and the later local-path evidence shows that the symbol never rebuilds enough to justify renewed board participation. That makes it a useful first anchor and decoy case, not because it is the cleanest stock, but because it is the cleanest role separation.

This matters because the layer is supposed to learn divergence, not celebrate leadership. If the first labels already confuse heat with valid continuation, the whole route goes crooked. A conservative registry with only a few hard rows is therefore better than a larger but softer one. Event trigger validity can now be learned without pretending that every event is board-supportive, and attention role learning can start without pretending that true capital selection is already solved.

## JOURNAL-0419 One Hard Role Seed Is Better Than Five Fake Certainties

Date: 2026-04-05

The next temptation after finding one useful role case was to promote all the other strong names into equal-status anchor or decoy labels. That would have been sloppy. The evidence is not symmetric. 航天发展 has explicit turning-point heat evidence and later weak-path confirmation, which is enough for a hard role seed. 再升科技, 神剑股份, 天银机电, and 西测测试 all matter, but they matter in different ways and with different evidence strengths. Some have event backing plus strong crowded rebound, some only have local concentration, and some look more like following high-beta beneficiaries than attention anchors.

This asymmetry is not a weakness. It is the point of the layer. If every strong symbol is promoted at the same confidence level, the model loses the distinction between attention, concentration, and later true selection. By keeping one hard role seed and several softer role candidates, the system stays honest and preserves room for later separation instead of collapsing everything into an overfit taxonomy too early.

## JOURNAL-0420 Separation Is Progress Even Without A Leader

Date: 2026-04-05

There is a common temptation in market labeling to treat every intermediate step as a failure if it does not immediately reveal the final leader. That is the wrong standard here. The useful progress in the latest pass is that the soft role candidates no longer sit in one mixed bucket. 再升科技 is now the best event-backed attention-carrier candidate. 神剑股份 and 天银机电 look more like concentration without anchor authority. 西测测试 looks more like an event-backed high-beta follow case. None of that is yet the same as true selection, and that distinction is exactly why the layer improved.

This matters because it preserves causal order. If the system jumps from mixed role candidates straight into capital_true_selection, it will confuse event backing, crowding, breakout path, and follow behavior. By forcing separation first, the training route keeps true selection blocked until there is enough carrier-grade evidence to compare. That is a better outcome than a premature winner label built on one attractive case.

## JOURNAL-0421 A Good Blocker Is Better Than A Premature Promotion

Date: 2026-04-05

The carrier-grade question now has a better answer than “not yet.” It has named missing evidence. There is only one event-backed carrier-grade soft case. There is only one hard anchor/decoy panel case. There is no dedicated followthrough surface yet, and no explicit event-to-board alignment score. Those are not vague hesitations. They are explicit absences. That changes the quality of the block. It is no longer a mood. It is a checklist.

This matters because it turns the next step into a disciplined search rather than a drift toward comfort. Instead of over-interpreting one attractive candidate, the route now says exactly what must exist before true selection can be promoted. That is a healthier training posture: when evidence is thin, the right advance is to formalize the gap, not to pretend it has already been crossed.

## JOURNAL-0422 A Negative Search Result Is Still Progress

Date: 2026-04-05

The search for a second carrier-grade case did not produce one. That is useful. It means the route can stop searching for comfort in the current named set and accept a harder truth: the present event-backed universe still has one primary carrier case and several non-carrier roles. 再升科技 remains the only current carrier-grade case. 西测测试 is still better read as a follow candidate. 神剑股份 and 天银机电 still look like concentration without carrier authority. 航天发展 still belongs on the counterpanel rather than in the candidate pool.

This matters because a negative search result protects the label stack from inflation. If the system promoted a second carrier out of impatience, it would weaken the meaning of the label exactly when the role layer is finally becoming disciplined. Keeping the negative result visible is better than manufacturing symmetry where the evidence does not support it.

## JOURNAL-0423 Counterpanels Should Be Harder To Earn Than Heat

Date: 2026-04-05

The counterpanel search produced another useful asymmetry. Hard anchor-decoy status is not just “a strong name that later failed to reopen the board.” It also requires hard heat-anchor evidence. That is why 航天发展 remains unique. 神剑股份 and 天银机电 may both support softer decoy-like readings, but neither currently owns a decisive retained heat-anchor source. 再升科技 and 西测测试 matter for other reasons, yet they do not belong in the hard counterpanel at all.

This matters because it keeps the role language clean. If every failed strong name becomes a hard decoy, the model loses the very distinction it is trying to learn. A counterpanel is supposed to be harder to earn than heat, not easier. The right outcome is therefore not disappointment that the panel is still thin, but relief that the system did not promote noise into structure.

## JOURNAL-0424 Followthrough Helps, But It Does Not Solve Selection

Date: 2026-04-05

The new followthrough layer is useful precisely because it refuses to do too much. It now distinguishes a durable symbol-level path from weaker or more temporary ones, and that is real progress. But the existence of symbol persistence still does not solve the higher problem. A name can carry followthrough in raw prices without reopening board participation, without resolving anchor-versus-decoy ambiguity, and without becoming a lawful true-selection case. The layer therefore adds signal while preserving the block.

This matters because one of the easiest mistakes in thematic work is to confuse persistence with permission. Once a symbol keeps going, it becomes psychologically tempting to upgrade everything about it at once: from attention carrier to leader, from leader to board restart proof, from restart proof to selection license. The new layer explicitly rejects that cascade. Followthrough is now visible, but it remains only one layer in the stack, not the final answer.

## JOURNAL-0425 Alignment Is Useful Only If It Stays Smaller Than Promotion

Date: 2026-04-05

The new board-event alignment layer is useful precisely because it does not try to do too much. It now distinguishes an event that lands in a genuinely supportive board state from an event that lands at a turning point, in a lockout regime, or in a raw-only zone where lawful board alignment cannot even be assigned. That is a real improvement over vague statements that some events simply 鈥渇eel stronger鈥 than others. The system can now say why an event belongs to a positive continuation context, a risk-turn context, a lockout-misaligned context, or an alignment-absent context.

This matters because event logic becomes dangerous when it quietly outruns the board state that is supposed to host it. If the model takes event excitement and directly upgrades it into selection authority, it will overfit narrative before it has secured lawful participation context. The new layer prevents that mistake. It makes alignment explicit, but it keeps alignment smaller than promotion.

## JOURNAL-0426 Partial Closure Is Not The Same As Readiness

Date: 2026-04-05

The readiness pass is useful because it converts the current stack into a more honest shape. Two named gaps are now explicit layers: symbol followthrough exists, and board-event alignment exists. That is progress. But the promotion block still survives for a structural reason. There is still only one primary carrier-grade case, and there is still only one hard anchor-decoy counterpanel case. In other words, the support stack is getting thicker while the decisive comparison stack remains thin.

This matters because it shows where false confidence tends to enter. Once auxiliary layers begin to look sophisticated, there is a strong temptation to call the whole module mature. That temptation is wrong here. Better supervision on persistence and alignment does not magically solve the fact that carrier evidence and counterpanel evidence are still single-case bottlenecks. The correct read is therefore not 鈥渢rue selection is almost ready,鈥 but 鈥渢rue selection is better supported and still correctly blocked.鈥?

## JOURNAL-0427 Local Exhaustion Is Also A Useful Result

Date: 2026-04-05

One of the easiest ways to waste time in a small labeled universe is to keep retuning the same five names after the route has already revealed what they can and cannot provide. The new evidence-source pass matters because it finally names that stopline. The current named set is good enough to establish one primary carrier case, one hard anchor-decoy panel case, several soft role candidates, and a richer followthrough and alignment stack. It is not good enough to manufacture a second carrier or a thicker hard counterpanel. That is not a tuning problem anymore. It is an evidence-source problem.

This matters because it changes the next honest move. If the route keeps grinding the same local set, it will only produce softer narratives around the same structural bottlenecks. The better move is to expand the comparison surface itself: more symbols for carrier search and thicker attention-heat evidence for counterpanel search. That is a cleaner frontier than pretending local refinement can solve a missing comparison stack.

## JOURNAL-0428 Expansion Is Useful Only If It Stays Narrow At First

Date: 2026-04-05

Once the route admits that the current named set is locally exhausted, the next temptation is to swing too far in the other direction and scan the whole concept universe without discipline. That would simply replace one kind of noise with another. The first expanded pass works because it stays narrow: formal/core symbols only. That is enough to prove a real point. There is one outside-named candidate, 000738, that deserves explicit second-carrier search. There is one watch, 600118, that has some strength but not enough local leadership. And there is one formal noncandidate, 002085, that should not be promoted just because it sits in the formal set.

This matters because it preserves the meaning of expansion. The goal is not to make the stack look larger. The goal is to find the next legitimate comparison case without inflating status labels. A narrow expansion that finds one real target is better than a broad scan that manufactures five weak ones.

## JOURNAL-0429 A Watch Is Stronger Than A Guess And Smaller Than A Promotion

Date: 2026-04-05

The new outside-named pass does not suddenly solve second-carrier promotion, and that is exactly why it is useful. 000738 now deserves a real place in the supervision stack because it shows repeated board-local rebound leadership and meaningful post-lockout breakout strength. That is enough to stop ignoring it. But it still lacks the same kind of retained event backing that made 603601 the current primary carrier-grade case, and it still does not have the downstream followthrough and role extensions that would make a direct promotion honest.

This matters because there is a middle category that good supervision needs to preserve: the lawful watch. If the system only knows how to say yes or no, it will either ignore promising new evidence or promote it too early. The right move here is neither. 000738 is now a real watch. That is stronger than a guess and smaller than a promotion, which is exactly the size the label should be.

## JOURNAL-0430 Leadership Without Backing Is Still Incomplete

Date: 2026-04-05

The 000738 extension pass clarifies something important about second-carrier search. A symbol can clearly earn its place as a watch through repeated local leadership and meaningful post-lockout strength, and still remain incomplete in exactly the way that matters most for promotion. That is what happened here. 000738 now has explicit local rebound leadership and a nontrivial followthrough path, but it still has no retained event-attention seed of its own. Its continuation also gives back too much to deserve a persistent label. So the stack improves without crossing the line.

This matters because it prevents a very common mistake: treating repeated leadership days as if they automatically imply causal backing. They do not. In a weak board, local leadership can still emerge without the same kind of event-legitimized role that the primary carrier case owns. The correct next step is therefore not to argue harder that 000738 looks strong enough, but to ask the narrower question the new audit exposes: where is its retained event backing, if it exists at all?

## JOURNAL-0431 Cross-Theme Strength Is Still Contamination If The Board-Specific Causal Line Is Missing

Date: 2026-04-05

The new 000738 pass matters because it shows how easy it is to misread a genuinely strong symbol when the label stack is still board-specific. 000738 did not need to become weak for the audit to downshift it. It stayed strong enough to deserve attention, but the surrounding evidence shifted the interpretation. Its broader metadata reads like a defense-aerospace multi-day reinforcement name, and the natural gas-turbine comparators the user raised are not even present in the current local commercial-aerospace surface. That is enough to break the clean same-theme story without denying the price strength itself.

## JOURNAL-0432 Local Heat Clarity Is Useful Even Before Real Heat Evidence Exists

Date: 2026-04-05

The new local heat-proxy layer is useful because it improves language without pretending to solve evidence scarcity. That matters. A stack that only knows “anchor” and “not anchor” will flatten too many different symbol behaviors into one bucket. Here the local evidence can already say something finer: 航天发展 is still the only explicit heat anchor seed because that status comes from named turning-point heat, not just from price strength; 再升科技 is the strongest soft heat-carrier proxy because it combines retained event backing, the strongest turnover concentration, and persistent symbol-level followthrough; 神剑股份、天银机电、西测测试 each still carry visible heat, but in different non-anchor ways.

This matters because role clarity is not the same thing as promotion authority. The stack should absolutely become more articulate about local heat roles if the evidence supports it. But the absence of a second hard counterpanel has not changed. So the correct lesson is not “we finally have true selection.” The correct lesson is smaller and more honest: local heat proxies can improve the map of who is drawing attention, carrying attention, or merely traveling with attention, while still leaving hard promotion closed.

This matters because the right lesson is not simply “ignore cross-theme names.” The real lesson is that future labeling needs an extra hygiene layer. If a symbol can plausibly be lifted by another business line or another concept stack, the system needs a concept-purity and basic-business reference check before it promotes that symbol into board-specific carrier evidence. Otherwise the stack will confuse cross-theme strength for board-native strength and teach the wrong causal story.

## JOURNAL-0433 The Missing Piece Is Not Another Strong Symbol But Another Hard Source

Date: 2026-04-05

The new source-hardness pass clarifies why the current stack still cannot thicken the hard counterpanel even after several rounds of local role work. The obstacle is not that the candidates fail to look strong enough. The obstacle is that almost none of them are backed by the kind of source that made ���췢չ lawful as a hard anchor-decoy case. �����Ƽ� and ������� both have retained event support, but those sources are continuation-oriented supply-chain validation, not symbol-named heat-axis evidence. �������� has a theme-heat source, but it was explicitly discarded as non-decisive. �񽣹ɷ� does not even have a retained event source.

This matters because it changes what ��more evidence�� should mean. The stack does not need more price narratives for the same names. It needs a second anchor-grade source, meaning a real decisive, retained, symbol-relevant heat event of the same order as the ���췢չ turning-point case. Until that exists, the right move is to keep role language rich but promotion closed.

## JOURNAL-0434 The Event Inventory Itself Can Be The Bottleneck

Date: 2026-04-05

The new symbol-named heat-source search matters because it removes one more place to hide. It is easy to keep saying that the stack needs more evidence in the abstract. It is harder and more useful to ask whether the current local event inventory even contains the kind of evidence being requested. Here the answer is no. There is only one retained symbol-named hard heat source in the local commercial-aerospace registry, and it is still the ���췢չ turning-point case. The other theme-heat rows are either explicitly discarded or only exist as unresolved forward anchors.

This matters because it means the current stopline is not just about candidate promotion discipline. It is also about event inventory limits. The stack cannot manufacture a second hard counterpanel if the underlying retained event inventory does not provide a second hard source. That is a cleaner stopping rule than endlessly reconsidering the same symbols.

## JOURNAL-0435 A Local Route Can Be Complete Even If Promotion Never Opens

Date: 2026-04-05

The new completion and handoff passes matter because they separate two ideas that are easy to confuse. A branch can become locally complete at the supervision layer without ever opening promotion. That is exactly what happened here. The board-local event-attention-capital route now owns a real negative-environment registry, an event-attention registry, role separation, heat-proxy clarification, followthrough, board-event alignment, and a fully explicit explanation for why capital_true_selection remains blocked. Nothing about that says the branch failed. It says the branch reached an honest boundary.

This matters because good research discipline is not just about finding new things. It is also about knowing when a local inventory has taught everything it can teach. Once that point arrives, continuing to retune the same five names and the same local event rows is no longer depth. It is drift. The right move is to freeze the local stack, preserve its language, and wait for a new evidence source rather than pretending the current one still contains hidden promotion authority.

## JOURNAL-0436 A Frozen Local Route Can Still Be A Strong Input To A Larger Frontier

Date: 2026-04-05

The new broader-attention opening matters because it preserves sequence discipline. Once the board-local route is frozen, the next honest move is not to pretend it can still generate new hard evidence from the same inventory. The next honest move is to treat that local route as a read-only input and open a larger evidence frontier around it. That is what the new protocol does. It does not claim that broader attention evidence already exists in hand. It only makes room for it without corrupting the local route that has already reached its stopline.

This matters because many research stacks drift precisely at this transition. They either keep squeezing the exhausted local inventory, or they silently smuggle a broader universe into the old labels and pretend continuity. The cleaner move is explicit frontier management: freeze the local branch, name the broader-evidence frontier, keep execution blocked, and only let promotion reopen when genuinely new evidence arrives.

## JOURNAL-0437 Inventory Before Expansion Prevents Another Fake Frontier

The broader_attention_evidence frontier is no longer empty protocol. It now has three concrete local source surfaces: market snapshots, theme snapshots, and retained decisive-event registry. This matters because the next step can be source-driven instead of story-driven. The right discipline is still to keep capital_true_selection blocked while the frontier is only being populated. Inventory is not promotion.

## JOURNAL-0438 A New Frontier Can Open Before Most Sources Are Actually Same-Plane Ready

The broader_attention_evidence frontier did gain real inventory, but applicability is asymmetric. The 2024 snapshot surfaces are useful priors, not live evidence for the 2026 commercial-aerospace route. The decisive-event registry is currently the only same-plane source that can be promoted without cheating. That is not a failure of the frontier; it is the first honest map of what the frontier can really use.

## JOURNAL-0439 A Good Registry Is More Useful After It Is Split By Expansion Role

The decisive-event registry became much more usable once it was split into utility classes. A single retained registry can support several different next steps, but those next steps should not be mixed. The first same-plane branch is broader symbol-pool expansion, not heat-axis thickening and not carrier-follow promotion. The utility split prevents another fake leap toward true selection.

## JOURNAL-0440 A Live Branch Can Still Be Blocked One Step Later By Materialization

The first same-plane branch did open, and the registry really does contain broader symbol-pool cues. But those cues remain trapped in source notes and extracted counts because the local security-master coverage is too thin to normalize them. This is an honest blocker, not a modeling failure. It also means the next useful move may be parallel rather than sequential: heat-axis and counterpanel expansion can proceed while symbol-pool materialization waits for better name-to-symbol coverage.

## JOURNAL-0441 A Parallel Branch Can Be Real Without Being Strong Enough To Change The Stopline

The heat-axis branch is now explicit and lawful, but it does not yet move the counterpanel stopline. One realized turning-point heat source plus one forward sentiment anchor is enough to formalize the branch and to reinforce the existing singleton hard case. It is not enough to claim that the counterpanel is materially thicker. This is useful progress, just not promotive progress.

## JOURNAL-0442 A Branch Can Add Signal By Reinforcing Known Cases Before It Ever Produces A New Winner

The carrier-follow branch turned out to be useful even without discovering a new promotable symbol. It strengthened the reading on �����Ƽ� and ������� and cleanly separated an outside-named supply-chain watch from the current local surface. That kind of reinforcement matters because it clarifies what the branch is good for and what it still cannot do. It still cannot open true selection.

## JOURNAL-0443 A Frontier Can Be Alive Long Before It Becomes Promotive

The broader-attention frontier is no longer hypothetical. It has inventory, applicability rules, and three formalized same-plane branches. But none of those branches is promotive yet. This is not stagnation. It is a better map. The right training discipline here is to keep the frontier alive without confusing reinforcement, structural priors, and blocked materialization with real promotive evidence.
JOURNAL-0444 | information-center-blueprint | Formalized the next foundational program as an A-share unified information center rather than another strategy branch. The current repo has meaningful identity, market, event, supervision, and governance fragments, but they are not yet unified into a point-in-time legal object system.
JOURNAL-0445 | storage-lifecycle | Added explicit hot/warm/cold/frozen/disposable storage policy. Key principle: keep structured truth layers and journals; compact or evict rebuildable intermediates and low-tier raw text before the workspace turns into a permanent cache swamp.
JOURNAL-0446 | info-center-identity | Identity moved from scaffold to usable foundation. The repo now has a canonical 82-symbol security master plus alias surface, explicit source-priority rules, and a first reusable name-to-symbol basis for later taxonomy and event layers.
JOURNAL-0447 | info-center-taxonomy | Taxonomy is now operationally complete enough to support downstream work. Concept and sector surfaces are partial but real; business-reference and concept-purity are honest backlog layers, not fake completed layers.
JOURNAL-0448 | info-center-events | Events moved from scattered board registries into a unified bootstrap object chain. The chain is still registry-derived, but it is now a reusable intake layer rather than a collection of isolated research CSVs.
JOURNAL-0449 | info-center-quality | Quality is no longer implicit. The repo now has explicit bootstrap source tiers, event-quality bands, repost-control rows, and contradiction backlog queues that downstream layers can consume instead of reinventing confidence heuristics row by row.
JOURNAL-0450 | info-center-attention | Attention moved into the center as a bootstrap registry rather than a collection of board-specific anecdotes. That is enough to support later serving and labels, but not enough to claim broad heat-source diversity.
JOURNAL-0451 | info-center-labels-features | Labels and features now form a true semantic middle layer. This matters because later PTI, replay, and serving steps can consume standard semantic objects instead of strategy-local ad hoc fields.
JOURNAL-0452 | info-center-pti | PTI proved why time legality needs its own workstream. Some events had no lawful visible timestamp, and the correct move was to keep them in visibility backlog rather than assign fake times. That establishes the culture the center needs later.
JOURNAL-0453 | info-center-market | Market V1 had to be storage-aware to stay honest. The center now knows what daily and intraday raw coverage exists without pretending it has already expanded every minute file into normalized symbol tables.
JOURNAL-0454 | info-center-replay | Replay is now real enough to be useful, but only as a read-only shadow surface. Binding PTI to market coverage immediately exposed where context is missing, which is exactly the point of replay at this stage.
JOURNAL-0455 | info-center-serving | Serving is no longer hypothetical. Research and shadow consumers now have explicit registries and routes, while live-like stays deferred. This keeps consumption disciplined and prevents accidental promotion.
JOURNAL-0456 | info-center-governance | Governance matters because once the center spans 13 workstreams, implied control is no longer enough. Schema, dataset, heartbeat, and gate registries now make the center inspectable rather than merely buildable.
JOURNAL-0457 | info-center-automation | Automation was intentionally materialized as job contracts instead of prematurely active jobs. That is the right order: contract first, activation later, once real sources and retention rules are ready to run safely.
JOURNAL-0458 | info-center-completion | The information center is now complete at the foundation level. The next phase should not be more blind construction. It should be explicit backlog closure, source activation, business-reference filling, concept-purity work, board-state derivation, and later live-like opening.
JOURNAL-0459 | info-center-business-purity | Business reference and concept purity no longer need to start from zero. The center now has a first structural answer to what a company mainly is and how mixed its concept exposure is, even before external fundamentals are layered in.
JOURNAL-0460 | info-center-contradiction-resolution | Contradiction handling improved once duplication was separated from true semantic conflict. Most current cases are merge-like duplicates rather than meaning conflicts, which means future review effort can focus on genuinely divergent evidence instead of bootstrap noise.
