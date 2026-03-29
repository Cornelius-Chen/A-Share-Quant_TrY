from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.audit.run_registry import RunRegistry
from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.backtest.report import write_comparison_report
from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import (
    load_daily_bars_from_csv,
    load_mainline_windows_from_csv,
    load_sector_snapshots_from_csv,
    load_stock_snapshots_from_csv,
)
from a_share_quant.data.universe import UniverseFilter
from a_share_quant.strategy.matrix_comparison import StrategyMatrixComparisonRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare multiple strategies across segmentation methods.")
    parser.add_argument(
        "--config",
        default="config/demo_strategy_matrix.yaml",
        help="Path to the strategy matrix YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)

    bars = load_daily_bars_from_csv(Path(config["paths"]["bars_csv"]))
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
    matrix_runner = StrategyMatrixComparisonRunner(engine=engine, config=config)
    strategy_names = [str(item) for item in config["strategy"]["strategy_names"]]
    segmentation_methods = [str(item) for item in config["regime"]["segmentation_methods"]]
    comparison = matrix_runner.run(
        strategy_names=strategy_names,
        segmentation_methods=segmentation_methods,
        bars=filtered_bars,
        index_bars=index_bars,
        sector_snapshots=sector_snapshots,
        stock_snapshots=stock_snapshots,
        mainline_windows=mainline_windows,
    )
    rows = comparison.comparison_rows()
    aggregate_summary = comparison.aggregate_summary()

    registry = RunRegistry(
        runs_dir=Path(config["paths"]["runs_dir"]),
        reports_dir=Path(config["paths"]["reports_dir"]),
    )
    run_record = registry.create_run(
        config_path=config_path,
        protocol_version=config["project"]["protocol_version"],
        run_type="strategy_matrix",
        strategy_family="strategy_matrix",
        notes="Compare strategy families across segmentation methods under one shared config.",
    )
    report_path = write_comparison_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        run_id=run_record.run_id,
        comparisons=rows,
        extras={
            "strategy_names": strategy_names,
            "segmentation_methods": segmentation_methods,
            "comparison_basis": "shared_data_shared_protocol_matrix_comparison",
        },
    )
    registry.finalize_run(
        record=run_record,
        result=comparison.results[-1]["experiment"].backtest_result,
        report_path=report_path,
        data_source=str(config["paths"]["bars_csv"]),
        data_range={
            "start": min(bar.trade_date.isoformat() for bar in filtered_bars),
            "end": max(bar.trade_date.isoformat() for bar in filtered_bars),
        },
        config_paths=[str(config_path)],
        summary_override=aggregate_summary,
    )

    print(f"Run complete: {run_record.run_id}")
    print(f"Comparison report: {report_path}")
    print(f"Aggregate summary: {aggregate_summary}")
    for row in rows:
        print(f"{row['strategy_name']} @ {row['segmentation_method']}: {row['summary']}")


if __name__ == "__main__":
    main()
