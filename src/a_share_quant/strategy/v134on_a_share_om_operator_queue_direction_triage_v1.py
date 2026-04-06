from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134om_a_share_source_internal_manual_operator_queue_audit_v1 import (
    V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ONAShareOMOperatorQueueDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ONAShareOMOperatorQueueDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ONAShareOMOperatorQueueDirectionTriageV1Report:
        report = V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "queue_row_count": report.summary["queue_row_count"],
            "ready_primary_review_count": report.summary["ready_primary_review_count"],
            "authoritative_status": "source_internal_manual_should_now_be_worked_as_operator_queue_not_as_flat_workpack",
        }
        triage_rows = [
            {
                "component": "primary_host_family",
                "direction": "start_with_primary_host_family_manual_record_fill",
            },
            {
                "component": "independent_hosts",
                "direction": "prepare_independent_hosts_but_keep_them_after_primary_review",
            },
            {
                "component": "sibling_host",
                "direction": "retain_sibling_host_blocked_until_primary_host_family_outcome_exists",
            },
            {
                "component": "queue_governance",
                "direction": "treat_operator_queue_as_the_active_source_internal_manual_control_surface",
            },
        ]
        interpretation = [
            "Source-side manual closure no longer needs additional structure; it now has an operator-ready queue.",
            "The next gain comes from filling queue rows in order, not from adding more registries.",
        ]
        return V134ONAShareOMOperatorQueueDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134ONAShareOMOperatorQueueDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ONAShareOMOperatorQueueDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134on_a_share_om_operator_queue_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
