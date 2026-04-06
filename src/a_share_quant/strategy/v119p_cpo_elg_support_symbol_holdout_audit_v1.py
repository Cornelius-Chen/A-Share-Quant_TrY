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


def _scored_add_rows(repo_root: Path) -> list[dict[str, Any]]:
    base_rows = [
        row
        for row in _load_csv_rows(repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv")
        if str(row.get("board_phase")) in {"main_markup", "diffusion"} and str(row.get("action_context")) == "add_vs_hold"
    ]
    daily_basic_rows = {
        (str(row["trade_date"]), str(row["symbol"])): row
        for row in _load_csv_rows(repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_cpo_daily_basic_v1.csv")
    }
    moneyflow_rows = {
        (str(row["trade_date"]), str(row["symbol"])): row
        for row in _load_csv_rows(repo_root / "data" / "raw" / "moneyflow" / "tushare_cpo_moneyflow_v1.csv")
    }

    raw_rows: list[dict[str, Any]] = []
    for row in base_rows:
        key = (str(row["signal_trade_date"]).replace("-", ""), str(row["symbol"]))
        daily_basic = daily_basic_rows.get(key)
        moneyflow = moneyflow_rows.get(key)
        if daily_basic is None or moneyflow is None:
            continue
        raw_rows.append(
            {
                **row,
                "turnover_rate_f": _to_float(daily_basic.get("turnover_rate_f")),
                "volume_ratio": _to_float(daily_basic.get("volume_ratio")),
                "large_buy_sell_ratio": (_to_float(moneyflow.get("buy_lg_amount")) + 1.0)
                / (_to_float(moneyflow.get("sell_lg_amount")) + 1.0),
                "elg_buy_sell_ratio": (_to_float(moneyflow.get("buy_elg_amount")) + 1.0)
                / (_to_float(moneyflow.get("sell_elg_amount")) + 1.0),
            }
        )

    turnover_values = [_to_float(row["turnover_rate_f"]) for row in raw_rows]
    volume_ratio_values = [_to_float(row["volume_ratio"]) for row in raw_rows]
    large_ratio_values = [_to_float(row["large_buy_sell_ratio"]) for row in raw_rows]
    elg_ratio_values = [_to_float(row["elg_buy_sell_ratio"]) for row in raw_rows]
    turnover_mean = sum(turnover_values) / len(turnover_values)
    volume_ratio_mean = sum(volume_ratio_values) / len(volume_ratio_values)
    large_ratio_mean = sum(large_ratio_values) / len(large_ratio_values)
    elg_ratio_mean = sum(elg_ratio_values) / len(elg_ratio_values)
    turnover_std = math.sqrt(sum((value - turnover_mean) ** 2 for value in turnover_values) / len(turnover_values)) or 1.0
    volume_ratio_std = math.sqrt(sum((value - volume_ratio_mean) ** 2 for value in volume_ratio_values) / len(volume_ratio_values)) or 1.0
    large_ratio_std = math.sqrt(sum((value - large_ratio_mean) ** 2 for value in large_ratio_values) / len(large_ratio_values)) or 1.0
    elg_ratio_std = math.sqrt(sum((value - elg_ratio_mean) ** 2 for value in elg_ratio_values) / len(elg_ratio_values)) or 1.0

    scored_rows: list[dict[str, Any]] = []
    for row in raw_rows:
        turnover_score = (
            -_zscore(_to_float(row["turnover_rate_f"]), turnover_mean, turnover_std)
            - _zscore(_to_float(row["volume_ratio"]), volume_ratio_mean, volume_ratio_std)
            + 0.5 * _zscore(_to_float(row["large_buy_sell_ratio"]), large_ratio_mean, large_ratio_std)
        )
        score = _participation_score(row) + turnover_score + 0.25 * _zscore(
            _to_float(row["elg_buy_sell_ratio"]), elg_ratio_mean, elg_ratio_std
        )
        scored_rows.append(
            {
                "signal_trade_date": str(row["signal_trade_date"]),
                "symbol": str(row["symbol"]),
                "positive_add_label": _is_positive_add(row),
                "participation_turnover_elg_support_score": round(score, 6),
            }
        )
    return scored_rows


@dataclass(slots=True)
class V119PCpoElgSupportSymbolHoldoutAuditReport:
    summary: dict[str, Any]
    holdout_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "holdout_rows": self.holdout_rows, "interpretation": self.interpretation}


class V119PCpoElgSupportSymbolHoldoutAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V119PCpoElgSupportSymbolHoldoutAuditReport:
        rows = _scored_add_rows(self.repo_root)
        holdout_rows: list[dict[str, Any]] = []
        for holdout_symbol in sorted({str(row["symbol"]) for row in rows}):
            train_rows = [row for row in rows if str(row["symbol"]) != holdout_symbol]
            test_rows = [row for row in rows if str(row["symbol"]) == holdout_symbol]
            thresholds = sorted({_to_float(row["participation_turnover_elg_support_score"]) for row in train_rows}, reverse=True)
            best_threshold = thresholds[0]
            best_train_balanced_accuracy = -1.0
            for threshold in thresholds:
                tp = sum(bool(row["positive_add_label"]) and _to_float(row["participation_turnover_elg_support_score"]) >= threshold for row in train_rows)
                fn = sum(bool(row["positive_add_label"]) and _to_float(row["participation_turnover_elg_support_score"]) < threshold for row in train_rows)
                fp = sum((not bool(row["positive_add_label"])) and _to_float(row["participation_turnover_elg_support_score"]) >= threshold for row in train_rows)
                tn = sum((not bool(row["positive_add_label"])) and _to_float(row["participation_turnover_elg_support_score"]) < threshold for row in train_rows)
                positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
                negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
                balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
                if balanced_accuracy > best_train_balanced_accuracy:
                    best_train_balanced_accuracy = balanced_accuracy
                    best_threshold = threshold

            test_positive_rows = [row for row in test_rows if bool(row["positive_add_label"])]
            test_negative_rows = [row for row in test_rows if not bool(row["positive_add_label"])]
            test_positive_recall = sum(_to_float(row["participation_turnover_elg_support_score"]) >= best_threshold for row in test_positive_rows) / len(test_positive_rows) if test_positive_rows else None
            test_negative_reject_rate = sum(_to_float(row["participation_turnover_elg_support_score"]) < best_threshold for row in test_negative_rows) / len(test_negative_rows) if test_negative_rows else None
            test_balanced_accuracy = (test_positive_recall + test_negative_reject_rate) / 2.0 if test_positive_recall is not None and test_negative_reject_rate is not None else None
            holdout_rows.append(
                {
                    "holdout_symbol": holdout_symbol,
                    "train_best_threshold": round(best_threshold, 6),
                    "train_best_balanced_accuracy": round(best_train_balanced_accuracy, 6),
                    "test_positive_add_count": len(test_positive_rows),
                    "test_negative_add_count": len(test_negative_rows),
                    "test_positive_recall": None if test_positive_recall is None else round(test_positive_recall, 6),
                    "test_negative_reject_rate": None if test_negative_reject_rate is None else round(test_negative_reject_rate, 6),
                    "test_balanced_accuracy": None if test_balanced_accuracy is None else round(test_balanced_accuracy, 6),
                }
            )
        evaluable = [row["test_balanced_accuracy"] for row in holdout_rows if row["test_balanced_accuracy"] is not None]
        summary = {
            "acceptance_posture": "freeze_v119p_cpo_elg_support_symbol_holdout_audit_v1",
            "holdout_count": len(holdout_rows),
            "evaluable_holdout_count": len(evaluable),
            "mean_evaluable_test_balanced_accuracy": round(sum(evaluable) / len(evaluable), 6) if evaluable else 0.0,
            "min_evaluable_test_balanced_accuracy": round(min(evaluable), 6) if evaluable else 0.0,
            "recommended_next_posture": "pair_symbol_holdout_with_role_holdout_and_out_of_set_false_positive_audit_before_any_reclassification",
        }
        interpretation = [
            "V1.19P checks whether the ELG-supported hard candidate survives symbol holdouts.",
            "If symbol holdouts break badly, the branch may still be object-specific rather than stable add semantics.",
            "This remains a non-replay adversarial audit only.",
        ]
        return V119PCpoElgSupportSymbolHoldoutAuditReport(summary=summary, holdout_rows=holdout_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V119PCpoElgSupportSymbolHoldoutAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119PCpoElgSupportSymbolHoldoutAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(reports_dir=repo_root / "reports" / "analysis", report_name="v119p_cpo_elg_support_symbol_holdout_audit_v1", result=result)
    print(output_path)


if __name__ == "__main__":
    main()
