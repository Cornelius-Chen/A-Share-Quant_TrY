from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ma_a_share_network_fetch_adapter_foundation_audit_v1 import (
    V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MBAShareMANetworkFetchAdapterDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134MBAShareMANetworkFetchAdapterDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MBAShareMANetworkFetchAdapterDirectionTriageV1Report:
        audit = V134MAAShareNetworkFetchAdapterFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "network_fetch_adapter",
                "direction": "freeze_as_contract_and_stub_binding_surface",
            },
            {
                "component": "next_frontier",
                "direction": "bind_selected_adapters_to_orchestration_license_review_and_retry_policy_before_activation",
            },
        ]
        summary = {
            "adapter_count": audit.summary["adapter_count"],
            "host_binding_count": audit.summary["host_binding_count"],
            "authoritative_status": "network_fetch_adapter_foundation_complete_enough_to_freeze_as_scaffold",
        }
        interpretation = [
            "The network-fetch problem is now scoped to activation policy rather than missing structure.",
            "Actual fetch activation should happen selectively per source class after scheduler, licensing, and retry policy are attached.",
        ]
        return V134MBAShareMANetworkFetchAdapterDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MBAShareMANetworkFetchAdapterDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MBAShareMANetworkFetchAdapterDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mb_a_share_ma_network_fetch_adapter_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
