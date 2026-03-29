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
from a_share_quant.common.config import load_yaml_config, merge_config
from a_share_quant.data.loaders import (
    load_daily_bars_from_csv,
    load_sector_snapshots_from_csv,
    load_stock_snapshots_from_csv,
)
from a_share_quant.regime.mainline_sector_scorer import MainlineSectorScorer
from a_share_quant.strategy.experiment_runner import StrategyExperimentRunner
from a_share_quant.strategy.permission_loss_edge_analysis import (
    PermissionLossEdgeAnalyzer,
    load_json_report,
    write_permission_loss_edge_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a one-date permission-loss edge.")
    parser.add_argument(
        "--config",
        default="config/theme_permission_loss_edge_300750_v1.yaml",
        help="Path to the permission-loss edge YAML config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml_config(Path(args.config))
    dataset_config = load_yaml_config(Path(config["dataset"]["config_path"]))

    engine = BacktestEngine(
        initial_cash=float(config["backtest"]["initial_cash"]),
        cost_model=CostModel.from_config(config["cost_model"]),
        limit_model=LimitModel.from_config(config["limit_model"]),
        price_field=str(config["backtest"].get("price_field", "open")),
    )
    sector_snapshots = load_sector_snapshots_from_csv(Path(dataset_config["paths"]["sector_snapshots_csv"]))
    stock_snapshots = load_stock_snapshots_from_csv(Path(dataset_config["paths"]["stock_snapshots_csv"]))
    index_bars = []
    if "index_bars_csv" in dataset_config["paths"]:
        index_bars = load_daily_bars_from_csv(Path(dataset_config["paths"]["index_bars_csv"]))

    scorer = MainlineSectorScorer()
    sector_scores = scorer.score(sector_snapshots)
    trade_date = str(config["analysis"]["trade_date"])
    symbol = str(config["analysis"]["symbol"])
    ranked_sector_scores = [
        {
            "sector_id": score.sector_id,
            "sector_name": score.sector_name,
            "rank": score.rank,
            "composite_score": score.composite_score,
        }
        for score in sector_scores
        if score.trade_date.isoformat() == trade_date
    ]

    timeline_payload = load_json_report(Path(config["paths"]["timeline_report"]))
    candidate_evaluations: list[dict[str, object]] = []
    for candidate in config["candidates"]:
        candidate_name = str(candidate["candidate_name"])
        merged_config = merge_config(dataset_config, dict(candidate.get("override", {})))
        runner = StrategyExperimentRunner.from_config(engine=engine, config=merged_config)
        segments = runner._build_segments(sector_scores=sector_scores, index_bars=index_bars)
        permissions = runner.permission_engine.evaluate(sector_scores, segments)
        permission = next(
            (item for item in permissions if item.trade_date.isoformat() == trade_date),
            None,
        )
        if permission is None:
            raise ValueError(f"No permission row found for {trade_date} and candidate {candidate_name}.")
        previous_permission = next(
            (
                item
                for item in reversed(permissions)
                if item.trade_date.isoformat() < trade_date and item.is_attack_allowed
            ),
            None,
        )
        top_score = ranked_sector_scores[0] if ranked_sector_scores else None
        second_score = ranked_sector_scores[1] if len(ranked_sector_scores) > 1 else None
        previous_score = next(
            (
                row
                for row in ranked_sector_scores
                if previous_permission is not None
                and row["sector_id"] == previous_permission.approved_sector_id
            ),
            None,
        )
        assignments = runner.hierarchy_ranker.rank(
            stock_snapshots,
            allowed_sector_ids={
                item.approved_sector_id
                for item in permissions
                if item.is_attack_allowed and item.approved_sector_id is not None
            }
            or None,
        )
        assignment = next(
            (
                item
                for item in assignments
                if item.symbol == symbol and item.trade_date.isoformat() == trade_date
            ),
            None,
        )
        candidate_evaluations.append(
            {
                "candidate_name": candidate_name,
                "role": str(candidate["role"]),
                "min_top_score": float(merged_config["regime"].get("min_top_score", 0.0)),
                "min_score_margin": float(merged_config["regime"].get("min_score_margin", 0.0)),
                "switch_margin_buffer": float(merged_config["regime"].get("switch_margin_buffer", 0.0)),
                "permission_allowed": permission.is_attack_allowed,
                "permission_reason": permission.reason,
                "approved_sector_id": permission.approved_sector_id,
                "approved_sector_name": permission.approved_sector_name,
                "approved_score": permission.score,
                "previous_approved_sector_id": (
                    previous_permission.approved_sector_id if previous_permission is not None else None
                ),
                "score_minus_top_threshold": (
                    round(float(top_score["composite_score"]) - float(merged_config["regime"].get("min_top_score", 0.0)), 6)
                    if top_score is not None
                    else None
                ),
                "top_vs_second_margin": (
                    round(float(top_score["composite_score"]) - float(second_score["composite_score"]), 6)
                    if top_score is not None and second_score is not None
                    else None
                ),
                "top_vs_previous_margin": (
                    round(float(top_score["composite_score"]) - float(previous_score["composite_score"]), 6)
                    if top_score is not None and previous_score is not None
                    else None
                ),
                "symbol_assignment_layer": assignment.layer if assignment is not None else None,
                "symbol_assignment_reason": assignment.reason if assignment is not None else None,
            }
        )

    action_rows = []
    for record in timeline_payload.get("candidate_records", []):
        if str(record.get("symbol")) != symbol:
            continue
        record_date = next(
            (item for item in record.get("daily_records", []) if str(item.get("trade_date")) == trade_date),
            None,
        )
        if record_date is None:
            continue
        action_rows.append(
            {
                "candidate_name": str(record["candidate_name"]),
                "strategy_name": str(record["strategy_name"]),
                "permission_allowed": record_date["permission_allowed"],
                "approved_sector_id": record_date["approved_sector_id"],
                "assignment_layer": record_date["assignment_layer"],
                "assignment_reason": record_date["assignment_reason"],
                "emitted_actions": record_date["emitted_actions"],
            }
        )

    result = PermissionLossEdgeAnalyzer().analyze(
        symbol=symbol,
        trade_date=trade_date,
        ranked_sector_scores=ranked_sector_scores,
        candidate_evaluations=candidate_evaluations,
        action_rows=action_rows,
    )
    report_path = write_permission_loss_edge_report(
        reports_dir=Path(config["paths"]["reports_dir"]),
        report_name=str(config["report"]["name"]),
        result=result,
    )
    print(f"Permission-loss edge report: {report_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
