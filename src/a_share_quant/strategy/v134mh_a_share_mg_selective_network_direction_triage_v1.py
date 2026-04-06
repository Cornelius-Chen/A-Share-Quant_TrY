from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134mg_a_share_selective_network_activation_gate_audit_v1 import (
    V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MHAShareMGSelectiveNetworkDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MHAShareMGSelectiveNetworkDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MHAShareMGSelectiveNetworkDirectionTriageV1Report:
        report = V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "selective_candidate_host_count": report.summary["selective_candidate_host_count"],
            "authoritative_status": "selective_network_activation_kept_closed_until_license_and_scheduler_gates_open",
        }
        triage_rows = [
            {
                "component": "license_review_gate",
                "direction": "resolve_host_allowlist_before_any_selective_network_activation",
            },
            {
                "component": "runtime_scheduler_gate",
                "direction": "bind_policy_bound_adapters_to_runtime_scheduler_before_activation",
            },
        ]
        interpretation = [
            "The next source-side work is explicit and bounded: allowlist review, then scheduler runtime binding.",
            "No live activation should happen before both gates move from closed to explicitly open.",
        ]
        return V134MHAShareMGSelectiveNetworkDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MHAShareMGSelectiveNetworkDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MHAShareMGSelectiveNetworkDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mh_a_share_mg_selective_network_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
