# A-Share-Quant_TrY

Engineering-grade A-share research repo focused on offline backtesting and
mainline trend strategy comparison.

## Current scope

The repository currently contains:

- binding governance documents under `PROJECT_LIMITATION/`
- a first-pass Python package skeleton under `src/a_share_quant/`
- a minimal daily-bar backtest backbone
- early `regime` modules for sample segmentation, sector scoring, and attack permission
- early `trend` modules for hierarchy ranking, trend-filter candidates, and entry-rule candidates
- first-pass holding/exit modules and comparable Strategy A/B/C wrappers
- custom metric implementations for `mainline_capture_ratio` and `missed_mainline_count`
- experiment run registration and JSON reporting
- suite comparison reports with ranking, segment overview, trade overview, and window breakdowns
- configurable segmentation methods across `index_trend`, `sector_trend`, and `resonance`
- sample CSV data and a demo config
- tests for the phase-1 foundation

## Quick start

Create an environment and install the package in editable mode:

```bash
python -m pip install -e .[dev]
```

Run the demo backtest:

```bash
python scripts/run_backtest.py --config config/demo_backtest.yaml
```

Run the demo strategy experiment:

```bash
python scripts/run_strategy_experiment.py --config config/demo_strategy_experiment.yaml
```

Run the comparable A/B/C strategy suite:

```bash
python scripts/run_strategy_suite.py --config config/demo_strategy_suite.yaml
```

Run a segmentation-method comparison for one strategy family:

```bash
python scripts/run_segmentation_comparison.py --config config/demo_segmentation_comparison.yaml
```

Run tests:

```bash
pytest
```
