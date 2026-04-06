from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_v1 import (
    MaterializeAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1,
)


@dataclass(slots=True)
class V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1(self.repo_root).materialize()
        rows = [
            {
                "component": "consumer_preview",
                "component_state": "materialized",
                "metric": "preview_row_count",
                "value": str(materialized.summary["preview_row_count"]),
            },
            {
                "component": "consumer_preview",
                "component_state": "materialized",
                "metric": "additive_preview_count",
                "value": str(materialized.summary["additive_preview_count"]),
            },
            {
                "component": "consumer_stability",
                "component_state": "measured",
                "metric": "top_opportunity_change_if_promoted",
                "value": materialized.summary["top_opportunity_change_if_promoted"],
            },
            {
                "component": "consumer_stability",
                "component_state": "measured",
                "metric": "top_watch_change_if_promoted",
                "value": materialized.summary["top_watch_change_if_promoted"],
            },
        ]
        interpretation = [
            "This preview shows what the second-source candidate lane would surface before any main consumer promotion.",
            "It makes downstream impact explicit by comparing candidate top theme and top symbol against the current program snapshot.",
        ]
        return V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZIAShareInternalHotNewsControlledMergeCandidateConsumerPreviewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zi_a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
