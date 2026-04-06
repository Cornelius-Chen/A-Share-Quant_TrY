from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lb_a_share_automation_foundation_audit_v1 import (
    V134LBAShareAutomationFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LCAShareLBAutomationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LCAShareLBAutomationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LCAShareLBAutomationDirectionTriageV1Report:
        audit = V134LBAShareAutomationFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "automation_component": "ingest_pipeline_review_retention",
                "direction": "freeze_as_bootstrap_job_contracts_pending_future_activation",
            },
            {
                "automation_component": "orchestration_flows",
                "direction": "retain_as_control_plane_sequences_not_yet_bound_to_scheduler",
            },
            {
                "automation_component": "next_frontier",
                "direction": "freeze_information_center_foundation_as_complete_enough_and_shift_later_into_real_source_activation_or_module_backlog_closure",
            },
        ]
        summary = {
            "ingest_job_count": audit.summary["ingest_job_count"],
            "retention_job_count": audit.summary["retention_job_count"],
            "orchestration_flow_count": audit.summary["orchestration_flow_count"],
            "authoritative_status": (
                "automation_workstream_complete_enough_to_freeze_and_mark_information_center_foundation_complete"
            ),
        }
        interpretation = [
            "Automation is now specified enough that the information center has a full contract for how data gets in, moves through pipelines, is reviewed, and leaves via retention.",
            "The correct stopline is to freeze the foundation here and only activate concrete jobs when external source integrations and future evidence modules are ready.",
        ]
        return V134LCAShareLBAutomationDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LCAShareLBAutomationDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LCAShareLBAutomationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lc_a_share_lb_automation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
