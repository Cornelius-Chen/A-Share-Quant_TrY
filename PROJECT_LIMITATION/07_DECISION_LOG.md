# A-Share Quant Decision Log

## 目的

本文件记录关键设计决策，保证未来可以追溯“为什么这样做”�?
---

## 记录规则

需要记录的决策包括但不限于�?
1. 协议升级
2. 研究方向切换
3. 数据口径调整
4. 指标定义变更
5. 回测引擎核心行为变更
6. 策略晋级或淘�?
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
- Expected Benefits: Make “same data, same config, same runner�?comparison explicit and reproducible, which is central to the project philosophy.
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

### DEC-0013

- Date: 2026-03-28
- Title: Add a matrix comparison workflow across strategy families and segmentation methods
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T110729Z_d3ba5e4d
- Context: The repo could separately compare strategy families and segmentation methods, but still lacked a single workflow that answered the combined research question: which strategy family works best under which segmentation approach.
- Decision: Add a matrix comparison runner, CLI/config, and sample data path that compares Strategy A/B/C across `index_trend`, `sector_trend`, and `resonance` under one shared experiment contract.
- Alternatives Considered: Leave combined comparison to external scripting or manual analysis.
- Expected Benefits: Move the repo from isolated comparisons toward an actual research matrix, which is closer to how profitable variants will be evaluated in practice.
- Risks: The comparison grid increases report size and may eventually require more sophisticated presentation than raw JSON.
- Follow-up Actions: If we continue framework work, the next likely upgrade is richer rendered reports or more realistic datasets; otherwise the repo is ready to start focusing more on real research inputs and iterative validation.

### DEC-0014

- Date: 2026-03-28
- Title: Formalize the canonical data pack and repo storage layout for real research inputs
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: The lab-stage framework is now broad enough that the next bottleneck is no longer comparison infrastructure but data readiness. Without a concrete data storage and ingestion baseline, real-data work would drift into ad hoc local files and inconsistent schemas.
- Decision: Add a dedicated storage and ingestion plan that defines the first canonical dataset pack, target `data/` layout, required fields, promotion order, and minimum validation checks. Reserve the corresponding repo directories and ignore their contents by default.
- Alternatives Considered: Keep the guidance informal in chat, or fold all storage details into the higher-level data contract without a separate execution-oriented document.
- Expected Benefits: Turn the move from demo data to real data into an explicit, reviewable engineering step rather than an improvised one.
- Risks: The plan may still need adjustment once the first real provider is chosen and loader implementations are upgraded beyond CSV-only demos.
- Follow-up Actions: Implement canonical-table loaders/adapters and start assembling the six-table minimum dataset pack for the first formal baseline experiment.

### DEC-0015

- Date: 2026-03-28
- Title: Define LLM as a research-assistant layer rather than a near-term signal layer
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: An external A-share agent project suggested that LLM-based debate, summarization, and review workflows may become useful later. The key risk for this repo is that language-model assistance could enter too early and bypass the protocol-first research architecture.
- Decision: Add a dedicated LLM assistant policy that explicitly limits near-term usage to research support, documentation, summarization, review, and unstructured-information assistance, while forbidding direct use as a mainline-definition or trade-decision authority.
- Alternatives Considered: Treat LLM guidance as covered implicitly by the future ML policy, or defer all LLM policy until actual integration work begins.
- Expected Benefits: Preserve flexibility to add LLM assistance later while preventing accidental methodological drift in the current lab stage.
- Risks: The policy is intentionally conservative and may slow down some experimental AI features until validation and logging infrastructure grows further.
- Follow-up Actions: If LLM features are later implemented, require prompt/output logging and keep them outside the core signal path until they earn a protocol-level upgrade.

### DEC-0016

- Date: 2026-03-28
- Title: Start the free-data path with an AKShare bootstrap layer instead of binding the repo to one permanent vendor
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: The user chose to try a free data path first. The project needs real data soon, but jumping straight from sample CSVs to a fully committed vendor-specific canonical layer would be premature and brittle.
- Decision: Add an AKShare-based bootstrap script and adapter that exports a minimum free dataset pack into local canonical directories for `daily_bars`, `index_daily_bars`, `trading_calendar`, and a temporary `security_master_lite`.
- Alternatives Considered: Keep discussing providers without implementation, or bind the project immediately to a paid source before proving the real-data pipeline on a lower-cost path.
- Expected Benefits: Make the move from sample data to real data concrete now, while keeping vendor lock-in and up-front cost low.
- Risks: Free-source semantics remain weaker than a mature paid data stack, and the bootstrap layer does not yet solve full adjustment-factor or daily sector mapping quality.
- Follow-up Actions: Verify field quality from the first fetch, then add canonical loaders/adapters and decide how to fill the remaining gap tables.

### DEC-0017

- Date: 2026-03-28
- Title: Connect the bootstrap tables to the main code path before attempting full real-data strategy experiments
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T134553Z_caa626ed
- Context: The free bootstrap already produced local canonical tables for prices and calendar data, but the repository still lacked loader coverage and an actual runnable path that used those local tables instead of sample-only fixtures.
- Decision: Add canonical loaders for trading calendar and security master, add a bootstrap-backed backtest config with simple signals, and explicitly treat full real-data strategy experiments as blocked until real derived tables exist for `sector_snapshots`, `stock_snapshots`, and `mainline_windows`.
- Alternatives Considered: Skip the adapter step and jump straight to derived-table generation, or continue using sample-only fixtures while postponing integration of the newly bootstrapped data.
- Expected Benefits: Move one real-data workflow fully onto local canonical files now, while keeping the next gap clearly identified instead of hidden.
- Risks: The project now supports a mixed state where basic backtests can use real local bars but strategy experiments still depend on sample-derived inputs.
- Follow-up Actions: Implement generation or ingestion of real derived tables so the strategy experiment layer can also leave sample fixtures behind.

### DEC-0018

- Date: 2026-03-28
- Title: Add a bootstrap-derived layer so strategy experiments can start using local real bars
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T135433Z_2fa99fee, 20260328T135433Z_76dcbcba
- Context: After the free bootstrap and local-real-data backtest path were working, the next blocker was that strategy experiments still depended on sample fixtures for `sector_snapshots`, `stock_snapshots`, and `mainline_windows`.
- Decision: Add a clearly temporary bootstrap-derived generator that uses local daily bars plus explicit sector assignments to create heuristic `sector_mapping_daily`, `sector_snapshots`, `stock_snapshots`, and `mainline_windows`, along with dedicated strategy-experiment and strategy-suite configs that consume those generated files.
- Alternatives Considered: Wait for a full protocol-grade derived-data pipeline before allowing any real-data strategy experiment, or keep the strategy layer on sample fixtures longer.
- Expected Benefits: Let the strategy experiment path begin moving onto local real bars now, while keeping the provisional nature of the derived tables explicit.
- Risks: The generated derived tables are heuristic and should not be mistaken for final research-grade sector or hierarchy truth. The first bootstrap suite also currently produces no A/B/C differentiation, which indicates the provisional derived layer is still too coarse for meaningful family comparison.
- Follow-up Actions: Replace the bootstrap heuristics step by step with stronger mapping sources, formalized snapshot generation rules, and more defensible mainline-window definitions.

### DEC-0019

- Date: 2026-03-28
- Title: Replace the hand-written bootstrap sector map with a CNInfo industry-history mapping path
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T140237Z_69ecbb95, 20260328T140238Z_0143987f
- Context: The first bootstrap-derived bridge worked, but it still depended on a hard-coded symbol-to-sector map, which was too weak to support meaningful progress toward a credible research data layer.
- Decision: Implement a `sector_mapper` module and bootstrap script that use AKShare's CNInfo industry-change history per symbol to generate a daily `sector_mapping_daily` table, then make the bootstrap-derived generator prefer that mapping as input.
- Alternatives Considered: Keep the manual mapping longer, or attempt a slower board-constituent crawl across all Eastmoney industry boards.
- Expected Benefits: Move the free-data path toward a more realistic and traceable sector mapping source without introducing a paid dependency yet.
- Risks: CNInfo history can still produce `UNKNOWN` periods when no classification record is returned in the requested date range, and the mapping still reflects one chosen classification field rather than a multi-taxonomy truth.
- Follow-up Actions: Improve fallback behavior for early `UNKNOWN` periods and consider supporting multiple classification levels or concept mappings once the basic daily mapping path stabilizes.

### DEC-0020

- Date: 2026-03-28
- Title: Rework bootstrap-derived stock snapshots around sector-relative ranking so Strategy C can differ from Strategy B for the right reason
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T141400Z_78c73530, 20260328T141908Z_c223ab10
- Context: After the CNInfo sector mapping upgrade and a clean serial rerun, Strategy A/B/C no longer fully overlapped, but Strategy B and Strategy C still remained too similar. Inspection showed the bootstrap-derived stock snapshots produced only `9` `late_mover` assignments out of `1936`, which meant the provisional hierarchy logic was structurally suppressing the quality late-mover layer.
- Decision: Rebuild the bootstrap-derived `stock_snapshots` heuristics around per-sector relative ranking, blending absolute return features with sector-relative trailing-return rank, current-return rank, and turnover rank. Keep the outputs explicitly heuristic, but make `late_mover_quality` reward strong sectors plus stable, liquid, non-leader names instead of collapsing almost everything outside `leader/core` into `junk`.
- Alternatives Considered: Leave the formulas unchanged and only expand the free-data symbol universe, or lower the hierarchy thresholds until more `late_mover` assignments appear without changing the underlying signal construction.
- Expected Benefits: Make the provisional free-data research path more structurally faithful to the project protocol by allowing Strategy C to gain exposure through actual `late_mover` candidates rather than by threshold tricks.
- Risks: The revised heuristics are still bootstrap-only formulas and may overfit to small free-data universes if they are mistaken for protocol-grade hierarchy definitions.
- Follow-up Actions: Keep growing the symbol universe, inspect cross-sector layer balance, and eventually replace these heuristics with a proper research-grade snapshot pipeline once higher-quality canonical data becomes available.

### DEC-0021

- Date: 2026-03-28
- Title: Add a formal bootstrap data-pack audit and upgrade security-master bootstrap before chasing more strategy detail
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: Once the free-data path could already drive backtests and strategy suites, the next risk became false confidence about data readiness. The repo needed a machine-readable answer to which canonical tables were actually ready, which were only bootstrap-grade, and which were still missing outright.
- Decision: Add a dedicated data-pack audit module, script, config, and tests. At the same time, upgrade the free `security_master` bootstrap so it fetches `list_date` per configured symbol through `stock_individual_info_em`, and reuse that information to stop writing all-zero `listed_days` into `daily_bars`.
- Alternatives Considered: Keep tracking readiness manually in chat or markdown, or postpone data-quality visibility until a paid provider is chosen.
- Expected Benefits: Turn data-preparation progress into an explicit engineering artifact, tighten the bootstrap dataset where free improvements are low-risk, and identify the next real blocker as `adjustment_factors` instead of vaguely saying "data is not complete yet."
- Risks: The free-data audit can still only validate what exists locally, and the new `listed_days` field remains a bootstrap approximation based on calendar-day difference rather than a fully canonical trading-session count.
- Follow-up Actions: Preserve the audit as a recurring gate, add a proper `adjustment_factors` source or adapter next, and keep using the audit report to decide whether data work or strategy work is the correct next bottleneck.

### DEC-0022

- Date: 2026-03-28
- Title: Use AKShare qfq-factor to bootstrap a real adjustment-factors table and align daily-bars adjust_factor with it
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: After the data-pack audit was added, the most important remaining canonical gap became explicit: `adjustment_factors` was missing entirely, and `daily_bars.adjust_factor` still contained placeholder `1.0` values. This blocked the bootstrap pack from being treated as even provisionally complete.
- Decision: Add an `adjustment_factors` bootstrap export based on AKShare's `stock_zh_a_daily(..., adjust=\"qfq-factor\")`, expand the factor events into a per-trade-date table, and reuse the same factors when writing bootstrap `daily_bars.adjust_factor` so the free-data pack stays internally consistent on a qfq basis.
- Alternatives Considered: Leave the factor table missing until a paid provider is chosen, or write a fake all-ones adjustment-factor table just to satisfy the schema.
- Expected Benefits: Close the highest-value canonical data gap now, improve price-series trustworthiness, and let the data-pack audit distinguish between genuinely sourced factors and placeholders.
- Risks: The factor path is still tied to the free provider's qfq semantics, and the bootstrap pack remains provisional until sector mapping and broader data depth improve.
- Follow-up Actions: Keep validating the factor semantics against raw/qfq prices, and later decide whether the canonical long-term factor standard should remain qfq-based or move to a different provider/formulation.

### DEC-0023

- Date: 2026-03-28
- Title: Add a concept-mapping layer and let bootstrap-derived research prefer primary concept mappings when available
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: The project had reached a point where the only remaining canonical weakness was no longer missing tables but weak semantic mapping. Industry mapping alone is too blunt for A-share mainline research because market attention often trades concepts, themes, and relation chains rather than formal industry classifications.
- Decision: Add a dedicated `concept_mapping_daily` bootstrap path based on AKShare Eastmoney concept boards, add loaders and audit coverage for that table, and let the bootstrap-derived mapping layer prefer a symbol's primary concept mapping over its industry mapping when concept coverage exists.
- Alternatives Considered: Keep all mapping logic industry-only until a paid data source arrives, or hardcode ad hoc theme labels directly into derived snapshot generation.
- Expected Benefits: Create the correct architecture for theme-aware research now, so later concept coverage improvements can plug directly into the same derived and strategy flows instead of forcing a redesign.
- Risks: The current bootstrap stock universe is dominated by large-cap industry names, so the first concept-bootstrap runs may legitimately produce sparse or empty coverage. This is a data-universe limitation, not proof that the architecture is wrong.
- Follow-up Actions: Expand the bootstrap universe toward more theme-driven stocks, or add a curated concept-watchlist layer so the concept mapping path can be exercised on symbols where market theme semantics actually matter.

### DEC-0024

- Date: 2026-03-28
- Title: Add a separate theme-validation bootstrap universe instead of mutating the industry-heavy baseline universe in place
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T152016Z_99cb04e8
- Context: Once the concept-mapping architecture existed, the next blocker was empirical rather than structural: the original eight-stock bootstrap universe was too dominated by large-cap banking, property, insurance, and liquor names to meaningfully exercise a concept/theme layer.
- Decision: Add a parallel set of `theme_bootstrap_*` configs using a more theme-driven stock sample, keep the original bootstrap universe intact as the industry-heavy baseline, and use the theme universe specifically to validate concept mapping, concept-overridden derived tables, and strategy-family behavior under more topic-sensitive inputs.
- Alternatives Considered: Replace the original bootstrap universe directly, or keep concept mapping unvalidated until a larger paid dataset is available.
- Expected Benefits: Validate the concept layer immediately without destroying continuity in the existing baseline bootstrap runs.
- Risks: The theme-validation universe is still a small curated sample and should not be mistaken for a broad market baseline.
- Follow-up Actions: Promote lessons from the theme-validation pack back into the main baseline workflow only after concept coverage and run behavior are clearly understood.

### DEC-0025

- Date: 2026-03-28
- Title: Add an explicit baseline-vs-theme dataset comparison layer before deciding whether to merge the two universes
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260328T152618Z_855f3bd4
- Context: Once the theme-validation pack was working, the next decision was not whether the concept layer could run, but whether its behavior justified folding theme-driven symbols into the main baseline universe.
- Decision: Add a dataset-comparison runner and config that compare the same A/B/C strategy family across the original baseline bootstrap pack and the new theme-validation pack under one shared comparison report.
- Alternatives Considered: Merge the universes immediately, or compare the two packs manually by looking at separate suite runs.
- Expected Benefits: Make the industry-vs-theme tradeoff explicit before any universe merge, so the repo can distinguish "theme layer works" from "theme layer should now redefine the main baseline."
- Risks: The comparison still reflects two small curated packs rather than a broad formal sample, so it is useful for directional insight but not final strategy promotion.
- Follow-up Actions: Use the cross-dataset comparison to decide whether to keep the two-pack workflow longer or selectively merge specific theme-sensitive symbols into the main baseline pack.

### DEC-0026

- Date: 2026-03-28
- Title: Add a named rule-sweep layer so baseline and theme packs can screen rule candidates under one shared report
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T025326Z_54108c98
- Context: After the repo gained a clean baseline-vs-theme dataset comparison, the next bottleneck was no longer whether the two packs behaved differently, but how to compare candidate rule sets without duplicating entire config files or eyeballing separate reports.
- Decision: Add a `rule_sweep` runner, CLI, and config format that treat each rule hypothesis as a named nested-config override applied to each dataset pack's base suite config. Rank every `dataset + candidate + strategy` row together, and also produce a candidate leaderboard based on average rank across return, capture, and drawdown.
- Alternatives Considered: Manually maintain multiple near-duplicate suite configs per hypothesis, or compare rule changes one run at a time without a formal cross-pack leaderboard.
- Expected Benefits: Turn rule screening into a repeatable engineering artifact, keep the baseline/theme dual-track workflow intact, and make it obvious which candidates are stable across both packs versus which only win in narrow conditions.
- Risks: The current leaderboard still depends on small curated datasets, so "most stable candidate" should be interpreted as a lab-stage signal about robustness inside the current packs rather than a promotion-ready strategy verdict.
- Follow-up Actions: Use the rule-sweep layer to screen trend-filter, hierarchy, and holding candidates in batches, and only promote changes into the default configs after they remain competitive across both packs.

### DEC-0027

- Date: 2026-03-28
- Title: Externalize larger research watchlists into universe files before expanding the bootstrap packs further
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: After the first cross-pack rule sweep, the next bottleneck returned to sample coverage. But simply appending more symbols directly into every bootstrap YAML would have made the repo harder to review and much more error-prone as the watchlists continue to grow.
- Decision: Add symbol-file support to the free-data bootstrap config, create versioned universe files under `config/universes/`, and introduce larger `baseline_research_v1` and `theme_research_v1` watchlists through dedicated bootstrap configs rather than mutating the smaller lab packs in place.
- Alternatives Considered: Keep the symbol lists inline inside YAML configs, or jump directly to a much larger market-wide bootstrap before the config and review workflow were ready for it.
- Expected Benefits: Make sample-coverage expansion incremental, reviewable, and versioned, while preserving continuity in the smaller baseline/theme lab packs.
- Risks: Larger free-data bootstraps still depend on noisy upstream endpoints, so expanding the watchlists improves research coverage but does not remove the need for graceful degradation and targeted reruns.
- Follow-up Actions: Use the larger watchlists to grow concept coverage first on the theme side, then add the same style of research-pack configs for the derived, suite, and audit layers once the canonical bootstrap proves stable enough.

### DEC-0028

- Date: 2026-03-28
- Title: Promote the larger research watchlists into full data-pack pipelines before drawing new conclusions from them
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T030906Z_e45938a1, 20260329T031504Z_f8b47b78, 20260329T031505Z_7fdb1ea8
- Context: After the larger watchlists were bootstrapped, the repo still needed to answer whether they were merely larger raw-data packs or genuinely usable research packs with derived tables, suites, and audit gates.
- Decision: Add full `sector_mapping`, `derived_data`, `strategy_suite`, `data_audit`, and `dataset_comparison` configs for `baseline_research_v1` and `theme_research_v1`, then run those packs through the same experiment and audit flow used by the smaller lab packs.
- Alternatives Considered: Keep the larger watchlists as raw-data-only assets for later, or continue making decisions from the smaller baseline/theme packs while postponing the larger-pack integration work.
- Expected Benefits: Make the transition from small lab packs to broader research packs explicit and measurable, so future rule screening can stop depending mainly on tiny curated samples.
- Risks: The larger theme pack still depends on the current heuristic derived layer, which can suppress A/B/C separation even when concept coverage improves. A bigger pack alone does not guarantee a better hierarchy model.
- Follow-up Actions: Use the new research-pack comparison to identify whether the next bottleneck is still sample coverage or has shifted to derived/hierarchy quality, especially on the theme side.

### DEC-0029

- Date: 2026-03-28
- Title: Run the rule-sweep layer on the larger research packs instead of assuming the small-pack ranking generalizes
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T031533Z_b92f4ff0
- Context: The small-pack rule sweep identified `control_v1` as the most stable candidate, but once larger research packs became available there was no reason to assume that result would survive broader sample coverage.
- Decision: Add a dedicated `research_rule_sweep.yaml` and rerun the same named candidates across `baseline_research_v1` and `theme_research_v1`.
- Alternatives Considered: Treat the small-pack rule-sweep leaderboard as the default promotion signal, or wait until even larger datasets are available before retesting candidate rankings.
- Expected Benefits: Distinguish "stable on the tiny lab packs" from "still competitive on the first broader research packs" before default configs are touched.
- Risks: The research packs are broader than the original lab packs but still far from full-market scale, so the new leaderboard is stronger evidence, not final truth.
- Follow-up Actions: Keep both sweep configs for now and compare how candidate rankings move as sample coverage expands; if the ranking keeps changing, prioritize hierarchy/derived improvements before promoting any candidate as the new default.

### DEC-0030

- Date: 2026-03-28
- Title: Add a sequential research-pack refresh helper so dependent outputs are rebuilt in order
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T032116Z_29515aab
- Context: While expanding the larger research packs, a parallel refresh caused a stale `theme_research` derived file to survive into later suite runs. That produced a false impression that A/B/C had collapsed structurally on the larger theme pack, when the real issue was refresh ordering rather than the model itself.
- Decision: Add `scripts/refresh_research_pack.py` and explicitly treat `sector_mapping -> derived -> suite -> audit` as an ordered chain for named research packs.
- Alternatives Considered: Keep refreshing the packs with ad hoc shell command batches, or rely on human discipline not to run dependent steps in parallel.
- Expected Benefits: Remove one source of experimental self-contamination and make the larger research-pack runs more trustworthy.
- Risks: The helper does not solve upstream data-source noise; it only solves local ordering and stale-file risk.
- Follow-up Actions: Prefer the sequential helper for future research-pack rebuilds, and reinterpret earlier contradictory theme-pack conclusions in light of the stale-output issue.

### DEC-0031

- Date: 2026-03-28
- Title: Expand the larger-pack rule sweep into entry/holding-style candidates before touching core code logic
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T032409Z_f039e3dc
- Context: After the stale-output issue was fixed, the next question was no longer whether the larger packs were trustworthy, but which type of rule changes they actually prefer. The existing three-candidate sweep was too coarse to answer whether the next gain should come from faster entry, looser holding, stricter quality, or pullback/repair bias.
- Decision: Add `research_rule_sweep_v2.yaml` with six named candidates, including the original control/strict/expansion set plus `fast_entry_relaxed_hold`, `patient_hold_bias`, and `repair_breakout_focus`.
- Alternatives Considered: Start rewriting the strategy or hierarchy code directly, or continue iterating only the three original candidates and risk missing where the real sensitivity lies.
- Expected Benefits: Learn which family of rule changes matters on the larger packs before changing shared strategy code.
- Risks: The expanded sweep still changes multiple knobs per candidate, so it is a directional screen rather than a clean causal decomposition.
- Follow-up Actions: Use the v2 split to design narrower follow-up candidates, likely separating baseline-oriented expansion tweaks from theme-oriented quality/hold tweaks instead of forcing one default across both packs.

### DEC-0032

- Date: 2026-03-28
- Title: Split the next sweep into a baseline expansion branch and a theme quality branch
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T032659Z_e42d39bb, 20260329T032700Z_312321e7
- Context: The broader `research_rule_sweep_v2` showed a useful directional split, but it still mixed baseline-oriented and theme-oriented hypotheses into one leaderboard.
- Decision: Add `baseline_expansion_sweep.yaml` focused on expansion/entry breadth for `baseline_research_v1`, and `theme_quality_sweep.yaml` focused on quality/holding discipline for `theme_research_v1`.
- Alternatives Considered: Keep all candidates in one blended multi-pack sweep, or jump straight to code changes based on the mixed leaderboard.
- Expected Benefits: Turn the next protocol iteration into two cleaner local optimization problems instead of one noisy compromise.
- Risks: Single-pack sweeps are sharper for local direction-finding, but they give up some cross-pack robustness information and therefore should complement, not replace, the broader research-pack sweeps.
- Follow-up Actions: Use the baseline branch to refine expansion-vs-late-mover breadth, and use the theme branch to refine strict-quality vs selective-entry tradeoffs before changing defaults.

### DEC-0033

- Date: 2026-03-28
- Title: Materialize the current branch-local winners as executable suite configs without replacing the shared default
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T033222Z_3ca87220, 20260329T033222Z_137654fb
- Context: After the single-pack sweeps clarified the local winners, the repo still lacked an easy way to run those branch-specific interpretations directly without reusing sweep configs as de facto strategy configs.
- Decision: Add `baseline_research_strategy_suite_expansion.yaml` and `theme_research_strategy_suite_strict_quality.yaml` as explicit branch-local suite configs, and verify they reproduce the intended local winner behavior.
- Alternatives Considered: Keep the branch winners only in sweep reports, or prematurely overwrite the shared `baseline_research_strategy_suite.yaml` / `theme_research_strategy_suite.yaml` defaults.
- Expected Benefits: Preserve the shared default configs while making the local best-known branches directly runnable and auditable.
- Risks: Branch-local configs can be mistaken for promoted defaults if their purpose is not documented clearly.
- Follow-up Actions: Treat these as branch baselines for further local refinement, and only consider promotion into the shared default configs after they keep winning under broader cross-pack checks.

### DEC-0034

- Date: 2026-03-28
- Title: Refine each branch around its current local winner before creating any new promoted variant
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T033635Z_1e1f73ea, 20260329T033635Z_fe440fe2
- Context: After the branch-local baselines became executable, the next temptation was to immediately fork more suite configs from the best-looking single-row improvements. That would have blurred the line between a robust local winner and a single-axis tilt.
- Decision: Add `baseline_expansion_refinement_sweep.yaml` and `theme_strict_quality_refinement_sweep.yaml`, but keep them as refinement sweeps rather than promoting new suite configs unless a challenger clearly beats the branch control on overall stability.
- Alternatives Considered: Promote `expansion_regime_guard` and `strict_quality_capture_relief` immediately based on their best-row wins, or stop refining and accept the first branch baselines as final.
- Expected Benefits: Preserve research discipline by testing whether incremental local tweaks truly dominate the current branch winners before expanding the config surface further.
- Risks: Narrow branch-internal sweeps can converge too tightly around the current local optimum and miss a larger improvement that would only appear under a wider search later.
- Follow-up Actions: Keep `baseline_research_strategy_suite_expansion.yaml` and `theme_research_strategy_suite_strict_quality.yaml` as the active branch baselines for now, and use the new refinement sweep results to decide whether the next pass should widen the search again or target only one promising knob.

### DEC-0035

- Date: 2026-03-28
- Title: Separate branch-local winner validation from cross-pack promotion screening
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T033806Z_53e93bde
- Context: The branch-refinement pass showed that `expansion_branch_control` and `strict_quality_branch_control` still anchor their local branches, but that result alone does not answer which candidate deserves attention as a broader shared-default challenger.
- Decision: Add `branch_promotion_check.yaml` and explicitly compare `shared_default`, the baseline expansion branch, the theme strict-quality branch, and their most plausible nearby promotion variants under the same two-pack rule-sweep frame.
- Alternatives Considered: Treat the local branch winners as automatic promotion candidates, or keep relying only on the broader earlier sweeps without isolating branch-derived challengers explicitly.
- Expected Benefits: Preserve the difference between "best inside its own branch" and "best compromise candidate across both major research packs."
- Risks: A compromise candidate can look more stable than a local winner simply because it is less extreme, not because it is the best long-term alpha direction.
- Follow-up Actions: Treat `theme_capture_relief_branch` as a cross-pack compromise candidate for the next comparison round, but do not promote it yet without another targeted sweep against the shared default and the current branch baselines.

### DEC-0036

- Date: 2026-03-28
- Title: Materialize a shared-default challenger only after a dedicated compromise sweep beats both the shared default and the first compromise guess
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T033926Z_4693a3d3, 20260329T034007Z_a718a8d5, 20260329T034007Z_a9dbf982
- Context: The first promotion screen surfaced `theme_capture_relief_branch` as the broadest compromise candidate, but that was still one step removed from a real shared-default challenger because it had not been tested against nearby milder hybrids.
- Decision: Add `cross_pack_compromise_sweep.yaml` and only materialize a new shared-default challenger if a compromise candidate clearly beats both `shared_default` and `theme_capture_relief_branch`. After that sweep, materialize `balanced_compromise` as runnable suite configs for both `baseline_research_v1` and `theme_research_v1`.
- Alternatives Considered: Promote `theme_capture_relief_branch` directly as the new shared-default candidate, or stop at the sweep report without creating reusable suite configs.
- Expected Benefits: Keep the shared-default discussion tied to an explicitly screened compromise candidate rather than to a single surprise leaderboard result.
- Risks: A compromise-focused search can drift toward smoother all-around settings that are easier to rank well, while hiding whether the project is losing too much upside in the stronger branch-specific environments.
- Follow-up Actions: Use `baseline_research_strategy_suite_balanced_compromise.yaml` and `theme_research_strategy_suite_balanced_compromise.yaml` as the current shared-default challenger pair, then compare them directly against the shared default and branch-local baselines before any promotion.

### DEC-0037

- Date: 2026-03-28
- Title: Use a finalists-only promotion screen before discussing any shared-default replacement
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T034115Z_fbe67ff1
- Context: Once `balanced_compromise` emerged as the best shared-default challenger, the repo still lacked one final condensed report that put only the most relevant promotion candidates on the same table.
- Decision: Add `promotion_finalists_check.yaml` and restrict the comparison to `shared_default`, `baseline_expansion_branch`, `theme_strict_quality_branch`, and `balanced_compromise`.
- Alternatives Considered: Keep relying on the broader compromise sweep for promotion decisions, or compare every historical candidate again and reintroduce noise.
- Expected Benefits: Give the project one concise promotion-oriented report that separates the current default, the two branch-local winners, and the best shared-default challenger.
- Risks: A finalists-only screen is clearer, but it can hide whether an excluded candidate from an earlier sweep would have become competitive after subsequent data or hierarchy changes.
- Follow-up Actions: Treat `balanced_compromise` as the current promotion frontrunner for shared-default discussion, but require one more promotion-gate style comparison before any actual config replacement.

### DEC-0038

- Date: 2026-03-28
- Title: Turn the promotion discussion into a formal gate evaluation instead of another free-form leaderboard judgment
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T034115Z_fbe67ff1
- Context: After `balanced_compromise` won the finalists-only screen, the next risk was semantic drift: the repo could keep talking about a "promotion frontrunner" without ever stating what numeric evidence that challenger actually needed to replace the current shared default.
- Decision: Add `src/a_share_quant/strategy/promotion_gate.py`, `scripts/run_promotion_gate.py`, and `config/balanced_compromise_promotion_gate.yaml`, then evaluate `balanced_compromise` against `shared_default` on explicit thresholds for composite-rank improvement, mean-return improvement, drawdown improvement, capture regression tolerance, and row-level total-return wins.
- Alternatives Considered: Continue judging promotion readiness from comparison leaderboards alone, or postpone formal gate work until there are more data packs.
- Expected Benefits: Convert promotion from a narrative judgment into a repeatable gate that can be rerun for future shared-default challengers.
- Risks: A gate is only as good as its thresholds; if the tolerances are poorly chosen, the repo can become too eager or too conservative about promotion.
- Follow-up Actions: Use the new gate report as the first piece of structured evidence for `balanced_compromise`, then decide whether the project wants an additional validation gate before actually changing the shared default config.

### DEC-0039

- Date: 2026-03-28
- Title: Add a stricter second-stage validation gate and keep the shared default frozen unless the challenger survives pack-level capture scrutiny
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T034115Z_fbe67ff1
- Context: The first promotion gate proved that `balanced_compromise` is a serious challenger, but that still left an important question unanswered: is it strong enough to be called `validation-ready`, or does it improve overall stability by giving back too much opportunity capture in a key pack?
- Decision: Extend the promotion-gate evaluator with per-dataset checks, add `balanced_compromise_validation_gate.yaml`, and require a stricter second-stage check before any shared-default replacement discussion can move toward freeze.
- Alternatives Considered: Stop after the first gate pass and begin default-replacement planning immediately, or rely on qualitative judgment for the second-stage decision.
- Expected Benefits: Force the project to distinguish "good enough to discuss" from "good enough to freeze."
- Risks: If the pack-level capture threshold is too strict, the repo may become overly conservative and postpone useful default upgrades too long.
- Follow-up Actions: Keep `shared_default` as the official V1 default, keep `balanced_compromise` as the active challenger, and focus the next refinement on reducing baseline-pack capture regression if shared-default promotion remains the goal.

### DEC-0040

- Date: 2026-03-28
- Title: Treat the repo as freeze-preparation complete once regression replay and gate replay both succeed
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T035317Z_357001ee, 20260329T035317Z_c74026d3
- Context: After the second-stage validation gate failed for an explicit reason, the repo still needed one more thing before it could claim a meaningful V1 freeze state: a fresh replay showing that the current default, current challenger, and gate artifacts all still execute cleanly together.
- Decision: Run full `pytest`, replay the baseline and theme shared-default suites, replay both promotion gates, and record the resulting state in `22_V1_FREEZE_STATUS.md`.
- Alternatives Considered: Stop at the gate reports and assume the system is stable enough, or postpone the freeze-oriented replay until more strategy work accumulates.
- Expected Benefits: Turn V1 freeze from an informal feeling into an explicit repo state backed by regression evidence.
- Risks: Freeze-oriented replay reduces ambiguity, but it can still miss future regressions if not repeated after later changes.
- Follow-up Actions: Keep the repo in `freeze-but-do-not-promote-yet` mode until either the challenger improves its baseline-pack capture behavior or the policy decides that the current capture giveback is acceptable.

### DEC-0041

- Date: 2026-03-28
- Title: Test one narrow capture-recovery path around balanced_compromise before reopening broader default research
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T035625Z_f75beb65, 20260329T035657Z_9bf44b74
- Context: After the second-stage validation gate failed, the next question was whether there was an obvious low-cost fix near `balanced_compromise`, rather than a need to reopen broad candidate exploration.
- Decision: Add `balanced_compromise_capture_recovery_sweep.yaml` for a baseline-only local search, then promote the most plausible recovery idea into `balanced_capture_recovery_check.yaml` for a small cross-pack sanity check.
- Alternatives Considered: Immediately open a wider new candidate search, or freeze the project without checking whether a simple nearby repair existed.
- Expected Benefits: Learn whether the capture-regression problem has an easy local fix before spending another full cycle on shared-default exploration.
- Risks: A narrow recovery search can miss a better solution that requires coordinated changes across more than one knob.
- Follow-up Actions: Since the current recovery attempt did not beat `balanced_compromise` cross-pack, keep the repo frozen and only reopen this path if the project explicitly decides to spend another refinement cycle on shared-default promotion.

### DEC-0042

- Date: 2026-03-29
- Title: Close V1 as a research-system release while separating practical trading work into the next stage
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T035317Z_357001ee, 20260329T035317Z_c74026d3
- Context: After freeze replay and failed second-stage challenger validation, the repo had enough evidence to stop drifting on the question "is V1 done?" but it still needed a clean statement that V1 research completion is different from live-trading readiness.
- Decision: Add `23_PRACTICAL_TRADING_ROADMAP.md` to describe the path from research V1 to execution/shadow/small-live, and add `24_V1_RELEASE_SUMMARY.md` to declare the current release as a completed research-system foundation rather than a live-trading system.
- Alternatives Considered: Keep V1 open until a live-trading path exists, or declare V1 fully complete without explicitly separating research completion from trading readiness.
- Expected Benefits: Let the project legitimately freeze V1 without pretending that the trading stack already exists.
- Risks: Splitting the roadmap this way can make the repo feel less "complete" to someone expecting a tradable system immediately, even though it is more honest and operationally safer.
- Follow-up Actions: Treat research V1 as closed at the foundation level, then choose whether the next milestone is `V1.1 research refinement` or `V1.5 practical trading foundation`.

### DEC-0043

- Date: 2026-03-29
- Title: Add fixed time-slice validation before reopening any shared-default promotion discussion
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T041309Z_0352bb07
- Context: After freeze and gate work, the next missing piece was not another candidate search but a more explicit validation view across time slices. The repo needed a repeatable way to ask whether the current finalists behave differently across quarterly environments.
- Decision: Add `time_slice_validation.py`, `run_time_slice_validation.py`, and `time_slice_validation.yaml`, then validate the current finalists across quarterly 2024 slices on both `baseline_research_v1` and `theme_research_v1`.
- Alternatives Considered: Keep relying on aggregate multi-pack reports and gate summaries only, or wait until a full walk-forward retraining framework exists before adding any time-slice validation.
- Expected Benefits: Expose environment-specific strengths and weaknesses early, while keeping the validation framework lightweight enough for the current fixed-config stage.
- Risks: Fixed time slices are not yet a full walk-forward system, so the output is stronger than a single aggregate report but still not the final word on out-of-sample robustness.
- Follow-up Actions: Use the slice results to guide `V1.1 research refinement`, especially environment-boundary analysis for `balanced_compromise`, instead of reopening broad candidate exploration.

### DEC-0044

- Date: 2026-03-29
- Title: Summarize finalists by environment role so V1.1 can target boundary analysis instead of blind retuning
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T041309Z_0352bb07
- Context: The time-slice validation proved useful, but the repo still needed a cleaner interpretation layer. Without that, the next cycle could still drift back into "which candidate should we tweak?" instead of "which environment role does each candidate actually serve?"
- Decision: Add `environment_boundary.py`, `run_environment_boundary_analysis.py`, and `environment_boundary_analysis.yaml`, then derive a structured summary from the time-slice report.
- Alternatives Considered: Keep reading the slice report manually, or jump straight from slice validation into another refinement sweep.
- Expected Benefits: Turn validation output into a reusable research asset: one candidate can now be described as the broad stability contender, another as the capture specialist, and another as the drawdown specialist.
- Risks: Boundary summaries compress information, so they should be treated as navigation aids rather than substitutes for the underlying slice-level report.
- Follow-up Actions: Use the new boundary report to drive `V1.1` work toward environment-boundary analysis and theme-data quality, not toward another broad candidate leaderboard.

### DEC-0045

- Date: 2026-03-29
- Title: Quantify theme-pack concept-mapping quality before refining theme-side strategy logic further
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: After the environment-boundary work, the biggest remaining uncertainty shifted to the theme data itself. The project needed a concrete answer to whether theme weakness came from strategy logic or from the concept-mapping substrate.
- Decision: Add `theme_data_quality.py`, `run_theme_data_quality.py`, and `theme_data_quality.yaml`, then measure coverage, concept concentration, primary-concept stability, and multi-concept overlap on `theme_research_v1`.
- Alternatives Considered: Continue refining theme-side strategy candidates without a formal data-quality check, or assume the existing concept mapping is good enough because the pack already runs end to end.
- Expected Benefits: Turn vague concerns about "theme noise" into specific measurable defects that can guide the next data-quality iteration.
- Risks: A compact quality report simplifies a messy topic and may miss deeper semantic issues such as concept timing lag or event-driven relabeling.
- Follow-up Actions: Treat time-invariant primary concepts, high concentration, and low multi-concept overlap as the main theme-data problems to solve before trusting deeper theme-side strategy refinements.

### DEC-0046

- Date: 2026-03-29
- Title: Move theme concept mapping to a history-aware multi-label v2 before any more theme-side strategy tuning
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T044312Z_dbb98804
- Context: `theme_research_data_quality_v1.json` showed that the main theme-side weakness was not strategy thresholds but the concept layer itself: one-label mappings, time-invariant primary concepts, and excessive concentration in a single primary theme.
- Decision: Add a `theme_research_concept_mapping_v2` path that scans deeper into concept boards, keeps more than one concept per symbol when supported, and uses board-history-aware daily scoring to let the primary concept rotate over time instead of staying static.
- Alternatives Considered: Keep tuning theme-side strategy logic on top of the existing v1 concept map, or only widen board scanning without adding time-varying primary-concept logic.
- Expected Benefits: Reduce lookahead-like static labeling, improve multi-concept realism, and make the theme-side research pack a more credible substrate for future validation.
- Risks: The history-aware concept map is still a heuristic bootstrap layer, not a fully authoritative event-time ontology; it can improve realism while still missing some semantic edge cases.
- Follow-up Actions: Use the v2 concept map as the new theme-side refinement input, then decide whether the next theme-data step should target the remaining coverage gap (`002902`) or the still-high concept concentration ratio.

### DEC-0047

- Date: 2026-03-29
- Title: Prefer the cleaner theme-data substrate even when it removes apparent theme-side alpha
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T044445Z_862707c7
- Context: After introducing `theme_research_v2`, the project needed to decide whether to treat the weaker v2 performance as a regression to undo or as a more honest estimate of theme-side difficulty.
- Decision: Keep `theme_research_v2` as the preferred refinement substrate despite its weaker return/capture profile versus `theme_research_v1`, because the v2 concept layer is materially less static and more multi-label realistic.
- Alternatives Considered: Revert to the better-looking `theme_research_v1` pack immediately, or block all theme-data changes unless they improve both realism and backtest output in the same step.
- Expected Benefits: Keep the research process aligned with realism instead of rewarding static-label bias.
- Risks: This choice can make near-term theme-side metrics look worse, which may feel like "losing progress" unless the team is disciplined about valuing cleaner evidence over prettier backtests.
- Follow-up Actions: Treat `theme_research_v2` as the preferred pack for the next theme-data iteration, then work specifically on the remaining coverage and concentration problems instead of reverting to v1.

### DEC-0048

- Date: 2026-03-29
- Title: Expand to a representative market-research pack before attempting full-market coverage
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: none
- Context: After stabilizing the research V1 foundation and improving the theme concept layer, the next scaling question was whether to jump straight to all-A-share coverage. The repo still has unresolved concept-ontology issues, so immediate full-market expansion would scale noise faster than truth.
- Decision: Add `25_MARKET_RESEARCH_V0_PLAN.md`, define `config/universes/market_research_v0.txt`, and bootstrap a broader but still interpretable `market_research_v0` data pack as the next expansion layer.
- Alternatives Considered: Jump straight to full-market coverage now, or stay indefinitely on the much smaller baseline/theme packs without testing a broader mixed universe.
- Expected Benefits: Increase coverage realism while keeping the pack small enough to reason about by bucket and debug when the next issues appear.
- Risks: An intermediate pack still introduces more mixed-market noise than the small research packs, and it can become a maintenance burden if it grows without clear bucket discipline.
- Follow-up Actions: Use `market_research_v0` as the next wider validation substrate, then decide whether the next iteration should add concept mapping and derived tables for this pack or first refine the remaining theme-v2 data issues.

### DEC-0049

- Date: 2026-03-29
- Title: Treat market_research_v0 as a mixed-market validation pack with its own role rather than as a replacement for baseline or theme packs
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T050350Z_4ce8e316, 20260329T050409Z_2a036885
- Context: After building `market_research_v0`, the repo needed to understand whether this wider pack should replace one of the existing research packs or whether it played a different role.
- Decision: Keep `market_research_v0` as a third, mixed-market validation substrate. It should complement `baseline_research_v1` and `theme_research_v2`, not replace them.
- Alternatives Considered: Promote `market_research_v0` into the main baseline pack immediately, or treat it as redundant because the repo already has separate baseline/theme research lines.
- Expected Benefits: Preserve the interpretability of the smaller specialist packs while gaining a broader environment in which `B/C`-style diffusion and mixed-market behavior can be tested.
- Risks: A third pack increases research-management overhead and can create more cross-pack tension if used without clear role definitions.
- Follow-up Actions: Use `market_research_v0` in the next validation cycle to see whether shared/default candidates and branch specialists hold up on a broader mixed-market environment.

### DEC-0050

- Date: 2026-03-29
- Title: Promote validation from two packs to three packs before reopening any shared-default discussion
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T050713Z_259349ba, 20260329T050714Z_c0ed1f58
- Context: Once `market_research_v0` became runnable, keeping the validation stack on only the baseline/theme specialist packs would have underused the new broader environment.
- Decision: Add three-pack validation configs so quarterly time-slice validation, environment-boundary analysis, and finalists comparison all run on `baseline_research_v1 + theme_research_v2 + market_research_v0`.
- Alternatives Considered: Keep validation frozen on the older two-pack view until a much larger market pack exists, or replace the specialist packs with the mixed-market pack immediately.
- Expected Benefits: Force the current default/challenger conclusions to survive a broader mixed-market environment without losing the interpretability of the specialist packs.
- Risks: Three-pack validation adds another layer of evidence to interpret, and the mixed pack has lower concept coverage than the theme pack, so some theme-style conclusions may look weaker there by construction.
- Follow-up Actions: Use the three-pack validation outputs to decide whether the next cycle should focus on shared-default repair or on deeper environment-specific branch validation.

### DEC-0051

- Date: 2026-03-29
- Title: Keep the V1 freeze state unchanged after three-pack validation because the blocker remains baseline capture regression
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T050714Z_c0ed1f58
- Context: The repo needed to know whether adding `market_research_v0` would materially change the `shared_default` promotion verdict.
- Decision: Keep the freeze state unchanged. The challenger `balanced_compromise` remains the broadest stability candidate, but it still fails the stronger validation-ready gate because no single dataset may exceed the configured capture-regression tolerance, and the baseline pack still breaches that rule.
- Alternatives Considered: Relax the dataset-level capture-regression threshold now that a third pack exists, or treat the third-pack improvement in total return/drawdown as enough to override the baseline-pack failure.
- Expected Benefits: Preserve methodological consistency and avoid promoting the challenger just because the evidence base got larger while the original baseline-specific weakness remains unresolved.
- Risks: This keeps the repo in a "strong challenger, not yet promoted" state longer, which can feel conservative even though it is more honest.
- Follow-up Actions: If the project reopens shared-default work again, the target should remain narrow and explicit: baseline-pack capture recovery without giving back the broader stability advantage.

### DEC-0052

- Date: 2026-03-29
- Title: Diagnose the baseline capture blocker by target window before changing any more broad strategy thresholds
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: baseline_window_replay_diagnostic_v1
- Context: After three-pack validation confirmed that `balanced_compromise` still fails because of baseline-side capture regression, the repo needed to know whether the failure came from one broad structural weakness or from a few narrower timing mechanisms.
- Decision: Add `run_window_replay_diagnostic.py` and `window_replay_diagnostic_v1.yaml`, then inspect the highest-regression baseline windows (`600519_23`, `000333_19`) at the level of daily permission, hierarchy assignment, filter/entry confirmation, signals, fills, and position intervals.
- Alternatives Considered: Keep trying more generic hierarchy / holding threshold sweeps without deeper diagnosis, or reopen promotion-gate tuning directly.
- Expected Benefits: Turn the current blocker into a smaller set of testable repair hypotheses instead of continuing blind broad-parameter search.
- Risks: Window-focused diagnosis can overfit if it becomes the only evidence source, so it should be treated as a mechanism finder, not as a standalone promotion criterion.
- Follow-up Actions: Use the replay output to decide whether the next narrow repair cycle should target entry timing, mainline-switch sensitivity, or both.

### DEC-0053

- Date: 2026-03-29
- Title: Add a default-off mainline switch buffer as an experimental regime lever
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: baseline_window_replay_diagnostic_v2
- Context: The first window replay showed that the baseline blocker is mixed: `600519_23` is mainly a late-entry issue, while `000333_19` repeatedly exits because the approved mainline flips too quickly (`replaced_by_new_mainline`).
- Decision: Extend `AttackPermissionConfig` with `switch_margin_buffer`, defaulting to `0.0`, so experiments can optionally hold the previously approved sector unless the new top sector beats it by a configured margin.
- Alternatives Considered: Leave the permission engine fully memoryless and keep searching only through hierarchy thresholds, or add a much heavier regime-state machine immediately.
- Expected Benefits: Provide a narrow, auditable way to reduce fast sector-flip churn without changing default V1 behavior.
- Risks: Any hysteresis mechanism can hide real regime changes if it is set too high, so it must stay experimental until validated across broader evidence.
- Follow-up Actions: Combine `switch_margin_buffer` with the already diagnosed `repair_window` reset and evaluate whether the two fixes address different slices of the baseline capture problem.

### DEC-0054

- Date: 2026-03-29
- Title: Reject strategy-side theme late-mover admission as the next broad promotion path and move the remaining blocker upstream
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T053932Z_e0bd5d89
- Context: After `balanced_targeted_timing_repair` fully fixed the old baseline blocker, the remaining gate failure narrowed to a small cluster of `theme_research_v2` `mainline_trend_c` windows where the challenger got no window position because symbols stayed `junk` instead of entering the `late_mover` layer.
- Decision: Add a default-off `late_mover` entry override to `StrategyConfig` for experimentation, test it through `theme_window_replay_diagnostic_v2/v3`, and treat the result as a branch-closing negative conclusion: this strategy-side override is not the right broad repair path. Future work should focus on theme-side hierarchy generation and derived data quality, not on making `mainline_trend_c` buy `junk` assignments.
- Alternatives Considered: Keep the strategy layer strict and continue only with more theme data diagnosis, or keep iterating on increasingly permissive strategy-side admission and holding hacks.
- Expected Benefits: Convert the remaining theme blocker into a cleaner research boundary by proving that naive strategy-side relief creates a different distortion instead of a true broad repair.
- Risks: The repo could become temporarily more conservative by rejecting a branch that does improve some individual windows, but that is preferable to promoting a superficially fixed yet structurally noisier candidate.
- Follow-up Actions: Analyze theme-side `late_mover` admissibility as an upstream hierarchy/data problem, and keep `balanced_targeted_timing_repair` as the stronger broad challenger until a cleaner fix exists.

### DEC-0055

- Date: 2026-03-29
- Title: Move the remaining theme blocker into a dedicated late-mover admissibility analysis layer
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_late_mover_admissibility_v1
- Context: After rejecting the strategy-side theme-admit patch, the repo still needed a way to measure the remaining theme blocker without going back to anecdotal window replay.
- Decision: Add `late_mover_admissibility.py` and `run_late_mover_admissibility.py`, and treat the remaining `theme_research_v2` problem as an upstream admissibility question: how often the challenger has valid permission/filter/entry context but remains `junk` instead of entering the `late_mover` layer.
- Alternatives Considered: Keep relying on a few manually replayed windows only, or continue testing more strategy-side overrides without a pack-wide quantification layer.
- Expected Benefits: Turn the theme blocker into a measurable hierarchy/data issue with counts, symbols, window patterns, and assignment-reason distributions instead of more trial-and-error strategy tweaking.
- Risks: A pack-wide admissibility analysis still does not prove which upstream fix is correct; it only makes the remaining problem legible.
- Follow-up Actions: Use the new report to prioritize upstream theme work around `fallback_to_junk` and `low_composite_or_low_resonance` patterns rather than reopening strategy-side candidate hacking.

### DEC-0056

- Date: 2026-03-29
- Title: Test concept-aware late-mover-quality support as an upstream theme-derived experiment, but do not treat the first boost as a final fix
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T055538Z_a15322e6, 20260329T055559Z_d9b1c86e
- Context: The new hierarchy-gap analysis showed that the theme blocker is dominated by a narrow band: `late_mover_quality` sits below the challenger's `0.60` threshold but above the incumbent's `0.55` threshold on nearly every impacted gap day.
- Decision: Add a default-off concept-support boost to `late_mover_quality` in `bootstrap_derived.py`, generate `theme_research_v3`, and evaluate it as an upstream data/derived experiment rather than as a new default or immediate promotion path.
- Alternatives Considered: Keep the derived layer unchanged and only document the blocker, or jump straight to a much larger redesign of theme hierarchy logic without first testing a lighter upstream intervention.
- Expected Benefits: Check whether a small concept-aware lift in late-mover quality can reduce the number of blocked theme windows without falling back to strategy-side hacks.
- Risks: A blunt boost can improve capture while damaging return / drawdown quality, which would simply trade one distortion for another.
- Follow-up Actions: Treat `theme_research_v3` as evidence, not as a promotion candidate. If more upstream work continues, it should become more targeted than a uniform boost.

### DEC-0057

- Date: 2026-03-29
- Title: Replace the uniform theme concept-support boost with a narrow band-limited late-mover-quality repair
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T060019Z_8c727a50, 20260329T060020Z_cc6e8259
- Context: `theme_research_v3` proved that upstream concept-aware support can reduce late-mover admissibility blockers, but the first implementation was too blunt and damaged return / drawdown quality at the pack level.
- Decision: Keep the idea at the derived-data layer, but narrow it sharply. Only apply concept-support to symbols already sitting inside a configured `late_mover_quality` band, and optionally cap the score at the top of that band instead of allowing a free boost.
- Alternatives Considered: Revert fully back to `theme_research_v2`, keep the uniform `theme_research_v3` boost, or reopen strategy-side theme-admission hacks.
- Expected Benefits: Preserve the blocker reduction signal from `theme_research_v3` while preventing the broader pack from drifting into earlier, noisier participation.
- Risks: This still introduces an extra derived-data rule that could become a hidden form of theme favoritism if it is widened carelessly.
- Follow-up Actions: Recheck the broad challenger against `shared_default` using the new `theme_research_v4` pack, then decide whether the remaining promotion blocker is still theme capture or something narrower.

### DEC-0058

- Date: 2026-03-29
- Title: Keep shared-default promotion frozen even after theme v4 because the blocker has only narrowed, not disappeared
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T060122Z_99e67000, 20260329T060321Z_a2d656e8
- Context: After `theme_research_v4` sharply reduced the remaining theme admissibility blocker, the repo needed to know whether that was enough to promote the current broad challenger.
- Decision: Keep the freeze status unchanged. Re-evaluate the newer broad challenger `balanced_targeted_timing_repair`, but do not promote it yet because the stricter gate still fails. The important change is that the blocker is now much narrower: capture regression is inside tolerance, while the remaining misses are `composite_rank_improvement` and `mean_max_drawdown_improvement`.
- Alternatives Considered: Promote immediately because the old theme capture blocker is mostly repaired, or keep focusing only on the older `balanced_compromise` storyline instead of updating the freeze narrative.
- Expected Benefits: Preserve honesty about the current evidence while also updating the repo's research target from a broad capture crisis to a smaller stability-improvement question.
- Risks: The repo stays in freeze longer even though the challenger is clearly improving, which may feel slow.
- Follow-up Actions: Treat the next research cycle as a narrow refinement of `balanced_targeted_timing_repair`, not as a reopening of broad candidate expansion.

### DEC-0059

- Date: 2026-03-29
- Title: Narrow the remaining broad-challenger refinement to regime-buffer tuning and stop spending effort on tiny holding/exit tweaks
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T060715Z_e2f8dc2a, 20260329T060753Z_bad3ddaa, 20260329T060852Z_0f4c9bd2
- Context: After `theme_research_v4` repaired the old theme-side blocker, the remaining promotion gap became very small and mostly expressed through broad stability metrics rather than capture.
- Decision: Run a narrow refinement cycle around `balanced_targeted_timing_repair` and treat `switch_margin_buffer` as the only remaining productive lever. Keep the best micro-variant (`buffer_only_012`) as the current refinement frontrunner, and stop spending more time on tiny holding-threshold or exit-window adjustments because they do not add useful improvement.
- Alternatives Considered: Reopen broader hierarchy or entry exploration, or keep chasing marginal drawdown improvements through holding/exit micro-tuning.
- Expected Benefits: Keep the next research cycle tightly scoped around the only lever that still shows a real signal.
- Risks: The remaining gate miss may ultimately require a different class of improvement, so this narrowing could still hit a local ceiling.
- Follow-up Actions: Treat `buffer_only_012` as the current best refinement branch and use it as the new reference point if another narrow promotion cycle is opened.

### DEC-0060

- Date: 2026-03-29
- Title: Treat threshold-level refinement around the broad challenger as largely exhausted after the final regime interpolation pass
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T061427Z_eaa04329
- Context: After identifying `buffer_only_012` as the best narrow refinement branch, the repo still needed to know whether one last tiny interpolation on regime thresholds could close the remaining validation-ready drawdown gap.
- Decision: Run a final ultra-narrow interpolation pass around `buffer_only_012` (`min_score_margin`, `switch_margin_buffer`, `min_top_score`) and treat the result as a branch-closing diagnostic: threshold-only tuning is now near exhaustion.
- Alternatives Considered: Keep iterating on more threshold permutations without a stopping rule, or reopen broader strategy/hierarchy exploration immediately.
- Expected Benefits: Establish a clear stopping point for threshold micro-tuning so the next research cycle can move to a deeper structural question instead of drifting through endless near-duplicates.
- Risks: A tiny untested threshold combination could still exist, but the probability is now low relative to the cost of continued search.
- Follow-up Actions: Keep `buffer_only_012` as the best threshold-level refinement branch. If shared-default work continues, the next cycle should look for a structural drawdown improvement rather than more threshold interpolation.

### DEC-0061

- Date: 2026-03-29
- Title: Stop treating the remaining promotion gap as a global refinement problem and localize it to a theme-side structural drawdown pocket
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T061729Z_4197eb4d
- Context: After the final threshold interpolation failed on the same drawdown-improvement gate, the repo still needed to know whether the missing improvement was broad and diffuse or concentrated in a smaller structural pocket.
- Decision: Add `drawdown_gap_analysis.py` and a dedicated time-slice comparison for `buffer_only_012`, then treat the remaining blocker as localized. The current weakest pocket is `theme_research_v4`, especially `2024_q1`, with `mainline_trend_a` as the weakest dataset-strategy summary and all three strategy rows in that slice forming the worst local drawdown cluster.
- Alternatives Considered: Keep refining thresholds without structural diagnosis, or reopen broad cross-pack candidate search again.
- Expected Benefits: Move the next cycle from global tuning to a much narrower theme-side structural drawdown investigation.
- Risks: A local diagnosis can still miss a second-order issue elsewhere, but it is far more actionable than continuing broad parameter search.
- Follow-up Actions: If the repo reopens promotion work again, start from the `theme_research_v4 / 2024_q1` drawdown cluster instead of changing global defaults again.

### DEC-0062

- Date: 2026-03-29
- Title: Treat the remaining theme-side drawdown pocket as a symbol-sequence problem centered on `300750`, not as another global threshold problem
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_trade_divergence_v1, theme_q1_symbol_timeline_300750_v1
- Context: Once the drawdown gap was localized to `theme_research_v4 / 2024_q1`, the repo still needed to know whether that pocket came from a broad cluster of small differences or from a smaller number of repeated symbol-level trade-path shifts.
- Decision: Add `slice_trade_divergence.py` and `symbol_timeline_replay.py`, then treat `300750` as the first concrete structural driver. The key pattern is not a missing window or a broad capture miss: it is an altered trade sequence where the challenger adds an earlier losing trade and fails to take a later winning trade that the incumbent still captures.
- Alternatives Considered: Go straight back to threshold tuning, or keep diagnosing only at dataset/slice averages without checking symbol-level trade paths.
- Expected Benefits: Move the next refinement cycle from aggregate metrics to a specific symbol-sequence mechanism that can actually be investigated.
- Risks: One symbol can dominate a small slice, so the repo should still be careful not to overfit to `300750` alone.
- Follow-up Actions: If refinement continues, inspect whether the `300750` pattern is caused by theme-side sector approval sequence, assignment drift, or both, then check whether similar path-shift patterns exist on a second symbol before changing any broad rule.

### DEC-0063

- Date: 2026-03-29
- Title: Treat the first concrete theme-side blocker mechanism as a repeated approval-path plus assignment-drift sequence
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_path_shift_300750_v1
- Context: After identifying `300750` as the first concrete symbol-level driver, the repo still needed to know whether that damage came from one isolated trade artifact or from a repeated daily path-shift pattern.
- Decision: Add `symbol_path_shift_analysis.py` and confirm that the mechanism repeats across all three strategies on the same dates. The first stable interpretation is that the remaining blocker is a combined approval-path drift and assignment-drift sequence, not just one unlucky trade.
- Alternatives Considered: Stop at the trade-sequence description only, or jump into a repair attempt without first checking whether the day-level mechanism repeats across strategies.
- Expected Benefits: Turn the `300750` finding into a more robust structural claim before the repo considers any repair hypothesis.
- Risks: Even a repeated symbol-level pattern can still be too local if no second symbol shows the same structure.
- Follow-up Actions: Use `300750` as the reference mechanism and test whether a second symbol in the same slice shows the same approval/assignment sequence before any rule change is proposed.

### DEC-0064

- Date: 2026-03-29
- Title: Treat the first concrete blocker mechanism as two separate upstream effects: hysteresis on `2024-01-19` and threshold-edge permission loss on `2024-02-05`
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_path_shift_300750_v1
- Context: After the repeated `300750` shift dates were isolated, the repo still needed to know whether those dates represented one vague path drift or a smaller number of concrete upstream effects.
- Decision: Interpret the first `300750` mechanism as two distinct upstream effects. On `2024-01-19`, the challenger keeps `BK1173` even though the electronics sector score is slightly higher, which points to hysteresis / approval-path persistence. On `2024-02-05`, the top sector score is `2.583525`, which passes the default theme threshold (`2.5`) but fails the challenger threshold (`2.6`), so the challenger loses permission on a borderline day and misses the profitable follow-through trade.
- Alternatives Considered: Treat the path shift as a generic black-box sequence issue, or jump straight to a repair without first separating the hysteresis effect from the threshold-edge permission effect.
- Expected Benefits: Give the next cycle a much sharper question: which of these two upstream effects is the real repair target, and do they repeat on another symbol.
- Risks: This interpretation still comes from one symbol, so it should be validated on at least one more case before any rule change is proposed.
- Follow-up Actions: Look for a second symbol with the same `approval persistence + threshold-edge permission loss` shape before making any protocol change.

### DEC-0065

- Date: 2026-03-29
- Title: Treat `300750` as the first damage case, not the only mechanism case; validate the same path-shift shape on a second tradable symbol before any repair idea is entertained
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_timeline_002466_v1, theme_q1_symbol_path_shift_002466_v1
- Context: After isolating `300750` as the first concrete damage case, the repo still needed to know whether the mechanism was unique to that symbol or repeated more broadly in the same slice.
- Decision: Run the same timeline and path-shift replay on `002466`, a second `theme_research_v4 / 2024_q1` symbol with real trades but no pnl divergence. Treat the repeated `2024-01-19` approval-sector split and `2024-02-05` threshold-edge permission split as confirmation that the upstream path shape is real, while also recording that not every repeated path shift turns into a worse trade sequence.
- Alternatives Considered: Jump straight to a repair hypothesis from `300750` alone, or use only non-tradable / no-trade symbols such as `300390` as the second validation case.
- Expected Benefits: Separate “mechanism exists�?from “mechanism causes damage,�?which is necessary before any structural fix is proposed.
- Risks: A second symbol with zero pnl divergence can still understate how often the mechanism becomes economically meaningful.
- Follow-up Actions: Use `300750` as the first damage case and `002466` as the first non-damage validation case. The next symbol-level diagnosis should target another tradable theme symbol that sits between those two outcomes.

### DEC-0066

- Date: 2026-03-29
- Title: Treat `002902` as a second non-damage validation case that exposes assignment-layer divergence without changing realized trades
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_timeline_002902_v1, theme_q1_symbol_path_shift_002902_v1
- Context: After `300750` established the first damage case and `002466` established the first repeated-mechanism-but-no-damage case, the repo still needed one more tradable symbol to clarify whether theme-side path shifts can stay latent even when they repeat across more dates.
- Decision: Replay `002902` across the longer `2024-01-20 -> 2024-03-10` range. Treat its repeated `2024-01-23` leader-vs-junk assignment split, `2024-02-05` permission split, and `2024-02-28` exit-reason split as confirmation that the blocker is broader than one symbol but still conditional: repeated path shifts can remain economically silent when both candidates keep the same executed trade path.
- Alternatives Considered: Stop after `002466`, or jump straight to a repair idea from the `300750` damage case alone.
- Expected Benefits: Further reduce the chance that the repo confuses “mechanism repeats�?with “mechanism necessarily causes pnl damage.�?- Risks: Even three symbols are still not enough to claim a final structural rule; the repo should continue to treat this as diagnosis, not promotion evidence.
- Follow-up Actions: Keep `300750` as the first damage case, `002466` as the first repeated-shape case, and `002902` as the first repeated-assignment-divergence case. The next refinement question should focus on which state transition turns these latent splits into actual trade damage.

### DEC-0067

- Date: 2026-03-29
- Title: Treat emitted-action or active-position divergence as the current damage-transition boundary, not repeated path-shift dates alone
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_damage_transition_analysis_v1
- Context: After building three symbol-level reference cases inside the same `theme_research_v4 / 2024_q1` pocket, the repo needed a reusable statement of what actually separates a harmless repeated path shift from a promotion-relevant damage case.
- Decision: Add `damage_transition_analysis.py` and classify the current three cases into one damage case (`300750`) and two latent cases (`002466`, `002902`). Treat repeated approval/permission or assignment splits as economically relevant only when they also change emitted actions or active-position state.
- Alternatives Considered: Keep adding more symbol examples without abstracting a rule, or jump from a single damage case to a repair hypothesis without first stating a transition boundary.
- Expected Benefits: Give the next cycle a tighter target than “find more path shifts.�?The research question becomes: what state transition converts a repeated structural split into a changed trade sequence?
- Risks: The current rule is still based on a small number of symbols and should be treated as a working structural hypothesis, not protocol truth.
- Follow-up Actions: Use the new transition rule to guide the next `theme` diagnosis cycle. Prioritize cases where repeated path shifts also coincide with emitted-action or active-position differences.

### DEC-0068

- Date: 2026-03-29
- Title: Treat action-state trigger dates as the next ranking boundary inside the theme-side blocker pocket
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_action_state_divergence_v1
- Context: After deriving the first reusable damage-transition rule, the repo still needed a practical way to rank future symbol-level diagnostics without treating every repeated shift date as equally important.
- Decision: Add `action_state_divergence_analysis.py` and explicitly rank symbol cases by whether repeated shift dates also produce action-state trigger dates. Under the current three-symbol set, only `300750` crosses that boundary; `002466` and `002902` stay latent.
- Alternatives Considered: Keep using the broader damage-transition rule alone, or continue triaging future symbols manually from raw path-shift reports.
- Expected Benefits: Give the next `theme` refinement cycle a clearer filter: focus first on repeated splits that already change actions or active position state.
- Risks: A symbol with rare trigger dates could still be over-prioritized if the surrounding pnl context is weak.
- Follow-up Actions: Use action-state trigger dates as the default shortlist criterion for future theme-side replay work. Symbols with zero trigger dates should be treated as supporting evidence, not first-line repair targets.

### DEC-0069

- Date: 2026-03-29
- Title: Treat the remaining `300750` blocker as four distinct trigger types rather than one blended theme-side failure
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_trigger_taxonomy_300750_v1
- Context: After identifying `300750` as the only current symbol that crosses the repeated action-state trigger boundary, the repo still needed to know whether that damage was dominated by one trigger family or by several different ones.
- Decision: Add `trigger_taxonomy_analysis.py` and classify the repeated `300750` trigger dates into four repair-relevant types: `early_buy_trigger`, `forced_sell_trigger`, `missed_buy_trigger`, and `position_gap_exit_trigger`. Treat the blocker as a sequence of four explicit trigger classes instead of one blended theme-side failure.
- Alternatives Considered: Keep working with the broader action-state rule only, or jump into repair work without first naming the specific trigger classes.
- Expected Benefits: Let the next cycle target one trigger family at a time instead of trying to fix all remaining theme-side behavior at once.
- Risks: Equal counts across trigger classes do not yet prove equal economic importance; the next cycle still needs to judge which class is actually most damaging.
- Follow-up Actions: Use the trigger taxonomy to decide whether the next repair attempt should focus first on early entry, forced unwind, missed re-entry, or exit-gap behavior.

### DEC-0070

- Date: 2026-03-29
- Title: Prioritize incumbent-side missed re-entry and position-gap exit triggers ahead of challenger-side early entry and forced unwind
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_trigger_priority_300750_v1
- Context: After decomposing `300750` into four trigger families, the repo still needed to know which family should be repaired first rather than treating all four as equally important.
- Decision: Add `trigger_priority_analysis.py` and rank the trigger families by unique-cycle pnl contribution. The current result is decisive: incumbent-only unique cycles contribute `1969.137`, while challenger-only unique cycles contribute only `377.037`. Therefore `missed_buy_trigger` and `position_gap_exit_trigger` are the first repair priorities, while `early_buy_trigger` and `forced_sell_trigger` are secondary.
- Alternatives Considered: Continue treating the four trigger families as equal, or prioritize the earliest trigger in time rather than the trigger family with the larger economic contribution.
- Expected Benefits: Focus the next repair cycle on the trigger family most likely to improve `mean_max_drawdown_improvement` instead of diffusing effort across offsetting mechanisms.
- Risks: The priority ranking still comes from one damage symbol, so the repo should keep treating it as a focused research hypothesis rather than a global protocol rule.
- Follow-up Actions: If theme-side repair work continues, start with the `missed_buy_trigger -> position_gap_exit_trigger` chain and leave `early_buy_trigger -> forced_sell_trigger` as a secondary, lower-priority branch.

### DEC-0071

- Date: 2026-03-29
- Title: Treat the dominant theme-side blocker as a complete missed re-entry chain, not just a ranked trigger family
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_missed_reentry_chain_300750_v1
- Context: After ranking the four trigger families, the repo still needed to know whether the dominant `missed_buy_trigger -> position_gap_exit_trigger` branch was only a loose priority cue or a complete repeated chain that could stand on its own.
- Decision: Add `missed_reentry_chain_analysis.py` and confirm that the `2024-02-05 -> 2024-02-06` branch forms a complete chain in all three strategies for `300750`. The challenger loses permission and emits no buy on `2024-02-05`; on `2024-02-06` the incumbent still has the resulting position and exits it, while the challenger has no position to exit. Treat this chain as the current dominant theme-side blocker.
- Alternatives Considered: Keep talking about the blocker only through trigger-family ranking, or jump directly into a repair attempt without first proving that the missed re-entry branch is a full repeated chain.
- Expected Benefits: Give the next refinement step a much tighter target than a generic theme-side drawdown story. The repo can now study one two-date chain instead of four trigger classes at once.
- Risks: The complete-chain conclusion is still anchored to one damage symbol and should remain a focused research hypothesis, not a generalized protocol rule.
- Follow-up Actions: If refinement continues, inspect why the challenger loses permission on `2024-02-05` without immediately broadening the search again. The paired `2024-02-06` position-gap exit should be treated as a downstream consequence, not the first repair target.

### DEC-0072

- Date: 2026-03-29
- Title: Treat `2024-02-05` as a threshold-edge permission-loss date, not a broad regime-ambiguity date
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_permission_loss_edge_300750_v1
- Context: After proving that the dominant blocker is a complete `missed_buy -> position_gap_exit` chain, the repo still needed to know whether the first date in that chain came from a narrow threshold edge, a margin ambiguity, or a switch-buffer persistence effect.
- Decision: Add `permission_loss_edge_analysis.py` and confirm that the `2024-02-05` split is a narrow top-score threshold edge. `BK1173` scores `2.583525`; the incumbent still approves it under `min_top_score=2.5`, while the challenger rejects it under `min_top_score=2.6` with explicit reason `top_score_below_threshold`. The top-vs-second margin remains wide (`0.967343`), so the blocker is not a weak ranking ambiguity on that date.
- Alternatives Considered: Keep describing the missed re-entry only as a general regime-path issue, or jump straight to another refinement attempt without first pinning down the exact permission-loss mechanism.
- Expected Benefits: Give the next repair cycle a more precise target than "theme Q1 drawdown". The repo can now study a very small threshold-edge permission-loss mechanism instead of a broad blended hypothesis.
- Risks: The date-level explanation is still from one symbol and one slice, so it should be treated as a focused local mechanism rather than a final protocol-wide rule.
- Follow-up Actions: If refinement continues, study whether the right next step is to soften only this narrow permission edge or to leave it intact and accept the current freeze status.

### DEC-0073

- Date: 2026-03-29
- Title: Treat the `2.60 -> 2.58` theme threshold-edge relaxation as a tested but insufficient local repair
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T070422Z_3a231b85, buffer_top258_validation_gate_v1
- Context: After localizing the dominant blocker to a `0.016475` top-score miss on `2024-02-05`, the repo still needed to know whether directly relaxing that threshold edge would be enough to justify further promotion work.
- Decision: Run a very narrow three-pack threshold-edge sweep (`2.60 -> 2.59 -> 2.58`) and gate the best relaxed candidate. The result is negative in the sense that matters: `buffer_top258` slightly improves the `theme_research_v4` row, but it does not improve capture there, does not overtake `buffer_only_012` on composite stability, and still fails the stricter validation gate on `mean_max_drawdown_improvement` (`0.002509 < 0.003`).
- Alternatives Considered: Keep the threshold-edge conclusion at the date-diagnosis level only, or jump straight into a broader new refinement cycle without first checking whether this specific edge can be repaired cheaply.
- Expected Benefits: Close the loop on the most obvious local repair idea before opening any deeper structural work. The repo now knows that the narrow threshold-edge patch is real but not enough.
- Risks: This conclusion is still tied to the current three-pack gate and may change if the broader dataset mix changes substantially later.
- Follow-up Actions: Keep `buffer_only_012` as the stronger frozen challenger branch and treat `buffer_top258` as a documented local-repair probe rather than a promotion candidate.

### DEC-0074

- Date: 2026-03-29
- Title: Treat the remaining blocker as acceptable residual cost under the current freeze rather than continue narrow threshold grinding
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: residual_cost_acceptance_v1
- Context: After testing the obvious `2.60 -> 2.58` threshold-edge repair, the repo still needed a formal answer to whether the remaining blocker justified further narrow tuning or should instead be accepted as the residual price of the stricter challenger.
- Decision: Add `residual_cost_acceptance_analysis.py` and summarize the current posture as `freeze_and_accept_residual_cost`. The challenger still improves broad rank and return, the remaining strict-gate gap is numerically small (`0.000496` on mean drawdown improvement), the weakness is localized to `theme_research_v4 / 2024_q1`, and the cheap local relief test adds only `0.000005` of drawdown improvement relative to the frozen branch. Under the current evidence, further threshold grinding is not justified.
- Alternatives Considered: Keep treating the blocker as an open local tuning problem, or reopen a wider refinement search despite the localized and weakly repairable nature of the gap.
- Expected Benefits: Prevent the repo from spending more research budget on a nearly exhausted threshold-level path. The freeze status becomes a deliberate choice instead of an unresolved hesitation.
- Risks: If later data packs broaden the same blocker into a larger cross-pack weakness, this acceptance posture may need to be revisited.
- Follow-up Actions: Keep `shared_default` frozen as the official default and keep `buffer_only_012` as the strongest documented frozen challenger. If future work resumes here, it should start from deeper structure or new data, not from more threshold interpolation.

### DEC-0075

- Date: 2026-03-29
- Title: Shift the next V1.1 research cycle from frozen-blocker repair to specialist alpha pockets
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: 20260329T071117Z_fa50f33e, specialist_alpha_analysis_v1
- Context: After accepting the remaining `buffer_only_012` blocker as residual cost, the repo still needed to decide what the next high-value V1.1 research target should be instead of continuing to grind the same frozen issue.
- Decision: Run a new three-pack time-slice validation with the current official default, the strongest frozen challenger, and the two specialist branches, then add `specialist_alpha_analysis.py` to find pockets where a specialist beats both broad anchors in its native metric. The result is clear enough to redirect research: `baseline_expansion_branch` owns the largest capture pockets, while `theme_strict_quality_branch` owns the most drawdown-specialist pockets.
- Alternatives Considered: Continue refining the frozen blocker, or immediately widen the universe again without first mapping where specialist edge still exists.
- Expected Benefits: Reallocate research effort from a nearly exhausted freeze issue to non-overlapping specialist alpha opportunities.
- Risks: Slice-level opportunity pockets are not promotion evidence by themselves; they can still be local and should be treated as V1.1 research entry points, not new defaults.
- Follow-up Actions: Start the next alpha cycle from the specialist pockets, not from the frozen blocker. The first capture-oriented pocket is `theme_research_v4 / 2024_q1 / mainline_trend_c`; the first drawdown-oriented pocket is `baseline_research_v1 / 2024_q3 / mainline_trend_b,c`.

### DEC-0076

- Date: 2026-03-29
- Title: Treat `002466`, `000155`, `600338`, and `300518` as the first window-level capture drivers inside the top specialist pocket
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: specialist_pocket_window_analysis_v1
- Context: After identifying `theme_research_v4 / 2024_q1 / mainline_trend_c` as the strongest capture specialist pocket for `baseline_expansion_branch`, the repo still needed to know whether that pocket was driven by one diffuse aggregate effect or by a small number of concrete windows that broad anchors fail to open.
- Decision: Add `specialist_pocket_window_analysis.py` and classify the pocket at window level against the two broad anchors (`shared_default`, `buffer_only_012`). The result is concentrated enough to guide the next replay cycle: there are only `4` improved windows, and `2` of them are full both-anchor misses. The most important driver is `002466_2`, where the specialist captures `0.937549` of a `0.054354` window that both anchors miss entirely. The next strongest new-window driver is `000155_5`, while `600338_5` and `300518_7` are partial-capture improvements rather than pure window openings.
- Alternatives Considered: Keep treating the pocket only as a slice-level ranking fact, or jump directly into another symbol replay without first knowing which windows actually create the specialist edge.
- Expected Benefits: Convert the new V1.1 capture pocket from an abstract "good slice" into a short, replayable list of symbol-window drivers. This lets the repo study where expansion logic truly opens new windows versus where it only lifts already-open captures.
- Risks: A four-window pocket is still local and may change as the theme pack evolves, so it should guide the next research loop rather than become a protocol rule by itself.
- Follow-up Actions: Start the next capture-specialist replay from `002466_2`, then `000155_5`. Treat `600338_5` and `300518_7` as secondary cases because they improve partial capture rather than opening a fully missed window.

### DEC-0077

- Date: 2026-03-29
- Title: Treat `002466_2` as a hierarchy-admission opening edge, not a regime-permission opening edge
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_timeline_002466_capture_v1, theme_q1_specialist_window_opening_002466_v1
- Context: After reducing the first specialist capture pocket to four concrete windows, the repo still needed to know what exactly opened the strongest new window (`002466_2`) for `baseline_expansion_branch`.
- Decision: Replay `002466` with the real `baseline_expansion_branch` override from the three-pack validation and add `specialist_window_opening_analysis.py` to classify the first specialist-only opening date. The result is clean enough to lock in: on `2024-01-10`, specialist and broad anchors share the same permission path, the same passed filters, and the same triggered entry family, but only the specialist upgrades the symbol from `junk` to `late_mover` through `late_mover_quality_fallback`, which emits the first buy and opens the window one day earlier.
- Alternatives Considered: Keep reading the pocket only through path-shift or trade-level reports, or assume the opening edge came from a looser regime gate because the branch is expansion-oriented.
- Expected Benefits: Prevent the next capture-specialist cycle from chasing the wrong layer. The repo now knows that `002466_2` is primarily a hierarchy-admission case, not a regime-approval case.
- Risks: This is still one window inside one pocket; the same mechanism should be checked again on `000155_5` before it is treated as a broader capture-specialist rule.
- Follow-up Actions: Replay `000155_5` next and test whether it opens through the same pattern: aligned permission/filter/entry states plus a specialist-only `late_mover` or non-junk assignment upgrade.

### DEC-0078

- Date: 2026-03-29
- Title: Treat `000155_5` as a persistence edge rather than an opening edge inside the same capture pocket
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_timeline_000155_capture_v1, theme_q1_specialist_window_persistence_000155_v1
- Context: After proving that `002466_2` opens because the specialist upgrades hierarchy admission one day earlier, the repo still needed to know whether the second full both-anchor miss (`000155_5`) comes from the same opening mechanism or from a different type of specialist edge.
- Decision: Replay `000155` with the same branch set and add `specialist_window_persistence_analysis.py` to classify the first day where the specialist keeps the window alive while broad anchors churn out. The result is clearly a persistence case: all three candidates buy the window, but on `2024-02-22` the specialist keeps holding with `structure_intact` while both anchors emit `sell` because the symbol falls back to `junk`. The specialist then keeps the position through `2024-02-27` and converts the later move into a stronger captured window.
- Alternatives Considered: Assume `000155_5` is just another opening-edge replay like `002466_2`, or keep reading it only through aggregate capture ratios without identifying the day the branches actually diverge.
- Expected Benefits: Establish a clean two-part taxonomy for the first capture pocket: some windows are opened by hierarchy admission earlier, while others are preserved by refusing anchor-style churn.
- Risks: This is still one pocket-level case and should not yet be generalized beyond the current specialist study set.
- Follow-up Actions: Treat `002466_2` as the opening-edge template and `000155_5` as the persistence-edge template. The next replay should move to a partial-capture case such as `600338_5` or `300518_7` to see whether they belong to one of these two families or define a third one.

### DEC-0079

- Date: 2026-03-29
- Title: Treat `600338_5` as a staggered opening edge, not a third hybrid family
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_timeline_600338_capture_v1, theme_q1_specialist_window_opening_600338_v1
- Context: After separating the first capture-specialist pocket into opening edges (`002466_2`) and persistence edges (`000155_5`), the repo still needed to know whether a partial-capture lift like `600338_5` defines a third family or is just a weaker version of one of the first two.
- Decision: Replay `600338` and reuse `specialist_window_opening_analysis.py` on the exact pocket window. The result is that `600338_5` belongs to the opening family, not to a new hybrid class. On `2024-02-21`, the specialist emits the first buy while both anchors remain flat, even though permission, filters, and entry triggers are already aligned across all candidates. The difference again sits in hierarchy admission: the specialist upgrades the symbol to `late_mover`, while both anchors keep it in `junk`. The only reason the window is not a full miss is that anchors enter later and recover part of the move.
- Alternatives Considered: Treat the partial-capture lift as evidence of a third hybrid family, or defer classification until more partial windows were replayed.
- Expected Benefits: Keep the V1.1 capture taxonomy compact and interpretable. The repo can now treat `600338_5` as a staggered opening case rather than inventing a new family too early.
- Risks: The taxonomy could still expand later if `300518_7` or broader packs show a genuinely different mechanism.
- Follow-up Actions: Treat the first capture pocket as currently containing two confirmed families: opening edges and persistence edges. Replay `300518_7` next as the remaining partial-capture case to check whether it still fits one of these two families.

### DEC-0080

- Date: 2026-03-29
- Title: Close the first capture-specialist pocket taxonomy with `300518_7` as another light opening edge
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q1_symbol_timeline_300518_capture_v1, theme_q1_specialist_window_opening_300518_v1
- Context: After classifying `002466_2` as an opening edge, `000155_5` as a persistence edge, and `600338_5` as a staggered opening edge, the repo still had one unresolved partial-capture case (`300518_7`) and therefore had not yet closed the first capture pocket taxonomy.
- Decision: Replay `300518` and reuse the opening analyzer on `2024-03-18 -> 2024-03-20`. The result stays inside the existing taxonomy: `300518_7` is another opening edge. On `2024-03-18`, the specialist upgrades the symbol to `late_mover` and emits the first buy while both broad anchors keep permission and entry triggers aligned but leave the symbol in `junk`. The capture advantage is smaller because the anchors enter the move only one day later.
- Alternatives Considered: Keep the final partial-capture case open as an unresolved possibility of a third hybrid family, or postpone classification until a larger set of partial windows was available.
- Expected Benefits: Close the first specialist capture pocket with a stable, compact mechanism map. The repo can now move from taxonomy-building to comparing how often opening edges versus persistence edges appear in later pockets.
- Risks: Future larger packs may still surface a third family, but the first pocket no longer needs that uncertainty to remain open.
- Follow-up Actions: Treat the first capture pocket as closed under a two-family map: opening edges and persistence edges. The next specialist-alpha step should move from case taxonomy to cross-pocket frequency or to the drawdown-specialist branch.

### DEC-0081

- Date: 2026-03-29
- Title: Treat `600519` as the dominant symbol-level driver inside the first drawdown-specialist pocket
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: baseline_q3_symbol_timeline_000001_quality_v1, baseline_q3_symbol_timeline_000333_quality_v1, baseline_q3_symbol_timeline_600519_quality_v1, baseline_q3_symbol_cycle_delta_600519_v1
- Context: After deciding to leave the first capture-specialist pocket closed under a two-family taxonomy, the repo still needed to know where the cleanest `theme_strict_quality_branch` drawdown edge actually comes from inside `baseline_research_v1 / 2024_q3 / mainline_trend_b`.
- Decision: Replay the three traded symbols in that pocket (`000001`, `000333`, `600519`) and compare `shared_default`, `buffer_only_012`, and `theme_strict_quality_branch`. The result is concentrated enough to guide the next loop: `600519` is the only symbol where the quality branch produces a large positive delta (`+1957.0392`) while also reducing fills and trade count. A new `symbol_cycle_delta_analysis.py` report confirms why: the incumbent has four unique cycles totaling `-10698.5493`, while the challenger's unique cycles total `-8741.5101`. The quality branch still takes losses, but it avoids enough incumbent-only losing churn to dominate the pocket-level improvement.
- Alternatives Considered: Keep discussing the drawdown pocket only at the slice level, or assume the branch-level drawdown improvement is evenly distributed across all three symbols.
- Expected Benefits: Give the next drawdown-specialist cycle a concrete symbol-level target instead of another broad slice-level hypothesis.
- Risks: Exact-cycle matching is strict, so nearby but non-identical cycles still need replay before turning this into a deeper mechanism rule.
- Follow-up Actions: Start the next drawdown-specialist replay from `600519`, especially the incumbent-only losing cycles on `2024-07-03 -> 2024-07-05`, `2024-08-01 -> 2024-08-02`, and `2024-08-09 -> 2024-08-14`.

### DEC-0082

- Date: 2026-03-29
- Title: Freeze the first drawdown-specialist pocket under a three-part `600519` cycle taxonomy
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: baseline_q3_nearby_cycle_bridge_600519_v1, baseline_q3_cycle_mechanism_600519_v1
- Context: After localizing the cleanest drawdown-specialist pocket to `600519`, the repo still only knew that the quality branch "reduced bad churn". That was not specific enough to compare later drawdown pockets against.
- Decision: Add `cycle_mechanism_analysis.py` and classify the incumbent-only `600519` cycles using the nearby-cycle bridge plus the date-level timeline replay. The first drawdown-specialist pocket now sits inside a three-part negative-cycle map: `entry_suppression_avoidance` on `2024-08-01 -> 2024-08-02`, `earlier_exit_loss_reduction` on `2024-08-09 -> 2024-08-14`, and `later_exit_loss_extension` on `2024-07-03 -> 2024-07-05`. The remaining unmatched positive cycle on `2024-08-16 -> 2024-08-20` is only a small opportunity-cost case and does not change the pocket story.
- Alternatives Considered: Keep replaying `600519` only through raw trade lists, or continue describing the pocket with a vague statement like "quality is steadier" without turning it into a reusable mechanism map.
- Expected Benefits: Give the drawdown-specialist line the same kind of compact taxonomy already established on the first capture-specialist pocket.
- Risks: This is still one pocket driver. The taxonomy should be reused on later drawdown pockets before being treated as a broader research truth.
- Follow-up Actions: Use the three-part cycle taxonomy as the default lens for the next drawdown-specialist pocket instead of reopening broad branch searches.

### DEC-0083

- Date: 2026-03-29
- Title: Treat `baseline_research_v1 / 2024_q3` drawdown behavior as a shared `B/C` pocket, not two separate stories
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: baseline_q3_trade_divergence_quality_c_v1, baseline_q3_symbol_timeline_600519_quality_c_v1, baseline_q3_symbol_cycle_delta_600519_c_v1, baseline_q3_nearby_cycle_bridge_600519_c_v1, baseline_q3_cycle_mechanism_600519_c_v1, baseline_q3_cross_strategy_cycle_consistency_v1
- Context: After formalizing the first drawdown-specialist pocket on `mainline_trend_b`, the repo still needed to know whether `mainline_trend_c` should be treated as a second pocket or as the same structural drawdown map repeated on another strategy.
- Decision: Replay `mainline_trend_c` on the same `baseline_research_v1 / 2024_q3` slice, then compare the resulting `600519` cycle mechanism report against the existing `mainline_trend_b` version. The result is exact enough to freeze: `mainline_trend_b` and `mainline_trend_c` share the same three negative-cycle signatures on `600519` (`2024-07-03`, `2024-08-01`, `2024-08-09`) with the same mechanism labels (`later_exit_loss_extension`, `entry_suppression_avoidance`, `earlier_exit_loss_reduction`).
- Alternatives Considered: Keep replaying `B` and `C` separately as though they were independent drawdown pockets, or assume the similarity without generating a formal cross-strategy consistency report.
- Expected Benefits: Prevent duplicated replay effort on a pocket that is already structurally stable across two strategy variants.
- Risks: The pocket is now strategy-stable across `B/C`, but not yet across all later datasets or slices.
- Follow-up Actions: Reuse this `B/C` cycle map as one baseline drawdown template. The next drawdown-specialist research step should move to a different pocket rather than keep re-explaining this one.

### DEC-0084

- Date: 2026-03-29
- Title: Treat `market_research_v0 / 2024_q4 / mainline_trend_c` as a different drawdown family, not a copy of the baseline-Q3 `600519` map
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: market_q4_trade_divergence_quality_c_v1, market_q4_symbol_timeline_600519_quality_c_v1, market_q4_symbol_cycle_delta_600519_c_v1, market_q4_nearby_cycle_bridge_600519_c_v1, market_q4_cycle_mechanism_600519_c_v1
- Context: After proving that the first drawdown-specialist pocket is strategy-stable across `B/C`, the repo needed to know whether the next pocket on `market_research_v0 / 2024_q4 / mainline_trend_c` would reuse the same three-part cycle taxonomy or require a new mechanism family.
- Decision: Run the same `trade_divergence -> timeline -> cycle_delta -> nearby_bridge -> cycle_mechanism` chain on the strongest next drawdown pocket. The result is not a copy of the baseline-Q3 template. `600519` is still the main driver, but the decisive negative-cycle mechanism is now `preemptive_loss_avoidance_shift`: the challenger realizes a smaller loss on `2024-12-11 -> 2024-12-12` and then avoids the incumbent's larger `2024-12-13 -> 2024-12-16` loss. The same pocket also carries a very large `entry_suppression_opportunity_cost` on the incumbent's `2024-09-27 -> 2024-10-08` positive cycle.
- Alternatives Considered: Assume the market-Q4 pocket reused the same three baseline-Q3 mechanisms, or keep the new reduced-loss shape parked under a vague `other_reduced_loss_shift` label.
- Expected Benefits: Prevent the drawdown-specialist line from overfitting itself to the first pocket. The repo now knows that later pockets can introduce a second family rather than merely repeat the baseline-Q3 template.
- Risks: This new family is currently pinned on one strategy-pocket combination, so it still needs later reuse before it is treated as a broader market-level rule.
- Follow-up Actions: Treat `preemptive_loss_avoidance_shift` as the next drawdown-specialist family candidate. The next pocket should test whether this family repeats, or whether `market_q4` is a one-off case with unusually strong opportunity-cost tradeoffs.

### DEC-0085

- Date: 2026-03-29
- Title: Treat `theme_research_v4 / 2024_q4 / mainline_trend_c` as a third drawdown-specialist family centered on `carry_in_basis_advantage`
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q4_trade_divergence_quality_c_v1, theme_q4_symbol_timeline_300750_quality_c_v1, theme_q4_symbol_cycle_delta_300750_c_v1, theme_q4_nearby_cycle_bridge_300750_c_v1, theme_q4_cycle_mechanism_300750_c_v1
- Context: After establishing the baseline-Q3 `B/C` drawdown template and then discovering a second, more ambiguous market-Q4 family around `preemptive_loss_avoidance_shift`, the repo still needed to know whether the next strongest drawdown pocket on `theme_research_v4 / 2024_q4 / mainline_trend_c` would repeat one of those two families or introduce another mechanism.
- Decision: Run the same `trade_divergence -> timeline -> cycle_delta -> nearby_bridge -> cycle_mechanism` chain on the strongest positive symbol inside the `theme_q4` pocket, then upgrade the cycle analyzer if the reduced-loss shape is genuinely distinct. The result is not a replay of either prior family. `300750` is the main positive driver (`+1464.4411`), and its mechanism map splits into one standard `earlier_exit_loss_reduction` on `2024-10-28 -> 2024-10-30` plus one new `carry_in_basis_advantage` on `2024-11-06 -> 2024-11-07`, where the challenger entered earlier on `2024-11-05` and exited on the same day as the incumbent with a much better basis.
- Alternatives Considered: Leave the `2024-11-05 -> 2024-11-07` pattern under `other_reduced_loss_shift`, or force the whole pocket into the existing `preemptive_loss_avoidance_shift` family even though the challenger cycle overlaps the incumbent exit rather than ending before the incumbent cycle opens.
- Expected Benefits: Prevent the drawdown-specialist line from collapsing unlike mechanisms into one vague "reduced loss" bucket. The repo can now distinguish between avoiding a future bad cycle entirely (`preemptive_loss_avoidance_shift`) and entering earlier with a better basis so the later bad day no longer damages the trade (`carry_in_basis_advantage`).
- Risks: This third family is currently supported by one strategy-pocket-symbol chain. It still needs reuse before being treated as a broader research truth.
- Follow-up Actions: Treat `theme_q4` as the first confirmed `carry_in_basis_advantage` pocket. The next drawdown-specialist step should test whether later pockets repeat this family or fall back into the baseline-Q3 / market-Q4 maps.

### DEC-0086

- Date: 2026-03-29
- Title: Treat `theme_research_v4 / 2024_q3 / mainline_trend_c` as a partial reuse of the baseline-Q3 drawdown family
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q3_trade_divergence_quality_c_v1, theme_q3_symbol_timeline_002460_quality_c_v1, theme_q3_symbol_cycle_delta_002460_c_v1, theme_q3_nearby_cycle_bridge_002460_c_v1, theme_q3_cycle_mechanism_002460_c_v1
- Context: After confirming three drawdown-specialist families across `baseline_q3`, `market_q4`, and `theme_q4`, the repo still needed to know whether later pockets would keep branching or whether one of the earlier families would start repeating across different dataset-slice combinations.
- Decision: Replay the top positive driver inside `theme_research_v4 / 2024_q3 / mainline_trend_c`, then compare its cycle mechanism map against the existing family set. The result does not introduce a fourth family. `002460` is the top positive driver (`+534.775`), and its mechanism report is dominated by three repeated `entry_suppression_avoidance` rows (`2024-07-12`, `2024-08-01`, `2024-08-14`) plus two residual `other_worse_loss_shift` rows. This means the pocket mostly reuses the baseline-Q3 style of avoiding bad incumbent-only cycles, but with weaker and noisier nearby-cycle behavior around the edges.
- Alternatives Considered: Treat the mixed `theme_q3` map as a brand-new family because it includes worse nearby cycles, or ignore the pocket entirely because its positive edge is smaller than the earlier `600519` pockets.
- Expected Benefits: Show that the drawdown-specialist taxonomy is starting to repeat rather than expanding indefinitely. The repo can now say that baseline-Q3-style `entry_suppression_avoidance` is not a one-pocket accident.
- Risks: The `theme_q3` pocket is less clean than baseline-Q3 because the two worse nearby cycles mean the branch is not uniformly better. Reuse of the family does not imply the whole pocket is a high-confidence deployment template.
- Follow-up Actions: Treat `theme_q3 / 002460` as the first cross-pocket reuse of the baseline-Q3 family. The next drawdown-specialist step should prefer pockets that might repeat `preemptive_loss_avoidance_shift` or `carry_in_basis_advantage`, since baseline-style avoidance now has at least one external reuse case.

### DEC-0087

- Date: 2026-03-29
- Title: Treat `theme_research_v4 / 2024_q2 / mainline_trend_c` as the first `delayed_entry_basis_advantage` drawdown pocket
- Status: accepted
- Related Protocol Version: protocol_v1.0
- Related Runs: theme_q2_trade_divergence_quality_c_v1, theme_q2_symbol_timeline_300750_quality_c_v1, theme_q2_symbol_cycle_delta_300750_c_v1, theme_q2_nearby_cycle_bridge_300750_c_v1, theme_q2_cycle_mechanism_300750_c_v1
- Context: After confirming baseline-style reuse on `theme_q3 / 002460`, the repo still needed to know whether later drawdown pockets would repeat one of the newer basis-sensitive families or require another mechanism label.
- Decision: Replay the strongest remaining clean pocket on `theme_research_v4 / 2024_q2 / mainline_trend_c`, then extend the cycle analyzer if the reduced-loss shape is distinct. The result justifies a fourth family. `300750` is the top driver (`+802.5721`), and its key negative-cycle repair on `2024-05-20 -> 2024-05-22` is neither `preemptive_loss_avoidance_shift` nor `carry_in_basis_advantage`: the challenger enters *after* the incumbent on `2024-05-21`, exits on the same day, and still loses less because the entry basis is lower. This is now labeled `delayed_entry_basis_advantage`.
- Alternatives Considered: Leave the `2024-05-20 -> 2024-05-22` row under `other_reduced_loss_shift`, or force it into `earlier_exit_loss_reduction` even though both sides exit on the same day.
- Expected Benefits: Make the drawdown-specialist taxonomy more symmetric and interpretable. The repo can now distinguish three different reduced-loss basis families: avoiding the later cycle entirely (`preemptive_loss_avoidance_shift`), entering earlier with the same exit (`carry_in_basis_advantage`), and entering later with the same exit (`delayed_entry_basis_advantage`).
- Risks: The new family is still anchored on one pocket-symbol chain. It is a reusable mechanism label, not yet a fully generalized research law.
- Follow-up Actions: Treat `theme_q2 / 300750` as the first confirmed `delayed_entry_basis_advantage` case. Future drawdown pockets should now be checked against four families rather than three.

### DEC-0088

- Date: 2026-03-29
- Title: Use cycle-family inventory, not isolated pocket anecdotes, to prioritize the next drawdown-specialist loop
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: cycle_family_inventory_v1
- Context: After the repo accumulated at least four drawdown-specialist family labels, the next research risk was obvious: keep chasing whichever pocket was freshest in memory instead of ranking families by reuse, net negative improvement, and opportunity cost.
- Decision: Add `cycle_family_inventory.py`, `run_cycle_family_inventory.py`, and `cycle_family_inventory_v1.yaml`, then aggregate the five confirmed drawdown pocket reports into one inventory table. The resulting ranking is clear enough to guide the next loop. `entry_suppression_avoidance` is currently the strongest reusable family (`net_family_edge = 4870.1396`, repeated across two pockets). `preemptive_loss_avoidance_shift` has strong single-pocket edge (`2101.8677`) but carries very large opportunity-cost risk in its source pocket. `carry_in_basis_advantage` is cleaner and stronger than `delayed_entry_basis_advantage`, while `entry_suppression_opportunity_cost` is the main toxic family to avoid.
- Alternatives Considered: Keep prioritizing the next drawdown pocket manually from recent reports, or rank pockets only by raw specialist opportunity without normalizing family-level opportunity cost.
- Expected Benefits: Shift the V1.1 drawdown-specialist line from anecdote-driven exploration to asset-level management. The repo can now say which family is worth reusing, which one is still fragile, and which one is net-toxic.
- Risks: The inventory still only reflects five pockets, all on `mainline_trend_c`. It is a ranking aid, not a final truth table.
- Follow-up Actions: Treat `entry_suppression_avoidance` as the most reusable current family. When looking for the next non-baseline family to scale, prefer `carry_in_basis_advantage` over `preemptive_loss_avoidance_shift` because its net edge is cleaner and its opportunity-cost burden is lower.

### DEC-0089

- Date: 2026-03-29
- Title: Treat `carry_in_basis_advantage` as a cross-strategy reusable family after confirming the `theme_q4 / 300750` `B/C` duplicate
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_q4_trade_divergence_quality_b_v1, theme_q4_symbol_timeline_300750_quality_b_v1, theme_q4_symbol_cycle_delta_300750_b_v1, theme_q4_nearby_cycle_bridge_300750_b_v1, theme_q4_cycle_mechanism_300750_b_v1, theme_q4_cross_strategy_cycle_consistency_v1, cycle_family_inventory_v2
- Context: After `cycle_family_inventory_v1` ranked `carry_in_basis_advantage` as the cleanest non-baseline family, the repo still needed to know whether that family was only a single `mainline_trend_c` anecdote or whether the same pocket would repeat on another strategy with the same mechanism map.
- Decision: Complete the missing `theme_research_v4 / 2024_q4 / 300750 / mainline_trend_b` replay chain, then formalize the duplication with `cross_strategy_cycle_consistency_analysis` and a second inventory pass. The `B` and `C` reports are now identical on the negative side: both contain `earlier_exit_loss_reduction` on `2024-10-28 -> 2024-10-30` and `carry_in_basis_advantage` on `2024-11-06 -> 2024-11-07`. `cycle_family_inventory_v2` therefore lifts `carry_in_basis_advantage` to `report_count = 2`, `occurrence_count = 2`, and `net_family_edge = 1682.5046` with zero positive opportunity-cost drag.
- Alternatives Considered: Leave `carry_in_basis_advantage` tagged as a clean one-off until a different symbol repeats it, or skip the formal duplication step and continue selecting the next pocket manually.
- Expected Benefits: Upgrade the family from a clean pocket label to a true cross-strategy reusable specialist family. This gives the drawdown-specialist line a clearer non-baseline research candidate next to baseline-style `entry_suppression_avoidance`.
- Risks: The family still comes from one symbol (`300750`) and one dataset-slice pocket (`theme_q4`). It is now cross-strategy reusable, not yet cross-symbol generalized.
- Follow-up Actions: Treat `carry_in_basis_advantage` as the leading non-baseline family for the next specialist expansion loop. The next search should prefer another pocket or symbol that might reuse this family.

### DEC-0090

- Date: 2026-03-29
- Title: Use a replay shortlist instead of hand-picking the next drawdown-family candidate
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_q4_cycle_mechanism_300759_b_v1, theme_q4_cycle_mechanism_002466_c_v2, drawdown_family_candidate_shortlist_v2
- Context: After confirming that `carry_in_basis_advantage` repeats across `theme_q4 / 300750 / B-C`, the next research question shifted from "is `carry` real?" to "where should the repo spend the next replay budget?" The risk was obvious: keep manually chasing familiar symbols and pockets instead of ranking unanalysed candidates systematically.
- Decision: Verify two cheap follow-up candidates first, then add a reusable shortlist tool. `300759` on `theme_q4 / mainline_trend_b` turned out to be plain `earlier_exit_loss_reduction`, not a second `carry` case. `002466` on `theme_q4 / mainline_trend_c` turned out to be a mixed pocket with `entry_suppression_avoidance`, `earlier_exit_loss_reduction`, and toxic positive-cycle drag, also not a second `carry` case. After those checks, add `family_candidate_shortlist.py`, `run_family_candidate_shortlist.py`, and `drawdown_family_candidate_shortlist_v2.yaml` so future symbol selection starts from a ranked table rather than from memory. The refreshed shortlist now points to `theme_research_v4 / 2024_q3 / mainline_trend_c / 603799` as the next top unanalysed drawdown candidate.
- Alternatives Considered: Keep manually selecting the next symbol from whichever pocket was most recently open in context, or continue probing `theme_q4` symbols one by one without a reusable ranking rule.
- Expected Benefits: Reduce selection drift in the drawdown-specialist loop and make the next candidate choice reproducible. This also avoids mistaking "same pocket, same family noise" for a fresh non-baseline family.
- Risks: The shortlist uses trade-count gap and pnl delta as a lightweight heuristic. It is a replay-priority tool, not a proof engine.
- Follow-up Actions: Treat `theme_q3 / 603799 / mainline_trend_c` as the next replay target unless a stronger carry-like candidate appears from a broader scan.

### DEC-0091

- Date: 2026-03-29
- Title: Reclassify `theme_q3 / 603799` as a mixed pocket and advance the shortlist to the next unanalysed driver
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_q3_symbol_timeline_603799_quality_c_v1, theme_q3_symbol_cycle_delta_603799_c_v1, theme_q3_nearby_cycle_bridge_603799_c_v1, theme_q3_cycle_mechanism_603799_c_v1, drawdown_family_candidate_shortlist_v3
- Context: After `drawdown_family_candidate_shortlist_v2` surfaced `theme_q3 / 603799 / mainline_trend_c` as the top unanalysed drawdown candidate, the repo needed to know whether that row was pointing to a reusable family or just another mixed pocket.
- Decision: Replay the full `603799` chain before expanding the family inventory. The result does not justify a new family. The pocket consists of one clean `entry_suppression_avoidance` row on `2024-08-01 -> 2024-08-02` and one toxic positive-cycle truncation on `2024-09-27 -> 2024-10-10`, recorded as `other_worse_loss_shift`. Because the symbol is mixed rather than clean, do not add it to the drawdown-family inventory. Instead, refresh the shortlist with `603799` excluded. The new top candidate is now `market_research_v0 / 2024_q4 / mainline_trend_c / 300750`.
- Alternatives Considered: Add `603799` to the family inventory as another baseline-style avoidance pocket, or keep replaying more `theme_q3` symbols before updating the shortlist.
- Expected Benefits: Preserve family inventory quality by excluding mixed pockets that would dilute the signal. Keep the next replay target grounded in a refreshed queue instead of in stale rankings.
- Risks: The refreshed shortlist still ranks by lightweight heuristics. `market_q4 / 300750` may turn out to be another mixed pocket rather than a clean reusable family.
- Follow-up Actions: Use `market_q4 / 300750 / mainline_trend_c` as the next replay target.

### DEC-0092

- Date: 2026-03-29
- Title: Reclassify `market_q4 / 300750` as another baseline-style avoidance pocket and rotate the replay queue again
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_q4_symbol_timeline_300750_quality_c_v1, market_q4_symbol_cycle_delta_300750_c_v1, market_q4_nearby_cycle_bridge_300750_c_v1, market_q4_cycle_mechanism_300750_c_v1, drawdown_family_candidate_shortlist_v4
- Context: After rejecting `theme_q3 / 603799` as a clean family case, the refreshed replay queue pointed to `market_research_v0 / 2024_q4 / mainline_trend_c / 300750` as the next best candidate. The remaining question was whether this row would strengthen a non-baseline family or merely add another baseline-style suppression case.
- Decision: Replay the full `market_q4 / 300750` chain before expanding the family inventory. The result is clean but not new: [market_q4_cycle_mechanism_300750_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_300750_c_v1.json) contains a single `entry_suppression_avoidance` row on `2024-10-22 -> 2024-10-23`, with no reduced-loss basis behavior. Because this is another baseline-style avoidance case rather than a non-baseline family reuse, do not add it as a new specialist-family target. Refresh the replay queue again. The new top candidate is now `baseline_research_v1 / 2024_q3 / mainline_trend_c / 000333`.
- Alternatives Considered: Add `market_q4 / 300750` to the non-baseline family search anyway because the pnl delta is large, or keep it at the top of the queue until a second symbol repeats `carry_in_basis_advantage`.
- Expected Benefits: Keep the next specialist loop focused on unanalysed structure instead of spending more budget on already-understood baseline-style avoidance.
- Risks: The queue still uses a heuristic shortlist, so the next leader can also turn out to be mixed.
- Follow-up Actions: Use `baseline_q3 / 000333 / mainline_trend_c` as the next replay target.

### DEC-0093

- Date: 2026-03-29
- Title: Reclassify `baseline_q3 / 000333 / C` as strong baseline-style reuse and rotate the replay queue again
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: baseline_q3_symbol_timeline_000333_quality_c_v1, baseline_q3_symbol_cycle_delta_000333_c_v1, baseline_q3_nearby_cycle_bridge_000333_c_v1, baseline_q3_cycle_mechanism_000333_c_v1, drawdown_family_candidate_shortlist_v5
- Context: After `drawdown_family_candidate_shortlist_v4` surfaced `baseline_research_v1 / 2024_q3 / mainline_trend_c / 000333` as the next replay target, the open question was whether this row would add any non-baseline family evidence or merely strengthen the already-known baseline-style drawdown template.
- Decision: Replay the full `000333 / C` chain before changing the family inventory. The result is useful but not new. [baseline_q3_cycle_mechanism_000333_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/baseline_q3_cycle_mechanism_000333_c_v1.json) is dominated by three `earlier_exit_loss_reduction` rows and two `entry_suppression_avoidance` rows, but it also carries two large positive-cycle degradations (`other_worse_loss_shift` on `2024-08-19 -> 2024-08-20` and `2024-09-25 -> 2024-10-09`). Because the pocket strengthens the baseline-style family without improving the non-baseline search frontier, do not add a new family label. Refresh the queue again with `000333` excluded. The next replay order is now tracked in `drawdown_family_candidate_shortlist_v5`.
- Alternatives Considered: Promote `000333 / C` into the family inventory as another baseline-style asset, or keep it near the front of the queue until a second replay confirmed the opportunity-cost rows were not dominant.
- Expected Benefits: Tighten the line between "evidence that raises family confidence" and "evidence that changes the family frontier." This keeps the drawdown loop from bloating inventory with increasingly familiar baseline-style cases.
- Risks: The refreshed shortlist can still surface mixed pockets. Excluding strong baseline-style reuse also means the next candidates will likely be weaker and noisier.
- Follow-up Actions: Use the new shortlist to select the next non-baseline-family candidate instead of continuing to replay baseline-Q3 variations.

### DEC-0094

- Date: 2026-03-29
- Title: Reclassify `market_q4 / 002371 / C` as a clean single-row baseline-style pocket and rotate the queue again
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_q4_symbol_timeline_002371_quality_c_v1, market_q4_symbol_cycle_delta_002371_c_v1, market_q4_nearby_cycle_bridge_002371_c_v1, market_q4_cycle_mechanism_002371_c_v1, drawdown_family_candidate_shortlist_v6
- Context: After excluding `baseline_q3 / 000333`, the refreshed shortlist elevated `market_research_v0 / 2024_q4 / mainline_trend_c / 002371` to the top. The question was whether this pocket would finally extend the non-baseline family frontier or simply give another clean baseline-style suppression row.
- Decision: Replay the full `002371 / C` chain before touching the inventory. The answer is clean but not new: [market_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_002371_c_v1.json) contains exactly one mechanism row, `entry_suppression_avoidance` on `2024-12-30 -> 2024-12-31`, with no reduced-loss basis behavior and no mixed-cycle baggage. Because it only reinforces the baseline-style family and does not change the non-baseline search frontier, exclude it and refresh the queue again through `drawdown_family_candidate_shortlist_v6`.
- Alternatives Considered: Keep `002371` near the top because it is one of the cleanest single-row pockets, or add it to the inventory as a separate "single-row baseline pocket" subtype.
- Expected Benefits: Maintain inventory discipline. Cleanness alone is not enough if the mechanism does not expand the usable family frontier.
- Risks: The next candidates may be noisier and more mixed, because many of the remaining clean high-delta rows are already baseline-style.
- Follow-up Actions: Take the next replay target from `drawdown_family_candidate_shortlist_v6` instead of extending the baseline-style catalogue.

### DEC-0095

- Date: 2026-03-29
- Title: Treat `theme_q2 / 002466 / C` as a mixed reinforcement pocket, not a new family asset
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_q2_symbol_timeline_002466_quality_c_v1, theme_q2_symbol_cycle_delta_002466_c_v1, theme_q2_nearby_cycle_bridge_002466_c_v1, theme_q2_cycle_mechanism_002466_c_v1, cycle_family_inventory_v3, drawdown_family_candidate_shortlist_v8
- Context: After `cycle_family_inventory_v3` promoted `preemptive_loss_avoidance_shift` to a second reuse case via `market_q4 / 000858`, the refreshed queue still pointed to `theme_research_v4 / 2024_q2 / mainline_trend_c / 002466` as a high-delta candidate. The open question was whether this row would add a cleaner non-baseline family or just reinforce several existing ones at once.
- Decision: Replay the full `theme_q2 / 002466 / C` chain before changing the inventory. The result is informative but mixed. [theme_q2_cycle_mechanism_002466_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q2_cycle_mechanism_002466_c_v1.json) combines:
  - one `preemptive_loss_avoidance_shift` on `2024-04-10 -> 2024-04-11`
  - two `entry_suppression_avoidance` rows on `2024-05-10 -> 2024-05-13` and `2024-06-27 -> 2024-06-28`
  - one positive `delayed_entry_basis_advantage` row on `2024-04-02 -> 2024-04-09`
  This broadens confidence in multiple existing mechanisms but does not justify a new clean family asset. Exclude it from the queue and rotate again via `drawdown_family_candidate_shortlist_v8`.
- Alternatives Considered: Promote the pocket as a second `preemptive_loss_avoidance_shift`-like asset on the theme line, or merge it into the family inventory despite being multi-family.
- Expected Benefits: Preserve family inventory discipline while still recording the pocket as evidence that multiple known families can co-exist in one tradable theme-Q2 sequence.
- Risks: Excluding multi-family pockets may understate how specialist alpha is achieved in real sequences, where families often stack rather than appear in isolation.
- Follow-up Actions: Keep the inventory clean, but note that `theme_q2 / 002466 / C` is an example of stacked family behavior. Use the refreshed queue for the next replay.

### DEC-0096

- Date: 2026-03-29
- Title: Treat `theme_q4 / 002902 / B-C` as a cross-strategy mixed pocket and rotate the replay queue again
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_q4_symbol_timeline_002902_quality_b_v1, theme_q4_symbol_cycle_delta_002902_b_v1, theme_q4_nearby_cycle_bridge_002902_b_v1, theme_q4_cycle_mechanism_002902_b_v1, theme_q4_symbol_timeline_002902_quality_c_v1, theme_q4_symbol_cycle_delta_002902_c_v1, theme_q4_nearby_cycle_bridge_002902_c_v1, theme_q4_cycle_mechanism_002902_c_v1, drawdown_family_candidate_shortlist_v9
- Context: After `drawdown_family_candidate_shortlist_v8` surfaced `theme_research_v4 / 2024_q4 / 002902` at the top on both `B/C`, the most valuable question was whether this symbol was a real cross-strategy reusable family or just another repeated mixed pocket.
- Decision: Replay both `B` and `C` before touching the inventory. The answer is clear: the negative-cycle map is identical across `mainline_trend_b` and `mainline_trend_c`, but the map is mixed rather than frontier-expanding. Both reports contain:
  - one `earlier_exit_loss_reduction` on `2024-10-31 -> 2024-11-04`
  - two `entry_suppression_avoidance` rows on `2024-11-29 -> 2024-12-02` and `2024-12-27 -> 2024-12-30`
  - one negative `other_worse_loss_shift` on `2024-10-23 -> 2024-10-28`
  This makes `002902` useful as cross-strategy mixed-pocket evidence, but not clean enough for family inventory promotion. Exclude both `B/C` rows and refresh the queue via `drawdown_family_candidate_shortlist_v9`.
- Alternatives Considered: Promote `002902` as another cross-strategy reusable drawdown asset because the negative-cycle map repeats exactly, or keep only one of `B/C` excluded and leave the other on the queue.
- Expected Benefits: Preserve the difference between "cross-strategy repeatability" and "clean family asset." This keeps the queue focused on frontier-changing evidence instead of repeated mixed pockets.
- Risks: The more mixed pockets are excluded, the more likely it becomes that the remaining shortlist mainly contains weaker or noisier cases.
- Follow-up Actions: Treat `002902` as a reusable mixed-pocket example, not as a promoted family. Continue from `drawdown_family_candidate_shortlist_v9`.

### DEC-0097

- Date: 2026-03-29
- Title: Reclassify `market_q4 / 603259 / C` as another clean single-row baseline-style pocket and rotate the replay queue again
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_q4_symbol_timeline_603259_quality_c_v1, market_q4_symbol_cycle_delta_603259_c_v1, market_q4_nearby_cycle_bridge_603259_c_v1, market_q4_cycle_mechanism_603259_c_v1, drawdown_family_candidate_shortlist_v10
- Context: After clearing `002902` as a cross-strategy mixed pocket, the next v9 shortlist leader was `market_research_v0 / 2024_q4 / mainline_trend_c / 603259`. The only real question was whether this symbol would add a non-baseline mechanism or simply provide one more clean baseline-style suppression case.
- Decision: Replay the full `603259 / C` chain before touching the inventory. The result is extremely clean but not new. [market_q4_cycle_mechanism_603259_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_q4_cycle_mechanism_603259_c_v1.json) contains exactly one `entry_suppression_avoidance` row on `2024-10-30 -> 2024-10-31`, with no reduced-loss basis behavior and no mixed baggage. Because it only strengthens the existing baseline-style family and does not extend the non-baseline frontier, exclude it and refresh the queue via `drawdown_family_candidate_shortlist_v10`.
- Alternatives Considered: Keep `603259` as a possible subtype case because it is exceptionally clean, or add it to the family inventory as a repeated single-row baseline-style pocket.
- Expected Benefits: Prevent the replay queue from turning into a catalogue of increasingly similar single-row avoidance examples.
- Risks: Removing yet another clean row means the remaining queue will tilt further toward noisier and weaker candidates.
- Follow-up Actions: Use `drawdown_family_candidate_shortlist_v10` for the next replay target rather than deepening baseline-style single-row cases.

### DEC-0098

- Date: 2026-03-29
- Title: Treat `theme_q4 / 603087 / B-C` as another cross-strategy single-row baseline-style case and rotate the queue again
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_q4_symbol_timeline_603087_quality_b_v1, theme_q4_symbol_cycle_delta_603087_b_v1, theme_q4_nearby_cycle_bridge_603087_b_v1, theme_q4_cycle_mechanism_603087_b_v1, theme_q4_symbol_timeline_603087_quality_c_v1, theme_q4_symbol_cycle_delta_603087_c_v1, theme_q4_nearby_cycle_bridge_603087_c_v1, theme_q4_cycle_mechanism_603087_c_v1, drawdown_family_candidate_shortlist_v11
- Context: After `603259` also collapsed into a clean single-row avoidance case, the next v10 shortlist leader was `theme_q4 / 603087`, and it appeared on both `B/C`. The remaining question was whether this repetition would at least yield a richer cross-strategy structure than the one-row market examples.
- Decision: Replay both `B` and `C` before changing the queue. The answer is no: both [theme_q4_cycle_mechanism_603087_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_b_v1.json) and [theme_q4_cycle_mechanism_603087_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/theme_q4_cycle_mechanism_603087_c_v1.json) contain only one `entry_suppression_avoidance` row, with no reduced-loss basis behavior and no mixed baggage. This makes `603087` useful only as another cross-strategy baseline-style confirmation, not as a frontier-changing family asset. Exclude both rows and refresh the queue again via `drawdown_family_candidate_shortlist_v11`.
- Alternatives Considered: Stop after replaying `B` only and leave `C` in the queue, or promote `603087` as a cross-strategy single-row subtype.
- Expected Benefits: Avoid spending future replay budget on a symbol whose `B/C` behavior is already fully explained by the baseline-style family.
- Risks: The queue is now visibly thinning, and the remaining rows are more likely to be weak, mixed, or feature-limited.
- Follow-up Actions: Use `drawdown_family_candidate_shortlist_v11` to judge whether the next step is another replay or a controlled stop.

### DEC-0099

- Date: 2026-03-29
- Title: Declare the specialist replay loop to be in a feature-limited thinning phase and switch the next cycle to `feature-pack-a`
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: specialist_feature_gap_audit_v1
- Context: After clearing several high-delta queue leaders, the replay loop was no longer discovering clean frontier-expanding drawdown families. The remaining pockets were increasingly collapsing into one-row baseline-style reuse or repeated mixed pockets. The open question was whether to keep extending the replay queue or to treat the current state as a controlled stop and shift the research budget into feature expansion.
- Decision: Run a formal feature-gap audit before replaying another queue leader. [specialist_feature_gap_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_feature_gap_audit_v1.json) shows:
  - `classification_counts = {mixed_existing_families: 4, single_row_baseline_reuse: 4, stacked_family_pocket: 1}`
  - `feature_gap_suspect_count = 2`
  - `thinning_signal = true`
  This is sufficient to declare that the current specialist replay loop has entered a `feature-limited thinning phase`. The next step is therefore **not** `drawdown_family_candidate_shortlist_v12`; it is a bounded `feature gap -> feature-pack-a -> replay recheck` cycle. The phase guardrails are formalized in [26_V11_SPECIALIST_ALPHA_GUARDRAILS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/26_V11_SPECIALIST_ALPHA_GUARDRAILS.md).
- Alternatives Considered: Continue replaying `drawdown_family_candidate_shortlist_v11` as if the queue were still likely to produce new reusable families, or stop the line entirely without a formal handoff into feature work.
- Expected Benefits: Prevent the specialist loop from turning into a high-quality infinite replay cycle. Focus the next research budget on the most plausible explanation for the current mixed and stacked pockets: insufficient feature expressiveness.
- Risks: The audit can only indicate likely feature limits, not prove that a new family exists. It is still possible that the next feature pack yields little change, in which case the correct conclusion may become negative completion rather than family discovery.
- Follow-up Actions: Start `feature-pack-a`, using the current suspects (`theme_q4 / 002902` and `theme_q2 / 002466`) as the primary recheck targets.

### DEC-0100

- Date: 2026-03-29
- Title: Constrain `feature-pack-a` to two suspect pockets and a small feature shortlist
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: specialist_feature_gap_audit_v1
- Context: Once the replay loop is declared feature-limited, the next risk is replacing one infinite loop with another by adding too many features at once. The phase needs a bounded first expansion pack, not a broad factor library.
- Decision: Define [27_FEATURE_PACK_A_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/27_FEATURE_PACK_A_PLAN.md) as the next execution boundary. `feature-pack-a` is limited to:
  - two recheck targets: `theme_q4 / 002902` and `theme_q2 / 002466`
  - a narrow feature shortlist covering theme/concept support, hierarchy margins, approval-edge state, and short cycle context
  - a hard exit rule: after the pack, either promote, reject, or define a similarly narrow `feature-pack-b`
- Alternatives Considered: Continue replaying pockets while opportunistically adding features, or design a much larger feature expansion cycle before any recheck.
- Expected Benefits: Keep the next phase falsifiable and inexpensive. If feature expansion helps, it should help on the current suspects first.
- Risks: The selected feature pack may still be too small to change the interpretation boundary, in which case the result will be a negative research outcome rather than a new family asset.
- Follow-up Actions: Implement the `feature-pack-a` fields and rerun the two suspect pockets before extending the replay queue again.

### DEC-0101

- Date: 2026-03-29
- Title: Treat `feature-pack-a` v1 as a successful diagnostic pass and keep the replay queue paused
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_research_derived_data_v5, feature_pack_a_recheck_v1
- Context: The first bounded feature-expansion cycle had one narrow job: determine whether the current suspect pockets were likely true noise, or whether the existing feature set was compressing real edge structure into mixed / stacked labels.
- Decision: Implement the first-pass snapshot fields and run a recheck before resuming any replay work. [feature_pack_a_recheck_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_recheck_v1.json) shows `8/8` mechanism rows landing on at least one explicit threshold edge. This is enough to say `feature-pack-a` succeeded as a diagnostic step. The queue stays paused. The next move is no longer "replay another symbol"; it is "decide whether hierarchy/approval refinement is justified by these newly visible edges."
- Alternatives Considered: Resume `drawdown_family_candidate_shortlist` immediately after generating the richer snapshots, or treat the recheck as inconclusive because it did not yet produce a new family.
- Expected Benefits: Convert "feature gap" from a suspicion into evidence. Preserve replay budget for later, after the current suspect pockets have been exploited fully.
- Risks: Edge visibility is not the same as strategy-worthiness. Some of these edges may still be too local to justify changing hierarchy or approval logic.
- Follow-up Actions: Use the recheck output to separate hierarchy-heavy suspects from approval-edge suspects and decide the narrowest possible refinement target.

### DEC-0102

- Date: 2026-03-29
- Title: Split post-`feature-pack-a` work into sequential hierarchy/approval and concept-supported hierarchy tracks
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_a_triage_v1, feature_pack_b_readiness_v1
- Context: `feature-pack-a` v1 proved that the two main suspect pockets are real threshold-edge cases, but it also showed that they are not the same type of problem. The next risk is treating "feature expansion" as one blended lane and adding too many features at once.
- Decision: Run a formal triage first, then convert it into an execution order. [feature_pack_a_triage_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_a_triage_v1.json) splits the current suspects into:
  - `theme_q4 / 002902 / B` -> `hierarchy_approval_edge`
  - `theme_q2 / 002466 / C` -> `concept_supported_hierarchy_edge`
  [feature_pack_b_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_readiness_v1.json) then fixes the order:
  1. `theme_q4 / 002902 / B`
  2. `theme_q2 / 002466 / C`
  This order is now formalized in [28_FEATURE_PACK_B_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/28_FEATURE_PACK_B_PLAN.md).
- Alternatives Considered: Start with the more feature-rich concept pocket first, or blend both suspects into one larger `feature-pack-b`.
- Expected Benefits: Keep the next refinement cycle falsifiable and sequential. The cleaner hierarchy/approval edge should answer whether a narrow feature-pack-b can move the interpretation boundary without needing concept-aware features first.
- Risks: Solving the cleaner track first may not change the second track at all, which would make the concept-supported lane still necessary.
- Follow-up Actions: Implement `feature_pack_b_hierarchy_approval` first, leaving the replay queue paused.

### DEC-0103

- Date: 2026-03-29
- Title: Start `feature_pack_b_hierarchy_approval` with `theme_q4 / 002902 / B` and treat it as a coupled late-quality plus score-margin edge
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_a_recheck_v1, feature_pack_b_hierarchy_approval_v1
- Context: After triage and readiness ordering, the first open question was whether `theme_q4 / 002902 / B` should be attacked as a pure hierarchy case, a pure approval case, or a coupled edge.
- Decision: Extend the recheck output with `challenger_margin_gap`, `fallback_reason_score`, and `margin_straddle`, then run a focused hierarchy/approval pass before opening the concept-supported lane. [feature_pack_b_hierarchy_approval_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_v1.json) now shows:
  - `dominant_hierarchy_edge = late_mover_quality`
  - `dominant_approval_edge = score_margin_threshold`
  - `late_quality_straddles = 3`
  - `margin_straddles = 2`
  - `permission_split_rows = 2`
  This is enough to treat `002902` as a coupled hierarchy-plus-approval edge, with hierarchy leading and approval threshold state as the secondary amplifier.
- Alternatives Considered: Treat the pocket as a pure approval problem because permission splits are visible, or defer track A until the concept-supported lane is also instrumented.
- Expected Benefits: Keep `feature-pack-b` narrow and causal. The first refinement can now target a precise coupled boundary instead of a vague "theme mixed pocket."
- Risks: Even this cleaner track may still end with a negative result, because visible edge structure does not guarantee strategy-worthiness.
- Follow-up Actions: Keep the replay queue paused. The next implementation step should refine the `002902` hierarchy/approval lane before touching `002466`.

### DEC-0104

- Date: 2026-03-29
- Title: Treat `002902` track A as a negative-but-informative result and do not promote its local repairs
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_b_hierarchy_approval_v1, feature_pack_b_hierarchy_approval_sweep_v1, feature_pack_b_hierarchy_approval_sweep_v2
- Context: Once `theme_q4 / 002902 / B` was identified as a coupled `late_mover_quality + score_margin_threshold` edge, the remaining question was whether a narrow local repair could improve the pocket cheaply enough to justify further hierarchy/approval refinement.
- Decision: Run two pocket-local sweeps before changing any branch-level defaults. The first sweep ([feature_pack_b_hierarchy_approval_sweep_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v1.json)) showed that `min_composite_for_non_junk=0.58` repaired the assignment side, while `min_score_margin=0.05` repaired nothing. The second sweep ([feature_pack_b_hierarchy_approval_sweep_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_hierarchy_approval_sweep_v2.json)) showed that more aggressive margin relief can repair the approval side, but only at clearly worse symbol-level PnL:
  - control: `-312.215`
  - `margin_relief_003`: `-177.915` with only `1` repair
  - `margin_relief_000`: `-447.645` with `2` permission repairs
  - `coupled_relief_000_058`: `-464.429` with all `4` trigger repairs
  This is enough to conclude that `002902` is a useful explanatory pocket, but not a cheap local repair worth promoting.
- Alternatives Considered: Keep tuning the approval threshold more finely, or keep the non-junk relief as a local specialist tweak.
- Expected Benefits: Prevent track A from becoming another threshold-grinding loop. Preserve the conclusion that visible edge structure does not automatically imply a strategy-worthy refinement.
- Risks: The pocket may still contain a better repair path that is not threshold-based, but that would be a different research question, not a reason to keep this sweep open.
- Follow-up Actions: Close track A as a negative-but-informative result and move the next feature budget to `002466`.

### DEC-0105

- Date: 2026-03-29
- Title: Treat `002466` as a concept-to-late-mover bridge candidate, not a concept-to-non-junk candidate
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_b_concept_supported_hierarchy_v1
- Context: After closing track A on `002902`, the next open question was how the concept-supported hierarchy lane should be scoped. `002466` had both late-quality and non-junk straddles, so the risk was reopening track B with two competing bridge hypotheses at once.
- Decision: Run a focused concept-supported hierarchy pass before any concept-aware sweep. [feature_pack_b_concept_supported_hierarchy_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_supported_hierarchy_v1.json) shows:
  - `late_quality_straddles = 2`
  - `non_junk_straddles = 2`
  - `concept_supported_late_rows = 2`
  - `concept_supported_non_junk_rows = 2`
  - `avg_challenger_late_quality_margin = -0.073479`
  - `avg_challenger_non_junk_margin = 0.029458`
  Even with equal row counts, the tighter negative margin is on the late-quality side. So the dominant bridge is `concept_to_late_mover`, not `concept_to_non_junk`.
- Alternatives Considered: Treat the pocket as symmetric and expand both concept-supported hierarchy bridges at once, or prioritize non-junk because its straddles are more directly tied to junk fallback.
- Expected Benefits: Keep track B as narrow as track A. The next concept-aware refinement can now focus on how concept support should help late-mover admission, without reopening a broader hierarchy redesign.
- Risks: The current judgment still comes from one pocket. A later pocket could still justify a concept-to-non-junk track, but that is not the default next move anymore.
- Follow-up Actions: Start the next concept-aware refinement as a `concept_to_late_mover` lane rather than a blended concept hierarchy pack.

### DEC-0106

- Date: 2026-03-29
- Title: Close `feature-pack-b` track B as a negative-but-informative concept-to-late result
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: concept_to_late_bridge_analysis_v1, theme_q2_symbol_timeline_002466_quality_c_v1, theme_q2_symbol_timeline_002466_quality_c_v2, theme_q2_symbol_timeline_002466_quality_c_v3, feature_pack_b_concept_late_validation_v1
- Context: After track B was narrowed to a `concept_to_late_mover` bridge, the remaining question was whether a concept-aware late-mover uplift could repair the key bridge rows without destroying the challenger alpha that made the pocket interesting in the first place.
- Decision: Treat track B as an acceptance problem, not an open-ended refinement lane. [feature_pack_b_concept_late_validation_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_b_concept_late_validation_v1.json) now shows:
  - baseline `v1` pnl delta: `536.724`
  - best tested variant (`v2`) pnl delta: `94.049`
  - best alpha-retention ratio: `0.175228`
  - repaired trigger completion: `1 / 2`
  Both tested variants repaired the `2024-05-09` row but failed to repair `2024-06-26`, while materially degrading the specialist challenger.
- Alternatives Considered: Continue widening the concept-support band, or reopen a more general concept-to-hierarchy track.
- Expected Benefits: Prevent track B from becoming a second bounded-but-endless local optimization loop. Preserve the conclusion that the pocket is real, but not cheaply promotable under the current feature set.
- Risks: A future feature pack with more local causal features could still reopen this pocket. Closing the track now should therefore be read as "negative under current features," not "impossible forever."
- Follow-up Actions: Keep replay queue paused. Any future revisit should start from a new feature-pack definition, not from wider concept-to-late parameter search.

### DEC-0107

- Date: 2026-03-29
- Title: Start `feature-pack-c` as a local-causal feature cycle and keep the replay queue paused
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: specialist_feature_gap_audit_v1, feature_pack_b_hierarchy_approval_v1, feature_pack_b_hierarchy_approval_sweep_v2, feature_pack_b_concept_supported_hierarchy_v1, feature_pack_b_concept_late_validation_v1, feature_pack_c_readiness_v1
- Context: `feature-pack-b` has now produced two negative-but-informative exits. The open question is no longer "which pocket should be replayed next," but "which local causal features are still missing from the two strongest feature-gap suspects."
- Decision: Do not restart the replay queue. Use [feature_pack_c_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_readiness_v1.json) as the phase gate into a new narrow feature cycle:
  - `recommended_next_phase = feature_pack_c_local_causal_edges`
  - `track_a_closed = true`
  - `track_b_closed = true`
  - `do_restart_replay_queue = false`
  The pack definition is now written in [29_FEATURE_PACK_C_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/29_FEATURE_PACK_C_PLAN.md).
- Alternatives Considered: Reopen replay queue with `drawdown_family_candidate_shortlist`, or continue widening the concept-to-late variants on `002466`.
- Expected Benefits: Keep `V1.1` out of a second replay loop and focus the next budget on local causal observability rather than broader thresholds.
- Risks: If the new feature pack still cannot move either suspect pocket, specialist refinement may need another controlled stop after `feature-pack-c`.
- Follow-up Actions: Implement only the four local-causal feature groups listed in the feature-pack-c plan before considering any replay restart.

### DEC-0108

- Date: 2026-03-29
- Title: Keep unsupervised learning as a report-only sidecar and start with lightweight geometry only
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_c_readiness_v1
- Context: After `feature-pack-b` closed, it became reasonable to ask whether current mixed pockets are partly caused by weak feature geometry rather than by missing replay work. But introducing a heavy unsupervised stack too early would risk turning the research system into another uncontrolled branch.
- Decision: Add [30_UNSUPERVISED_FEATURE_RELATION_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/30_UNSUPERVISED_FEATURE_RELATION_PLAN.md) and constrain unsupervised work to a report-only sidecar. The initial scope is:
  - correlation / redundancy structure
  - `numpy`-level PCA / axis summaries
  - small pocket-grouping experiments
  It is explicitly **not** allowed to emit buy/sell decisions or enter the signal chain directly.
- Alternatives Considered: Start a full sklearn-based unsupervised branch immediately, or avoid unsupervised work entirely.
- Expected Benefits: Allow feature-relation discovery without contaminating the mainline research protocol or overexpanding dependencies.
- Risks: Even a sidecar can become a taxonomy-justification loop if it does not change any feature-pack decision.
- Follow-up Actions: If unsupervised work is started, begin with `U1 lightweight geometry` only and keep it downstream of `feature-pack-c`.

### DEC-0109

- Date: 2026-03-29
- Title: Open `feature-pack-c` with fallback decomposition plus late-quality residuals, not with concept support
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_c_fallback_reason_analysis_v1
- Context: `feature-pack-c` started with four candidate feature groups, but the first task was to determine which local deficit type actually dominates the two strongest suspects (`002902` and `002466`).
- Decision: Use [feature_pack_c_fallback_reason_analysis_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_fallback_reason_analysis_v1.json) as the first pack-C gate. The report shows:
  - `dominant_component_counts = {late_quality: 6, score_margin: 2}`
  - `approval_edge_active_count = 2`
  - `concept_supported_count = 4`
  - `recommended_first_feature_group = fallback_reason_decomposition_plus_late_quality_residuals`
  Therefore the first real pack-C implementation should focus on `late_quality` residual structure, using approval and concept support only as secondary context.
- Alternatives Considered: Start with concept-support excess because `002466` is the more obviously concept-aware pocket, or start with approval-threshold history because `002902` had visible permission splits.
- Expected Benefits: Prevent pack-C from reopening another blended lane. The next feature work now has a clear hierarchy: late-quality first, approval/context second.
- Risks: A later read could still show that concept-support excess matters more than this first decomposition suggests, especially once more local residual features exist.
- Follow-up Actions: Implement the first pack-C feature group around fallback decomposition and late-quality residuals before touching approval history or concept-support excess.

### DEC-0110

- Date: 2026-03-29
- Title: Keep `feature-pack-c` inside the raw late-quality stack after the first residual read
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_research_derived_data_v5, feature_pack_c_late_quality_residuals_v1
- Context: After pack-C established that current suspect rows are mostly late-quality-dominant, the next uncertainty was whether residual structure would immediately push us back toward concept support or approval-edge history.
- Decision: Use [feature_pack_c_late_quality_residuals_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_late_quality_residuals_v1.json) as the second pack-C gate. The report shows:
  - `dominant_residual_component_counts = {stability: 3, liquidity: 3, sector_strength: 2}`
  - `concept_boost_active_count = 1`
  - `raw_below_threshold_count = 8`
  - `recommended_second_feature_group = late_quality_stability_liquidity_context`
  Therefore pack-C should continue by exposing local context around the raw `stability/liquidity` contributors, not by reopening generic concept or approval tuning.
- Alternatives Considered: Promote concept-support excess because `002466` still shows positive concept support, or reopen approval-threshold history because `002902` previously showed permission splits.
- Expected Benefits: Keep pack-C causal and narrow. The residual read now points to the raw late-quality stack itself, especially `stability/liquidity`, which is the smallest feature surface still capable of changing the suspect pockets.
- Risks: The current recommendation comes from only two suspect pockets. Later pack-C reads could still rebalance toward concept or approval context.
- Follow-up Actions: Implement component-context reads around raw late-quality contributors before starting any unsupervised sidecar or replay restart.

### DEC-0111

- Date: 2026-03-29
- Title: Narrow pack-C from generic stability/liquidity context to turnover-share-first context
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_research_derived_data_v5, feature_pack_c_late_quality_residuals_v1, feature_pack_c_stability_liquidity_context_v1
- Context: After pack-C showed the suspect rows were late-quality-driven, the next uncertainty was whether the best explanatory branch inside that raw stack should start from volatility, turnover-share, or a broader mixed context.
- Decision: Use [feature_pack_c_stability_liquidity_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_stability_liquidity_context_v1.json) as the third pack-C gate. The report shows:
  - `row_count = 6`
  - `local_context_counts = {turnover_share_led: 3, mixed_stability_liquidity: 3}`
  - `volatility_led = 0`
  - `recommended_third_feature_group = late_quality_turnover_share_context`
  Therefore pack-C should not open a volatility-first branch. The next explicit feature lane should be turnover-share context, with stability held as mixed residual context rather than a lead lane.
- Alternatives Considered: Open a volatility context pack because `stability` appeared tied for the largest residual component count, or keep the next step blended across all stability/liquidity subcomponents.
- Expected Benefits: Keep pack-C from widening again. The next explanatory step now has a single local-causal anchor: turnover-share.
- Risks: A later pocket could still surface a clean volatility-led row, so this should be read as a current-suspect decision, not a universal rule.
- Follow-up Actions: Implement turnover-share context before considering volatility packs or any unsupervised geometry branch.

### DEC-0112

- Date: 2026-03-29
- Title: Treat turnover-share as a split descriptive lane, not a simple attention deficit
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_research_derived_data_v5, feature_pack_c_stability_liquidity_context_v1, feature_pack_c_turnover_share_context_v1
- Context: After pack-C narrowed from generic late-quality residuals into turnover-share, the next uncertainty was whether the lane would collapse into a single causal branch such as broad attention deficit or sector-peer crowding.
- Decision: Use [feature_pack_c_turnover_share_context_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_turnover_share_context_v1.json) as the fourth pack-C gate. The report shows:
  - `row_count = 3`
  - `local_turnover_context_counts = {sector_peer_dominance: 1, balanced_share_weakness: 2}`
  - `broad_attention_deficit = 0`
  - `recommended_fourth_feature_group = late_quality_balanced_turnover_context`
  Therefore the turnover-share lane remains descriptive and split. `002466` supplies one clean sector-peer-dominance row, while `002902` stays a balanced-share weakness pocket rather than a simple attention-deficit case.
- Alternatives Considered: Promote a broad-attention branch because turnover-share looked weak on multiple rows, or treat the entire lane as sector-peer dominance because one row showed a large sector-share gap.
- Expected Benefits: Prevent pack-C from inventing a fake single-factor story. The turnover-share lane is now properly constrained to one clean subcase and one mixed subcase.
- Risks: A later suspect pocket could still reveal a stronger sector-peer or broad-attention pattern than the current three rows.
- Follow-up Actions: Keep pack-C local and descriptive. If refinement continues, start from balanced turnover weakness rather than from a generic attention-deficit hypothesis.

### DEC-0113

- Date: 2026-03-29
- Title: Close `feature-pack-c` as explanatory and do not widen the turnover lane further
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: theme_research_derived_data_v5, feature_pack_c_balanced_turnover_weakness_v1, feature_pack_c_acceptance_v1
- Context: After pack-C narrowed into turnover-share context, the remaining uncertainty was whether the two `002902` rows represented a reusable balanced-turnover weakness feature or just another descriptive dead end.
- Decision: Use [feature_pack_c_balanced_turnover_weakness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_balanced_turnover_weakness_v1.json) and [feature_pack_c_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_pack_c_acceptance_v1.json) as the pack-C closing gate. The reports show:
  - `balanced_weakness_counts = {singleton_sector_masking: 2, true_balanced_share_weakness: 0}`
  - `acceptance_posture = close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar`
  - `ready_for_u1_lightweight_geometry = true`
  Therefore pack-C should now be treated as an explanatory success: it clarified why the remaining suspect pockets stay blocked, but it did not justify another generic turnover or attention branch.
- Alternatives Considered: Continue widening the turnover-share lane, reopen replay queue, or start unsupervised work immediately without a closing gate.
- Expected Benefits: Avoid a second local-causal infinite loop and create a clean phase handoff into a bounded sidecar instead of another replay/tuning cycle.
- Risks: A later pocket could still expose a real balanced-turnover weakness feature. Closing pack-C now should therefore be read as "closed under current suspects and current feature set," not as a universal impossibility claim.
- Follow-up Actions: Keep replay queue paused and, if refinement continues, start only `U1 lightweight geometry` as a report-only sidecar.

### DEC-0114

- Date: 2026-03-29
- Title: Use `U1 lightweight geometry` only to separate suspect pockets, not to create a new blended feature branch
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: feature_pack_c_acceptance_v1, u1_lightweight_geometry_v1
- Context: After `feature-pack-c` closed as explanatory, the remaining question was whether a bounded unsupervised sidecar would actually change a feature-pack decision or simply restate known labels.
- Decision: Run the first `numpy`-only sidecar on the existing suspect rows and treat it as useful only if it changes the next-stage interpretation boundary. [u1_lightweight_geometry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u1_lightweight_geometry_v1.json) shows:
  - `case_centroid_distance = 4.080383`
  - `separation_reading = cases_geometrically_separable`
  - `pc1` dominated by concept-support geometry
  - `pc2` dominated by late-quality / resonance geometry
  This is enough to conclude that `002902` and `002466` should not be treated as one combined next-stage feature problem.
- Alternatives Considered: Stop after pack-C without any sidecar, or let unsupervised work expand immediately toward heavier clustering/embedding.
- Expected Benefits: Prove that a bounded sidecar can improve interpretation quality without contaminating the signal chain or creating a new open-ended branch.
- Risks: The current result comes from only two suspect pockets. It improves local phase control, but does not justify a broad unsupervised expansion by itself.
- Follow-up Actions: Keep U1 bounded. Do not open a blended `feature-pack-d`; only continue unsupervised work if a larger suspect set appears or if U2 clustering would change a real feature-pack decision.

### DEC-0115

- Date: 2026-03-29
- Title: Hold `U2 pocket clustering` until a larger or less separable suspect set appears
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: specialist_feature_gap_audit_v1, feature_pack_c_acceptance_v1, u1_lightweight_geometry_v1, u2_pocket_clustering_readiness_v1
- Context: After `feature-pack-c` closed and `U1` separated the two current suspects, the next risk was opening clustering simply because a sidecar tool exists, not because clustering is decision-relevant.
- Decision: Add a readiness gate and require `U2` to start only when the suspect set is materially larger and still blended enough that clustering could change the next feature-pack decision. [u2_pocket_clustering_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/u2_pocket_clustering_readiness_v1.json) shows:
  - `suspect_count = 2`
  - `u1_cases_geometrically_separable = true`
  - `u2_ready = false`
  - `recommended_next_phase = hold_u2_and_wait_for_larger_or_less_separable_suspect_set`
- Alternatives Considered: Open clustering immediately after a successful U1 run, or stop all sidecar work without a formal U2 gate.
- Expected Benefits: Keep the unsupervised sidecar bounded and prevent "tool availability" from becoming a new refinement loop.
- Risks: A future larger suspect batch could justify U2, so this is a parking decision, not a permanent ban.
- Follow-up Actions: Leave U2 parked until a new suspect batch changes the readiness conditions.

### DEC-0116

- Date: 2026-03-29
- Title: Treat `market_research_v1` as the next broad substrate and require full pack completion before reuse
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_research_v1_free_data_bootstrap, market_research_v1_sector_mapping, market_research_concept_mapping_v1, market_research_derived_data_v1, market_research_data_audit_v1, 20260329T111733Z_3e700662
- Context: After `feature-pack-c` closed and `U1`/`U2` established a stop condition for specialist refinement, the repo needed a broader but still controlled source of future suspect pockets. `market_research_v1` had already been planned, but not yet promoted from substrate idea to runnable research pack.
- Decision: Complete `market_research_v1` through the full pack chain before treating it as a usable next-stage substrate. This cycle is now complete:
  - raw `daily_bars`: `9670` rows across `40` symbols
  - `concept_mapping_daily`: `16679` rows across `26` symbols
  - `sector_snapshots`: `5467` rows across `35` sectors
  - `mainline_windows`: `70`
  - audit summary in [market_research_data_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v1.json):
    - `canonical_ready_count = 6`
    - `canonical_partial_count = 0`
    - `derived_ready_count = 3`
    - `baseline_ready = true`
  - suite summary in [20260329T111733Z_3e700662_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T111733Z_3e700662_comparison.json):
    - `mainline_trend_c` is best on total return and capture
    - `mainline_trend_a` remains lowest drawdown
- Alternatives Considered: Reopen replay queue immediately using the older packs, or wait for a much larger market pack before validating whether `market_research_v1` is already operational.
- Expected Benefits: Create a broader, cleaner substrate for future suspect generation without prematurely treating it as a new default-validation pack.
- Risks: `market_research_v1` may still overrepresent already-known liquid names, so it should be read as a controlled expansion pack rather than a market-wide truth surface.
- Follow-up Actions: Use `market_research_v1` as the next candidate source only after a new suspect batch actually appears. Keep replay queue paused and `U2` parked until that happens.

### DEC-0117

- Date: 2026-03-29
- Title: Use `market_research_v1` as the next suspect-generating pack, not as a new validation default
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: 20260329T112015Z_d5db1be9, specialist_alpha_analysis_v2
- Context: After `market_research_v1` became runnable, the next question was whether it only replicated existing broad conclusions or whether it actually produced new specialist opportunity structure.
- Decision: Run a fresh three-pack time-slice validation with `market_research_v1` replacing `market_research_v0`, then update specialist analysis on top of that report. The results show:
  - [20260329T112015Z_d5db1be9_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T112015Z_d5db1be9_comparison.json)
    still ranks `buffer_only_012` as the broad stability leader
  - [specialist_alpha_analysis_v2.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v2.json)
    identifies the best new drawdown-specialist pocket as
    `market_research_v1 / 2024_q3 / mainline_trend_c`
    and the strongest new capture-specialist pockets as
    `market_research_v1 / 2024_q2 / mainline_trend_a|b|c`
  Therefore `market_research_v1` should now be treated as the next suspect-generating pack, while the official shared-default freeze remains unchanged.
- Alternatives Considered: Keep using `market_research_v0` as the main broad expansion pack, or immediately reopen replay queue without first confirming that `market_research_v1` changes specialist opportunity geography.
- Expected Benefits: Shift the next research loop onto a broader and fresher substrate without confusing that move with a change in the frozen default stack.
- Risks: Some of the new `market_research_v1` pockets may still collapse back into existing baseline-style families; their existence alone is not proof of new assets.
- Follow-up Actions: Keep `U2` parked, but use `market_research_v1` as the first source when the next specialist suspect batch is reopened.

### DEC-0118

- Date: 2026-03-29
- Title: Treat `market_research_v1 / 2024_q3 / mainline_trend_c / 300308` as clean baseline-style family reuse, not as a new drawdown family
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q3_trade_divergence_quality_c_v1, market_v1_q3_symbol_timeline_300308_quality_c_v1, market_v1_q3_symbol_cycle_delta_300308_c_v1, market_v1_q3_nearby_cycle_bridge_300308_c_v1, market_v1_q3_cycle_mechanism_300308_c_v1
- Context: After `market_research_v1` revealed a new drawdown-specialist pocket at `2024_q3 / mainline_trend_c`, the first question was whether it represented a genuinely new family or just a broader-pack reuse of the older baseline-style drawdown mechanisms.
- Decision: Replay the dominant positive symbol `300308` through the full cycle chain and classify the resulting mechanism map. The result is clean:
  - [market_v1_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_c_v1.json) identifies `300308` as the strongest positive driver with `pnl_delta = 1781.321`
  - [market_v1_q3_cycle_mechanism_300308_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_c_v1.json) shows:
    - `2` rows of `entry_suppression_avoidance`
    - `1` row of `earlier_exit_loss_reduction`
    - `0` worsened rows
  Therefore this pocket should be treated as clean reuse of the established baseline-style drawdown family rather than as a new non-baseline family.
- Alternatives Considered: Leave the pocket at trade-divergence level only, or prematurely elevate it into a new market-v1 family because the symbol-level pnl delta is large.
- Expected Benefits: Strengthen confidence that `market_research_v1` is producing interpretable suspect pockets, not just noisier variants of earlier results.
- Risks: Other `market_research_v1` pockets may still reveal non-baseline families later; this decision only classifies the first dominant q3 example.
- Follow-up Actions: Keep using `market_research_v1` for new suspects, but score future q3/q4 pockets against the current family inventory before creating any new family label.

### DEC-0119

- Date: 2026-03-29
- Title: Classify `market_research_v1 / 2024_q2 / mainline_trend_c / 300502` as a persistence-driven capture edge
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q2_trade_divergence_capture_c_v1, market_v1_q2_symbol_timeline_300502_capture_c_v1, market_v1_q2_specialist_window_persistence_300502_v1
- Context: After `market_research_v1` revealed new capture-specialist pockets in `2024_q2`, the first question was whether the strongest symbol-level edge came from specialist opening behavior or from specialist persistence after a shared entry.
- Decision: Replay the dominant symbol `300502` against the strongest broad anchor and then classify the resulting window through the specialist persistence analyzer. The result is:
  - [market_v1_q2_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_trade_divergence_capture_c_v1.json) identifies `300502` as the largest positive symbol with `pnl_delta = 467.532`
  - [market_v1_q2_specialist_window_persistence_300502_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_persistence_300502_v1.json) shows:
    - specialist persistence on `2024-06-17`
    - both broad anchors exit on the same date with `assignment_became_junk`
    - specialist remains `late_mover` with `structure_intact`
  Therefore this pocket should be treated as a persistence edge, not as an opening edge.
- Alternatives Considered: Treat the q2 capture pocket as another opening-family case by default, or defer all classification until more q2 symbols were replayed.
- Expected Benefits: Add a cleaner market-v1 capture mechanism to the current taxonomy and avoid overgeneralizing all capture pockets into opening-only stories.
- Risks: Additional q2 symbols may still show opening-family behavior, so this result classifies the dominant symbol rather than the whole slice.
- Follow-up Actions: Continue q2 replay only if needed, but evaluate later symbols against this new persistence interpretation before assuming they belong to an opening family.

### DEC-0120

- Date: 2026-03-29
- Title: Freeze the current `V1.1` boundary with a stage review before replaying more `market_research_v1` symbols
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_research_data_audit_v1, 20260329T111733Z_3e700662, 20260329T112015Z_d5db1be9, specialist_alpha_analysis_v2, market_v1_q3_cycle_mechanism_300308_c_v1, market_v1_q2_specialist_window_persistence_300502_v1
- Context: After `market_research_v1` became operational and immediately started producing interpretable specialist pockets, the next risk was letting replay pace outrun phase definition.
- Decision: Add a formal stage review and treat the current state as a phase-boundary clarification, not just another run of journal notes. The review fixes these conclusions:
  - `market_research_v1` is now the next official suspect-generating substrate
  - broad freeze remains unchanged
  - current new output shape is "new pockets + clean reuse + persistence edge"
  - the repo should continue specialist work only through narrow, mechanism-first replay
- Alternatives Considered: Continue directly to the next symbol replay and let stage meaning remain implicit in logs and recent reports.
- Expected Benefits: Prevent a high-quality replay loop from slowly turning back into uncontrolled queue expansion.
- Risks: A later symbol could still materially change the stage boundary, so this review should be updated rather than treated as immutable.
- Follow-up Actions: Use [32_V11_STAGE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/32_V11_STAGE_REVIEW.md) as the current phase boundary before any further `market_research_v1` specialist continuation.

### DEC-0121

- Date: 2026-03-29
- Title: Update the q2 market-v1 capture reading from "possibly persistence-led" to "mixed opening plus persistence"
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q2_trade_divergence_capture_c_v1, market_v1_q2_symbol_timeline_300502_capture_c_v1, market_v1_q2_specialist_window_persistence_300502_v1, market_v1_q2_symbol_timeline_002371_capture_c_v1, market_v1_q2_specialist_window_opening_002371_v1
- Context: After `300502` was classified as a persistence edge, the q2 capture slice still risked being over-compressed into one persistence-led story.
- Decision: Replay the next strongest q2 capture symbol `002371` before treating the slice as understood. [market_v1_q2_specialist_window_opening_002371_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_specialist_window_opening_002371_v1.json) shows a clean opening edge:
  - specialist opens on `2024-06-05`
  - both anchors already share permission, filters, and entry triggers
  - both anchors remain `junk`, while specialist upgrades to `late_mover`
  Therefore the q2 market-v1 capture slice should now be treated as mixed:
  one clean persistence edge (`300502`) plus one clean opening edge (`002371`).
- Alternatives Considered: Keep using `300502` as the sole representative q2 capture example, or continue replaying more q2 symbols before acknowledging the slice has already diversified into two capture mechanisms.
- Expected Benefits: Prevent a premature and overly narrow q2 slice narrative; keep the stage review honest.
- Risks: Additional q2 symbols may still refine the proportions between opening and persistence, but the slice is no longer safely described as persistence-only.
- Follow-up Actions: Use the mixed q2 reading in the stage review, and continue only if another q2 symbol would materially change the mechanism boundary again.

### DEC-0122

- Date: 2026-03-29
- Title: Close the current `market_research_v1 / 2024_q2 / mainline_trend_c` slice as a mixed capture pocket
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q2_trade_divergence_capture_c_v1, market_v1_q2_specialist_window_persistence_300502_v1, market_v1_q2_specialist_window_opening_002371_v1, market_v1_q2_capture_slice_acceptance_v1
- Context: After `300502` established a persistence edge and `002371` established an opening edge, the open question was whether q2 still needed symbol-by-symbol continuation or whether the slice had already changed the stage boundary enough to stop.
- Decision: Add a dedicated q2 slice acceptance gate rather than continuing by momentum. [market_v1_q2_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q2_capture_slice_acceptance_v1.json) shows:
  - `acceptance_posture = close_market_q2_capture_slice_as_mixed_opening_plus_persistence`
  - `top_positive_symbols = [300502, 002371, 603259]`
  - `mixed_mechanism_confirmed = true`
  - `do_continue_q2_capture_replay = false`
  Therefore the current q2 slice is now closed at the slice level.
- Alternatives Considered: Continue replaying the third q2 symbol immediately, or leave the stop decision implicit in the stage review prose.
- Expected Benefits: Keep the current specialist continuation narrow and economical; prevent the q2 line from turning into another high-quality replay loop after its mechanism boundary is already known.
- Risks: A later q2 symbol could still add a third mechanism, but that should now require explicit reason to reopen rather than default continuation.
- Follow-up Actions: Shift future attention to a different market-v1 slice unless a strong reason emerges to reopen q2 specifically.

### DEC-0123

- Date: 2026-03-29
- Title: Close `market_research_v1 / 2024_q3` as a cross-strategy baseline-style drawdown slice
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q3_trade_divergence_quality_b_v1, market_v1_q3_symbol_timeline_300308_quality_b_v1, market_v1_q3_symbol_cycle_delta_300308_b_v1, market_v1_q3_nearby_cycle_bridge_300308_b_v1, market_v1_q3_cycle_mechanism_300308_b_v1, market_v1_q3_cross_strategy_cycle_consistency_v1, market_v1_q3_drawdown_slice_acceptance_v1
- Context: After q3/C had already been classified as a clean baseline-style reuse, the remaining open question was whether q3 should stay open for more replay or be closed at slice level once q3/B was checked.
- Decision: Replay the same dominant q3 symbol `300308` through the full q3/B chain and then add a dedicated q3 drawdown slice acceptance gate. The new evidence shows:
  - [market_v1_q3_trade_divergence_quality_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_trade_divergence_quality_b_v1.json) again identifies `300308` as the dominant positive symbol
  - [market_v1_q3_cycle_mechanism_300308_b_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cycle_mechanism_300308_b_v1.json) matches the same baseline-style drawdown template already seen in q3/C
  - [market_v1_q3_cross_strategy_cycle_consistency_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_cross_strategy_cycle_consistency_v1.json) confirms `identical_negative_cycle_map = true`
  - [market_v1_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q3_drawdown_slice_acceptance_v1.json) concludes:
    - `close_market_q3_drawdown_slice_as_cross_strategy_baseline_style_reuse`
    - `shared_top_driver = 300308`
    - `do_continue_q3_drawdown_replay = false`
  Therefore q3 should now be treated as closed at slice level under the current family inventory.
- Alternatives Considered: Leave q3 in an implicitly open state and keep replaying more q3 symbols, or record q3/B only as another isolated case without a stop gate.
- Expected Benefits: Prevent q3 from turning into another high-quality replay loop after its cross-strategy structure is already known.
- Risks: A future q3 suspect could still challenge this closure, but it should now require explicit reason to reopen rather than momentum.
- Follow-up Actions: Move specialist continuation to other market-v1 slices unless a later q3 symbol is expected to break the current cross-strategy map.

### DEC-0124

- Date: 2026-03-29
- Title: Treat the first `market_research_v1 / 2024_q4 / mainline_trend_c` replay as a novelty-lowering read, not a new family frontier
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q4_trade_divergence_quality_c_v1, market_v1_q4_symbol_timeline_002371_quality_c_v1, market_v1_q4_symbol_cycle_delta_002371_c_v1, market_v1_q4_nearby_cycle_bridge_002371_c_v1, market_v1_q4_cycle_mechanism_002371_c_v1
- Context: After q2 and q3 were both closed at slice level, q4 became the next market-v1 slice most likely to change the current specialist-stage conclusion.
- Decision: Replay only the top positive q4/C driver `002371` before deciding whether q4 deserves wider continuation. The result is:
  - [market_v1_q4_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_trade_divergence_quality_c_v1.json) identifies `002371` as the dominant positive symbol with `pnl_delta = 1509.5429`
  - [market_v1_q4_cycle_mechanism_002371_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_002371_c_v1.json) shows the mechanism is only a single-row `entry_suppression_avoidance`
  Therefore the first q4 replay should be treated as a novelty-lowering read: q4 remains open, but its leading symbol does not expand the family boundary.
- Alternatives Considered: Immediately keep replaying deeper into q4 by momentum, or prematurely close q4 after one symbol.
- Expected Benefits: Keep q4 continuation honest and stage-aware: one strong q4 symbol is enough to reduce novelty expectations, but not enough to close the slice.
- Risks: A later q4 symbol may still reveal a cleaner non-baseline family, so this decision deliberately keeps q4 open.
- Follow-up Actions: If q4 continues, prioritize the next strongest symbol only if it still has potential to change the current stage boundary.

### DEC-0125

- Date: 2026-03-29
- Title: Close `market_research_v1 / 2024_q4` as a mixed drawdown slice after the second strong symbol
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: market_v1_q4_trade_divergence_quality_c_v1, market_v1_q4_cycle_mechanism_002371_c_v1, market_v1_q4_symbol_timeline_000977_quality_c_v1, market_v1_q4_symbol_cycle_delta_000977_c_v1, market_v1_q4_nearby_cycle_bridge_000977_c_v1, market_v1_q4_cycle_mechanism_000977_c_v1, market_v1_q4_drawdown_slice_acceptance_v1
- Context: After the first q4 symbol only produced a single-row `entry_suppression_avoidance`, q4 remained open but with lower novelty prior. The next question was whether the second strong q4 symbol could still widen the slice-level reading.
- Decision: Replay `000977` as the next strongest q4/C symbol and then add a dedicated q4 drawdown slice acceptance gate. The new evidence shows:
  - [market_v1_q4_cycle_mechanism_000977_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_cycle_mechanism_000977_c_v1.json) adds reduced-loss structure:
    - `preemptive_loss_avoidance_shift`
    - `earlier_exit_loss_reduction`
  - [market_v1_q4_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v1_q4_drawdown_slice_acceptance_v1.json) concludes:
    - `close_market_q4_drawdown_slice_as_avoidance_plus_reduced_loss_mix`
    - `top_positive_symbols = [002371, 000977, 000858]`
    - `do_continue_q4_drawdown_replay = false`
  Therefore q4 should now be treated as a bounded mixed drawdown slice rather than an open replay lane.
- Alternatives Considered: Keep q4 open for a third symbol immediately, or treat q4 as still too weak to classify after only one reduced-loss case.
- Expected Benefits: Prevent q4 from turning into another drift-prone replay line once its slice-level mechanism boundary is already known.
- Risks: A later q4 symbol could still add more nuance, but it should now require explicit reason to reopen rather than queue momentum.
- Follow-up Actions: Move specialist continuation away from q4 unless a later q4 candidate is expected to challenge the current mixed-slice verdict.

### DEC-0126

- Date: 2026-03-29
- Title: Start sector/theme conditioning before any per-sector training
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: sector_theme_context_audit_v1
- Context: After `market_research_v1` q2/q3/q4 were all closed at slice level, the next question was whether specialist continuation should move directly into board-specific modeling.
- Decision: Add a report-only sector/theme context audit first. [sector_theme_context_audit_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/sector_theme_context_audit_v1.json) shows:
  - `recommended_first_conditional_feature_group = theme_load_plus_turnover_concentration_context`
  - `recommended_second_conditional_feature_group = sector_state_heat_breadth_context`
  - `do_sector_specific_training_now = false`
  Therefore the next refinement step should add conditional context features instead of splitting the strategy into per-sector models.
- Alternatives Considered: Start per-sector training immediately, or continue specialist replay without adding state context.
- Expected Benefits: Keep the next refinement branch narrow, interpretable, and aligned with current slice evidence.
- Risks: Slice-level separation still does not prove that any future grouped model should outperform a conditioned global model.
- Follow-up Actions: Build the next context feature branch around theme load plus turnover concentration first.

### DEC-0127

- Date: 2026-03-29
- Title: Validate the first context branch as conditioned late-quality on theme-turnover state
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: context_feature_pack_a_v1
- Context: After the sector/theme context audit established that board-specific training was premature, the next question was whether explicit context fields could support a narrow first branch rather than remain only a report-level intuition.
- Decision: Add explicit context fields to `StockSnapshot` and validate them on the already-closed `market_research_v1` slices. [context_feature_pack_a_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_v1.json) shows:
  - `bucket_counts = {interaction_high: 1, sector_heat_led: 1, turnover_led_theme_light: 1}`
  - `interaction_spread = 0.179943`
  - `heat_spread = 0.126929`
  - `breadth_spread = 0.005463`
  - `recommended_next_feature_branch = conditioned_late_quality_on_theme_turnover_context`
  - `defer_sector_heat_branch = true`
  Therefore the first conditional context branch should be theme-turnover conditioned late-quality, while the heat/breadth branch stays deferred.
- Alternatives Considered: Keep context purely at report level, or jump directly into sector heat/breadth conditioning.
- Expected Benefits: Convert the context conclusion into reusable fields and a narrow next branch without opening per-sector modeling.
- Risks: Slice-level separation still does not guarantee that the conditioned branch will improve promotion-relevant behavior.
- Follow-up Actions: Start the next refinement branch on `conditioned_late_quality_on_theme_turnover_context`.

### DEC-0128

- Date: 2026-03-29
- Title: Close the first context-conditioned hierarchy branch as non-material
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: context_feature_pack_a_conditioned_late_quality_v1, 20260329T122538Z_a98eb978, 20260329T122501Z_40f2a08a, context_feature_pack_a_conditioned_late_quality_acceptance_v1
- Context: After `context_feature_pack_a_v1` pointed to `conditioned_late_quality_on_theme_turnover_context`, the next question was whether a bounded hierarchy experiment could turn that explanatory context signal into a kept strategy rule.
- Decision: Run one default-off hierarchy experiment on `market_research_v1` with small late-quality relief only in `mid/high` interaction buckets, then compare it against the current control suite. The evidence now says:
  - [context_feature_pack_a_conditioned_late_quality_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_v1.json) shows `17` candidate rows, all inside `interaction_high` or `interaction_mid`, and only in `2024_q2` / `2024_q4`
  - [context_feature_pack_a_conditioned_late_quality_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_a_conditioned_late_quality_acceptance_v1.json) concludes:
    - `acceptance_posture = close_conditioned_late_quality_branch_as_non_material`
    - `material_improvement_count = 0`
    - `harmed_strategy_count = 1`
    - `do_promote_conditioned_branch = false`
  Therefore this branch should stay as explanatory context evidence, not as a retained hierarchy rule.
- Alternatives Considered: Keep tuning the conditioned late-quality relief values, or widen the branch into a broader context-conditioned hierarchy rewrite.
- Expected Benefits: Preserve the sector/theme context insight without opening another drift-prone tuning line or confusing explanation with retained alpha.
- Risks: A later larger suspect batch could still make this context axis worth revisiting in a more local form.
- Follow-up Actions: Keep sector/theme context as analysis, not per-sector training and not a kept hierarchy branch, unless a later suspect set materially changes the acceptance posture.

### DEC-0129

- Date: 2026-03-29
- Title: Close the deferred sector-heat/breadth branch as sparse
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: context_feature_pack_b_sector_heat_breadth_v1
- Context: After the first context branch was closed as non-material, the remaining question was whether the deferred `sector_state_heat_breadth_context` branch still had enough repeated near-threshold misses to justify a second bounded rule path.
- Decision: Run a report-only audit over the already-closed `market_research_v1` q2/q3/q4 slices before any rule experiment. [context_feature_pack_b_sector_heat_breadth_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/context_feature_pack_b_sector_heat_breadth_v1.json) shows:
  - `candidate_row_count = 1`
  - `candidate_slice_names = ['2024_q4']`
  - the only surviving candidate is `000977` on `2024-10-24`
  - `recommended_posture = close_sector_heat_breadth_context_branch_as_sparse`
  - `do_continue_context_feature_pack_b = false`
  Therefore the deferred heat/breadth line should remain explanatory only and should not open a retained hierarchy rule or a per-sector training path.
- Alternatives Considered: Open a bounded heat/breadth-conditioned non-junk experiment anyway, or restart a wider suspect replay to search for more heat/breadth examples first.
- Expected Benefits: Preserve stop-rule discipline and prevent a sparse context branch from turning into another tuning loop.
- Risks: A future larger suspect batch could still make heat/breadth context materially more reusable than it appears now.
- Follow-up Actions: Keep sector/theme context at the analysis layer and reopen heat/breadth work only if a later batch produces multi-slice support.

### DEC-0130

- Date: 2026-03-29
- Title: Pause the current V1.1 specialist loop and prepare a new suspect batch
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: v11_continuation_readiness_v1
- Context: After q2/q3/q4 market-v1 slices were all closed, the first context branch was closed as non-material, the second was closed as sparse, and U2 clustering remained not ready, the remaining question was whether the repo still had any justified continuation lane inside the current specialist batch.
- Decision: Add an explicit continuation readiness gate before allowing more local replay. [v11_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v11_continuation_readiness_v1.json) concludes:
  - `all_market_v1_slices_closed = true`
  - `all_context_branches_closed = true`
  - `u2_ready = false`
  - `recommended_next_phase = pause_specialist_refinement_and_prepare_new_suspect_batch`
  Therefore the current specialist loop should stop here instead of inventing another continuation lane inside the same closed geography.
- Alternatives Considered: Keep replaying marginal market-v1 symbols, reopen context-conditioned rule tuning, or open U2 pocket clustering early.
- Expected Benefits: Preserve the stage boundary, avoid replay drift, and redirect effort toward a materially different next suspect batch.
- Risks: A later reader could mistake "pause current loop" for "stop specialist research forever"; the intended meaning is narrower and should stay tied to the current batch only.
- Follow-up Actions: Treat the next productive move as suspect-batch preparation rather than local replay continuation.

### DEC-0131

- Date: 2026-03-29
- Title: Design the next suspect batch by missing context archetypes, not random expansion
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: next_suspect_batch_design_v1
- Context: Once the current specialist loop is paused, the next risk is expanding `market_research_v2` as a random larger watchlist instead of a decision-boundary-driven batch.
- Decision: Add an explicit batch-design report before creating the next seed universe. [next_suspect_batch_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_design_v1.json) concludes:
  - `recommended_next_batch_name = market_research_v2_seed`
  - `recommended_batch_posture = expand_by_missing_context_archetypes`
  - current missing archetypes:
    - `theme_loaded + balanced_turnover + broad_sector`
    - `theme_loaded + balanced_turnover + narrow_sector`
    - `theme_light + concentrated_turnover + broad_sector`
  Therefore the next batch should target those missing environments rather than just add more names from already-observed geometry.
- Alternatives Considered: Reopen local replay, add a random larger market watchlist, or jump straight to per-sector buckets.
- Expected Benefits: Keep the next batch auditable, tied to actual context gaps, and less likely to dilute the specialist line with random sample growth.
- Risks: The current archetype grid is still derived from a small number of closed slices and may need revision once the next batch is actually built.
- Follow-up Actions: Build `market_research_v2_seed` conservatively and map each new symbol to one intended missing archetype.

### DEC-0132

- Date: 2026-03-29
- Title: Approve the first market_research_v2_seed manifest for bootstrap
- Status: accepted
- Related Protocol Version: protocol_v1.1
- Related Runs: next_suspect_batch_manifest_v1
- Context: After fixing the missing-archetype design rule, the next question was whether the first concrete `market_research_v2_seed` universe was clean enough to become the next bootstrap substrate.
- Decision: Add a manifest audit before any new free-data expansion. [next_suspect_batch_manifest_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v1.json) shows:
  - `seed_universe_count = 9`
  - `new_symbol_count = 9`
  - `overlap_with_market_v1_count = 0`
  - `missing_archetype_count = 0`
  - `ready_to_bootstrap_market_research_v2_seed = true`
  Therefore the first seed universe is clean enough to use as the next controlled bootstrap batch.
- Alternatives Considered: Keep the v2 batch at design-only status, or expand the seed further before any bootstrap.
- Expected Benefits: Move from abstract next-phase planning to an auditable concrete seed without reopening random sample growth.
- Risks: The intended archetype labels remain hypotheses until the v2 seed is actually bootstrapped and audited on real data.
- Follow-up Actions: Bootstrap `market_research_v2_seed` rather than reopen replay or add more ad hoc symbols.
## DEC-0133 Market Research v2 Seed Is Runnable but Secondary

Date: 2026-03-29

Decision:

Treat `market_research_v2_seed` as a real runnable research pack and an active
secondary specialist substrate, but do not elevate it above
`market_research_v1` in the current `V1.1` hierarchy.

Why:

1. The seed pack now audits as `baseline_ready=true`.
2. It already produces interpretable A/B/C separation.
3. The first four-pack validation keeps broad freeze unchanged.
4. The first specialist read shows real pockets, but not a stage-rewriting wave.

Evidence:

- [market_research_data_audit_v2_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_seed.json)
- [20260329T130402Z_0e1d8809_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130402Z_0e1d8809_comparison.json)
- [20260329T130537Z_f0a9da05_comparison.json](D:/Creativity/A-Share-Quant_TrY/reports/20260329T130537Z_f0a9da05_comparison.json)
- [specialist_alpha_analysis_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v3.json)

## DEC-0134 Treat The First v2 Seed Q4 Capture Read As Mixed

Date: 2026-03-29

Decision:

Treat `market_research_v2_seed / 2024_q4 / mainline_trend_c` as a mixed
opening-plus-carry pocket rather than a clean new family boundary.

Why:

1. `603986` is the dominant q4/C capture symbol.
2. The replay confirms a real specialist-only opening edge on `2024-12-12`.
3. But the same symbol also carries a positive trade that starts before q4.
4. So this read is useful, but still too contaminated to rewrite the current family map.

Evidence:

- [market_v2_seed_q4_trade_divergence_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_trade_divergence_capture_c_v1.json)
- [market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_symbol_timeline_603986_capture_c_v1.json)
- [market_v2_seed_q4_specialist_window_opening_603986_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_specialist_window_opening_603986_v1.json)
- [market_v2_seed_q4_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_capture_slice_acceptance_v1.json)

## DEC-0135 Treat The First v2 Seed Q3 Drawdown Read As Mixed

Date: 2026-03-29

Decision:

Treat `market_research_v2_seed / 2024_q3 / mainline_trend_c` as a mixed
drawdown slice rather than a clean new-family frontier.

Why:

1. `603986` is the dominant q3/C drawdown symbol.
2. Its negative side is a clean `entry_suppression_avoidance`.
3. But the same symbol also carries a positive
   `entry_suppression_opportunity_cost`.
4. So the lane is useful and interpretable, but still too mixed to justify
   further symbol-by-symbol replay under the current stage rules.

Evidence:

- [market_v2_seed_q3_trade_divergence_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_trade_divergence_quality_c_v1.json)
- [market_v2_seed_q3_symbol_timeline_603986_quality_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_symbol_timeline_603986_quality_c_v1.json)
- [market_v2_seed_q3_cycle_mechanism_603986_c_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_cycle_mechanism_603986_c_v1.json)
- [market_v2_seed_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_drawdown_slice_acceptance_v1.json)

## DEC-0136 Hold v2 Seed As A Bounded Secondary Substrate

Date: 2026-03-29

Decision:

Hold `market_research_v2_seed` as a bounded secondary specialist substrate and
do not open another local replay lane under the current evidence.

Why:

1. The pack is already `baseline_ready`.
2. It already contributes real specialist pockets.
3. Its first q4/C and q3/C lanes are both now slice-closed mixed reads.
4. So the correct posture is to keep the pack active in the hierarchy, but
   wait for a later refresh instead of forcing a third lane.

Evidence:

- [market_research_data_audit_v2_seed.json](D:/Creativity/A-Share-Quant_TrY/reports/data/market_research_data_audit_v2_seed.json)
- [specialist_alpha_analysis_v3.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/specialist_alpha_analysis_v3.json)
- [market_v2_seed_q4_capture_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q4_capture_slice_acceptance_v1.json)
- [market_v2_seed_q3_drawdown_slice_acceptance_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_q3_drawdown_slice_acceptance_v1.json)
- [market_v2_seed_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_continuation_readiness_v1.json)

## DEC-0137 Do Not Open The Next Batch Refresh Yet

Date: 2026-03-29

Decision:

Do not open `market_research_v2_refresh` yet.

Instead, wait for a new archetype-gap signal or a materially different suspect
geography before starting the next post-v2 refresh cycle.

Why:

1. The primary `V1.1` loop is already paused.
2. `market_research_v2_seed` is also locally paused.
3. `v2_seed` is useful and bounded, not empty.
4. So another refresh would currently be momentum-driven, not trigger-driven.

Evidence:

- [v11_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v11_continuation_readiness_v1.json)
- [market_v2_seed_continuation_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/market_v2_seed_continuation_readiness_v1.json)
- [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json)

## DEC-0138 Enter Explicit No-Trigger Waiting State

Date: 2026-03-29

Decision:

Enter an explicit no-trigger waiting state after `v2_seed` instead of treating
the repo as merely "paused".

Why:

1. The next refresh is already gated.
2. None of the trigger classes is active.
3. So the correct posture is to wait for a real trigger rather than find more
   local work inside a closed phase.

Evidence:

- [next_batch_refresh_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_batch_refresh_readiness_v1.json)
- [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json)

## DEC-0139 Add An Operator Checklist To The No-Trigger Wait State

Date: 2026-03-29

Decision:

Add an explicit action plan for the no-trigger waiting state.

Why:

1. A wait state is safer when it is operationally explicit.
2. The next refresh should not rely on memory or improvised sequencing.
3. The repo now needs a short checklist for both the idle case and the future trigger case.

Evidence:

- [refresh_trigger_monitor_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_monitor_v1.json)
- [refresh_trigger_action_plan_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/refresh_trigger_action_plan_v1.json)

## DEC-0140 Add A One-Page Phase Status Snapshot

Date: 2026-03-29

Decision:

Add a one-page phase status snapshot that compresses the current gate stack
into a single read.

Why:

1. The repo now has multiple aligned gate layers.
2. A single summary reduces operator ambiguity.
3. The current phase should be inspectable from one report before any future action.

Evidence:

- [phase_status_snapshot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/phase_status_snapshot_v1.json)

## DEC-0141 Add A One-Command Phase Status Refresh Chain

Date: 2026-03-29

Decision:

Add a one-command refresh chain for the current waiting-state gate stack.

Why:

1. The repo now has multiple aligned status layers.
2. They should refresh in one fixed order.
3. The operator should not have to remember the sequence manually.

Evidence:

- [41_PHASE_STATUS_REFRESH_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/41_PHASE_STATUS_REFRESH_RUNBOOK.md)
- `python scripts/run_phase_status_refresh.py`

## DEC-0142 Add A Console Entry For The Current Wait State

Date: 2026-03-29

Decision:

Add a short console entrypoint for the current phase state.

Why:

1. The repo now has a complete wait-state stack.
2. Operators should be able to read the current phase in one command without opening JSON.
3. This is a low-risk way to make the no-trigger wait state easier to enforce.

Evidence:

- `python scripts/run_phase_status_console.py`

## DEC-0143 Add A One-Command Phase Guard For The Waiting State

Date: 2026-03-29

Decision:

Add a guarded one-command entrypoint that refreshes the current phase stack and
prints the final operator-facing read.

Why:

1. The repo now has refresh, snapshot, and console layers that are all useful.
2. Operators still need a single safest command when they only want the final answer.
3. The current explicit no-trigger wait state should be enforceable from one entrypoint.

Evidence:

- [42_PHASE_GUARD_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/42_PHASE_GUARD_RUNBOOK.md)
- `python scripts/run_phase_guard.py`

## DEC-0144 Add A Canonical Intake Step For New Refresh Signals

Date: 2026-03-29

Decision:

Add a canonical intake artifact and command for newly observed refresh-trigger
signals.

Why:

1. The repo now has a complete waiting-state gate stack.
2. A future trigger should be recorded in a standard form before rerunning the guard.
3. This reduces ad hoc trigger handling and keeps refresh decisions auditable.

Evidence:

- [43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md)
- `python scripts/run_refresh_trigger_intake.py --trigger-name new_archetype_gap --trigger-type archetype_gap --source manual_review --rationale "Found a materially different suspect geography." --dataset market_research_v1 --dataset market_research_v2_seed --symbol 603986 --slice 2024_q4`

## DEC-0146 Align The A-Share Broker Commission Assumption To The Live Contract

Date: 2026-03-29

Decision:

Lower the repo's default A-share broker commission assumption from `3.0 bps` to `1.2 bps` to match the provided broker contract rate `0.12��`, while leaving statutory stock taxes/fees to a separate decision.

Why:

1. The repo should reflect the owner's actual broker commission when that input is available.
2. The provided contract clearly covers A-share stock trading commission and minimum charge.
3. The screenshot does not fully enumerate statutory exchange and tax charges, so those should not be guessed from the broker contract alone.

Evidence:

- live contract screenshot provided by the owner on 2026-03-29
- SSE investor fee page for stock handling fees: https://one.sse.com.cn/onething/gptz/
- [cost_model.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/backtest/cost_model.py)
- [base.yaml](D:/Creativity/A-Share-Quant_TrY/config/base.yaml)

## DEC-0147 Align The Statutory A-Share Stock Tax/Fee Assumptions To The Current Public Schedule

Date: 2026-03-29

Decision:

Update the repo's default statutory and exchange-collected A-share stock-fee assumptions to use:

- `stamp_tax_bps = 5.0` on sells only
- `transfer_fee_bps = 0.1` on buys and sells
- `exchange_handling_bps = 0.341` on buys and sells
- `regulatory_fee_bps = 0.2` on buys and sells

Why:

1. The owner-provided contract only settles the broker commission dimension.
2. Stamp duty and transfer fee are public statutory/clearing charges and should
   be modeled using the current published schedule rather than an older repo default.
3. The repo should separate broker commission assumptions from statutory and exchange-collected tax/fee assumptions.

Evidence:

- public stamp-duty reduction notice effective 2023-08-28:
  https://www.gov.cn/zhengce/zhengceku/202308/content_6900591.htm
- ChinaClear market fee schedule pages for current transfer-fee assumptions:
  https://www.chinaclear.cn/zdjs/fbzyls/xmdf.shtml
- SSE investor fee page for stock handling fees: https://one.sse.com.cn/onething/gptz/
- [cost_model.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/backtest/cost_model.py)
- [base.yaml](D:/Creativity/A-Share-Quant_TrY/config/base.yaml)
- explicit config defaults under [config](D:/Creativity/A-Share-Quant_TrY/config)

## DEC-0145 Canonicalize The Allowed Refresh Trigger Types

Date: 2026-03-29

Decision:

Constrain refresh-trigger intake to a small canonical set of trigger types.

Why:

1. The waiting-state exit path should stay auditable.
2. Future trigger handling should not drift into free-form labels.
3. Canonical trigger labels make later refresh decisions easier to compare.

Evidence:

- [43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/43_REFRESH_TRIGGER_INTAKE_RUNBOOK.md)
- `python scripts/run_refresh_trigger_intake.py --trigger-name new_archetype_gap --trigger-type archetype_gap --source manual_review --rationale "Found a materially different suspect geography." --dataset market_research_v1 --dataset market_research_v2_seed --symbol 603986 --slice 2024_q4`

## DEC-0148 Open V1.2 As Data Expansion And Factorization Prep

Date: 2026-03-29

Decision:

Leave the current `V1.1` waiting state intact and explicitly open the next
active phase as `V1.2 Data Expansion And Factorization Prep`.

Why:

1. The current specialist loop has already been correctly paused.
2. The next bottleneck is no longer local replay depth.
3. The repo now needs new sample geography and a more formal feature/factor
   preparation layer.

Evidence:

- [32_V11_STAGE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/32_V11_STAGE_REVIEW.md)
- [44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md)

## DEC-0149 Use AkShare As The Primary Batch-Ingestion Layer For V1.2, With Official Sites As Rule/Fee Truth Sources

Date: 2026-03-29

Decision:

Use AkShare as the primary structured collection layer for `V1.2`, while using
official sites selectively for fees, rules, and other governance-level truth.

Why:

1. The repo already has working AkShare-based bootstrap, sector, and concept paths.
2. AkShare is sufficient to start the next refreshed research batch.
3. Official sites are still the better source for fee and rule truth, but are
   not the right default backbone for wide batch ingestion.

Evidence:

- [free_data_bootstrap.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/free_data_bootstrap.py)
- [sector_mapper.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/sector_mapper.py)
- [concept_mapper.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/concept_mapper.py)
- [45_DATA_SOURCE_INVENTORY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/45_DATA_SOURCE_INVENTORY.md)

## DEC-0148 Open V1.2 As Data Expansion And Factorization Prep

Date: 2026-03-29

Decision:

Leave the current `V1.1` waiting state intact and explicitly open the next active phase as `V1.2 Data Expansion And Factorization Prep`.

Why:

1. The current specialist loop has already been correctly paused.
2. The next bottleneck is no longer local replay depth.
3. The repo now needs new sample geography and a more formal feature/factor preparation layer.

Evidence:

- [32_V11_STAGE_REVIEW.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/32_V11_STAGE_REVIEW.md)
- [44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/44_V12_DATA_EXPANSION_AND_FACTORIZATION_PREP.md)

## DEC-0149 Use AkShare As The Primary Batch-Ingestion Layer For V1.2, With Official Sites As Rule/Fee Truth Sources

Date: 2026-03-29

Decision:

Use AkShare as the primary structured collection layer for `V1.2`, while using official sites selectively for fees, rules, and other governance-level truth.

Why:

1. The repo already has working AkShare-based bootstrap, sector, and concept paths.
2. AkShare is sufficient to start the next refreshed research batch.
3. Official sites are still the better source for fee and rule truth, but are not the right default backbone for wide batch ingestion.

Evidence:

- [free_data_bootstrap.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/free_data_bootstrap.py)
- [sector_mapper.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/sector_mapper.py)
- [concept_mapper.py](D:/Creativity/A-Share-Quant_TrY/src/a_share_quant/data/concept_mapper.py)
- [45_DATA_SOURCE_INVENTORY.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/45_DATA_SOURCE_INVENTORY.md)

## DEC-0150 Prepare Market Research v2 Refresh As The First Runnable V1.2 Batch

Date: 2026-03-29

Decision:

Define `market_research_v2_refresh` as the first runnable refreshed batch inside `V1.2`, with a full manifest/bootstrap/mapping/derived/audit/suite config set.

Why:

1. `V1.2` should move immediately from phase planning into runnable batch preparation.
2. The next batch should add materially new symbols beyond `market_research_v1 + market_research_v2_seed`.
3. The first refresh should stay archetype-targeted rather than becoming a blind watchlist expansion.

Evidence:

- [46_MARKET_RESEARCH_V2_REFRESH_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/46_MARKET_RESEARCH_V2_REFRESH_PLAN.md)
- [config/market_research_v2_refresh_manifest.yaml](D:/Creativity/A-Share-Quant_TrY/config/market_research_v2_refresh_manifest.yaml)
- [reports/analysis/next_suspect_batch_manifest_v2_refresh.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/next_suspect_batch_manifest_v2_refresh.json)

## DEC-0151 Open The First Formal Feature / Factor Registry Layer Inside V1.2

Date: 2026-03-29

Decision:

Freeze the repo's current mechanism/context findings into `feature_factor_registry_v1` before opening any factor evaluation protocol.

Why:

1. `V1.2` should now move from data expansion into formal asset classification.
2. The repo already has enough evidence to separate retained features, explanatory-only features, and candidate factors.
3. The next step should evaluate candidate factors, not reopen local replay by momentum.

Evidence:

- [47_FEATURE_FACTOR_REGISTRY_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/47_FEATURE_FACTOR_REGISTRY_V1.md)
- [feature_factor_registry_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/feature_factor_registry_v1.json)

## DEC-0152 Use A Formal Protocol To Split The First Candidate-Factor Bucket

Date: 2026-03-29

Decision:

Open `factor_evaluation_protocol_v1` and classify the current candidate-factor bucket into `evaluate_now`, `evaluate_with_penalty`, and `hold_for_more_sample`.

Why:

1. The registry alone is not enough; `V1.2` now needs a bounded protocol-level handoff into factor work.
2. The repo should stop treating every candidate factor as equally ready.
3. The first factor workstream should start with the cleanest non-baseline candidate rather than reopen replay or widen the registry immediately.

Evidence:

- [48_FACTOR_EVALUATION_PROTOCOL_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/48_FACTOR_EVALUATION_PROTOCOL_V1.md)
- [factor_evaluation_protocol_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/factor_evaluation_protocol_v1.json)

## DEC-0153 Open The First Bounded Factor Lane For Carry-In-Basis Advantage

Date: 2026-03-29

Decision:

Use `carry_in_basis_first_pass_v1` to open a bounded factor lane for `carry_in_basis_advantage`, while explicitly keeping it below retained-feature promotion.

Why:

1. The new protocol already isolates `carry_in_basis_advantage` as the clean `evaluate_now` factor.
2. The factor repeats across `mainline_trend_b` and `mainline_trend_c` with clean net edge and no toxic companion-pocket baggage.
3. `V1.2` should now move from protocol classification into one bounded factor workstream instead of spreading immediately across the penalty and thin buckets.

Evidence:

- [49_CARRY_IN_BASIS_FIRST_PASS.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/49_CARRY_IN_BASIS_FIRST_PASS.md)
- [carry_in_basis_first_pass_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_in_basis_first_pass_v1.json)

## DEC-0154 Restrict The First Carry Factor Lane To Row-Isolated Design

Date: 2026-03-29

Decision:

Use `carry_factor_design_v1` to keep the first carry factor lane narrow: carry may enter bounded factor design, but only as a row-isolated negative-cycle basis factor rather than whole-pocket scoring.

Why:

1. The first-pass gate is already open, but the current evidence still embeds carry inside mixed pockets with `earlier_exit_loss_reduction`.
2. `V1.2` should move forward without accidentally promoting mixed-pocket behavior into a broad factor rule.
3. The clean next move is to isolate carry rows before any wider factor scoring logic is considered.

Evidence:

- [50_CARRY_FACTOR_DESIGN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/50_CARRY_FACTOR_DESIGN_V1.md)
- [carry_factor_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_design_v1.json)

## DEC-0155 Define The First Carry Observable Schema Before Any Scoring Logic

Date: 2026-03-29

Decision:

Use `carry_observable_schema_v1` to define the first explicit row-level observable set for `carry_in_basis_advantage` before opening any scoring design.

Why:

1. The carry lane is now admitted and bounded, but still needs explicit fields before any scoring logic can be defensible.
2. `V1.2` should move from narrative factor design into field-level factor design without widening the lane.
3. The current mixed-pocket evidence requires row isolation, so the schema must be row-specific rather than pocket-wide.

Evidence:

- [51_CARRY_OBSERVABLE_SCHEMA_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/51_CARRY_OBSERVABLE_SCHEMA_V1.md)
- [carry_observable_schema_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_observable_schema_v1.json)

## DEC-0156 Open The First Bounded Carry Scoring Design

Date: 2026-03-29

Decision:

Use `carry_scoring_design_v1` to convert the row-isolated carry observable schema into an explicit bounded score, while keeping strategy integration and retained-feature promotion turned off.

Why:

1. The carry lane already has admission, design boundary, and schema layers; the next clean step is a bounded score.
2. `V1.2` should now test whether the lane can hold a real factor score without widening into a broad pocket-scoring rule.
3. The current B/C rows are fully isomorphic, so scoring can proceed as a pilot even though cross-row discrimination is not yet present.

Evidence:

- [52_CARRY_SCORING_DESIGN_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/52_CARRY_SCORING_DESIGN_V1.md)
- [carry_scoring_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_scoring_design_v1.json)

## DEC-0157 Open The First Carry Factor Pilot As Report-Only Micro-Pilot

Date: 2026-03-29

Decision:

Use `carry_factor_pilot_v1` to open the first carry factor pilot, but keep it in report-only micro-pilot mode until later batches provide more row diversity and score dispersion.

Why:

1. The carry lane already has admission, schema, and score, so the repo can now open a real pilot posture.
2. The current evidence is still too symmetric for a rankable or strategy-linked pilot.
3. `V1.2` should continue advancing without pretending that a two-row isomorphic sample already justifies broader factor deployment.

Evidence:

- [53_CARRY_FACTOR_PILOT_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/53_CARRY_FACTOR_PILOT_V1.md)
- [carry_factor_pilot_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/carry_factor_pilot_v1.json)

## DEC-0158 Close The First V1.2 Factorization Cycle As Representative But Bounded

Date: 2026-03-29

Decision:

Use `v12_factorization_review_v1` to close the first `V1.2` factorization cycle as a representative success, but keep the second factor lane closed until later batches add more row diversity or materially different evidence.

Why:

1. The repo now has a full first bounded factorization chain: registry -> protocol -> carry first pass -> design -> schema -> scoring -> pilot.
2. That is enough to count as a real factorization milestone.
3. But the current carry pilot is still report-only and the penalty/thin buckets remain unresolved, so widening now would be premature.

Evidence:

- [54_V12_FACTORIZATION_REVIEW_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/54_V12_FACTORIZATION_REVIEW_V1.md)
- [v12_factorization_review_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_factorization_review_v1.json)

## DEC-0159 Keep V1.2 Open And Prepare A Later Refresh Batch For Factor Row Diversity

Date: 2026-03-29

Decision:

Use `v12_phase_readiness_v1` to keep `V1.2` open rather than closing it now, and treat a later refresh batch as the correct next source of factor-row diversity.

Why:

1. `V1.2` has already produced a real first bounded factorization cycle.
2. But the carry pilot remains report-only, so row diversity is still insufficient for wider factor work or phase closure.
3. The clean next move is therefore not a second factor lane, but a later refresh batch designed to add more diverse factor rows.

Evidence:

- [55_V12_PHASE_READINESS_V1.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/55_V12_PHASE_READINESS_V1.md)
- [v12_phase_readiness_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_phase_readiness_v1.json)

## DEC-0160 Design The Next Refresh Around Factor-Row Diversity Rather Than Generic Expansion

Date: 2026-03-29

Decision:

Use `v12_next_refresh_factor_diversity_design_v1` to define the next refresh batch as a factor-row diversity batch, not as a general market expansion batch.

Why:

1. The current bottleneck is now specific: the carry pilot lacks row diversity.
2. Opening a second factor lane before fixing that bottleneck would be premature.
3. The next refresh should therefore target new row shapes: basis spread, carry duration, exit alignment, and cross-dataset carry reuse.

Evidence:

- [56_V12_NEXT_REFRESH_FACTOR_DIVERSITY_PLAN.md](D:/Creativity/A-Share-Quant_TrY/PROJECT_LIMITATION/56_V12_NEXT_REFRESH_FACTOR_DIVERSITY_PLAN.md)
- [v12_next_refresh_factor_diversity_design_v1.json](D:/Creativity/A-Share-Quant_TrY/reports/analysis/v12_next_refresh_factor_diversity_design_v1.json)

## DEC-0161 V1.2 opens market_research_v3_factor_diversity_seed manifest as the next executable refresh step
- Context: `carry_in_basis_advantage` completed registry, protocol, design, schema, scoring, and report-only pilot, but remained bottlenecked by row diversity.
- Decision: open and pass a dedicated manifest gate for `market_research_v3_factor_diversity_seed` instead of expanding sample size generically.
- Why: the next refresh now needs to solve four explicit row-diversity gaps: `basis_spread_diversity`, `carry_duration_diversity`, `exit_alignment_diversity`, and `cross_dataset_carry_reuse`.
- Evidence:
  - `reports/analysis/v12_next_refresh_factor_diversity_design_v1.json`
  - `reports/analysis/market_research_v3_factor_diversity_seed_manifest_v1.json`
- Consequence: `market_research_v3_factor_diversity_seed` is now ready for bootstrap and becomes the immediate next V1.2 action.

## DEC-0162 V1.2 advances market_research_v3_factor_diversity_seed from manifest-ready to runnable substrate
- Context: the next refresh manifest for carry row diversity had already turned green.
- Decision: complete free-data bootstrap, sector/concept mapping, derived generation, audit, and the first A/B/C suite for `market_research_v3_factor_diversity_seed`.
- Why: V1.2 now needs actual row-diversity substrate evidence, not only refresh-design correctness.
- Evidence:
  - `reports/data/market_research_data_audit_v3_factor_diversity_seed.json`
  - `reports/20260330T005408Z_70e5fe8c_comparison.json`
- Consequence: `market_research_v3_factor_diversity_seed` is now a runnable research pack and the next step is to compare its first specialist geography against the current carry-row bottleneck.

## DEC-0163 V1.2 promotes market_research_v3_factor_diversity_seed into the active specialist map
- Context: `market_research_v3_factor_diversity_seed` completed manifest, bootstrap, audit, and first suite run.
- Decision: include the new pack in six-pack time-slice validation and specialist alpha analysis instead of leaving it as a passive refresh artifact.
- Why: V1.2 now needs to test whether the new pack actually changes carry-row diversity and specialist geography.
- Evidence:
  - `reports/20260330T005654Z_c28cab1a_comparison.json`
  - `reports/analysis/specialist_alpha_analysis_v5.json`
  - `reports/analysis/market_v3_factor_diversity_q4_trade_divergence_capture_c_v1.json`
- Consequence: `market_research_v3_factor_diversity_seed / 2024_q4 / mainline_trend_c` is now the first active v3 specialist lane, with `002049` identified as the top positive driver.

## DEC-0164: v3 q4 002049 lane is opening-led, not persistence-led
Date: 2026-03-30

- `market_research_v3_factor_diversity_seed / 2024_q4 / mainline_trend_c / 002049` was narrowed with existing opening/persistence analyzers rather than a new lane-specific tool.
- The first decisive edge is a specialist-only opening on `2024-11-05`.
- Anchors shared permission and entry family but remained `junk`, while the specialist upgraded to `late_mover` and emitted `buy`.
- The checked late window does not show a clean persistence edge.
- Current posture: treat the first `v3` lane as `opening-led first lane`, not as evidence that the carry lane has structurally broken through.

## DEC-0165: first v3 lane closed as opening-led, not carry breakthrough
Date: 2026-03-30

- `market_v3_q4_first_lane_acceptance_v1.json` now formally closes the first `market_research_v3_factor_diversity_seed` lane.
- `002049 / 2024_q4 / mainline_trend_c` remains the top positive driver, but the lane does not change the current carry reading.
- The lane is opening-led: aligned permission and entry family, anchors blocked by `junk`, specialist upgraded into `late_mover` on `2024-11-05`.
- The checked late window does not show a clean persistence edge.
- Posture: do not open a second `v3` lane yet and do not interpret `v3` as carry-breakthrough evidence.

## DEC-0166: v12 primary bottleneck remains carry row diversity gap after first v3 lane
Date: 2026-03-30

- `v12_bottleneck_check_v1.json` now combines phase readiness, next-refresh design, and first-lane acceptance.
- The first `v3` lane is useful but does not change the main V1.2 bottleneck.
- `002049 / q4 / C` closes as opening-led, while row diversity still remains missing for the carry lane.
- Posture: keep V1.2 on the factor-row-diversity track, keep the second `v3` lane closed, and do not redirect the phase toward a broader capture-opening expansion.

## DEC-0167: V1.2 now has a criteria-first entry for the next refresh
Date: 2026-03-30

- `v12_next_refresh_entry_v1.json` now translates the current V1.2 bottleneck into an executable next-refresh posture.
- The next batch is now named `market_research_v4_carry_row_diversity_refresh`.
- Posture: prepare the next refresh entry now, but do not open a manifest yet.
- This keeps the main line focused on carry row diversity and prevents the first opening-led `v3` lane from widening replay or redirecting V1.2 into generic capture expansion.

## DEC-0168: v4 refresh symbol-selection criteria are now frozen
Date: 2026-03-30

- `v12_v4_refresh_criteria_v1.json` now freezes the symbol-selection rules for `market_research_v4_carry_row_diversity_refresh`.
- The next refresh must target one primary row-diversity gap per symbol, remain observable under the carry schema, and avoid pure opening-led clones as the primary reason for admission.
- Posture: `v4` manifest may now be drafted, but only under these criteria; replay remains closed during manifest drafting.

## DEC-0169: v4 carry-row-diversity refresh manifest is now green
Date: 2026-03-30

- `market_research_v4_carry_row_diversity_refresh_manifest_v1.json` is now green.
- The manifest adds `8` new symbols, covers all four carry row-diversity targets, and passes the stricter criteria gate.
- No symbol uses `opening_led_clone` as its primary admission reason.
- Posture: the next healthy move is bootstrap, not more manifest debate and not replay.

## DEC-0170: v4 refresh is now baseline-ready and active in the specialist map
Date: 2026-03-30

- `market_research_data_audit_v4_carry_row_diversity_refresh.json` now audits as `baseline_ready = true` after rerunning the chain in the correct order.
- `20260330T015501Z_a2b9cc4a_comparison.json` is the first suite run for `v4`.
- `20260330T015559Z_22ccd733_comparison.json` and `specialist_alpha_analysis_v6.json` now place `v4` into the current seven-pack map.
- `v4` is not an empty refresh: it already contributes specialist geography, with the first visible pocket at `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a`.
- Posture: keep replay closed for this turn; next step should open only one `v4` lane, not widen immediately.
## DEC-0171 2026-03-30
- Closed `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 601919` as an opening-led first lane rather than a carry breakthrough.
- Kept the second `v4` lane closed because the checked late window did not produce a clean persistence edge.
- Preserved the main `V1.2` bottleneck as missing carry row diversity.
## DEC-0172 2026-03-30
- Formalized a deferred `catalyst persistence` context hypothesis branch to test whether sustained external catalysts separate carry-led lanes from opening-led lanes.
- Kept the branch report-only and explicitly outside the current `V1.2` carry-row-diversity mainline.
- Preserved the main reading that missing carry row diversity remains the current primary bottleneck.
## DEC-0173 2026-03-30
- Froze `catalyst_event_registry_schema_v1` for the deferred catalyst-persistence hypothesis branch.
- Canonicalized source authority, execution strength, rumor risk, consolidation, and reacceleration fields so later catalyst rows can be seeded consistently.
- Kept the branch report-only and outside the active `V1.2` carry-row-diversity mainline.
## DEC-0174 2026-03-30
- Opened `v12_bounded_training_pilot_v1` as the first explicit report-only training step under `V1.2`.
- The pilot cleanly separates frozen `opening_led`, `persistence_led`, and `carry_row_present` artifacts, which confirms that current structured observables are trainable at a bounded level.
- Kept both strategy-level ML and news-branch training explicitly closed.
## DEC-0175 2026-03-30
- Added `v12_training_readiness_check_v1` to distinguish between a successful micro-pilot and a branch that is ready to scale.
- The check keeps the training branch report-only because the sample is still small and carry rows remain duplicated.
- Preserved strategy-level ML and news-branch training as closed.
## DEC-0176 2026-03-30
- Froze `v12_training_sample_expansion_design_v1` and `v12_training_sample_manifest_v1` so the bounded training branch now requests additional rows only from future true carry cases and clean persistence cases.
- Explicitly froze the opening-led class count and kept both penalty-track and deferred basis families closed as carry-class substitutes.
- Preserved the main `V1.2` training reading that the next bottleneck is sample breadth discipline rather than model choice.
## DEC-0177 2026-03-30
- Added `v12_training_sample_binding_gate_v1` so the bounded training manifest now actively rejects currently surfaced opening-led first lanes from `v3` and `v4`.
- Kept future clean persistence rows and future true carry rows as the only approved binding sources for the next training expansion step.
- Prevented silent widening of the report-only training branch beyond the frozen manifest posture.
## DEC-0178 2026-03-30
- Added `v12_training_lane_binding_check_v1` as the per-lane intake check for the bounded training branch.
- Confirmed that the currently closed `v3` and `v4` first lanes remain rejected because both are opening-led while the opening class is frozen.
- Preserved the next valid training-expansion sources as only future clean persistence rows and future true carry rows.
## DEC-0179 2026-03-30
- Opened `catalyst_event_registry_seed_v1` as the first bounded catalyst sample under `V1.2`.
- Seeded a balanced 2/2/2 lane sample across opening-led, persistence-led, and carry-row-present cases using already-closed lane artifacts and frozen carry rows.
- Kept the catalyst branch in a report-first posture: the next step is filling event-level fields for the bounded sample rather than widening into a general news crawl.
## DEC-0179 2026-03-30
- Opened `catalyst_event_registry_seed_v1` as the first bounded catalyst sample under `V1.2`.
- Seeded a balanced 2/2/2 lane sample across opening-led, persistence-led, and carry-row-present cases using already-closed lane artifacts and frozen carry rows.
- Kept the catalyst branch in a report-first posture: the next step is filling event-level fields for the bounded sample rather than widening into a general news crawl.
## DEC-0180 2026-03-30
- Opened `catalyst_event_registry_fill_v1` as the first bounded catalyst fill layer.
- Populated market-context scope and mapped context names for all six seeded rows while explicitly leaving official source authority unresolved.
- Preserved the catalyst branch posture as market-context-first and report-only until a later manual or semi-manual source fill exists.
## DEC-0181 2026-03-30
- Opened `catalyst_event_registry_source_fill_v1` as the first partial source layer on top of the bounded catalyst seed.
- Resolved 5 of 6 rows to official or high-trust industry context references while keeping 1 row explicitly unresolved.
- Moved the catalyst branch to a state where a first bounded catalyst-context audit is now justified without pretending the source layer is complete.
## DEC-0182 2026-03-30
- Completed `catalyst_context_audit_v1` on the first bounded catalyst sample.
- The current bounded audit shows directional separation: opening rows remain single-pulse, persistence rows cluster in multi-day reinforcement, and carry rows cluster in followthrough context.
- Kept the catalyst branch report-only and explicitly declined promotion into a retained factor or training feature at this stage.
## DEC-0182 2026-03-30
- Completed `catalyst_context_audit_v1` on the first bounded catalyst sample.
- The current bounded audit shows directional separation: opening rows remain single-pulse, persistence rows cluster in multi-day reinforcement, and carry rows cluster in followthrough context.
- Kept the catalyst branch report-only and explicitly declined promotion into a retained factor or training feature at this stage.

## DEC-0183 2026-03-30
- Added `v12_catalyst_branch_phase_check_v1` to ensure the catalyst branch does not silently replace the main V1.2 direction.
- Confirmed that the catalyst branch is active and useful, but still bounded and supportive rather than mainline-defining.
- Preserved the main V1.2 bottleneck as missing carry row diversity.
## DEC-0184 2026-03-30
- Added `v12_carry_row_hunting_strategy_v1` to freeze the next mainline carry hunt inside the existing `v4` refresh.
- Confirmed that the repo should not open a new refresh batch or widen replay now; it should keep hunting one `v4` symbol at a time.
- Fixed the next recommended target as `000725`, prioritizing basis-spread diversity ahead of the remaining exit-alignment track.
### DEC-0185 V1.2 000725 carry-row hunt closes inactive
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Close `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 000725` as `no_active_structural_lane`.
- Do not widen replay and do not open a new refresh batch from this symbol-level result.
- Advance the next bounded carry-row hunt target to `600703`.

Rationale:
- `000725` was the first `basis_spread_diversity` target inside the existing v4 refresh.
- The checked lane produced `pnl_delta = 0.0`, no specialist-only opening edge, and no clean persistence edge.
- A zero-delta lane with identical trade-count signature should not be force-promoted into carry evidence.

Evidence:
- `reports/analysis/market_v4_q2_symbol_timeline_000725_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_000725_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_000725_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_000725_v1.json`
- `PROJECT_LIMITATION/76_V12_CARRY_ROW_HUNT_000725_V1.md`
### DEC-0186 V1.2 600703 carry-row hunt closes inactive
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Close `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 600703` as `no_active_structural_lane`.
- Keep the no-widening discipline and do not open another refresh batch from this result.
- Advance the next bounded carry-row hunt target to `600150` from the `carry_duration_diversity` track.

Rationale:
- `600703` was the second `basis_spread_diversity` target after `000725`.
- The checked lane again produced `pnl_delta = 0.0`, no specialist-only opening edge, and no clean persistence edge.
- Two consecutive inactive basis-spread hunts are enough to justify moving to the duration track instead of repeating the same structure.

Evidence:
- `reports/analysis/market_v4_q2_symbol_timeline_600703_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_600703_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_600703_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_600703_v1.json`
- `PROJECT_LIMITATION/77_V12_CARRY_ROW_HUNT_600703_V1.md`
### DEC-0187 V1.2 600150 carry-row hunt closes inactive
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Close `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 600150` as `no_active_structural_lane`.
- Keep the bounded hunt inside the current v4 refresh and move to `601127`.
- Do not widen replay and do not reinterpret inactive duration-track rows as carry evidence.

Rationale:
- `600150` was the first `carry_duration_diversity` target after two inactive `basis_spread_diversity` checks.
- The lane still produced `pnl_delta = 0.0`, no specialist-only opening edge, and no clean persistence edge.
- This means the current v4 hunt still has not produced an active carry-supporting lane, so discipline matters more than forcing interpretation.

Evidence:
- `reports/analysis/market_v4_q2_symbol_timeline_600150_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_600150_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_600150_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_600150_v1.json`
- `PROJECT_LIMITATION/78_V12_CARRY_ROW_HUNT_600150_V1.md`
### DEC-0188 V1.2 601127 carry-row hunt closes inactive
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Close `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a / 601127` as `no_active_structural_lane`.
- Do not widen replay into lower-priority v4 tracks immediately.
- Run a short phase-level check before deciding whether `cross_dataset_carry_reuse` or `exit_alignment_diversity` should be touched.

Rationale:
- `601127` was the second `carry_duration_diversity` target after the inactive `basis_spread_diversity` checks and the first inactive duration-track check.
- The lane again produced `pnl_delta = 0.0`, no specialist-only opening edge, and no clean persistence edge.
- This means the current v4 hunt has exhausted the checked high-priority tracks without producing an active carry-supporting lane.

Evidence:
- `reports/analysis/market_v4_q2_symbol_timeline_601127_capture_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_opening_601127_a_v1.json`
- `reports/analysis/market_v4_q2_specialist_window_persistence_601127_a_v1.json`
- `reports/analysis/market_v4_q2_symbol_hunt_acceptance_601127_v1.json`
- `PROJECT_LIMITATION/79_V12_CARRY_ROW_HUNT_601127_V1.md`
### DEC-0189 V1.2 v4 q2/A high-priority hunt pauses for reassessment
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Pause the current `market_research_v4_carry_row_diversity_refresh / 2024_q2 / mainline_trend_a` hunt before opening lower-priority tracks.
- Keep the global `V1.2` primary bottleneck as `carry_row_diversity_gap`.
- Do not open `cross_dataset_carry_reuse` or `exit_alignment_diversity` tracks until the v4 hunt posture is reassessed.

Rationale:
- All checked high-priority `basis_spread_diversity` and `carry_duration_diversity` targets closed as `no_active_structural_lane`.
- This is enough to say the currently checked `v4 / q2 / A` hunt area is exhausted at high priority.
- It is not enough to say the global carry-row-diversity problem is solved or that lower-priority v4 tracks should automatically be pursued.

Evidence:
- `reports/analysis/v12_v4_hunt_phase_check_v1.json`
- `PROJECT_LIMITATION/80_V12_V4_HUNT_PHASE_CHECK_V1.md`
### DEC-0190 V1.2 v4 reassessment keeps substrate active but local hunt exhausted
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Keep `market_research_v4_carry_row_diversity_refresh` as an active substrate in the wider V1.2 map.
- Keep the checked `v4 / q2 / A` high-priority hunt region paused.
- Do not open lower-priority local v4 tracks now; instead return to a higher-level batch/substrate decision.

Rationale:
- `v4` still appears in the specialist opportunity map, so it should not be discarded.
- But the checked high-priority `q2 / A` hunt area is exhausted without surfacing an active carry-supporting lane.
- That combination means the substrate is still alive while the current local hunt is not worth widening.

Evidence:
- `reports/analysis/v12_v4_hunt_phase_check_v1.json`
- `reports/analysis/v12_v4_reassessment_v1.json`
- `PROJECT_LIMITATION/81_V12_V4_REASSESSMENT_V1.md`
### DEC-0191 V1.2 returns to next refresh preparation
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Do not reopen local `v3` replay.
- Do not reopen local `v4` replay.
- Prepare the next refresh batch for `carry_row_diversity` instead.

Rationale:
- `V1.2` still says row diversity is missing.
- `v4` remains active globally but is locally exhausted in the checked high-priority hunt area.
- Reopening existing local substrate replay would add churn without addressing the current bottleneck.

Evidence:
- `reports/analysis/v12_phase_readiness_v1.json`
- `reports/analysis/v12_v4_reassessment_v1.json`
- `reports/analysis/v12_batch_substrate_decision_v1.json`
- `PROJECT_LIMITATION/82_V12_BATCH_SUBSTRATE_DECISION_V1.md`
### DEC-0192 V1.2 next refresh entry v2 opens v5 posture
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Prepare the next executable refresh entry as `market_research_v5_carry_row_diversity_refresh`.
- Freeze the next batch posture as `criteria_first_true_carry_plus_clean_persistence_refresh`.
- Keep local `v3` and `v4` replay closed while this new entry is being converted into criteria and manifest.

Rationale:
- The main `V1.2` bottleneck remains missing carry row diversity.
- The training manifest still needs `2` additional true carry rows and `2` additional clean persistence rows.
- Catalyst context is useful but remains support-only, so it should not replace the main carry/persistence batch objective.

Evidence:
- `reports/analysis/v12_batch_substrate_decision_v1.json`
- `reports/analysis/v12_training_sample_manifest_v1.json`
- `reports/analysis/v12_catalyst_branch_phase_check_v1.json`
- `reports/analysis/v12_next_refresh_entry_v2.json`
- `PROJECT_LIMITATION/83_V12_NEXT_REFRESH_ENTRY_V2.md`
### DEC-0193 V1.2 v5 refresh criteria frozen
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Freeze symbol-selection criteria for `market_research_v5_carry_row_diversity_refresh`.
- Keep the next batch focused on `true carry rows` first and `clean persistence rows` second.
- Exclude opening-clone chasing, relabeling, and reopening the locally exhausted `v4 / q2 / A` replay zone.

Rationale:
- The current training manifest still needs `2` additional true carry rows and `2` additional clean persistence rows.
- `carry_observable_schema_v1` already defines the bounded carry row observability contract.
- The next refresh should therefore solve the explicit sample gap instead of behaving like another general sample expansion.

Evidence:
- `reports/analysis/v12_next_refresh_entry_v2.json`
- `reports/analysis/v12_training_sample_manifest_v1.json`
- `reports/analysis/carry_observable_schema_v1.json`
- `reports/analysis/v12_v5_refresh_criteria_v1.json`
- `PROJECT_LIMITATION/84_V12_V5_REFRESH_CRITERIA_V1.md`
### DEC-0194 V1.2 v5 refresh manifest v1 accepted
Date: 2026-03-30
Type: Research Decision
Status: Accepted

Decision:
- Accept the first manifest for `market_research_v5_carry_row_diversity_refresh`.
- Keep the manifest narrow: `4` new symbols only.
- Preserve the `2 true carry + 2 clean persistence` split.

Rationale:
- The current training gap requires `2` additional true carry rows and `2` additional clean persistence rows.
- The manifest satisfies the frozen v5 criteria while staying fully new versus the combined reference base.
- This is enough to open the next data batch without slipping back into generic sample growth.

Evidence:
- `reports/analysis/v12_v5_refresh_criteria_v1.json`
- `reports/analysis/market_research_v5_carry_row_diversity_refresh_manifest_v1.json`
- `PROJECT_LIMITATION/85_MARKET_RESEARCH_V5_CARRY_ROW_DIVERSITY_REFRESH_PLAN.md`
- 2026-03-30: Bootstrapped `market_research_v5_carry_row_diversity_refresh`, reached `baseline_ready = true`, ran pack suite (`20260330T041310Z_130eb2ed_comparison.json`), ran eight-pack time-slice validation (`20260330T041451Z_b6297292_comparison.json`), and rebuilt specialist map (`reports/analysis/specialist_alpha_analysis_v8.json`). `v5` is now active in specialist geography, but `V1.2` still reads as a carry-row-diversity bottleneck rather than a resolved factor-training state.
