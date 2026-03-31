# V1.12G Feature Schema V2

- Mission: freeze the minimum semantic expansion needed after `V1.12F`.
- Total feature count: `15`
- Newly added semantic features:
  - `catalyst_freshness_state`
  - `cross_day_catalyst_persistence`
  - `theme_breadth_confirmation_proxy`
- Intended purpose:
  - separate fresh vs stale catalyst conditions
  - separate one-day catalyst shock from cross-day persistence
  - give a lightweight breadth confirmation proxy without leaking execution-level variables
- Boundary:
  - no intraday variables
  - no label rewrite
  - no scope widening
