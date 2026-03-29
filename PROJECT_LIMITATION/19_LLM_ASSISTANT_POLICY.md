# A-Share Quant V1 LLM Assistant Policy

## Objective

This document defines if, when, and how large language models may assist the project.

Its purpose is not to promote LLM usage by default, but to prevent future LLM integration from distorting protocol discipline, auditability, or result interpretation.

---

## Top-Level Position

1. LLM is allowed as a future enhancement.
2. LLM is not part of the V1 alpha-generating core.
3. LLM should enter the system as a research assistant before it enters any signal path.
4. LLM usage must strengthen research quality, not weaken reproducibility.

---

## Role Boundary

In this project, LLM should be treated primarily as one of these:

1. research explainer
2. report summarizer
3. news and policy summarizer
4. experiment reviewer
5. anomaly triage assistant

LLM should not initially be treated as:

1. the definition of a mainline
2. the direct source of buy/sell truth
3. the sole judge of strategy promotion
4. a substitute for protocol-bound scoring logic

---

## Recommended Introduction Order

### Stage 1: Documentation And Review Assistant

Allowed uses:

1. summarize experiment results
2. draft postmortems
3. convert run artifacts into readable research notes
4. generate structured pros/cons from backtest outputs

Why this stage comes first:

1. low protocol risk
2. high productivity gain
3. easy human review

### Stage 2: External Information Assistant

Allowed uses:

1. summarize news related to a sector or symbol
2. summarize policy documents or industry developments
3. produce structured evidence tables for human review

Required restriction:

1. outputs must remain auxiliary evidence, not direct trading signals

### Stage 3: Research Challenge Assistant

Allowed uses:

1. generate bullish interpretation of a result
2. generate bearish interpretation of a result
3. challenge hidden assumptions in a strategy or experiment
4. suggest follow-up validation questions

This is the closest analogue to a debate-room workflow, but still restricted to research review rather than decision authority.

### Stage 4: Candidate Feature Or Ranking Assistant

Allowed only after stronger validation infrastructure exists.

Possible uses:

1. convert unstructured text into structured candidate tags
2. create auxiliary ranking signals for sectors or stocks
3. propose candidate features for later formalization

Required restriction:

1. no direct promotion into production signal logic without formal protocol review, versioning, and benchmark comparison

---

## Explicitly Allowed Near-Term Use Cases

Near-term LLM use is allowed for:

1. writing experiment summaries from run artifacts
2. drafting `DECISION_LOG` and `RESEARCH_JOURNAL` entries for human confirmation
3. generating comparison commentary for A/B/C or segmentation runs
4. summarizing sector-related news into structured notes
5. summarizing policy or industry documents into research inputs
6. producing risk checklists for suspicious result changes
7. generating postmortem templates after data or backtest anomalies

---

## Explicitly Forbidden Near-Term Use Cases

Near-term LLM use is not allowed for:

1. directly labeling a stock as leader/core/late mover without a protocol-defined scoring path
2. directly deciding whether a trade should be executed
3. replacing `mainline_capture_ratio` or `missed_mainline_count` with subjective LLM judgment
4. overriding sample segmentation with ad hoc narrative reasoning
5. promoting a strategy because an LLM explanation sounds convincing
6. hiding prompt or model changes from experiment records
7. using non-reproducible chat outputs as official research evidence without stored prompt/response artifacts

---

## Requirements For Any LLM Usage

If LLM is used in any workflow, all of the following must be recorded:

1. model name
2. provider
3. prompt template or prompt reference
4. input source references
5. output artifact path
6. date and run context
7. whether the LLM output was informational, advisory, or directly consumed downstream

If the LLM output affects a research conclusion, it must also be logged in:

1. [07_DECISION_LOG.md](./07_DECISION_LOG.md)
2. [08_RESEARCH_JOURNAL.md](./08_RESEARCH_JOURNAL.md)

---

## Evidence Hierarchy

When LLM is present, evidence priority should remain:

1. canonical market data
2. protocol-defined derived tables and metrics
3. reproducible experiment outputs
4. human-reviewed research notes
5. LLM-generated summaries and interpretations

This order must not be inverted.

---

## Promotion Barrier

An LLM-assisted component may only move closer to the strategy core if:

1. its inputs are versioned
2. its outputs are stored
3. its prompts are controlled
4. its model changes are tracked
5. it is benchmarked against a non-LLM baseline
6. it improves protocol-priority metrics rather than only producing better narratives
7. it survives out-of-sample or walk-forward validation

Without these conditions, LLM must remain an assistant only.

---

## Relationship To ML Policy

This document is adjacent to [17_FUTURE_ML_POLICY.md](./17_FUTURE_ML_POLICY.md), but not identical.

Difference:

1. ML policy governs predictive or ranking models in the research stack.
2. LLM policy governs language-driven assistance, interpretation, and possible unstructured-information processing.

Common rule:

1. neither ML nor LLM may bypass protocol discipline, data governance, or validation standards

---

## One-Sentence Rule

LLM may help the project think, explain, and review earlier than it helps the project decide.
