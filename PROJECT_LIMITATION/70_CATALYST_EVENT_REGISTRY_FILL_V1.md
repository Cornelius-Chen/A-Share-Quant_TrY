# 70. Catalyst Event Registry Fill V1

## Purpose

The catalyst branch now has:

1. a schema
2. a bounded seed sample

It still needs a first actual fill step.

This fill intentionally begins with local market-context mappings rather than a
wide source-ingestion pipeline.

## Fill Posture

The first fill is:

1. `market-context-only`
2. `official-source-unresolved`
3. `bounded and auditable`

This means the branch now fills:

1. theme-versus-sector scope
2. mapped context name
3. market-context event type

while still leaving:

1. official source authority
2. policy scope
3. execution strength
4. rumor risk

for the next manual or semi-manual layer.

## Why This Matters

This avoids two bad moves:

1. pretending we already have authoritative news mapping
2. delaying all progress until a full source-ingestion pipeline exists

## Intended Next Step

After this fill:

1. manually or semi-manually add authoritative source references where possible
2. then run the first bounded catalyst-context audit
