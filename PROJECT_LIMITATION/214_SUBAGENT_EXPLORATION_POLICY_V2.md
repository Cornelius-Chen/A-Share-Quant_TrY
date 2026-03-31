# Subagent Exploration Policy V2

- Mission: let subagents generate reviewable candidate structure and bounded experiment outputs without taking over governance.
- Subagent task taxonomy:
  - `exploration`: bounded new attempts that may fail completely
  - `drafting`: candidate splits, candidate substates, candidate feature drafts
  - `structuring`: organize errors, stages, samples, and feature behavior into reviewable objects
  - `execution`: run fixed experiments and fixed reports under frozen rules

## Hard Limits
- max parallel subagents: `2`
- max tasks per round: `3`
- default compute posture: low
- no heavy-model escalation
- no automatic scope widening
- no label rewrite
- no phase-direction judgment
- no more than `1` unreviewed subagent batch

## Mandatory Review
- Review cadence depends on task type:
  - `structuring` and `execution`:
    - review by bounded volume or bounded time window
    - default trigger: `3` tasks or `2` days
  - `drafting` and `exploration`:
    - review by bounded thematic stage or milestone
    - default trigger: one thematic batch
- After each completed batch, mainline must review:
  - whether the outputs changed the future decision basis
  - whether any candidate draft should be discarded
  - whether any candidate draft is worth bounded follow-up
- No second subagent batch may open before this review.

## Forbidden Governance Transfer
- subagents may not:
  - define or freeze formal labels
  - promote features into the formal registry
  - define strategy signals
  - define execution timing logic
  - choose phase direction
