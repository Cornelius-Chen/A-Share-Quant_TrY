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


def _is_positive_add(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


def _participation_score(row: dict[str, Any]) -> float:
    return (
        _to_float(row.get("f30_high_time_ratio_rz"))
        + _to_float(row.get("f60_high_time_ratio_rz"))
        + _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_last_bar_volume_share_rz"))
        + _to_float(row.get("f60_close_vs_vwap_rz"))
        + _to_float(row.get("f30_close_vs_vwap_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        - _to_float(row.get("f60_last_bar_return_rz"))
    )


def _zscore(value: float, mean_value: float, std_value: float) -> float:
    if std_value == 0.0:
        return 0.0
    return (value - mean_value) / std_value


@dataclass(slots=True)
class V119RCpoElgSupportOutOfSetFalsePositiveAuditReport:
    summary: dict[str, Any]
    context_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "context_rows": self.context_rows, "interpretation": self.interpretation}


class V119RCpoElgSupportOutOfSetFalsePositiveAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V119RCpoElgSupportOutOfSetFalsePositiveAuditReport:
        base_rows = [
            row
            for row in _load_csv_rows(self.repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv")
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
        ]
        daily_basic_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(self.repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv")
        }
        moneyflow_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(self.repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv")
        }

        add_rows: list[dict[str, Any]] = []
        all_rows: list[dict[str, Any]] = []
        for row in base_rows:
            key = (str(row["signal_trade_date"]).replace("-", ""), str(row["symbol"]))
            daily_basic = daily_basic_rows.get(key)
            moneyflow = moneyflow_rows.get(key)
            if daily_basic is None or moneyflow is None:
                continue
            merged = {
                **row,
                "turnover_rate_f": _to_float(daily_basic.get("turnover_rate_f")),
                "volume_ratio": _to_float(daily_basic.get("volume_ratio")),
                "large_buy_sell_ratio": (_to_float(moneyflow.get("buy_lg_amount")) + 1.0)
                / (_to_float(moneyflow.get("sell_lg_amount")) + 1.0),
                "elg_buy_sell_ratio": (_to_float(moneyflow.get("buy_elg_amount")) + 1.0)
                / (_to_float(moneyflow.get("sell_elg_amount")) + 1.0),
            }
            all_rows.append(merged)
            if str(row.get("action_context")) == "add_vs_hold":
                add_rows.append(merged)

        turnover_values = [_to_float(row["turnover_rate_f"]) for row in add_rows]
        volume_ratio_values = [_to_float(row["volume_ratio"]) for row in add_rows]
        large_ratio_values = [_to_float(row["large_buy_sell_ratio"]) for row in add_rows]
        elg_ratio_values = [_to_float(row["elg_buy_sell_ratio"]) for row in add_rows]
        turnover_mean = sum(turnover_values) / len(turnover_values)
        volume_ratio_mean = sum(volume_ratio_values) / len(volume_ratio_values)
        large_ratio_mean = sum(large_ratio_values) / len(large_ratio_values)
        elg_ratio_mean = sum(elg_ratio_values) / len(elg_ratio_values)
        turnover_std = math.sqrt(sum((value - turnover_mean) ** 2 for value in turnover_values) / len(turnover_values)) or 1.0
        volume_ratio_std = math.sqrt(sum((value - volume_ratio_mean) ** 2 for value in volume_ratio_values) / len(volume_ratio_values)) or 1.0
        large_ratio_std = math.sqrt(sum((value - large_ratio_mean) ** 2 for value in large_ratio_values) / len(large_ratio_values)) or 1.0
        elg_ratio_std = math.sqrt(sum((value - elg_ratio_mean) ** 2 for value in elg_ratio_values) / len(elg_ratio_values)) or 1.0

        scored_add_rows: list[dict[str, Any]] = []
        for row in add_rows:
            turnover_score = (
                -_zscore(_to_float(row["turnover_rate_f"]), turnover_mean, turnover_std)
                - _zscore(_to_float(row["volume_ratio"]), volume_ratio_mean, volume_ratio_std)
                + 0.5 * _zscore(_to_float(row["large_buy_sell_ratio"]), large_ratio_mean, large_ratio_std)
            )
            score = _participation_score(row) + turnover_score + 0.25 * _zscore(
                _to_float(row["elg_buy_sell_ratio"]), elg_ratio_mean, elg_ratio_std
            )
            scored_add_rows.append({**row, "score": score})

        thresholds = sorted({_to_float(row["score"]) for row in scored_add_rows}, reverse=True)
        best_threshold = thresholds[0]
        best_balanced_accuracy = -1.0
        for threshold in thresholds:
            tp = sum(_is_positive_add(row) and _to_float(row["score"]) >= threshold for row in scored_add_rows)
            fn = sum(_is_positive_add(row) and _to_float(row["score"]) < threshold for row in scored_add_rows)
            fp = sum((not _is_positive_add(row)) and _to_float(row["score"]) >= threshold for row in scored_add_rows)
            tn = sum((not _is_positive_add(row)) and _to_float(row["score"]) < threshold for row in scored_add_rows)
            positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
            negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
            balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
            if balanced_accuracy > best_balanced_accuracy:
                best_balanced_accuracy = balanced_accuracy
                best_threshold = threshold

        context_totals: dict[str, int] = {}
        context_passes: dict[str, int] = {}
        for row in all_rows:
            turnover_score = (
                -_zscore(_to_float(row["turnover_rate_f"]), turnover_mean, turnover_std)
                - _zscore(_to_float(row["volume_ratio"]), volume_ratio_mean, volume_ratio_std)
                + 0.5 * _zscore(_to_float(row["large_buy_sell_ratio"]), large_ratio_mean, large_ratio_std)
            )
            score = _participation_score(row) + turnover_score + 0.25 * _zscore(
                _to_float(row["elg_buy_sell_ratio"]), elg_ratio_mean, elg_ratio_std
            )
            context = str(row.get("action_context"))
            context_totals[context] = context_totals.get(context, 0) + 1
            if score >= best_threshold:
                context_passes[context] = context_passes.get(context, 0) + 1

        context_rows = [
            {
                "action_context": context,
                "row_count": context_totals[context],
                "pass_count": context_passes.get(context, 0),
                "pass_rate": round(context_passes.get(context, 0) / context_totals[context], 6),
            }
            for context in sorted(context_totals)
        ]
        summary = {
            "acceptance_posture": "freeze_v119r_cpo_elg_support_out_of_set_false_positive_audit_v1",
            "best_add_pool_threshold": round(best_threshold, 6),
            "best_add_pool_balanced_accuracy": round(best_balanced_accuracy, 6),
            "entry_leakage_rate": next((row["pass_rate"] for row in context_rows if row["action_context"] == "entry_vs_skip"), 0.0),
            "close_leakage_rate": next((row["pass_rate"] for row in context_rows if row["action_context"] == "close_vs_hold"), 0.0),
            "reduce_leakage_rate": next((row["pass_rate"] for row in context_rows if row["action_context"] == "reduce_vs_hold"), 0.0),
            "recommended_next_posture": "send_PQR_to_three_run_adversarial_review_before_preserving_hard_candidate_status",
        }
        interpretation = [
            "V1.19R checks whether the ELG-supported hard candidate leaks into non-add contexts.",
            "A line that still fires too often on entry or exit contexts is not ready to keep hard-candidate language without another adversarial review.",
            "This is the non-replay leakage audit for the current strongest CPO line.",
        ]
        return V119RCpoElgSupportOutOfSetFalsePositiveAuditReport(summary=summary, context_rows=context_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V119RCpoElgSupportOutOfSetFalsePositiveAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119RCpoElgSupportOutOfSetFalsePositiveAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(reports_dir=repo_root / "reports" / "analysis", report_name="v119r_cpo_elg_support_out_of_set_false_positive_audit_v1", result=result)
    print(output_path)


if __name__ == "__main__":
    main()
