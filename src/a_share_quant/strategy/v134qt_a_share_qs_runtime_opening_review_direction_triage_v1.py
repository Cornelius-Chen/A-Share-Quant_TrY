from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Report:
        report = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "review_row_count": report.summary["review_row_count"],
            "scheduler_pending_count": report.summary["scheduler_pending_count"],
            "governance_closed_count": report.summary["governance_closed_count"],
            "authoritative_status": "runtime_opening_followthrough_should_continue_from_single_scheduler_governance_review_surface_only",
        }
        triage_rows = [
            {
                "component": "opening_review_surface",
                "direction": "use_the_single_row_scheduler_governance_review_surface_as_the_only_source-side_opening_followthrough_surface",
            },
            {
                "component": "next_controlled_movement",
                "direction": "activate_scheduler_runtime_binding_first_then_reaudit_live_like_and_execution_governance_opening",
            },
            {
                "component": "opening_boundary",
                "direction": "retain_silent_opening_disallowed_and_do_not_auto-promote_the_html-article_candidate",
            },
        ]
        interpretation = [
            "Source-side no longer needs more queue, lane, or deployment-candidate expansion; opening followthrough should continue only from the single combined review surface.",
            "Scheduler movement should come first, while governance opening remains an explicit re-audit step rather than an automatic consequence.",
        ]
        return V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QTAShareQSRuntimeOpeningReviewDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qt_a_share_qs_runtime_opening_review_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
