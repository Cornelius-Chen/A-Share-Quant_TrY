from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _balanced_accuracy(rows: list[dict[str, Any]], threshold: float) -> dict[str, float]:
    positives = [row for row in rows if bool(row.get("positive_reduce_label"))]
    negatives = [row for row in rows if not bool(row.get("positive_reduce_label"))]
    tp = sum(1 for row in positives if _to_float(row.get("board_risk_off_reduce_score_candidate")) >= threshold)
    fp = sum(1 for row in negatives if _to_float(row.get("board_risk_off_reduce_score_candidate")) >= threshold)
    tn = len(negatives) - fp
    tpr = tp / len(positives) if positives else 0.0
    tnr = tn / len(negatives) if negatives else 0.0
    return {
        "threshold": round(threshold, 6),
        "positive_recall": round(tpr, 6),
        "negative_reject_rate": round(tnr, 6),
        "balanced_accuracy": round((tpr + tnr) / 2.0, 6),
    }


@dataclass(slots=True)
class V121KCpoReduceSideBoardRiskOffTimeSplitValidationReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V121KCpoReduceSideBoardRiskOffTimeSplitValidationAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v121j_payload: dict[str, Any]) -> V121KCpoReduceSideBoardRiskOffTimeSplitValidationReport:
        rows = list(v121j_payload.get("scored_rows", []))
        split_defs = (
            ("holdout_2023", {"2023"}),
            ("holdout_2024", {"2024"}),
            ("holdout_2025_plus", {"2025", "2026"}),
        )
        split_rows: list[dict[str, Any]] = []
        for split_name, holdout_years in split_defs:
            train_rows = [row for row in rows if str(row["signal_trade_date"])[:4] not in holdout_years]
            test_rows = [row for row in rows if str(row["signal_trade_date"])[:4] in holdout_years]
            thresholds = sorted({_to_float(row.get("board_risk_off_reduce_score_candidate")) for row in train_rows}, reverse=True)
            best_train = None
            for threshold in thresholds:
                record = _balanced_accuracy(train_rows, threshold)
                if best_train is None or record["balanced_accuracy"] > best_train["balanced_accuracy"]:
                    best_train = record
            best_train = best_train or {"threshold": 0.0, "balanced_accuracy": 0.0}
            test_record = _balanced_accuracy(test_rows, _to_float(best_train["threshold"]))
            split_rows.append(
                {
                    "split_name": split_name,
                    "holdout_years": sorted(holdout_years),
                    "train_row_count": len(train_rows),
                    "test_row_count": len(test_rows),
                    "train_positive_count": sum(1 for row in train_rows if bool(row.get("positive_reduce_label"))),
                    "test_positive_count": sum(1 for row in test_rows if bool(row.get("positive_reduce_label"))),
                    "train_best_threshold": best_train["threshold"],
                    "train_best_balanced_accuracy": best_train["balanced_accuracy"],
                    "test_balanced_accuracy": test_record["balanced_accuracy"],
                    "test_positive_recall": test_record["positive_recall"],
                    "test_negative_reject_rate": test_record["negative_reject_rate"],
                }
            )

        mean_test_balanced_accuracy = sum(_to_float(row["test_balanced_accuracy"]) for row in split_rows) / len(split_rows)
        min_test_balanced_accuracy = min(_to_float(row["test_balanced_accuracy"]) for row in split_rows)
        summary = {
            "acceptance_posture": "freeze_v121k_cpo_reduce_side_board_risk_off_time_split_validation_v1",
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(mean_test_balanced_accuracy, 6),
            "min_test_balanced_accuracy": round(min_test_balanced_accuracy, 6),
            "stability_posture": (
                "candidate_stable_enough_for_next_adversarial_review"
                if min_test_balanced_accuracy >= 0.5
                else "candidate_unstable_under_time_split"
            ),
            "recommended_next_posture": "send_IJK_to_three_run_adversarial_review_only_if_external_gap_is_not_trivial",
        }
        interpretation = [
            "V1.21K applies chronology discipline to the first formal reduce-side board risk-off branch.",
            "A risk-off line that cannot survive crude year splits is not trustworthy enough to govern de-risk behavior.",
            "This closes the first three-run block for the reduce-side board risk-off direction.",
        ]
        return V121KCpoReduceSideBoardRiskOffTimeSplitValidationReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121KCpoReduceSideBoardRiskOffTimeSplitValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121KCpoReduceSideBoardRiskOffTimeSplitValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v121j_payload=json.loads((repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121k_cpo_reduce_side_board_risk_off_time_split_validation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
