# Long Horizon Autonomy Policy

## Final Goal
- Build a credible, continuously iterable A-share quantitative research and strategy system that progressively approaches practical deployment readiness.

## Autonomy Scope
- Autonomous execution is allowed inside the current roadmap when it does not violate existing freeze, gate, validation, or scope controls.
- After a phase closes, the next phase may be opened only if a legal next phase exists under the current phase map and governance rules.
- New phases may be named autonomously when the transition is justified by bottleneck change, phase-level review, or explicit completion/failure conditions.
- Nighttime or unattended execution may continue across multiple legal steps, but only within phase guard, stop criteria, and scope boundary.

## Core Principles
- Evidence before expansion; small validation before broader rollout.
- Report-only results must not be promoted directly into the strategy mainline.
- Acceptance, validation, audit, logs, and phase documents are mandatory and may not be skipped to preserve momentum.
- Ambiguous interpretation is never treated as a formal conclusion.
- Closed phases may not be reopened without a concrete, documented reason.
- Success, acceptance, validation, and retained-feature standards may not be relaxed merely to keep work moving.
- Negative conclusions are valid outputs.
- Prefer minimal necessary changes over broad refactors for local research tasks.
- Exploration may be loosened only at the proposal/design layer; admission, promotion, and strategy-mainline standards remain strict.

## Phase Governance
- A new phase requires a documented trigger: current phase completion, failure, bottleneck change, or a phase-level review conclusion.
- Finishing a local task is not enough to justify a new phase.
- Every new phase must begin with a phase charter before execution.

## Required Phase Charter Fields
- `mission`
- `in_scope`
- `out_of_scope`
- `success_criteria`
- `stop_criteria`
- `handoff_condition`

## Default Priority Order
1. Legal next actions inside the current phase
2. Current phase bottleneck check or phase-level review
3. Waiting-state summary

The system must not skip directly to:
- a new refresh batch
- a new data pack
- a new research mainline
- a new heavy dependency
- a new paid external data source

## Automatic Continuation Rules
- Closing a local task does not imply the full round is over.
- Local task closure must be followed by updates to acceptance, decision log, research journal, phase doc, and phase status.
- If a legal next step exists inside the current phase, execution should continue automatically.
- If repeated local work is uninformative, the system must switch to a phase-level review instead of cycling through more candidates.
- If repeated phase-level reviews do not change the bottleneck judgment and no legal high-value step remains, the system must enter explicit waiting state.
- Autonomous execution optimizes for decision-value increase, not action continuity. If the next phase cannot materially improve the decision basis, it must not be opened merely to keep work moving.

## Inactivity Thresholds
- For single-symbol hunts or single-lane replays:
  - three consecutive failures to produce an active structural lane require phase-level review
- For phase-level reviews:
  - two consecutive reviews that do not change the bottleneck judgment prohibit forced branch expansion
- For new substrates:
  - if the first lane closes without changing the bottleneck judgment, the substrate must not widen into broad replay only because it is active

## Repetition Prohibition
- Once the system has explicitly concluded that:
  - the current evidence pool is exhausted
  - no new cross-family or otherwise non-redundant admissible case exists
  - or another same-pool probe would not provide high information gain
- it must not open another micro-phase on the same evidence pool, same core shortfall, and same feature merely by renaming the review/probe.

## Closure Root-Cause Classification
- Every phase closure must classify the current primary bottleneck as exactly one of:
  - `data_or_evidence_gap`
  - `feature_definition_or_non_redundancy_gap`
  - `method_or_consumption_gap`
  - `direction_not_working_under_current_setup`
- The closure output must name one primary cause only.
- Multi-cause ambiguity is not an acceptable closure reading; the system must force a single dominant bottleneck classification.

## Waiting State
- Waiting state is valid and not treated as failure.
- In waiting state, only the following are allowed:
  - state snapshot updates
  - waiting-state summaries
  - preservation of the restart entry point
- New tasks must not be manufactured merely to avoid waiting.

## Solution Shift Mode
- Trigger any of the following and the system must stop execution-mode phase creation and switch into `Solution Shift Mode`:
  - the same main branch enters waiting state twice in sequence without a material phase-judgment change
  - the current evidence pool is explicitly exhausted
  - no new cross-family or otherwise non-redundant admissible cases remain
  - the next plausible phase would only repeat bounded review, re-review, probe, or gap-reordering on the same problem
- In `Solution Shift Mode`, no new micro-phase may be opened automatically.
- The required output is a `Solution Shift Memo`, and it must choose exactly one of:
  - `Data Acquisition Plan`
  - `Feature Hypothesis Plan`
  - `Method Change Plan`
  - `Freeze Recommendation`
- Every `Solution Shift Memo` must explicitly state:
  - the current primary bottleneck category
  - why the current path no longer increases decision value
  - how the new proposal changes the decision basis instead of merely producing more artifacts
  - why freezing is correct if no viable change path exists
- `Solution Shift Mode` is intentionally looser at the exploration layer:
  - it may propose small design-first or memo-first next steps
  - it may recommend a narrowly scoped exploratory phase
  - it may recommend a one-off owner-led exception probe
- `Solution Shift Mode` is not looser at the admission layer:
  - it may not directly promote report-only results
  - it may not bypass validation or acceptance gates
  - it may not widen replay or collection merely because a new idea exists
  - it may not auto-create a follow-on chain from an exploratory exception phase

## Solution Shift Layer
- The project distinguishes between:
  - `exploration_layer`
  - `admission_and_mainline_layer`
- `exploration_layer` may be relatively flexible:
  - design-first outputs are allowed
  - proposal artifacts are allowed without full evidence closure
  - small, time-boxed, owner-led exploratory phases are allowed
  - candidate acquisition plans, feature hypothesis plans, trigger-source maps, and archetype-expansion plans are valid outputs
- `admission_and_mainline_layer` remains strict:
  - report-only cannot enter the strategy mainline
  - provisional candidacy cannot be treated as promotion
  - strategy integration, retained-feature promotion, and widened replay remain gated exactly as before

## Exploration Outputs
- The following are valid outputs when the system is in `Solution Shift Mode` or otherwise working at the exploration layer:
  - `data_acquisition_memo`
  - `feature_hypothesis_memo`
  - `trigger_source_mapping`
  - `archetype_expansion_plan`
  - `time_boxed_exception_phase_charter`
- These outputs are legal even when they do not immediately produce a full replay/review/closure loop, because their purpose is to change the future decision basis rather than to force premature evidence closure.

## Subagent Exploration Layer
- Subagents may only be used for bounded, repetitive, non-blocking exploratory work.
- Subagents may also be used for candidate-structure drafting and low-governance structuring work, as long as those outputs remain review-only.
- Subagents must not be used to outsource:
  - label-schema definition
  - feature candidacy or promotion judgment
  - phase switching
  - strategy-signal definition
  - execution-timing judgment
- Every subagent task must declare:
  - `hypothesis`
  - `success_if`
  - `stop_if`
  - `used_for`
  - fixed dataset or evidence pool
  - fixed output template
- Default subagent limits:
  - maximum parallel subagents: `2`
  - maximum tasks per round: `3`
  - low-compute posture by default
- No more than one unreviewed subagent batch may exist at any time.
- Mainline review cadence must follow task type:
  - repetitive `structuring` / `execution` work may be reviewed by bounded volume or bounded time window
  - `drafting` / `exploration` work must be reviewed by bounded thematic stage
- A new subagent batch may not begin until the previous batch has reached its cadence trigger and been reviewed.
- If a subagent task cannot clearly change the future decision basis, it must not be opened.

## Auto-Allowed Actions
- Single-lane replay, single-symbol hunt, and phase-level checks that are legal inside the active phase
- Artifact, phase document, decision log, research journal, and README state updates
- Targeted tests directly related to the current change
- Shortlist, acceptance, phase status, and runbook refreshes
- Initialization of the minimum legal action for the next phase once phase guard allows it

## Auto-Forbidden Actions
- Opening a new refresh batch without explicit charter and gate approval
- Expanding replay queues
- Introducing heavy dependencies or major environment changes
- Introducing new paid external data sources
- Large core-framework refactors
- Promoting report-only or micro-pilot results into retained features or main signals
- Cross-phase jumps without a defined route
- Lowering evidence standards for unattended execution

## Mandatory Stop-And-Ask Conditions
- The main direction or main goal needs to change
- A new heavy dependency, large environment change, or paid external data source is required
- A large core refactor is required
- A core working hypothesis is overturned
- Two or more materially different routes remain plausible
- The next action is high-risk, high-cost, or irreversible
- Acceptance, validation, promotion, or retained-feature standards appear to need revision
- The phase map itself appears to need rewriting rather than phase-local progress

## Testing And Validation
- Default to targeted tests directly related to the current change
- Expand validation only when touching core execution, shared infrastructure, phase transition logic, or the validation framework
- Every round must explicitly record:
  - which tests ran
  - whether they passed
  - whether full `pytest` was not run
  - why full `pytest` was not run

## Delivery Requirements
- Every round must produce either an artifact or a formal conclusion
- Every round must update phase doc, decision log, and research journal
- Every round must state tests and the next step
- Every phase must have closure conditions and may not refine forever
- Every local task closure must state:
  - the conclusion
  - whether phase judgment changed
  - the next legal action
  - why waiting state is entered if no legal action remains

## Cross-Phase Protocol
- When a phase closes, the system must first check:
  - whether success, stop, or failure conditions are met
  - whether a legal next phase exists
  - whether a phase-level review is required first
- If a legal next phase exists:
  - write the phase charter
  - initialize the minimum legal action
  - continue execution
- If no legal next phase exists:
  - output waiting-state summary
  - keep no-trigger wait
- New phases must not be invented solely to avoid stopping.
