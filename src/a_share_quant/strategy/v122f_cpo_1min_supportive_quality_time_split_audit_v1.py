from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_supportive_continuation_utils import load_supportive_continuation_rows


@dataclass(slots=True)
class V122FCpo1MinSupportiveQualityTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


def _balanced_accuracy(y_true: list[bool], y_pred: list[bool]) -> float:
    positives = [i for i, value in enumerate(y_true) if value]
    negatives = [i for i, value in enumerate(y_true) if not value]
    pos_recall = sum(y_pred[i] for i in positives) / len(positives) if positives else 0.0
    neg_recall = sum((not y_pred[i]) for i in negatives) / len(negatives) if negatives else 0.0
    return (pos_recall + neg_recall) / 2.0


class V122FCpo1MinSupportiveQualityTimeSplitAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122FCpo1MinSupportiveQualityTimeSplitAuditReport:
        rows = load_supportive_continuation_rows(self.repo_root)
        unique_dates = sorted({row["trade_date"] for row in rows})
        split_rows = []
        test_scores: list[float] = []
        for split_index in range(1, len(unique_dates)):
            train_dates = set(unique_dates[:split_index])
            test_dates = set(unique_dates[split_index:])
            train_rows = [row for row in rows if row["trade_date"] in train_dates]
            test_rows = [row for row in rows if row["trade_date"] in test_dates]
            if not train_rows or not test_rows:
                continue
            threshold = float(np.quantile([row["supportive_quality_score"] for row in train_rows], 0.75))
            y_true = [bool(row["positive_forward_5"]) for row in test_rows]
            y_pred = [row["supportive_quality_score"] >= threshold for row in test_rows]
            ba = _balanced_accuracy(y_true, y_pred)
            test_scores.append(ba)
            split_rows.append(
                {
                    "train_end_date": max(train_dates),
                    "test_start_date": min(test_dates),
                    "test_row_count": len(test_rows),
                    "threshold": round(threshold, 8),
                    "balanced_accuracy": round(ba, 8),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122f_cpo_1min_supportive_quality_time_split_audit_v1",
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(test_scores)), 8) if test_scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(test_scores)), 8) if test_scores else 0.0,
            "recommended_next_posture": "continue_only_if_quality_score_remains_directional_under_date_split",
        }
        interpretation = [
            "V1.22F checks whether the supportive quality score survives date splits on the recent 1-minute plane.",
            "This is still a local chronology audit, but it is the minimum guardrail against same-window self-delusion.",
            "The score should only continue if it keeps directional separation under date split.",
        ]
        return V122FCpo1MinSupportiveQualityTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122FCpo1MinSupportiveQualityTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122FCpo1MinSupportiveQualityTimeSplitAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122f_cpo_1min_supportive_quality_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
