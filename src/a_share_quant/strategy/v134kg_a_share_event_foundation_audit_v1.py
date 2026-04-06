from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.events.event_objects.materialize_a_share_event_foundation_v1 import (
    MaterializeAShareEventFoundationV1,
)


@dataclass(slots=True)
class V134KGAShareEventFoundationAuditV1Report:
    summary: dict[str, Any]
    event_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "event_rows": self.event_rows,
            "interpretation": self.interpretation,
        }


class V134KGAShareEventFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_event_foundation_status_v1.csv"

    def analyze(self) -> V134KGAShareEventFoundationAuditV1Report:
        materialized = MaterializeAShareEventFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        event_rows = [
            {
                "event_component": "source_master",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["source_master_path"],
                "coverage_note": f"materialized_source_count = {summary['materialized_source_count']}",
            },
            {
                "event_component": "document_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["document_registry_path"],
                "coverage_note": f"materialized_document_count = {summary['materialized_document_count']}",
            },
            {
                "event_component": "claim_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["claim_registry_path"],
                "coverage_note": f"materialized_claim_count = {summary['materialized_claim_count']}",
            },
            {
                "event_component": "event_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["event_registry_path"],
                "coverage_note": f"materialized_event_count = {summary['materialized_event_count']}",
            },
            {
                "event_component": "evidence_span_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["evidence_registry_path"],
                "coverage_note": f"materialized_evidence_count = {summary['materialized_evidence_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(event_rows[0].keys()))
            writer.writeheader()
            writer.writerows(event_rows)

        report_summary = {
            "acceptance_posture": "build_v134kg_a_share_event_foundation_audit_v1",
            "input_registry_row_count": summary["input_registry_row_count"],
            "materialized_source_count": summary["materialized_source_count"],
            "materialized_document_count": summary["materialized_document_count"],
            "materialized_event_count": summary["materialized_event_count"],
            "event_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_event_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KG completes the first event workstream pass by transforming existing catalyst registries into a minimum source-document-claim-event-evidence chain.",
            "This is still a bootstrap object model, but it is now a real ingestable event layer rather than scattered board-specific registry files.",
        ]
        return V134KGAShareEventFoundationAuditV1Report(
            summary=report_summary,
            event_rows=event_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KGAShareEventFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KGAShareEventFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kg_a_share_event_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
