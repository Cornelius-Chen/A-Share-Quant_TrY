# 118 V15 Retained-Feature Candidacy Review

## Mission
- Review whether current report-only context features meet the minimum admissibility threshold for retained-feature candidacy without promoting them into the strategy mainline.

## In Scope
- feature admissibility review
- evidence sufficiency review
- non-redundancy or orthogonality review
- safe-containment review
- bounded candidacy decisions

## Out Of Scope
- retained-feature promotion
- strategy integration
- formal model work
- new wide replay or refresh expansion
- local regime segmentation

## Success Criteria
- freeze a clear candidacy review protocol
- produce admissibility judgments for the current bounded report-only context features
- close the phase with a clear retained-candidacy posture or a bounded rejection posture

## Stop Criteria
- if current feature definitions are too unstable for candidacy review
- if evidence remains too sparse to support bounded admissibility judgments
- if the work drifts into direct promotion or strategy integration

## Handoff Condition
- After the charter opens, only replay-independent candidacy-review artifacts are allowed until the phase-level posture is explicit.

## 2026-03-30 V1.5 phase switch and candidacy protocol freeze
- `v15_phase_charter_v1.json`: owner-approved phase switch opened `V1.5 Retained-Feature Candidacy Review` after `V1.4` entered waiting state.
- `v15_feature_candidacy_protocol_v1.json`: froze the first bounded admissibility protocol for retained-feature candidacy review.
- Current `V1.5` posture is review-only: bounded report-only context features may be reviewed for candidacy, but retained-feature promotion and strategy integration remain disallowed.
- The next legal step is per-feature admissibility review, not promotion or model work.
## 2026-03-30 V1.5 admissibility review and phase closure
- `v15_feature_admissibility_review_v1.json`: reviewed all `5` bounded report-only context features.
- Current candidacy split is `4 allow_provisional_candidacy_review`, `1 hold_for_more_evidence`, `0 reject_candidacy`.
- `v15_phase_check_v1.json`: `V1.5` remains review-only and below promotion threshold.
- `v15_phase_closure_check_v1.json`: `V1.5` success criteria are satisfied as bounded candidacy-review work, so the phase enters explicit waiting state.