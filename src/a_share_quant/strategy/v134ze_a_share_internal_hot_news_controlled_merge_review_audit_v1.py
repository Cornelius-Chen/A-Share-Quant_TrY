from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_review_v1 import (
    MaterializeAShareInternalHotNewsControlledMergeReviewV1,
)


@dataclass(slots=True)
class V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsControlledMergeReviewV1(self.repo_root).materialize()
        rows = [
            {
                "component": "merge_review",
                "component_state": "materialized",
                "metric": "combined_row_count",
                "value": str(materialized.summary["combined_row_count"]),
            },
            {
                "component": "merge_review",
                "component_state": "materialized",
                "metric": "merge_cluster_count",
                "value": str(materialized.summary["merge_cluster_count"]),
            },
            {
                "component": "duplicate_candidates",
                "component_state": "measured",
                "metric": "cross_source_duplicate_candidate_count",
                "value": str(materialized.summary["cross_source_duplicate_candidate_count"]),
            },
            {
                "component": "additive_candidates",
                "component_state": "measured",
                "metric": "additive_sina_candidate_count",
                "value": str(materialized.summary["additive_sina_candidate_count"]),
            },
        ]
        interpretation = [
            "This review surface measures whether a second source can be added without uncontrolled duplicate fan-out.",
            "It separates cross-source duplicate candidates from additive themed rows before any primary fastlane merge.",
        ]
        return V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ze_a_share_internal_hot_news_controlled_merge_review_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
