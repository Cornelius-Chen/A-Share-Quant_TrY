from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mm_a_share_network_activation_queue_surface_audit_v1 import (
    V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MNAShareMMNetworkActivationQueueDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MNAShareMMNetworkActivationQueueDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MNAShareMMNetworkActivationQueueDirectionTriageV1Report:
        report = V134MMAShareNetworkActivationQueueSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "allowlist_queue_count": report.summary["allowlist_queue_count"],
            "runtime_queue_count": report.summary["runtime_queue_count"],
            "authoritative_status": "network_activation_queue_surface_complete_enough_to_freeze_until_queue_processing",
        }
        triage_rows = [
            {
                "component": "allowlist_decision_queue",
                "direction": "process_license_terms_and_allowlist_decisions_before_any_host_activation",
            },
            {
                "component": "runtime_deployment_queue",
                "direction": "deploy_scheduler_runtime_only_after_allowlist_progress_and gate alignment",
            },
        ]
        interpretation = [
            "The source-side path has reached a queue-processing stopline.",
            "Further progress now requires actual review decisions or scheduler deployment work, not more inventory scaffolding.",
        ]
        return V134MNAShareMMNetworkActivationQueueDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MNAShareMMNetworkActivationQueueDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MNAShareMMNetworkActivationQueueDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mn_a_share_mm_network_activation_queue_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
