## 2026-03-30 V1.12BF CPO aggressive no-leak black-box portfolio pilot

### Why this phase exists
- After freezing the oracle benchmark, the project needed its first truly no-leak portfolio line.
- The goal was not elegance or explanation first.
- The goal was to see how much of the cycle could be captured with only point-in-time visible information.

### What this phase did
- Used the frozen `10`-row guarded CPO layer.
- Enforced no-leak by training only on dates whose full `20`-day future window had already elapsed.
- Ran a single-position-or-cash aggressive black-box portfolio line.
- Produced:
  - trade process trace
  - equity curve
  - drawdown curve
  - explicit oracle-gap rows

### Why this matters
- It is the first real answer to:
  - how far a lawful no-leak CPO line still sits from the hindsight ceiling
- It also exposes whether the remaining gap looks like missing factors, missing regime context, or a portfolio decision problem.
