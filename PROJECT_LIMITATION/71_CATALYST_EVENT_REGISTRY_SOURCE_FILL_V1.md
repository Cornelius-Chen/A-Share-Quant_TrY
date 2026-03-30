# 71. Catalyst Event Registry Source Fill V1

## Purpose

After the first market-context fill, the catalyst branch still needs a
source-level layer.

This artifact introduces that layer cautiously:

1. resolve official or high-trust sources where the context is clear
2. leave the rest explicitly unresolved

## Fill Posture

The first source fill is intentionally:

1. partial
2. official-or-high-trust where available
3. unresolved elsewhere

This prevents the branch from pretending that all catalyst context can already
be fully sourced.

## Why This Matters

A bounded catalyst audit needs more than board context, but it still should not
be built on forced guesses.

This step keeps the branch honest by distinguishing:

1. rows with a reasonable official/industry context reference
2. rows that still need later manual sourcing

## Intended Next Step

After this partial source fill:

1. compare resolved versus unresolved rows in a bounded catalyst-context audit
2. decide whether catalyst context changes any factor decision boundary
