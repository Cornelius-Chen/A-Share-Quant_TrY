## 2026-03-30 V1.12BC CPO portfolio objective protocol

### Why this phase exists
- The project is now close enough to bounded training-facing work that portfolio experimentation needs a hard protocol.
- Without this split, hindsight upper-bound thinking would easily contaminate no-leak model evaluation.

### What this phase did
- Froze `3` objective tracks:
  - `oracle_upper_bound_track`
  - `aggressive_no_leak_black_box_track`
  - `neutral_selective_no_leak_track`
- Froze `3` model-scope levels:
  - stable black box
  - mid black box
  - deep black box
- Froze a hard stop rule:
  - marginal improvement `< 0.5%`
  - for `3` consecutive rounds

### Why this matters
- It separates hindsight benchmarking from lawful no-leak portfolio experimentation.
- It also prevents unlimited model-zoo drift by forcing a marginal-gain stop rule.
- This is a protocol freeze, not a training-rights opening.
