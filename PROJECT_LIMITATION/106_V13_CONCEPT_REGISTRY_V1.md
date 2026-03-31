# 106 V13 Concept Registry V1

## Mission
- Build the first bounded concept registry from seed rows, source support, and confidence rules.

## In Scope
- concept seed rows
- concept source layer
- confidence and symbol-link rules

## Out Of Scope
- direct strategy integration
- wide ingestion
- model work

## Success Criteria
- Produce a consumable bounded registry that keeps unresolved link-mode proof below `core_confirmed`.

## Stop Criteria
- If the registry would require unstated symbol-link assumptions to look stronger than it is, stop and keep rows provisional.

## Handoff Condition
- After this registry, the next legal action is bounded manual link-mode assignment.
