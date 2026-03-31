## V1.12BC Result

- Objective tracks frozen: `3`
- No-leak tracks: `2`
- Oracle track: `1`
- Model-scope levels: `3`
- Marginal stop threshold: `0.005`
- Marginal stop patience: `3`

### Track split
- `oracle_upper_bound_track`
  - hindsight benchmark only
  - may use future information
  - cannot train models or generate signals
- `aggressive_no_leak_black_box_track`
  - no-leak experimental portfolio
  - maximize total return
- `neutral_selective_no_leak_track`
  - no-leak experimental portfolio
  - optimize return/drawdown and profit factor
  - cash is allowed

### Required output bundle
- equity curve
- drawdown curve
- trade process trace
- portfolio plot bundle

### Boundary
- formal training: closed
- formal signal generation: closed
