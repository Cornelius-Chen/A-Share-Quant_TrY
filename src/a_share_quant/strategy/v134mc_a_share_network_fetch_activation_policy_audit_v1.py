from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.orchestration.materialize_a_share_network_fetch_activation_policy_v1 import (
    MaterializeAShareNetworkFetchActivationPolicyV1,
)


@dataclass(slots=True)
class V134MCAShareNetworkFetchActivationPolicyAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_network_fetch_activation_policy_status_v1.csv"
        )

    def analyze(self) -> V134MCAShareNetworkFetchActivationPolicyAuditV1Report:
        materialized = MaterializeAShareNetworkFetchActivationPolicyV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "adapter_policy_registry",
                "component_state": "materialized_policy_bindings",
                "artifact_path": summary["adapter_policy_path"],
                "coverage_note": f"adapter_policy_count = {summary['adapter_policy_count']}",
            },
            {
                "component": "retry_policy_registry",
                "component_state": "materialized_retry_bindings",
                "artifact_path": summary["retry_policy_path"],
                "coverage_note": f"retry_policy_count = {summary['retry_policy_count']}",
            },
            {
                "component": "orchestration_binding_registry",
                "component_state": "materialized_host_bindings",
                "artifact_path": summary["binding_path"],
                "coverage_note": f"host_binding_count = {summary['host_binding_count']}",
            },
            {
                "component": "activation_policy_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"deferred_host_count = {summary['deferred_host_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134mc_a_share_network_fetch_activation_policy_audit_v1",
            "adapter_policy_count": summary["adapter_policy_count"],
            "retry_policy_count": summary["retry_policy_count"],
            "host_binding_count": summary["host_binding_count"],
            "selective_candidate_host_count": summary["selective_candidate_host_count"],
            "ready_now_host_count": summary["ready_now_host_count"],
            "deferred_host_count": summary["deferred_host_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_network_fetch_activation_policy_bound_for_selective_future_activation",
        }
        interpretation = [
            "The network-fetch problem is now narrower: adapters are not missing, and policy/retry/orchestration bindings are explicit.",
            "What remains is activation approval and license review, not structural ambiguity.",
        ]
        return V134MCAShareNetworkFetchActivationPolicyAuditV1Report(
            summary=report_summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MCAShareNetworkFetchActivationPolicyAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mc_a_share_network_fetch_activation_policy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
