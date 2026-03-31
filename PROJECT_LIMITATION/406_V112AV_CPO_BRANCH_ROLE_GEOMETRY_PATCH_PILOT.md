# V1.12AV CPO Branch Role Geometry Patch Pilot

## Purpose
- Repair the failure exposed by `V1.12AU`.
- Keep the widened `11`-row geometry.
- Patch only branch-role geometry.

## Result
- `role_state` recovered on widened geometry:
  - `0.8972 -> 1.0000`
- Core targets became stable again.
- Guarded targets stayed stable.

## Meaning
- The branch-row failure in `V1.12AU` was patchable.
- The active question is no longer “are branch rows hopeless?”
- The next question is whether branch rows can move from review-only toward guarded training context.
