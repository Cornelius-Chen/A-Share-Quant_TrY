from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mc_a_share_network_fetch_activation_policy_audit_v1 import (
    V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MDAShareMCNetworkFetchActivationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MDAShareMCNetworkFetchActivationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MDAShareMCNetworkFetchActivationDirectionTriageV1Report:
        report = V134MCAShareNetworkFetchActivationPolicyAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "adapter_policy_count": report.summary["adapter_policy_count"],
            "host_binding_count": report.summary["host_binding_count"],
            "authoritative_status": "network_fetch_activation_policy_complete_enough_to_freeze_until_selective_activation_shift",
        }
        triage_rows = [
            {
                "component": "network_fetch_activation_policy",
                "direction": "freeze_policy_retry_and_orchestration_bindings_without_auto_activation",
            },
            {
                "component": "next_frontier",
                "direction": "selectively_activate_licensed_T2_T3_hosts_after_scheduler_runtime_and_manual_allowlist_review",
            },
        ]
        interpretation = [
            "The remaining network-fetch blocker is no longer missing policy; it is selective activation approval.",
            "That means live_like and execution can continue to stay blocked for governance reasons without structural uncertainty in fetch policy.",
        ]
        return V134MDAShareMCNetworkFetchActivationDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MDAShareMCNetworkFetchActivationDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MDAShareMCNetworkFetchActivationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134md_a_share_mc_network_fetch_activation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
