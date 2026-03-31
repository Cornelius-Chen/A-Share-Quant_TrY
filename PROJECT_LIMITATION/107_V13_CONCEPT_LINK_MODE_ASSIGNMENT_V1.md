# 107 V13 Concept Link Mode Assignment V1

## Mission
- Apply bounded manual link-mode assignments to the provisional concept registry.

## In Scope
- existing concept registry rows
- official or high-trust source-backed manual assignments
- bounded reclassification into `core_confirmed` or `market_confirmed_indirect`

## Out Of Scope
- wide new source hunting
- strategy integration
- model work

## Success Criteria
- Remove `pending_manual_assignment` from the current bounded concept registry without overstating weak concept links.

## Stop Criteria
- If a row cannot be supported by explicit link proof, it must remain indirect or provisional rather than being promoted.

## Handoff Condition
- After manual link-mode assignment, the next legal step is bounded registry reclassification / phase check.
