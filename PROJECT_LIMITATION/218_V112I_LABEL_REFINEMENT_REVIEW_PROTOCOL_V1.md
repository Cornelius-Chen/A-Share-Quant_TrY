# V1.12I Label Refinement Review Protocol V1

## Candidate Review Gates

1. Candidate substates must show distinct error behavior.
2. Candidate substates must show distinct semantic-v2 profiles.
3. Candidate substates must reduce review confusion without fragmenting the sample too far.

## Rejection Gates

- Reject if buckets only reflect symbol identity rather than stage meaning.
- Reject if buckets do not carry different semantic-v2 patterns.
- Reject if the split would create tiny unstable shards with little review value.

## Review Questions

- Does `high_level_consolidation` contain at least one candidate substate with clearly different semantic-v2 meaning?
- Would a bounded split improve decision quality more than further feature refinement alone?
- Can the candidate split remain review-only first rather than pretending to legislate a new schema immediately?
