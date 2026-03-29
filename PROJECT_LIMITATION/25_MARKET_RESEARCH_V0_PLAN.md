# Market Research v0 Plan

## Purpose

`market_research_v0` is an intermediate expansion pack between the current
small research packs and a future full-market pack.

It exists to improve market-representation without immediately taking on the
full noise, maintenance cost, and theme-mapping fragility of all-A-share
coverage.

## Why not full market now

The current repo still has unresolved theme-data issues:

1. concept coverage gaps remain
2. concept concentration is still too high
3. the theme ontology is still a bootstrap heuristic, not a final market-wide
   semantic layer

Going straight to full-market coverage now would scale these issues up faster
than it would improve research truthfulness.

## Design principles

`market_research_v0` should be:

1. larger than `baseline_research_v1`
2. broader than `theme_research_v1`
3. still interpretable by bucket
4. biased toward liquid, representative, and repeatedly market-relevant names
5. diverse enough to stress the current regime / trend / hierarchy logic

## Composition

The v0 pack should include:

1. benchmark-sensitive financial and large-cap anchors
2. domestic-demand and defensive consumer leaders
3. cyclical / energy / materials representatives
4. core technology and optical-chain names
5. new-energy leaders and diffusion names
6. theme-heavy growth and lithium-related names
7. pharma / healthcare anchors plus theme-sensitive biotech names

## Explicit non-goals

`market_research_v0` is not intended to:

1. fully represent every A-share industry
2. solve final theme ontology quality
3. replace `baseline_research_v1` or `theme_research_v1`
4. become the final validation pack for live-readiness

## Role in the roadmap

This pack should answer:

1. whether the current research conclusions survive a broader liquid universe
2. whether baseline/theme branch behavior still separates in a wider setting
3. whether concept-mapping v2 holds up once mixed with broader market anchors

Only after this pack becomes stable should the repo consider:

1. a larger `market_research_v1`
2. broader walk-forward validation on mixed universes
3. eventual full-market expansion
