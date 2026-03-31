# V1.12AU CPO Bounded Row-Geometry Widen Pilot

## Purpose
- Test one lawful row-geometry widen after `V1.12AT`.
- Add branch review rows only.
- Keep spillover, pending, formal training, and signal rights closed.

## Added rows
- `300570`
- `688498`
- `688313`
- `300757`

## Result
- Row count: `7 -> 11`
- Sample count: `3175`
- Guarded targets stayed stable.
- Core targets did not stay fully stable because `role_state_label` degraded.

## Reading
- Branch rows are still too early for the next training-facing truth layer.
- The active problem is no longer implementation.
- The active problem is branch-role geometry.
