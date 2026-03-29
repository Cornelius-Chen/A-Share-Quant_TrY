from __future__ import annotations

import argparse
import sys
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
from a_share_quant.strategy.theme_hierarchy_gap_analysis import (
    ThemeHierarchyGapAnalyzer,
    write_theme_hierarchy_gap_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze theme hierarchy gap blockers.")
    parser.add_argument(
        "--config",
        default="config/theme_hierarchy_gap_analysis_v1.yaml",
        help="Path to the theme hierarchy gap YAML config.",
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

    result = ThemeHierarchyGapAnalyzer().analyze(
        dataset_pack=dataset_pack,
        strategy_name=str(config["strategy"]["strategy_name"]),
        candidates=candidates,
        incumbent_name=str(config["comparison"]["incumbent_candidate"]),
        challenger_name=str(config["comparison"]["challenger_candidate"]),
        admissibility_report_path=Path(config["paths"]["admissibility_report"]),
        lookback_days=int(config["analysis"].get("lookback_days", 5)),
        top_k=int(config["analysis"].get("top_k", 30)),
        engine=engine,
    )
    report_path = write_theme_hierarchy_gap_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
        extras={
            "dataset_name": dataset_pack.dataset_name,
            "strategy_name": str(config["strategy"]["strategy_name"]),
            "candidate_names": [candidate.candidate_name for candidate in candidates],
        },
    )
    print(f"Theme hierarchy gap report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
