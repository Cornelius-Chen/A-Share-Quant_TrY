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


SCAN_COLUMNS = [
    "churn_rejection_score",
    "vwap_rejection_imbalance_score",
    "gap_exhaustion_stall_score",
]


@dataclass(slots=True)
class V123ACpo1MinOrthogonalDownsideScanReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V123ACpo1MinOrthogonalDownsideScanAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123ACpo1MinOrthogonalDownsideScanReport:
        rows = load_recent_1min_downside_rows(self.repo_root)
        y_true = [row["proxy_action_label"] in POSITIVE_LABELS for row in rows]
        base_scores = np.asarray([float(row["downside_failure_score"]) for row in rows], dtype=float)

        candidate_rows: list[dict[str, Any]] = []
        for score_name in SCAN_COLUMNS:
            scores = np.asarray([float(row[score_name]) for row in rows], dtype=float)
            threshold = float(np.quantile(scores, 0.75))
            y_pred = [score >= threshold for score in scores]
            positives = scores[np.asarray(y_true, dtype=bool)]
            negatives = scores[~np.asarray(y_true, dtype=bool)]
            gap = float(positives.mean() - negatives.mean()) if len(positives) and len(negatives) else 0.0
            corr = float(np.corrcoef(base_scores, scores)[0, 1])
            candidate_rows.append(
                {
                    "score_name": score_name,
                    "mean_gap_positive_minus_negative": round(gap, 8),
                    "q75_threshold": round(threshold, 8),
                    "q75_balanced_accuracy": round(balanced_accuracy(y_true, y_pred), 8),
                    "corr_vs_downside_failure": round(corr, 8),
                    "orthogonal_enough": abs(corr) <= 0.65,
                }
            )

        viable_rows = [row for row in candidate_rows if row["orthogonal_enough"]]
        chosen_row = max(
            viable_rows if viable_rows else candidate_rows,
            key=lambda row: (row["mean_gap_positive_minus_negative"], row["q75_balanced_accuracy"]),
        )

        summary = {
            "acceptance_posture": "freeze_v123a_cpo_1min_orthogonal_downside_scan_v1",
            "sample_count": len(rows),
            "scan_count": len(candidate_rows),
            "chosen_score_name": chosen_row["score_name"],
            "chosen_gap": chosen_row["mean_gap_positive_minus_negative"],
            "chosen_q75_balanced_accuracy": chosen_row["q75_balanced_accuracy"],
            "chosen_corr_vs_downside_failure": chosen_row["corr_vs_downside_failure"],
            "recommended_next_posture": "time_split_audit_chosen_orthogonal_1min_downside_score",
        }
        interpretation = [
            "V1.23A scans only low-correlation 1-minute downside candidates rather than tuning the existing downside_failure family.",
            "The chosen score must be reasonably orthogonal to downside_failure first, then competitive on discovery gap and q75 balanced accuracy.",
            "The next step is chronology audit on the chosen orthogonal branch.",
        ]
        return V123ACpo1MinOrthogonalDownsideScanReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123ACpo1MinOrthogonalDownsideScanReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123ACpo1MinOrthogonalDownsideScanAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123a_cpo_1min_orthogonal_downside_scan_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

