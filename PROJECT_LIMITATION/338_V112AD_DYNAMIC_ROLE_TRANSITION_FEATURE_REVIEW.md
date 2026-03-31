# V1.12AD CPO Dynamic Role-Transition Feature Review

## Goal
- Upgrade static role buckets into a stage-conditioned role-transition review layer.
- Preserve the fact that a row may be:
  - leader in one window
  - challenger in another
  - spillover or maturity marker later
- Keep the output review-only.

## Why This Matters
- Static `leader / adjacent / branch / spillover` language is not enough for:
  - re-ignition
  - late-cycle catch-up
  - role demotion
  - role replacement
- Future trading and future modeling both need dynamic role reading, not only timeless role labels.

## Governance Boundary
- No automatic feature promotion.
- No automatic label freeze.
- No automatic training rights.
- No automatic role replacement.
