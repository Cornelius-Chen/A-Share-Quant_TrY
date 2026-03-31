# 108 V13 Concept Registry Reclassification V1

## Purpose
- Replace the fully provisional bounded concept registry with a reclassified registry that uses explicit manual `symbol_link_mode` proof.

## In Scope
- bounded reclassification of the current four concept rows
- application of manual link-mode assignments
- confirmation of `core_confirmed` versus `market_confirmed_indirect`

## Out Of Scope
- new concept ingestion
- strategy integration
- retained-feature promotion

## Success Criteria
- produce a bounded reclassified registry
- remove provisional status from the currently assigned rows
- preserve bounded-context guardrails

## Stop Criteria
- if the current rows still lack explicit link-mode proof
- if reclassification would require wider ingestion or unbounded source collection
