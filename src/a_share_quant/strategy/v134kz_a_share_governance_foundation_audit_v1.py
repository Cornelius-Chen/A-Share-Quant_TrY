from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.governance.registry.materialize_a_share_governance_foundation_v1 import (
    MaterializeAShareGovernanceFoundationV1,
)


@dataclass(slots=True)
class V134KZAShareGovernanceFoundationAuditV1Report:
    summary: dict[str, Any]
    governance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "governance_rows": self.governance_rows,
            "interpretation": self.interpretation,
        }


class V134KZAShareGovernanceFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_governance_foundation_status_v1.csv"

    def analyze(self) -> V134KZAShareGovernanceFoundationAuditV1Report:
        materialized = MaterializeAShareGovernanceFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        governance_rows = [
            {
                "governance_component": "schema_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["schema_path"],
                "coverage_note": f"schema_count = {summary['schema_count']}",
            },
            {
                "governance_component": "dataset_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["dataset_path"],
                "coverage_note": f"dataset_count = {summary['dataset_count']}",
            },
            {
                "governance_component": "workstream_heartbeat",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["heartbeat_path"],
                "coverage_note": f"heartbeat_count = {summary['heartbeat_count']}",
            },
            {
                "governance_component": "promotion_gates",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["gate_path"],
                "coverage_note": f"closed_gate_count = {summary['closed_gate_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(governance_rows[0].keys()))
            writer.writeheader()
            writer.writerows(governance_rows)

        report_summary = {
            "acceptance_posture": "build_v134kz_a_share_governance_foundation_audit_v1",
            "schema_count": summary["schema_count"],
            "dataset_count": summary["dataset_count"],
            "heartbeat_count": summary["heartbeat_count"],
            "closed_gate_count": summary["closed_gate_count"],
            "governance_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_governance_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KZ gives the information center its first explicit control plane: schema, dataset, heartbeat, and promotion gates are now materialized instead of implied.",
            "This is the minimum governance layer needed before automation can be allowed to mutate storage and lifecycle state.",
        ]
        return V134KZAShareGovernanceFoundationAuditV1Report(
            summary=report_summary,
            governance_rows=governance_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134KZAShareGovernanceFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KZAShareGovernanceFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kz_a_share_governance_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
