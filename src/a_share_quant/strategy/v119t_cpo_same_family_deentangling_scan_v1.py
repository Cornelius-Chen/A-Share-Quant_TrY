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
class V119TCpoSameFamilyDeentanglingScanReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "variant_rows": self.variant_rows, "interpretation": self.interpretation}


class V119TCpoSameFamilyDeentanglingScanAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _scored_rows(self) -> list[dict[str, Any]]:
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
        add_rows = [row for row in raw_rows if str(row.get("action_context")) == "add_vs_hold"]
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
        for row in raw_rows:
            turnover_score = (
                -_zscore(_to_float(row["turnover_rate_f"]), turnover_mean, turnover_std)
                - _zscore(_to_float(row["volume_ratio"]), volume_ratio_mean, volume_ratio_std)
                + 0.5 * _zscore(_to_float(row["large_buy_sell_ratio"]), large_ratio_mean, large_ratio_std)
            )
            row["base_score"] = (
                _participation_score(row)
                + turnover_score
                + 0.25 * _zscore(_to_float(row["elg_buy_sell_ratio"]), elg_ratio_mean, elg_ratio_std)
            )
        by_date: dict[str, list[float]] = {}
        by_symbol: dict[str, list[float]] = {}
        for row in raw_rows:
            by_date.setdefault(str(row["signal_trade_date"]), []).append(_to_float(row["base_score"]))
            by_symbol.setdefault(str(row["symbol"]), []).append(_to_float(row["base_score"]))
        for row in raw_rows:
            row["date_resid"] = _to_float(row["base_score"]) - sum(by_date[str(row["signal_trade_date"])]) / len(by_date[str(row["signal_trade_date"])])
            row["symbol_resid"] = _to_float(row["base_score"]) - sum(by_symbol[str(row["symbol"])]) / len(by_symbol[str(row["symbol"])])
            row["symbol_date_blend_033"] = 0.67 * _to_float(row["symbol_resid"]) + 0.33 * _to_float(row["date_resid"])
        return raw_rows

    def _metrics(self, rows: list[dict[str, Any]], score_key: str) -> dict[str, float]:
        add_rows = [row for row in rows if str(row.get("action_context")) == "add_vs_hold"]
        thresholds = sorted({_to_float(row[score_key]) for row in add_rows}, reverse=True)
        best_threshold = thresholds[0]
        best_balanced_accuracy = -1.0
        for threshold in thresholds:
            tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= threshold for row in add_rows)
            fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < threshold for row in add_rows)
            fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= threshold for row in add_rows)
            tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < threshold for row in add_rows)
            positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
            negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
            balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
            if balanced_accuracy > best_balanced_accuracy:
                best_balanced_accuracy = balanced_accuracy
                best_threshold = threshold

        split_scores: list[float] = []
        for holdout_years in ({"2023"}, {"2024"}, {"2025", "2026"}):
            train_rows = [row for row in add_rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in add_rows if str(row["signal_trade_date"])[:4] in holdout_years]
            train_thresholds = sorted({_to_float(row[score_key]) for row in train_rows}, reverse=True)
            train_best_threshold = train_thresholds[0]
            train_best_balanced_accuracy = -1.0
            for threshold in train_thresholds:
                tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= threshold for row in train_rows)
                fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < threshold for row in train_rows)
                fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= threshold for row in train_rows)
                tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < threshold for row in train_rows)
                positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
                negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
                balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
                if balanced_accuracy > train_best_balanced_accuracy:
                    train_best_balanced_accuracy = balanced_accuracy
                    train_best_threshold = threshold
            tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= train_best_threshold for row in test_rows)
            fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < train_best_threshold for row in test_rows)
            fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= train_best_threshold for row in test_rows)
            tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < train_best_threshold for row in test_rows)
            positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
            negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
            split_scores.append((positive_recall + negative_reject_rate) / 2.0)

        symbol_scores: list[float] = []
        for holdout_symbol in sorted({str(row["symbol"]) for row in add_rows}):
            train_rows = [row for row in add_rows if str(row["symbol"]) != holdout_symbol]
            test_rows = [row for row in add_rows if str(row["symbol"]) == holdout_symbol]
            if not any(_is_positive_add(row) for row in test_rows) or not any(not _is_positive_add(row) for row in test_rows):
                continue
            train_thresholds = sorted({_to_float(row[score_key]) for row in train_rows}, reverse=True)
            train_best_threshold = train_thresholds[0]
            train_best_balanced_accuracy = -1.0
            for threshold in train_thresholds:
                tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= threshold for row in train_rows)
                fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < threshold for row in train_rows)
                fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= threshold for row in train_rows)
                tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < threshold for row in train_rows)
                positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
                negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
                balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
                if balanced_accuracy > train_best_balanced_accuracy:
                    train_best_balanced_accuracy = balanced_accuracy
                    train_best_threshold = threshold
            tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= train_best_threshold for row in test_rows)
            fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < train_best_threshold for row in test_rows)
            fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= train_best_threshold for row in test_rows)
            tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < train_best_threshold for row in test_rows)
            positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
            negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
            symbol_scores.append((positive_recall + negative_reject_rate) / 2.0)

        role_scores: list[float] = []
        for holdout_role in sorted({str(row.get("role_family")) for row in add_rows}):
            train_rows = [row for row in add_rows if str(row.get("role_family")) != holdout_role]
            test_rows = [row for row in add_rows if str(row.get("role_family")) == holdout_role]
            if not any(_is_positive_add(row) for row in test_rows) or not any(not _is_positive_add(row) for row in test_rows):
                continue
            train_thresholds = sorted({_to_float(row[score_key]) for row in train_rows}, reverse=True)
            train_best_threshold = train_thresholds[0]
            train_best_balanced_accuracy = -1.0
            for threshold in train_thresholds:
                tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= threshold for row in train_rows)
                fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < threshold for row in train_rows)
                fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= threshold for row in train_rows)
                tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < threshold for row in train_rows)
                positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
                negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
                balanced_accuracy = (positive_recall + negative_reject_rate) / 2.0
                if balanced_accuracy > train_best_balanced_accuracy:
                    train_best_balanced_accuracy = balanced_accuracy
                    train_best_threshold = threshold
            tp = sum(_is_positive_add(row) and _to_float(row[score_key]) >= train_best_threshold for row in test_rows)
            fn = sum(_is_positive_add(row) and _to_float(row[score_key]) < train_best_threshold for row in test_rows)
            fp = sum((not _is_positive_add(row)) and _to_float(row[score_key]) >= train_best_threshold for row in test_rows)
            tn = sum((not _is_positive_add(row)) and _to_float(row[score_key]) < train_best_threshold for row in test_rows)
            positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
            negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
            role_scores.append((positive_recall + negative_reject_rate) / 2.0)

        context_rates: dict[str, float] = {}
        for context in sorted({str(row.get("action_context")) for row in rows}):
            context_rows = [row for row in rows if str(row.get("action_context")) == context]
            context_rates[context] = sum(_to_float(row[score_key]) >= best_threshold for row in context_rows) / len(context_rows)

        return {
            "best_add_pool_balanced_accuracy": round(best_balanced_accuracy, 6),
            "time_split_mean": round(sum(split_scores) / len(split_scores), 6),
            "time_split_min": round(min(split_scores), 6),
            "symbol_holdout_mean": round(sum(symbol_scores) / len(symbol_scores), 6),
            "symbol_holdout_min": round(min(symbol_scores), 6),
            "role_holdout_mean": round(sum(role_scores) / len(role_scores), 6),
            "role_holdout_min": round(min(role_scores), 6),
            "entry_leakage_rate": round(context_rates.get("entry_vs_skip", 0.0), 6),
            "close_leakage_rate": round(context_rates.get("close_vs_hold", 0.0), 6),
        }

    def analyze(self) -> V119TCpoSameFamilyDeentanglingScanReport:
        rows = self._scored_rows()
        variant_rows = []
        for variant_name, score_key in (
            ("base_score", "base_score"),
            ("date_resid", "date_resid"),
            ("symbol_resid", "symbol_resid"),
            ("symbol_date_blend_033", "symbol_date_blend_033"),
        ):
            metrics = self._metrics(rows, score_key)
            variant_rows.append({"variant_name": variant_name, **metrics})
        summary = {
            "acceptance_posture": "freeze_v119t_cpo_same_family_deentangling_scan_v1",
            "variant_count": len(variant_rows),
            "best_symbol_holdout_variant": max(variant_rows, key=lambda row: row["symbol_holdout_mean"])["variant_name"],
            "best_close_leakage_variant": min(variant_rows, key=lambda row: row["close_leakage_rate"])["variant_name"],
            "recommended_next_posture": "stop_same_family_micro_tuning_if_no_single_variant_improves_holdout_and_leakage_together",
        }
        interpretation = [
            "V1.19T scans narrow same-family de-entangling variants instead of opening another broad feature branch.",
            "The purpose is to test whether simple residualization or relative-score transforms can simultaneously preserve chronology and reduce object/context leakage.",
            "If no single narrow variant dominates on both axes, same-family micro-tuning should stop.",
        ]
        return V119TCpoSameFamilyDeentanglingScanReport(summary=summary, variant_rows=variant_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V119TCpoSameFamilyDeentanglingScanReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119TCpoSameFamilyDeentanglingScanAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(reports_dir=repo_root / "reports" / "analysis", report_name="v119t_cpo_same_family_deentangling_scan_v1", result=result)
    print(output_path)


if __name__ == "__main__":
    main()
