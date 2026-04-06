from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.ingest_jobs.materialize_a_share_source_activation_foundation_v1 import (
    MaterializeAShareSourceActivationFoundationV1,
)


@dataclass(slots=True)
class V134LOAShareSourceActivationFoundationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LOAShareSourceActivationFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_source_activation_foundation_status_v1.csv"

    def analyze(self) -> V134LOAShareSourceActivationFoundationAuditV1Report:
        materialized = MaterializeAShareSourceActivationFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "source_activation_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["activation_path"],
                "coverage_note": f"activation_row_count = {summary['activation_row_count']}",
            },
            {
                "component": "source_health_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["health_path"],
                "coverage_note": f"active_local_ingest_count = {summary['active_local_ingest_count']}",
            },
            {
                "component": "ingest_activation_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["ingest_path"],
                "coverage_note": f"locally_activatable_job_count = {summary['locally_activatable_job_count']}",
            },
            {
                "component": "source_activation_residual_backlog",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"residual_count = {summary['residual_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lo_a_share_source_activation_foundation_audit_v1",
            "activation_row_count": summary["activation_row_count"],
            "active_local_ingest_count": summary["active_local_ingest_count"],
            "historical_url_catalog_count": summary["historical_url_catalog_count"],
            "placeholder_count": summary["placeholder_count"],
            "locally_activatable_job_count": summary["locally_activatable_job_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_source_activation_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "This is the first real source-activation layer: local file feeds are now explicitly activatable, while URL-based sources are kept as catalogued-but-unfetched rather than being faked as live.",
            "That closes the gap between contract-only automation and real ingest without overclaiming network reliability.",
        ]
        return V134LOAShareSourceActivationFoundationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LOAShareSourceActivationFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LOAShareSourceActivationFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lo_a_share_source_activation_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
