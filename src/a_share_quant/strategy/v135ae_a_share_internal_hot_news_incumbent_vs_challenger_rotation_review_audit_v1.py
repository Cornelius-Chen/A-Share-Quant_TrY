from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_v1 import (
    MaterializeAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1,
)


@dataclass(slots=True)
class V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1(self.repo_root).materialize()
        rows = [
            {
                "component": "incumbent_focus",
                "component_state": "materialized",
                "metric": "incumbent_theme_slug",
                "value": materialized.summary["incumbent_theme_slug"],
            },
            {
                "component": "incumbent_focus",
                "component_state": "materialized",
                "metric": "incumbent_support_row_count",
                "value": str(materialized.summary["incumbent_support_row_count"]),
            },
            {
                "component": "challenger_focus",
                "component_state": "materialized",
                "metric": "challenger_theme_slug",
                "value": materialized.summary["challenger_theme_slug"],
            },
            {
                "component": "challenger_focus",
                "component_state": "materialized",
                "metric": "challenger_support_row_count",
                "value": str(materialized.summary["challenger_support_row_count"]),
            },
            {
                "component": "rotation_review",
                "component_state": "materialized",
                "metric": "review_state",
                "value": materialized.summary["review_state"],
            },
        ]
        interpretation = [
            "This review places the current accepted focus beside the strongest challenger and applies a simple thresholded decision rule.",
            "It is intentionally conservative: challenger superiority must be materially larger before opening the next rotation review.",
        ]
        return V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ae_a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
