from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _is_positive_add(row: dict[str, Any]) -> bool:
    return (
        str(row.get("action_context")) == "add_vs_hold"
        and str(row.get("action_favored_3d")) == "True"
        and _to_float(row.get("expectancy_proxy_3d")) > 0.0
        and _to_float(row.get("max_adverse_return_3d")) > -0.04
    )


def _cooling_controlled_score(row: dict[str, Any]) -> float:
    d5_last = max(_to_float(row.get("d5_30_last_bar_return_rz")), 0.0)
    f60_high = max(_to_float(row.get("f60_high_time_ratio_rz")) - 750000000.0, 0.0)
    close_stretch = max(_to_float(row.get("f60_close_location_rz")) - 850000000.0, 0.0)
    base = (
        -_to_float(row.get("d5_30_last_bar_return_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        + _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("f30_high_time_ratio_rz"))
        + _to_float(row.get("f60_high_time_ratio_rz"))
        + _to_float(row.get("f60_close_vs_vwap_rz"))
        - _to_float(row.get("d5_30_close_vs_vwap_rz"))
        - _to_float(row.get("d15_60_close_vs_vwap_rz"))
        - _to_float(row.get("f30_close_location_rz"))
        - _to_float(row.get("f60_close_location_rz"))
    )
    return base - (d5_last + f60_high + close_stretch)


def _breakout_damage_score(row: dict[str, Any]) -> float:
    positive_score = (
        _to_float(row.get("f30_breakout_efficiency_rz"))
        + _to_float(row.get("f60_breakout_efficiency_rz"))
        + _to_float(row.get("f30_last_bar_return_rz"))
        + _to_float(row.get("f60_last_bar_return_rz"))
        + _to_float(row.get("f30_pullback_from_high_rz"))
        + _to_float(row.get("f60_pullback_from_high_rz"))
    )
    negative_score = (
        _to_float(row.get("f30_afternoon_volume_share_rz"))
        + _to_float(row.get("f60_afternoon_volume_share_rz"))
        + _to_float(row.get("d5_30_last_bar_upper_shadow_ratio_rz"))
        + _to_float(row.get("d15_60_last_bar_upper_shadow_ratio_rz"))
        + _to_float(row.get("f30_failed_push_proxy"))
        + _to_float(row.get("f60_failed_push_proxy"))
        + _to_float(row.get("d15_60_failed_push_proxy"))
    )
    return positive_score - negative_score


def _best_balanced_accuracy(rows: list[dict[str, Any]], score_key: str) -> tuple[float, float]:
    thresholds = sorted({_to_float(row.get(score_key)) for row in rows}, reverse=True)
    positives = [row for row in rows if bool(row.get("positive_add_label"))]
    negatives = [row for row in rows if not bool(row.get("positive_add_label"))]
    best_bal = -1.0
    best_threshold = 0.0
    for threshold in thresholds:
        tp = sum(1 for row in positives if _to_float(row.get(score_key)) >= threshold)
        tn = sum(1 for row in negatives if _to_float(row.get(score_key)) < threshold)
        tpr = tp / len(positives) if positives else 0.0
        tnr = tn / len(negatives) if negatives else 0.0
        bal = (tpr + tnr) / 2.0
        if bal > best_bal:
            best_bal = bal
            best_threshold = threshold
    return best_threshold, best_bal


@dataclass(slots=True)
class V118MCpoBreakoutDamageSoftComponentTimeSplitReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V118MCpoBreakoutDamageSoftComponentTimeSplitAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path, alpha: float) -> V118MCpoBreakoutDamageSoftComponentTimeSplitReport:
        rows = [
            dict(row)
            for row in _load_csv_rows(rows_path)
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
            and str(row.get("action_context")) == "add_vs_hold"
        ]
        for row in rows:
            row["positive_add_label"] = _is_positive_add(row)
            row["integrated_score"] = round(
                _cooling_controlled_score(row) - alpha * _breakout_damage_score(row),
                6,
            )
        split_defs = (
            ("holdout_2023", {"2023"}),
            ("holdout_2024", {"2024"}),
            ("holdout_2025_plus", {"2025", "2026"}),
        )
        split_rows: list[dict[str, Any]] = []
        for split_name, holdout_years in split_defs:
            train_rows = [row for row in rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in rows if str(row["signal_trade_date"])[:4] in holdout_years]
            threshold, train_bal = _best_balanced_accuracy(train_rows, "integrated_score")
            positives = [row for row in test_rows if bool(row["positive_add_label"])]
            negatives = [row for row in test_rows if not bool(row["positive_add_label"])]
            tp = sum(1 for row in positives if _to_float(row["integrated_score"]) >= threshold)
            tn = sum(1 for row in negatives if _to_float(row["integrated_score"]) < threshold)
            tpr = tp / len(positives) if positives else 0.0
            tnr = tn / len(negatives) if negatives else 0.0
            split_rows.append(
                {
                    "split_name": split_name,
                    "holdout_years": sorted(holdout_years),
                    "train_best_threshold": round(threshold, 6),
                    "train_best_balanced_accuracy": round(train_bal, 6),
                    "test_balanced_accuracy": round((tpr + tnr) / 2.0, 6),
                    "test_positive_recall": round(tpr, 6),
                    "test_negative_reject_rate": round(tnr, 6),
                }
            )

        mean_test_bal = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test_bal = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
        baseline_mean_test_bal = 0.736111
        summary = {
            "acceptance_posture": "freeze_v118m_cpo_breakout_damage_soft_component_time_split_v1",
            "alpha": alpha,
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(mean_test_bal, 6),
            "min_test_balanced_accuracy": round(min_test_bal, 6),
            "baseline_mean_test_balanced_accuracy": baseline_mean_test_bal,
            "stability_posture": (
                "no_material_time_split_gain"
                if alpha == 0.0 or mean_test_bal <= baseline_mean_test_bal + 1e-9
                else "material_time_split_gain"
            ),
            "recommended_next_posture": "send_KLM_to_triage_and_decide_whether_active_soft_integration_is_worthkeeping",
        }
        interpretation = [
            "V1.18M checks whether the breakout-damage soft component changes chronology behavior when attached to the live cooling candidate.",
            "If time-split behavior stays unchanged, the component may still be worth archiving but does not deserve active integration effort.",
        ]
        return V118MCpoBreakoutDamageSoftComponentTimeSplitReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118MCpoBreakoutDamageSoftComponentTimeSplitReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    alpha = 0.0
    v118k_path = repo_root / "reports" / "analysis" / "v118k_cpo_breakout_damage_soft_component_integration_review_v1.json"
    if v118k_path.exists():
        payload = json.loads(v118k_path.read_text(encoding="utf-8"))
        alpha = float(payload["summary"]["best_alpha"])
    result = V118MCpoBreakoutDamageSoftComponentTimeSplitAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        alpha=alpha,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118m_cpo_breakout_damage_soft_component_time_split_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
