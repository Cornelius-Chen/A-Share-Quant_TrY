# V1.10A Probe Protocol V1

## Scope
- target feature: `policy_followthrough_support`
- source pool: closed followthrough-like lanes with policy or industry context
- sample limit: `2`

## Non-Redundancy Rule
- must be outside the current `300750` symbol-family anchor
- must not reuse the same event-day same-symbol cluster
- must not rely on already-admitted `V1.8C` cases
