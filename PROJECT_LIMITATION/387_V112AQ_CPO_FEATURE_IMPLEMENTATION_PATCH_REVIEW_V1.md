# V1.12AQ CPO Feature Implementation Patch Review V1

## Result
- `feature_implementation` remains the primary bottleneck.
- `row_geometry` remains secondary, but should not be widened yet.
- Minimum bounded patch scope:
  - `3` daily-board rules
  - `3` future-calendar rules

## Decision
- Patch implementation first.
- Keep row-geometry widen closed for now.
- Formal training and signal generation remain closed.
