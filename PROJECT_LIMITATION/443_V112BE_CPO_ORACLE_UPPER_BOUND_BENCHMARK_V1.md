## V1.12BE Result

- Track: `oracle_upper_bound_track`
- Training-layer rows: `10`
- Samples: `2935`
- Trades: `25`
- Equity-curve points: `551`
- Drawdown-curve points: `551`

### Frozen result
- `future_information_allowed = True`
- `total_return = 752.0861`
- `max_drawdown = -0.3774`
- `profit_factor = inf`
- `hit_rate = 1.0`
- `cash_ratio = 0.0472`

### Key read
- The oracle line is intentionally extreme because it chooses the best available 20-day forward-return path ex post.
- Its value is not realism.
- Its value is to provide a clear hindsight ceiling for later no-leak tracks.

### Boundary
- formal training: closed
- formal signal generation: closed
- no-leak status: not applicable, because this is explicitly hindsight-only
