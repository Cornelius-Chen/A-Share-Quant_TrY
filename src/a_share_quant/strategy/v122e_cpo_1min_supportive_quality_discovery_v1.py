from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_supportive_continuation_utils import load_supportive_continuation_rows


@dataclass(slots=True)
class V122ECpo1MinSupportiveQualityDiscoveryReport:
    summary: dict[str, Any]
    score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "score_rows": self.score_rows,
            "interpretation": self.interpretation,
        }


class V122ECpo1MinSupportiveQualityDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122ECpo1MinSupportiveQualityDiscoveryReport:
        rows = load_supportive_continuation_rows(self.repo_root)
        positive_scores = [row["supportive_quality_score"] for row in rows if row["positive_forward_5"]]
        negative_scores = [row["supportive_quality_score"] for row in rows if not row["positive_forward_5"]]
        discovery_gap = float(np.mean(positive_scores) - np.mean(negative_scores)) if positive_scores and negative_scores else 0.0
        threshold = float(np.quantile([row["supportive_quality_score"] for row in rows], 0.75)) if rows else 0.0
        threshold_rows = [row for row in rows if row["supportive_quality_score"] >= threshold]
        threshold_positive_rate = (
            float(np.mean([row["positive_forward_5"] for row in threshold_rows])) if threshold_rows else 0.0
        )

        summary = {
            "acceptance_posture": "freeze_v122e_cpo_1min_supportive_quality_discovery_v1",
            "sample_count": len(rows),
            "positive_count": len(positive_scores),
            "negative_count": len(negative_scores),
            "discovery_mean_gap_positive_minus_negative": round(discovery_gap, 8),
            "threshold_q75": round(threshold, 8),
            "threshold_positive_rate": round(threshold_positive_rate, 8),
            "recommended_next_posture": "audit_supportive_quality_score_out_of_set",
        }
        score_rows = [
            {
                "group": "positive_forward_5",
                "sample_count": len(positive_scores),
                "mean_supportive_quality_score": round(float(np.mean(positive_scores)), 8) if positive_scores else 0.0,
            },
            {
                "group": "non_positive_forward_5",
                "sample_count": len(negative_scores),
                "mean_supportive_quality_score": round(float(np.mean(negative_scores)), 8) if negative_scores else 0.0,
            },
        ]
        interpretation = [
            "V1.22E hardens the supportive continuation family with a visible-only quality score instead of inventing a new family.",
            "The score should only continue if positive short-horizon outcomes cluster in the upper-score region.",
            "This remains a non-replay discovery step and must be followed by out-of-set audit.",
        ]
        return V122ECpo1MinSupportiveQualityDiscoveryReport(
            summary=summary,
            score_rows=score_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122ECpo1MinSupportiveQualityDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122ECpo1MinSupportiveQualityDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122e_cpo_1min_supportive_quality_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
