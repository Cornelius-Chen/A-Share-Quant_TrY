# 69. Catalyst Event Registry Seed V1

## Purpose

Schema alone is not enough.

The catalyst branch needs a first bounded sample of rows that can later be
filled with source-level event information.

This artifact provides that seed.

## Seed Composition

The first seed intentionally mixes:

1. opening-led lanes
2. persistence-led lanes
3. carry-row-present cases

This keeps the sample auditable while still covering the lane families that
matter most for the catalyst-persistence hypothesis.

## Why This Matters

The catalyst branch should not begin with a wide news crawl.

It should begin with:

1. already-closed lanes
2. already-frozen carry rows
3. a small sample that can be manually or semi-manually enriched

That keeps the branch explainable and prevents narrative drift.

## Intended Next Step

After this seed:

1. fill source-level event fields for the seeded rows
2. attach market-confirmation and persistence context
3. only then run the first bounded catalyst-context audit
