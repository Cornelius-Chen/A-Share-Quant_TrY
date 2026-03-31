# 109 V13 Concept Registry Usage Rules V1

## Purpose
- Freeze bounded usage rules for reclassified concept-registry rows so the branch cannot drift into strategy integration.

## In Scope
- bounded context usage priority
- distinction between primary and secondary concept rows
- explicit prohibition of strategy integration

## Out Of Scope
- model training
- signal promotion
- new concept ingestion

## Success Criteria
- define how `core_confirmed` and `market_confirmed_indirect` rows may be consumed
- keep all concept rows outside strategy integration
- prepare the branch for a phase closure check
