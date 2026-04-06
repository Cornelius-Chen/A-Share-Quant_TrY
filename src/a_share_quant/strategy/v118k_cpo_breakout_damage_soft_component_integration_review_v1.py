from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAS = (0.0, 0.25, 0.5, 1.0)


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
class V118KCpoBreakoutDamageSoftComponentIntegrationReviewReport:
    summary: dict[str, Any]
    alpha_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "alpha_rows": self.alpha_rows,
            "interpretation": self.interpretation,
        }


class V118KCpoBreakoutDamageSoftComponentIntegrationReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, rows_path: Path) -> V118KCpoBreakoutDamageSoftComponentIntegrationReviewReport:
        rows = [
            dict(row)
            for row in _load_csv_rows(rows_path)
            if str(row.get("board_phase")) in {"main_markup", "diffusion"}
            and str(row.get("action_context")) == "add_vs_hold"
        ]
        for row in rows:
            row["positive_add_label"] = _is_positive_add(row)
            row["cooling_controlled_score"] = round(_cooling_controlled_score(row), 6)
            row["breakout_damage_score"] = round(_breakout_damage_score(row), 6)

        alpha_rows: list[dict[str, Any]] = []
        baseline_threshold, baseline_bal = _best_balanced_accuracy(rows, "cooling_controlled_score")
        for alpha in ALPHAS:
            score_key = f"integrated_score_a_{str(alpha).replace('.', '_')}"
            for row in rows:
                row[score_key] = round(
                    _to_float(row["cooling_controlled_score"]) - alpha * _to_float(row["breakout_damage_score"]),
                    6,
                )
            threshold, bal = _best_balanced_accuracy(rows, score_key)
            positives = [row for row in rows if bool(row["positive_add_label"])]
            negatives = [row for row in rows if not bool(row["positive_add_label"])]
            pos_mean = sum(_to_float(row[score_key]) for row in positives) / len(positives)
            neg_mean = sum(_to_float(row[score_key]) for row in negatives) / len(negatives)
            alpha_rows.append(
                {
                    "alpha": alpha,
                    "best_threshold": round(threshold, 6),
                    "best_balanced_accuracy": round(bal, 6),
                    "mean_gap_positive_minus_negative": round(pos_mean - neg_mean, 6),
                }
            )

        best_alpha_row = max(alpha_rows, key=lambda row: row["best_balanced_accuracy"])
        summary = {
            "acceptance_posture": "freeze_v118k_cpo_breakout_damage_soft_component_integration_review_v1",
            "base_best_threshold": round(baseline_threshold, 6),
            "base_best_balanced_accuracy": round(baseline_bal, 6),
            "best_alpha": best_alpha_row["alpha"],
            "best_alpha_balanced_accuracy": best_alpha_row["best_balanced_accuracy"],
            "best_alpha_gap": best_alpha_row["mean_gap_positive_minus_negative"],
            "material_improvement_over_base": best_alpha_row["best_balanced_accuracy"] > round(baseline_bal, 6),
            "recommended_next_posture": "external_audit_best_alpha_if_any_material_integration_gain_exists",
        }
        interpretation = [
            "V1.18K tests whether the newly reclassified breakout-damage soft component actually improves the live cooling candidate, rather than just sounding useful in theory.",
            "The integration is intentionally soft: subtract a scaled breakout-damage score from the retained cooling-controlled score, without creating a new hard gate.",
            "If no alpha materially improves discrimination, breakout-damage should remain archived as a soft component with no active integration role.",
        ]
        return V118KCpoBreakoutDamageSoftComponentIntegrationReviewReport(
            summary=summary,
            alpha_rows=alpha_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V118KCpoBreakoutDamageSoftComponentIntegrationReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V118KCpoBreakoutDamageSoftComponentIntegrationReviewAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v118k_cpo_breakout_damage_soft_component_integration_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
