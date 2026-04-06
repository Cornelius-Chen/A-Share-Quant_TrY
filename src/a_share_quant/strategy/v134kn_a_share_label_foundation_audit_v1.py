from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.labels.materialize_a_share_label_foundation_v1 import (
    MaterializeAShareLabelFoundationV1,
)


@dataclass(slots=True)
class V134KNAShareLabelFoundationAuditV1Report:
    summary: dict[str, Any]
    label_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_rows": self.label_rows,
            "interpretation": self.interpretation,
        }


class V134KNAShareLabelFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_label_foundation_status_v1.csv"

    def analyze(self) -> V134KNAShareLabelFoundationAuditV1Report:
        materialized = MaterializeAShareLabelFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        label_rows = [
            {
                "label_component": "label_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["label_registry_path"],
                "coverage_note": f"label_definition_count = {summary['label_definition_count']}",
            },
            {
                "label_component": "label_assignment_surface",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["label_assignment_path"],
                "coverage_note": f"label_assignment_count = {summary['label_assignment_count']}",
            },
            {
                "label_component": "state_label_backlog",
                "component_state": "backlog_materialized_not_assigned",
                "artifact_path": summary["state_backlog_path"],
                "coverage_note": f"state_backlog_count = {summary['state_backlog_count']}",
            },
            {
                "label_component": "governance_label_backlog",
                "component_state": "backlog_materialized_not_assigned",
                "artifact_path": summary["governance_backlog_path"],
                "coverage_note": f"governance_backlog_count = {summary['governance_backlog_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(label_rows[0].keys()))
            writer.writeheader()
            writer.writerows(label_rows)

        report_summary = {
            "acceptance_posture": "build_v134kn_a_share_label_foundation_audit_v1",
            "label_definition_count": summary["label_definition_count"],
            "label_assignment_count": summary["label_assignment_count"],
            "state_backlog_count": summary["state_backlog_count"],
            "governance_backlog_count": summary["governance_backlog_count"],
            "label_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_label_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KN completes the first label workstream pass by creating a central label registry plus a bootstrap assignment surface for fact and semantic labels.",
            "State and governance labels remain explicit backlog layers instead of being faked before PTI and serving surfaces exist.",
        ]
        return V134KNAShareLabelFoundationAuditV1Report(
            summary=report_summary,
            label_rows=label_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KNAShareLabelFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KNAShareLabelFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kn_a_share_label_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
