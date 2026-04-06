from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.orchestration.materialize_a_share_network_activation_queue_surface_v1 import (
    MaterializeAShareNetworkActivationQueueSurfaceV1,
)


@dataclass(slots=True)
class V134MMAShareNetworkActivationQueueSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_network_activation_queue_surface_status_v1.csv"
        )

    def analyze(self) -> V134MMAShareNetworkActivationQueueSurfaceAuditV1Report:
        materialized = MaterializeAShareNetworkActivationQueueSurfaceV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "allowlist_decision_queue",
                "component_state": "materialized_pending_queue",
                "artifact_path": summary["allowlist_queue_path"],
                "coverage_note": f"allowlist_queue_count = {summary['allowlist_queue_count']}",
            },
            {
                "component": "runtime_deployment_queue",
                "component_state": "materialized_pending_queue",
                "artifact_path": summary["runtime_queue_path"],
                "coverage_note": f"runtime_queue_count = {summary['runtime_queue_count']}",
            },
            {
                "component": "queue_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": "all queued items remain undecided",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "allowlist_queue_count": summary["allowlist_queue_count"],
            "runtime_queue_count": summary["runtime_queue_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_network_activation_queue_surface_materialized",
        }
        interpretation = [
            "Source-side activation is now staged as explicit queues rather than implicit future work.",
            "The next remaining work is queue processing, not additional scaffolding.",
        ]
        return V134MMAShareNetworkActivationQueueSurfaceAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MMAShareNetworkActivationQueueSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mm_a_share_network_activation_queue_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
