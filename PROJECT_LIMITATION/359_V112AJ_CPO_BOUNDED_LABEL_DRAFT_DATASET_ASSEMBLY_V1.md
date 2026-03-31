# V1.12AJ CPO Bounded Label-Draft Dataset Assembly V1

## Row Split
- truth-candidate rows: `7`
  - primary: `3`
  - secondary: `4`
- context-only rows: `13`
  - review support
  - overlay only
  - excluded pending

## Label Bundle Split
- ready labels: `3`
- guarded labels: `5`
- review-only future labels: `1`
- confirmed-only review labels: `1`

## Main Constraint
- only ready + guarded labels may enter the truth-candidate bundle
- review-only and confirmed-only labels remain outside draft truth
