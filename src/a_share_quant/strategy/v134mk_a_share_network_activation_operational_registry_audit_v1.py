from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.orchestration.materialize_a_share_network_activation_operational_registry_v1 import (
    MaterializeAShareNetworkActivationOperationalRegistryV1,
)


@dataclass(slots=True)
class V134MKAShareNetworkActivationOperationalRegistryAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_network_activation_operational_registry_status_v1.csv"
        )

    def analyze(self) -> V134MKAShareNetworkActivationOperationalRegistryAuditV1Report:
        materialized = MaterializeAShareNetworkActivationOperationalRegistryV1(self.repo_root).materialize()
        summary = materialized.summary
        manual_review_pending_count = sum(
            row["license_review_state"] == "manual_review_pending" for row in materialized.license_rows
        )
        scheduler_stub_count = sum(
            row["runtime_binding_state"] == "scheduler_stub_not_activated" for row in materialized.scheduler_rows
        )

        rows = [
            {
                "component": "license_review_registry",
                "component_state": "materialized_pending_review_surface",
                "artifact_path": summary["license_path"],
                "coverage_note": f"manual_review_pending_count = {manual_review_pending_count}",
            },
            {
                "component": "scheduler_runtime_registry",
                "component_state": "materialized_runtime_stub_surface",
                "artifact_path": summary["scheduler_path"],
                "coverage_note": f"scheduler_stub_count = {scheduler_stub_count}",
            },
            {
                "component": "operational_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"review_only_excluded_count = {summary['review_only_excluded_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "license_review_row_count": summary["license_review_row_count"],
            "scheduler_runtime_row_count": summary["scheduler_runtime_row_count"],
            "manual_review_pending_count": manual_review_pending_count,
            "scheduler_stub_count": scheduler_stub_count,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_network_activation_operational_registries_materialized",
        }
        interpretation = [
            "Selective activation now has operational registries instead of only policy conclusions.",
            "The remaining source-side work is explicit queue processing and runtime deployment, not registry design.",
        ]
        return V134MKAShareNetworkActivationOperationalRegistryAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MKAShareNetworkActivationOperationalRegistryAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mk_a_share_network_activation_operational_registry_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
