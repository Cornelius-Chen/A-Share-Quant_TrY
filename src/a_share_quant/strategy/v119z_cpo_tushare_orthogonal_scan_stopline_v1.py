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


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float]) -> float:
    if not values:
        return 1.0
    mean_value = _mean(values)
    return math.sqrt(sum((value - mean_value) ** 2 for value in values) / len(values)) or 1.0


def _balanced_accuracy(rows: list[dict[str, Any]], score_key: str, threshold: float) -> tuple[float, float, float]:
    tp = sum(bool(row["positive_add_label"]) and _to_float(row[score_key]) >= threshold for row in rows)
    fn = sum(bool(row["positive_add_label"]) and _to_float(row[score_key]) < threshold for row in rows)
    fp = sum((not bool(row["positive_add_label"])) and _to_float(row[score_key]) >= threshold for row in rows)
    tn = sum((not bool(row["positive_add_label"])) and _to_float(row[score_key]) < threshold for row in rows)
    positive_recall = tp / (tp + fn) if (tp + fn) else 0.0
    negative_reject_rate = tn / (tn + fp) if (tn + fp) else 0.0
    return (positive_recall + negative_reject_rate) / 2.0, positive_recall, negative_reject_rate


def _best_threshold_metrics(rows: list[dict[str, Any]], score_key: str) -> tuple[float, float, float, float]:
    thresholds = sorted({_to_float(row[score_key]) for row in rows}, reverse=True)
    best: tuple[float, float, float, float] | None = None
    for threshold in thresholds:
        balanced_accuracy, positive_recall, negative_reject_rate = _balanced_accuracy(rows, score_key, threshold)
        candidate = (balanced_accuracy, threshold, positive_recall, negative_reject_rate)
        if best is None or balanced_accuracy > best[0]:
            best = candidate
    assert best is not None
    return best


@dataclass(slots=True)
class V119ZCpoTushareOrthogonalScanStoplineReport:
    summary: dict[str, Any]
    scan_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "scan_rows": self.scan_rows,
            "interpretation": self.interpretation,
        }


class V119ZCpoTushareOrthogonalScanStoplineAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V119ZCpoTushareOrthogonalScanStoplineReport:
        base_rows = json.loads(
            (
                self.repo_root / "reports" / "analysis" / "v119l_cpo_participation_turnover_elg_support_discovery_v1.json"
            ).read_text(encoding="utf-8")
        )["candidate_score_rows"]
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
        stk_limit_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "reference" / "stk_limit" / "tushare_cpo_stk_limit_v1.csv"
            )
        }
        daily_bar_rows = {
            (str(row["trade_date"]).replace("-", ""), str(row["symbol"])): row
            for row in _load_csv_rows(
                self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
            )
        }

        rows: list[dict[str, Any]] = []
        for row in base_rows:
            key = (str(row["signal_trade_date"]).replace("-", ""), str(row["symbol"]))
            daily_basic = daily_basic_rows.get(key)
            moneyflow = moneyflow_rows.get(key)
            stk_limit = stk_limit_rows.get(key)
            daily_bar = daily_bar_rows.get(key)
            if daily_basic is None or moneyflow is None or stk_limit is None or daily_bar is None:
                continue
            buy_sm = _to_float(moneyflow["buy_sm_amount"])
            sell_sm = _to_float(moneyflow["sell_sm_amount"])
            buy_md = _to_float(moneyflow["buy_md_amount"])
            sell_md = _to_float(moneyflow["sell_md_amount"])
            buy_lg = _to_float(moneyflow["buy_lg_amount"])
            sell_lg = _to_float(moneyflow["sell_lg_amount"])
            buy_elg = _to_float(moneyflow["buy_elg_amount"])
            sell_elg = _to_float(moneyflow["sell_elg_amount"])
            total_buy = buy_sm + buy_md + buy_lg + buy_elg + 1e-9
            total_sell = sell_sm + sell_md + sell_lg + sell_elg + 1e-9
            pre_close = _to_float(daily_bar["pre_close"])
            close = _to_float(daily_bar["close"])
            high = _to_float(daily_bar["high"])
            up_limit = _to_float(stk_limit["up_limit"])
            if up_limit <= pre_close:
                continue
            rows.append(
                {
                    **row,
                    "free_share": _to_float(daily_basic["free_share"]),
                    "circ_mv": _to_float(daily_basic["circ_mv"]),
                    "float_share": _to_float(daily_basic["float_share"]),
                    "md_support_ratio": (buy_md + 1.0) / (sell_md + 1.0),
                    "net_mf_scaled": _to_float(moneyflow["net_mf_amount"]) / max(total_buy + total_sell, 1e-9),
                    "lgelg_net_scaled": ((buy_lg + buy_elg) - (sell_lg + sell_elg)) / max(total_buy + total_sell, 1e-9),
                    "sm_buy_share": buy_sm / total_buy,
                    "sm_buy_sell_ratio": (buy_sm + 1.0) / (sell_sm + 1.0),
                    "retail_crowding_ratio": (buy_sm + 1.0) / (buy_md + buy_lg + buy_elg + 1.0),
                    "up_gap": (up_limit - close) / max(abs(up_limit), 1e-9),
                    "close_to_up_band": (close - pre_close) / max(up_limit - pre_close, 1e-9),
                    "high_to_up_band": (high - pre_close) / max(up_limit - pre_close, 1e-9),
                }
            )

        feature_names = (
            "free_share",
            "circ_mv",
            "float_share",
            "md_support_ratio",
            "net_mf_scaled",
            "lgelg_net_scaled",
            "sm_buy_share",
            "sm_buy_sell_ratio",
            "retail_crowding_ratio",
            "up_gap",
            "close_to_up_band",
            "high_to_up_band",
        )
        feature_stats = {name: (_mean([_to_float(row[name]) for row in rows]), _std([_to_float(row[name]) for row in rows])) for name in feature_names}

        candidate_formulas = {
            "base_parent": {},
            "plus_md_support": {"md_support_ratio": 0.25},
            "plus_net_flow_scaled": {"net_mf_scaled": 0.25},
            "plus_lgelg_net_scaled": {"lgelg_net_scaled": 0.25},
            "plus_free_share": {"free_share": 0.25},
            "minus_circ_mv": {"circ_mv": -0.25},
            "plus_sm_buy_share": {"sm_buy_share": 0.25},
            "minus_retail_crowding_ratio": {"retail_crowding_ratio": -0.25},
            "limit_discipline_support": {"up_gap": 0.05, "close_to_up_band": -0.05, "high_to_up_band": -0.05},
        }

        scan_rows: list[dict[str, Any]] = []
        for candidate_name, weights in candidate_formulas.items():
            scored_rows: list[dict[str, Any]] = []
            for row in rows:
                score = _to_float(row["participation_turnover_elg_support_score"])
                for feature_name, weight in weights.items():
                    mean_value, std_value = feature_stats[feature_name]
                    score += weight * ((_to_float(row[feature_name]) - mean_value) / std_value)
                scored_rows.append({**row, "scan_score": score})
            best_balanced_accuracy, best_threshold, _, _ = _best_threshold_metrics(scored_rows, "scan_score")

            split_scores: list[float] = []
            for holdout_years in ({"2023"}, {"2024"}, {"2025", "2026"}):
                train_rows = [row for row in scored_rows if str(row["signal_trade_date"])[:4] not in holdout_years]
                test_rows = [row for row in scored_rows if str(row["signal_trade_date"])[:4] in holdout_years]
                train_best_balanced_accuracy, train_best_threshold, _, _ = _best_threshold_metrics(train_rows, "scan_score")
                test_balanced_accuracy, _, _ = _balanced_accuracy(test_rows, "scan_score", train_best_threshold)
                split_scores.append(test_balanced_accuracy)
            scan_rows.append(
                {
                    "candidate_name": candidate_name,
                    "weights": weights,
                    "external_best_balanced_accuracy": round(best_balanced_accuracy, 6),
                    "time_split_mean_balanced_accuracy": round(_mean(split_scores), 6),
                    "time_split_min_balanced_accuracy": round(min(split_scores), 6),
                    "matches_or_beats_parent_external": best_balanced_accuracy >= 0.909091,
                    "matches_or_beats_parent_time_split": min(split_scores) >= 0.833333 and _mean(split_scores) >= 0.875,
                }
            )

        viable_rows = [
            row
            for row in scan_rows
            if bool(row["matches_or_beats_parent_external"]) and bool(row["matches_or_beats_parent_time_split"])
        ]
        summary = {
            "acceptance_posture": "freeze_v119z_cpo_tushare_orthogonal_scan_stopline_v1",
            "scan_candidate_count": len(scan_rows),
            "viable_increment_candidate_count": len(viable_rows),
            "parent_external_best_balanced_accuracy": 0.909091,
            "parent_time_split_mean_balanced_accuracy": 0.875,
            "parent_time_split_min_balanced_accuracy": 0.833333,
            "orthogonal_scan_stopline_reached": len(viable_rows) == 0,
            "recommended_next_posture": "stop_tushare_daily_orthogonal_micro_scan_and_shift_to_new_data_plane",
        }
        interpretation = [
            "V1.19Z is a stopline scan, not a new branch. It checks whether any remaining narrow orthogonal ideas inside the current Tushare daily_basic/moneyflow/stk_limit plane beat the parent ELG-supported combo.",
            "The scan covers float/cap, medium-flow support, net-flow scaling, retail crowding, and limit-band discipline variants under the same evaluation surface.",
            "If none of them clear the parent on both external and chronology surfaces, this data plane should be treated as locally exhausted rather than endlessly re-mined.",
        ]
        return V119ZCpoTushareOrthogonalScanStoplineReport(
            summary=summary,
            scan_rows=scan_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V119ZCpoTushareOrthogonalScanStoplineReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V119ZCpoTushareOrthogonalScanStoplineAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v119z_cpo_tushare_orthogonal_scan_stopline_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
