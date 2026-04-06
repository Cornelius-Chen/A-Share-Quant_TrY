from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.ingest_jobs.materialize_a_share_network_fetch_adapter_foundation_v1 import (
    MaterializeAShareNetworkFetchAdapterFoundationV1,
)


@dataclass(slots=True)
class V134MAAShareNetworkFetchAdapterFoundationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_network_fetch_adapter_foundation_status_v1.csv"

    def analyze(self) -> V134MAAShareNetworkFetchAdapterFoundationAuditV1Report:
        materialized = MaterializeAShareNetworkFetchAdapterFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "adapter_registry",
                "component_state": "materialized_contracts",
                "artifact_path": summary["adapter_path"],
                "coverage_note": f"adapter_count = {summary['adapter_count']}",
            },
            {
                "component": "host_binding_registry",
                "component_state": "materialized_stub_bindings",
                "artifact_path": summary["host_path"],
                "coverage_note": f"host_binding_count = {summary['host_binding_count']}",
            },
            {
                "component": "adapter_residual_backlog",
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
            "acceptance_posture": "build_v134ma_a_share_network_fetch_adapter_foundation_audit_v1",
            "adapter_count": summary["adapter_count"],
            "host_binding_count": summary["host_binding_count"],
            "stub_ready_host_count": summary["stub_ready_host_count"],
            "residual_count": summary["residual_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_network_fetch_adapter_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "This is the first sanctioned network-fetch layer: adapter families and host bindings are now explicit, even though activation remains deferred.",
            "That converts the old network-fetch gap into a smaller, better-named gap: activation and operational policy, not missing adapter structure.",
        ]
        return V134MAAShareNetworkFetchAdapterFoundationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MAAShareNetworkFetchAdapterFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ma_a_share_network_fetch_adapter_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
