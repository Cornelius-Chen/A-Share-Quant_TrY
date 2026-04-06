from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v123_daily_residual_downside_utils import (
    build_daily_residual_downside_sample,
    score_daily_residual_candidates,
)


@dataclass(slots=True)
class V123MCpoDailyResidualDownsideDiscoveryReport:
    summary: dict[str, Any]
    feature_snapshot_rows: list[dict[str, Any]]
    candidate_score_rows: list[dict[str, Any]]
    scored_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_snapshot_rows": self.feature_snapshot_rows,
            "candidate_score_rows": self.candidate_score_rows,
            "scored_rows": self.scored_rows,
            "interpretation": self.interpretation,
        }


class V123MCpoDailyResidualDownsideDiscoveryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123MCpoDailyResidualDownsideDiscoveryReport:
        dataset = build_daily_residual_downside_sample(repo_root=self.repo_root)
        scored_rows, candidate_rows = score_daily_residual_candidates(dataset.sample_rows)
        positives = [row for row in scored_rows if bool(row["positive_label"])]
        negatives = [row for row in scored_rows if not bool(row["positive_label"])]

        feature_snapshot_rows: list[dict[str, Any]] = []
        for feature_name in dataset.feature_names:
            positive_mean = sum(float(row[feature_name]) for row in positives) / len(positives)
            negative_mean = sum(float(row[feature_name]) for row in negatives) / len(negatives)
            feature_snapshot_rows.append(
                {
                    "feature_name": feature_name,
                    "positive_mean": round(positive_mean, 6),
                    "negative_mean": round(negative_mean, 6),
                    "mean_gap_positive_minus_negative": round(positive_mean - negative_mean, 6),
                }
            )
        feature_snapshot_rows.sort(key=lambda row: abs(float(row["mean_gap_positive_minus_negative"])), reverse=True)

        chosen_candidate = candidate_rows[0]
        summary = {
            "acceptance_posture": "freeze_v123m_cpo_daily_residual_downside_discovery_v1",
            "sample_posture": "held_pair_high_cash_non_overheated_daily_subset",
            "residual_interval_start": dataset.residual_interval_start,
            "residual_interval_end": dataset.residual_interval_end,
            "sample_row_count": len(scored_rows),
            "positive_row_count": len(positives),
            "negative_row_count": len(negatives),
            "selected_candidate_name": chosen_candidate["candidate_name"],
            "selected_discovery_mean_gap_positive_minus_negative": chosen_candidate[
                "discovery_mean_gap_positive_minus_negative"
            ],
            "selected_q75_balanced_accuracy": chosen_candidate["q75_balanced_accuracy"],
            "recommended_next_posture": "chronology_audit_residual_downside_before_any_status_upgrade",
        }
        interpretation = [
            "V1.23M opens a residual daily downside branch aimed at the one large drawdown that heat guardrails did not improve.",
            "The sample is intentionally narrow: both 300308 and 300502 held together, but cash still above 60%, so this is not a generic overheated carry problem.",
            "The point is to see whether pair deterioration can explain the remaining downside that survives position heat caps.",
        ]
        return V123MCpoDailyResidualDownsideDiscoveryReport(
            summary=summary,
            feature_snapshot_rows=feature_snapshot_rows,
            candidate_score_rows=candidate_rows,
            scored_rows=scored_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123MCpoDailyResidualDownsideDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123MCpoDailyResidualDownsideDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123m_cpo_daily_residual_downside_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
