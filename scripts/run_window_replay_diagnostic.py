from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.backtest.cost_model import CostModel
from a_share_quant.backtest.engine import BacktestEngine
from a_share_quant.backtest.limit_model import LimitModel
from a_share_quant.common.config import load_yaml_config
from a_share_quant.data.loaders import (
    load_daily_bars_from_csv,
    load_mainline_windows_from_csv,
    load_sector_snapshots_from_csv,
    load_stock_snapshots_from_csv,
)
from a_share_quant.data.universe import UniverseFilter
from a_share_quant.strategy.dataset_comparison import DatasetPack
from a_share_quant.strategy.rule_sweep import RuleCandidate
from a_share_quant.strategy.window_replay_diagnostic import (
    ReplayTargetWindow,
    WindowReplayDiagnostic,
    write_window_replay_diagnostic,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay target windows for a few finalists.")
    parser.add_argument(
        "--config",
        default="config/window_replay_diagnostic_v1.yaml",
        help="Path to the window replay diagnostic YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml_config(config_path)

    dataset_config_path = Path(config["dataset"]["config_path"])
    dataset_config = load_yaml_config(dataset_config_path)
    bars = load_daily_bars_from_csv(Path(dataset_config["paths"]["bars_csv"]))
    filtered_bars = UniverseFilter.from_config(dataset_config["universe"]).apply(bars)
    dataset_pack = DatasetPack(
        dataset_name=str(config["dataset"]["dataset_name"]),
        config=dataset_config,
        bars=filtered_bars,
        index_bars=load_daily_bars_from_csv(Path(dataset_config["paths"]["index_bars_csv"])),
        sector_snapshots=load_sector_snapshots_from_csv(Path(dataset_config["paths"]["sector_snapshots_csv"])),
        stock_snapshots=load_stock_snapshots_from_csv(Path(dataset_config["paths"]["stock_snapshots_csv"])),
        mainline_windows=load_mainline_windows_from_csv(Path(dataset_config["paths"]["mainline_windows_csv"])),
    )
    window_lookup = {
        window.window_id: window
        for window in dataset_pack.mainline_windows
    }

    engine = BacktestEngine(
        initial_cash=float(config["backtest"]["initial_cash"]),
        cost_model=CostModel.from_config(config["cost_model"]),
        limit_model=LimitModel.from_config(config["limit_model"]),
        price_field=str(config["backtest"].get("price_field", "open")),
    )
    candidates = [
        RuleCandidate(
            candidate_name=str(item["candidate_name"]),
            description=str(item["description"]) if item.get("description") is not None else None,
            override=dict(item.get("override", {})),
        )
        for item in config["candidates"]
    ]
    target_windows = [
        ReplayTargetWindow(
            window_id=str(item["window_id"]),
            symbol=str(item["symbol"]),
            start_date=date.fromisoformat(str(item["start_date"])),
            end_date=date.fromisoformat(str(item["end_date"])),
            capturable_return=float(window_lookup[str(item["window_id"])].capturable_return),
        )
        for item in config["analysis"]["windows"]
    ]

    diagnostic = WindowReplayDiagnostic().analyze(
        dataset_pack=dataset_pack,
        strategy_names=[str(item) for item in config["strategy"]["strategy_names"]],
        candidates=candidates,
        target_windows=target_windows,
        lookback_days=int(config["analysis"].get("lookback_days", 5)),
        incumbent_name=str(config["comparison"]["incumbent_candidate"]),
        challenger_name=str(config["comparison"]["challenger_candidate"]),
        engine=engine,
    )
    report_path = write_window_replay_diagnostic(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=diagnostic,
        extras={
            "dataset_name": dataset_pack.dataset_name,
            "strategy_names": [str(item) for item in config["strategy"]["strategy_names"]],
            "candidate_names": [candidate.candidate_name for candidate in candidates],
        },
    )
    print(f"Window replay diagnostic: {report_path}")
    print(f"Summary: {diagnostic.summary}")


if __name__ == "__main__":
    main()
