from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _is_positive_row(row: dict[str, Any]) -> bool:
    ctx = str(row.get("action_context"))
    af = str(row.get("action_favored_3d")) == "True"
    exp = _to_float(row.get("expectancy_proxy_3d"))
    adv = _to_float(row.get("max_adverse_return_3d"))
    if ctx == "reduce_vs_hold":
        return af and _to_float(row.get("reduce_payoff_decay_vs_hold_proxy_3d"), default=999.0) < 0.0
    if ctx == "add_vs_hold":
        return af and exp > 0.0 and adv > -0.04
    if ctx == "entry_vs_skip":
        return af and exp > 0.0
    if ctx == "close_vs_hold":
        return af and exp < -0.05 and adv < -0.08
    return False


def _is_positive_reduce(row: dict[str, Any]) -> bool:
    return str(row.get("action_context")) == "reduce_vs_hold" and _is_positive_row(row)


def _zscore(value: float, mean_value: float, std_value: float) -> float:
    if std_value == 0.0:
        return 0.0
    return (value - mean_value) / std_value


@dataclass(slots=True)
class V121PCpoReduceContextSeparationDiscoveryReport:
    summary: dict[str, Any]
    feature_separation_rows: list[dict[str, Any]]
    candidate_score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_separation_rows": self.feature_separation_rows,
            "candidate_score_rows": self.candidate_score_rows,
            "interpretation": self.interpretation,
        }


class V121PCpoReduceContextSeparationDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _joined_rows(self) -> list[dict[str, Any]]:
        base_rows = _load_csv_rows(
            self.repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv"
        )
        daily_basic_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv"
            )
        }
        moneyflow_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv"
            )
        }

        joined_rows: list[dict[str, Any]] = []
        for row in base_rows:
            if str(row.get("action_context")) not in {"reduce_vs_hold", "add_vs_hold", "entry_vs_skip", "close_vs_hold"}:
                continue
            if not _is_positive_row(row):
                continue
            key = (str(row["signal_trade_date"]).replace("-", ""), str(row["symbol"]))
            daily_basic = daily_basic_rows.get(key)
            moneyflow = moneyflow_rows.get(key)
            if daily_basic is None or moneyflow is None:
                continue
            merged = dict(row)
            merged.update(
                {
                    "turnover_rate_f": _to_float(daily_basic.get("turnover_rate_f")),
                    "volume_ratio": _to_float(daily_basic.get("volume_ratio")),
                    "buy_lg_amount": _to_float(moneyflow.get("buy_lg_amount")),
                    "sell_lg_amount": _to_float(moneyflow.get("sell_lg_amount")),
                    "buy_elg_amount": _to_float(moneyflow.get("buy_elg_amount")),
                    "sell_elg_amount": _to_float(moneyflow.get("sell_elg_amount")),
                }
            )
            total_buy = merged["buy_lg_amount"] + merged["buy_elg_amount"]
            total_sell = merged["sell_lg_amount"] + merged["sell_elg_amount"]
            merged["large_sell_buy_ratio"] = (total_sell + 1.0) / (total_buy + 1.0)
            joined_rows.append(merged)
        return joined_rows

    def analyze(self) -> V121PCpoReduceContextSeparationDiscoveryReport:
        rows = self._joined_rows()
        positive_rows = [row for row in rows if _is_positive_reduce(row)]
        negative_rows = [row for row in rows if not _is_positive_reduce(row)]

        raw_feature_names = (
            "board_avg_return",
            "board_breadth",
            "turnover_rate_f",
            "volume_ratio",
            "large_sell_buy_ratio",
        )
        feature_separation_rows: list[dict[str, Any]] = []
        for feature_name in raw_feature_names:
            pos_mean = sum(_to_float(row.get(feature_name)) for row in positive_rows) / len(positive_rows)
            neg_mean = sum(_to_float(row.get(feature_name)) for row in negative_rows) / len(negative_rows)
            feature_separation_rows.append(
                {
                    "feature_name": feature_name,
                    "positive_mean": round(pos_mean, 6),
                    "negative_mean": round(neg_mean, 6),
                    "mean_gap_positive_minus_negative": round(pos_mean - neg_mean, 6),
                    "preferred_direction": "higher_is_better" if pos_mean > neg_mean else "lower_is_better",
                    "abs_gap": round(abs(pos_mean - neg_mean), 6),
                }
            )
        feature_separation_rows.sort(key=lambda row: row["abs_gap"], reverse=True)

        board_avg_values = [_to_float(row["board_avg_return"]) for row in rows]
        board_breadth_values = [_to_float(row["board_breadth"]) for row in rows]
        turnover_values = [_to_float(row["turnover_rate_f"]) for row in rows]
        volume_ratio_values = [_to_float(row["volume_ratio"]) for row in rows]
        sell_buy_values = [_to_float(row["large_sell_buy_ratio"]) for row in rows]

        board_avg_mean = sum(board_avg_values) / len(board_avg_values)
        board_breadth_mean = sum(board_breadth_values) / len(board_breadth_values)
        turnover_mean = sum(turnover_values) / len(turnover_values)
        volume_ratio_mean = sum(volume_ratio_values) / len(volume_ratio_values)
        sell_buy_mean = sum(sell_buy_values) / len(sell_buy_values)

        board_avg_std = math.sqrt(sum((value - board_avg_mean) ** 2 for value in board_avg_values) / len(board_avg_values)) or 1.0
        board_breadth_std = math.sqrt(sum((value - board_breadth_mean) ** 2 for value in board_breadth_values) / len(board_breadth_values)) or 1.0
        turnover_std = math.sqrt(sum((value - turnover_mean) ** 2 for value in turnover_values) / len(turnover_values)) or 1.0
        volume_ratio_std = math.sqrt(sum((value - volume_ratio_mean) ** 2 for value in volume_ratio_values) / len(volume_ratio_values)) or 1.0
        sell_buy_std = math.sqrt(sum((value - sell_buy_mean) ** 2 for value in sell_buy_values) / len(sell_buy_values)) or 1.0

        candidate_score_rows: list[dict[str, Any]] = []
        for row in rows:
            board_avg_z = _zscore(_to_float(row["board_avg_return"]), board_avg_mean, board_avg_std)
            board_breadth_z = _zscore(_to_float(row["board_breadth"]), board_breadth_mean, board_breadth_std)
            turnover_z = _zscore(_to_float(row["turnover_rate_f"]), turnover_mean, turnover_std)
            volume_ratio_z = _zscore(_to_float(row["volume_ratio"]), volume_ratio_mean, volume_ratio_std)
            sell_buy_z = _zscore(_to_float(row["large_sell_buy_ratio"]), sell_buy_mean, sell_buy_std)
            score = -board_avg_z - board_breadth_z + 0.75 * turnover_z - 0.75 * sell_buy_z - 0.25 * volume_ratio_z
            candidate_score_rows.append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "action_context": str(row["action_context"]),
                    "positive_reduce_label": _is_positive_reduce(row),
                    "board_avg_return": round(_to_float(row["board_avg_return"]), 6),
                    "board_breadth": round(_to_float(row["board_breadth"]), 6),
                    "turnover_rate_f": round(_to_float(row["turnover_rate_f"]), 6),
                    "volume_ratio": round(_to_float(row["volume_ratio"]), 6),
                    "large_sell_buy_ratio": round(_to_float(row["large_sell_buy_ratio"]), 6),
                    "reduce_context_separation_score_candidate": round(score, 6),
                }
            )
        candidate_score_rows.sort(
            key=lambda row: (not bool(row["positive_reduce_label"]), -_to_float(row["reduce_context_separation_score_candidate"]))
        )

        positive_mean = sum(
            _to_float(row["reduce_context_separation_score_candidate"]) for row in candidate_score_rows if row["positive_reduce_label"]
        ) / len(positive_rows)
        negative_mean = sum(
            _to_float(row["reduce_context_separation_score_candidate"]) for row in candidate_score_rows if not row["positive_reduce_label"]
        ) / len(negative_rows)

        summary = {
            "acceptance_posture": "freeze_v121p_cpo_reduce_context_separation_discovery_v1",
            "candidate_discriminator_name": "reduce_context_separation_score_candidate",
            "positive_reduce_row_count": len(positive_rows),
            "comparator_positive_row_count": len(negative_rows),
            "candidate_score_mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
            "top_separation_feature": feature_separation_rows[0]["feature_name"],
            "recommended_next_posture": "externally_audit_reduce_context_separation_before_any_status_change",
        }
        interpretation = [
            "V1.21P stops treating reduce specificity as a broad risk problem and turns it into an explicit context-separation problem.",
            "The branch tries to separate positive reduce rows from positive add, entry, and close rows using board deterioration plus participation shape rather than replay outcomes.",
            "This is still discovery-only and should die quickly if the external action-context audit is weak.",
        ]
        return V121PCpoReduceContextSeparationDiscoveryReport(
            summary=summary,
            feature_separation_rows=feature_separation_rows,
            candidate_score_rows=candidate_score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121PCpoReduceContextSeparationDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121PCpoReduceContextSeparationDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121p_cpo_reduce_context_separation_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
