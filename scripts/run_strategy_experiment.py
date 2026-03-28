from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.audit.run_registry import RunRegistry
from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.backtest.report import write_report
from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import (
    load_daily_bars_from_csv,
    load_mainline_windows_from_csv,
    load_sector_snapshots_from_csv,
    load_stock_snapshots_from_csv,
)
from a_share_quant.data.universe import UniverseFilter
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a strategy-family experiment.")
    parser.add_argument(
        "--config",
        default="config/demo_strategy_experiment.yaml",
        help="Path to the strategy experiment YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)

    bars = load_daily_bars_from_csv(Path(config["paths"]["bars_csv"]))
    index_bars = []
    if "index_bars_csv" in config["paths"]:
        index_bars = load_daily_bars_from_csv(Path(config["paths"]["index_bars_csv"]))
    sector_snapshots = load_sector_snapshots_from_csv(Path(config["paths"]["sector_snapshots_csv"]))
    stock_snapshots = load_stock_snapshots_from_csv(Path(config["paths"]["stock_snapshots_csv"]))
    mainline_windows = load_mainline_windows_from_csv(Path(config["paths"]["mainline_windows_csv"]))
    filtered_bars = UniverseFilter.from_config(config["universe"]).apply(bars)
    if not filtered_bars:
        raise ValueError("Universe filters removed all bars. Check data or config.")

    engine = BacktestEngine(
        initial_cash=float(config["backtest"]["initial_cash"]),
        cost_model=CostModel.from_config(config["cost_model"]),
        limit_model=LimitModel.from_config(config["limit_model"]),
        price_field=str(config["backtest"].get("price_field", "open")),
    )
    runner = StrategyExperimentRunner.from_config(engine=engine, config=config)
    strategy_name = str(config["strategy"]["strategy_name"])
    experiment = runner.run(
        strategy_name=strategy_name,
        bars=filtered_bars,
        index_bars=index_bars,
        sector_snapshots=sector_snapshots,
        stock_snapshots=stock_snapshots,
        mainline_windows=mainline_windows,
    )

    registry = RunRegistry(
        runs_dir=Path(config["paths"]["runs_dir"]),
        reports_dir=Path(config["paths"]["reports_dir"]),
    )
    run_record = registry.create_run(
        config_path=config_path,
        protocol_version=config["project"]["protocol_version"],
        run_type="strategy_experiment",
        strategy_family=strategy_name,
        notes="Demo strategy-family experiment with regime, trend, and custom mainline metrics.",
    )
    report_path = write_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        run_id=run_record.run_id,
        result=experiment.backtest_result,
        extras={
            "generated_signals": [asdict(signal) for signal in experiment.signals],
            "segment_count": len(experiment.segments),
            "permission_count": len(experiment.permissions),
            "segment_overview": experiment.segment_overview,
            "trade_overview": experiment.trade_overview,
            "window_breakdown": experiment.window_breakdown,
        },
    )
    registry.finalize_run(
        record=run_record,
        result=experiment.backtest_result,
        report_path=report_path,
        data_source=str(config["paths"]["bars_csv"]),
        data_range={
            "start": min(bar.trade_date.isoformat() for bar in filtered_bars),
            "end": max(bar.trade_date.isoformat() for bar in filtered_bars),
        },
        config_paths=[str(config_path)],
    )

    print(f"Run complete: {run_record.run_id}")
    print(f"Strategy: {strategy_name}")
    print(f"Summary: {experiment.backtest_result.summary}")
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
