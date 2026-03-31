## V1.12BF Result

- Track: `aggressive_no_leak_black_box_track`
- Training-layer rows: `10`
- Samples: `2935`
- Trades: `20`
- Equity-curve points: `552`
- Drawdown-curve points: `552`

### Frozen result
- `no_leak_enforced = True`
- `total_return = 1.5405`
- `max_drawdown = -0.6941`
- `profit_factor = 2.1629`
- `hit_rate = 0.4`
- `cash_ratio = 0.2391`

### Oracle gap
- oracle total return: `752.0861`
- aggressive no-leak total return: `1.5405`
- return gap: `750.5456`
- oracle trade count: `25`
- aggressive trade count: `20`

### Key read
- The aggressive no-leak line is profitable, but still dramatically below the hindsight ceiling.
- The bigger warning is not just the return gap.
- The bigger warning is the drawdown:
  - oracle `-0.3774`
  - aggressive no-leak `-0.6941`
- So the next problem is no longer "can it make money at all?"
- The next problem is how to reduce gap and drawdown without reintroducing leakage.

### Boundary
- formal training: closed
- formal signal generation: closed
- this remains a bounded experimental portfolio line
