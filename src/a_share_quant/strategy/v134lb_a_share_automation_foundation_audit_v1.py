from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.orchestration.materialize_a_share_automation_foundation_v1 import (
    MaterializeAShareAutomationFoundationV1,
)


@dataclass(slots=True)
class V134LBAShareAutomationFoundationAuditV1Report:
    summary: dict[str, Any]
    automation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "automation_rows": self.automation_rows,
            "interpretation": self.interpretation,
        }


class V134LBAShareAutomationFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_automation_foundation_status_v1.csv"

    def analyze(self) -> V134LBAShareAutomationFoundationAuditV1Report:
        materialized = MaterializeAShareAutomationFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        automation_rows = [
            {
                "automation_component": "ingest_jobs",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["ingest_path"],
                "coverage_note": f"ingest_job_count = {summary['ingest_job_count']}",
            },
            {
                "automation_component": "pipeline_jobs",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["pipeline_path"],
                "coverage_note": f"pipeline_job_count = {summary['pipeline_job_count']}",
            },
            {
                "automation_component": "review_jobs",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["review_path"],
                "coverage_note": f"review_job_count = {summary['review_job_count']}",
            },
            {
                "automation_component": "retention_jobs",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["retention_path"],
                "coverage_note": f"retention_job_count = {summary['retention_job_count']}",
            },
            {
                "automation_component": "orchestration_flows",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["orchestration_path"],
                "coverage_note": f"orchestration_flow_count = {summary['orchestration_flow_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(automation_rows[0].keys()))
            writer.writeheader()
            writer.writerows(automation_rows)

        report_summary = {
            "acceptance_posture": "build_v134lb_a_share_automation_foundation_audit_v1",
            "ingest_job_count": summary["ingest_job_count"],
            "pipeline_job_count": summary["pipeline_job_count"],
            "review_job_count": summary["review_job_count"],
            "retention_job_count": summary["retention_job_count"],
            "orchestration_flow_count": summary["orchestration_flow_count"],
            "automation_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_automation_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34LB completes the first automation workstream pass by defining reproducible ingest, pipeline, review, retention, and orchestration registries.",
            "Automation remains contract-first rather than blindly active, which is appropriate because governance was only just materialized.",
        ]
        return V134LBAShareAutomationFoundationAuditV1Report(
            summary=report_summary,
            automation_rows=automation_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LBAShareAutomationFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LBAShareAutomationFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lb_a_share_automation_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
