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
from a_share_quant.backtest.report import write_report
from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import load_daily_bars_from_csv, load_signals_from_csv
from a_share_quant.data.universe import UniverseFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal A-share backtest.")
    parser.add_argument(
        "--config",
        default="config/demo_backtest.yaml",
        help="Path to the backtest YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)

    bars = load_daily_bars_from_csv(Path(config["paths"]["bars_csv"]))
    signals = load_signals_from_csv(Path(config["paths"]["signals_csv"]))
    filtered_bars = UniverseFilter.from_config(config["universe"]).apply(bars)
    if not filtered_bars:
        raise ValueError("Universe filters removed all bars. Check data or config.")

    registry = RunRegistry(
        runs_dir=Path(config["paths"]["runs_dir"]),
        reports_dir=Path(config["paths"]["reports_dir"]),
    )
    run_record = registry.create_run(
        config_path=config_path,
        protocol_version=config["project"]["protocol_version"],
        run_type="baseline",
        strategy_family="manual_signals",
        notes="Demo backtest run from CSV market bars and signals.",
    )

    engine = BacktestEngine(
        initial_cash=float(config["backtest"]["initial_cash"]),
        cost_model=CostModel.from_config(config["cost_model"]),
        limit_model=LimitModel.from_config(config["limit_model"]),
        price_field=str(config["backtest"].get("price_field", "open")),
    )
    result = engine.run(filtered_bars, signals)

    report_path = write_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        run_id=run_record.run_id,
        result=result,
    )
    registry.finalize_run(
        record=run_record,
        result=result,
        report_path=report_path,
        data_source=str(config["paths"]["bars_csv"]),
        data_range={
            "start": min(bar.trade_date.isoformat() for bar in filtered_bars),
            "end": max(bar.trade_date.isoformat() for bar in filtered_bars),
        },
        config_paths=[str(config_path)],
    )

    print(f"Run complete: {run_record.run_id}")
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
