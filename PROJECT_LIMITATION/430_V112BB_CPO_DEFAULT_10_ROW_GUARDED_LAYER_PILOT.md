## 2026-03-30 V1.12BB CPO default 10-row guarded-layer pilot

### Why this phase exists
- `V1.12BA` already removed the `7`-row vs `10`-row fork.
- The next lawful step was not another abstract review.
- The next lawful step was to run the actual bounded pilot on the new default `10`-row guarded layer.

### What this phase did
- Used the `10`-row bounded training-facing layer from `V1.12AZ` as the single default pilot layer.
- Reused the validated feature stack:
  - core skeleton features
  - role patch features
  - board/calendar implementation features
  - branch role-geometry patch features
- Compared current pilot behavior against:
  - the old `7`-row core baseline
  - the prior `10`-row guarded-branch pilot

### Why this matters
- It converts the `10`-row layer from a governance decision into a real experimental baseline.
- After this phase, further widen decisions can be judged against one default layer instead of a split baseline.
- This remains report-only and does not open formal training or signal rights.
