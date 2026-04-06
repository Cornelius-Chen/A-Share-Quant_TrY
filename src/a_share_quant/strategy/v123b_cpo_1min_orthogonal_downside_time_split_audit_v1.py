from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v123_1min_orthogonal_downside_utils import (
    POSITIVE_LABELS,
    balanced_accuracy,
    load_recent_1min_downside_rows,
)


@dataclass(slots=True)
class V123BCpo1MinOrthogonalDownsideTimeSplitAuditReport:
    summary: dict[str, Any]
    split_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "split_rows": self.split_rows,
            "interpretation": self.interpretation,
        }


class V123BCpo1MinOrthogonalDownsideTimeSplitAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123BCpo1MinOrthogonalDownsideTimeSplitAuditReport:
        selection_path = self.repo_root / "reports" / "analysis" / "v123a_cpo_1min_orthogonal_downside_scan_v1.json"
        with selection_path.open("r", encoding="utf-8") as handle:
            selection_report = json.load(handle)
        score_name = selection_report["summary"]["chosen_score_name"]

        rows = load_recent_1min_downside_rows(self.repo_root)
        unique_dates = sorted({row["trade_date"] for row in rows})
        split_rows: list[dict[str, Any]] = []
        scores: list[float] = []
        for split_index in range(1, len(unique_dates)):
            train_dates = set(unique_dates[:split_index])
            test_dates = set(unique_dates[split_index:])
            train_rows = [row for row in rows if row["trade_date"] in train_dates]
            test_rows = [row for row in rows if row["trade_date"] in test_dates]
            if not train_rows or not test_rows:
                continue
            threshold = float(np.quantile([float(row[score_name]) for row in train_rows], 0.75))
            y_true = [row["proxy_action_label"] in POSITIVE_LABELS for row in test_rows]
            y_pred = [float(row[score_name]) >= threshold for row in test_rows]
            ba = balanced_accuracy(y_true, y_pred)
            scores.append(ba)
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
            "acceptance_posture": "freeze_v123b_cpo_1min_orthogonal_downside_time_split_audit_v1",
            "chosen_score_name": score_name,
            "split_count": len(split_rows),
            "mean_test_balanced_accuracy": round(float(np.mean(scores)), 8) if scores else 0.0,
            "min_test_balanced_accuracy": round(float(np.min(scores)), 8) if scores else 0.0,
            "recommended_next_posture": "symbol_holdout_audit_chosen_orthogonal_1min_downside_score",
        }
        interpretation = [
            "V1.23B applies chronology audit to the best low-correlation 1-minute downside candidate chosen in V1.23A.",
            "This is the minimum transfer hurdle before considering the new branch alive.",
            "The next step is symbol holdout audit.",
        ]
        return V123BCpo1MinOrthogonalDownsideTimeSplitAuditReport(
            summary=summary,
            split_rows=split_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123BCpo1MinOrthogonalDownsideTimeSplitAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123BCpo1MinOrthogonalDownsideTimeSplitAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123b_cpo_1min_orthogonal_downside_time_split_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

