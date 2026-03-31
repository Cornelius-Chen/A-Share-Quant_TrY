## 2026-03-30 V1.12BE CPO oracle upper-bound benchmark

### Why this phase exists
- The project now has a lawful portfolio-objective protocol and a default 10-row experimental baseline.
- Before opening any no-leak portfolio track, it needs a hindsight-only upper-bound line.

### What this phase did
- Used the frozen `10`-row guarded CPO layer as the benchmark universe.
- Allowed future information because this is the oracle track by design.
- Produced:
  - trade process trace
  - equity curve
  - drawdown curve
  - phase/role capture summaries

### Why this matters
- It tells the project how rich the cycle was under perfect hindsight.
- It also creates a hard comparison target for later aggressive and neutral no-leak portfolio tracks.
- This is a benchmark line, not a trainable or deployable line.
