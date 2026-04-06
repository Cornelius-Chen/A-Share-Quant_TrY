from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mk_a_share_network_activation_operational_registry_audit_v1 import (
    V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Report:
        report = V134MKAShareNetworkActivationOperationalRegistryAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "license_review_row_count": report.summary["license_review_row_count"],
            "scheduler_runtime_row_count": report.summary["scheduler_runtime_row_count"],
            "authoritative_status": "network_activation_operations_ready_for_queue_processing_but_not_activation",
        }
        triage_rows = [
            {
                "component": "license_review_registry",
                "direction": "process_allowlist_decisions_before_any_selective_host_activation",
            },
            {
                "component": "scheduler_runtime_registry",
                "direction": "deploy_runtime_binding_only_after_allowlist_policy_and governance approval remain aligned",
            },
        ]
        interpretation = [
            "The source-side activation path is now operationally staged: review queue first, runtime deployment second.",
            "This still does not authorize activation; it only makes the path executable when gates are later opened.",
        ]
        return V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MLAShareMKNetworkActivationOperationalDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ml_a_share_mk_network_activation_operational_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
