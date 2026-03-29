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
from a_share_quant.strategy.dataset_comparison import DatasetComparisonRunner, DatasetPack


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare strategy suites across multiple dataset packs.")
    parser.add_argument(
        "--config",
        default="config/dataset_comparison.yaml",
        help="Path to the dataset-comparison YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)

    engine = BacktestEngine(
        initial_cash=float(config["backtest"]["initial_cash"]),
        cost_model=CostModel.from_config(config["cost_model"]),
        limit_model=LimitModel.from_config(config["limit_model"]),
        price_field=str(config["backtest"].get("price_field", "open")),
    )
    dataset_packs: list[DatasetPack] = []
    data_ranges: list[dict[str, str]] = []
    for dataset_payload in config["datasets"]:
        dataset_name = str(dataset_payload["dataset_name"])
        dataset_config_path = Path(dataset_payload["config_path"])
        dataset_config = load_yaml_config(dataset_config_path)
        bars = load_daily_bars_from_csv(Path(dataset_config["paths"]["bars_csv"]))
        filtered_bars = UniverseFilter.from_config(dataset_config["universe"]).apply(bars)
        if not filtered_bars:
            raise ValueError(f"Universe filters removed all bars for dataset {dataset_name}.")

        index_bars = load_daily_bars_from_csv(Path(dataset_config["paths"]["index_bars_csv"]))
        sector_snapshots = load_sector_snapshots_from_csv(Path(dataset_config["paths"]["sector_snapshots_csv"]))
        stock_snapshots = load_stock_snapshots_from_csv(Path(dataset_config["paths"]["stock_snapshots_csv"]))
        mainline_windows = load_mainline_windows_from_csv(Path(dataset_config["paths"]["mainline_windows_csv"]))
        dataset_packs.append(
            DatasetPack(
                dataset_name=dataset_name,
                config=dataset_config,
                bars=filtered_bars,
                index_bars=index_bars,
                sector_snapshots=sector_snapshots,
                stock_snapshots=stock_snapshots,
                mainline_windows=mainline_windows,
            )
        )
        data_ranges.append(
            {
                "dataset_name": dataset_name,
                "start": min(bar.trade_date.isoformat() for bar in filtered_bars),
                "end": max(bar.trade_date.isoformat() for bar in filtered_bars),
            }
        )

    comparison = DatasetComparisonRunner(engine=engine).run(
        strategy_names=[str(item) for item in config["strategy"]["strategy_names"]],
        dataset_packs=dataset_packs,
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
        run_type="dataset_comparison",
        strategy_family="dataset_comparison",
        notes="Compare strategy-family suites across baseline and theme dataset packs.",
    )
    report_path = write_comparison_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        run_id=run_record.run_id,
        comparisons=rows,
        extras={
            "dataset_names": [pack.dataset_name for pack in dataset_packs],
            "comparison_basis": "shared_strategy_family_cross_dataset_comparison",
        },
    )
    registry.finalize_run(
        record=run_record,
        result=comparison.suites[-1]["suite"].results[-1].backtest_result,
        report_path=report_path,
        data_source="multiple_dataset_packs",
        data_range={"packs": data_ranges},
        config_paths=[str(config_path)] + [str(item["config_path"]) for item in config["datasets"]],
        summary_override=aggregate_summary,
    )

    print(f"Run complete: {run_record.run_id}")
    print(f"Comparison report: {report_path}")
    print(f"Aggregate summary: {aggregate_summary}")
    for row in rows:
        print(f"{row['dataset_name']} @ {row['strategy_name']}: {row['summary']}")


if __name__ == "__main__":
    main()
