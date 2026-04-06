from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134kx_a_share_serving_foundation_audit_v1 import (
    V134KXAShareServingFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134KYAShareKXServingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134KYAShareKXServingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134KYAShareKXServingDirectionTriageV1Report:
        audit = V134KXAShareServingFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "serving_component": "research_views",
                "direction": "freeze_as_current_default_research_surface",
            },
            {
                "serving_component": "shadow_views",
                "direction": "retain_as_read_only_shadow_serving_surface",
            },
            {
                "serving_component": "live_like_views",
                "direction": "keep_deferred_until_governance_and_automation_bindings_exist",
            },
            {
                "serving_component": "next_frontier",
                "direction": "shift_into_governance_workstream_to_add_registry_control_heartbeat_and_promotion_gates",
            },
        ]
        summary = {
            "research_view_count": audit.summary["research_view_count"],
            "shadow_view_count": audit.summary["shadow_view_count"],
            "live_like_view_count": audit.summary["live_like_view_count"],
            "authoritative_status": "serving_workstream_complete_enough_to_freeze_and_shift_into_governance",
        }
        interpretation = [
            "Serving is now sufficient for research and read-only shadow consumption.",
            "The next bottleneck is governance, because promotion control and operational registry discipline must exist before live-like serving can be opened.",
        ]
        return V134KYAShareKXServingDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134KYAShareKXServingDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KYAShareKXServingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ky_a_share_kx_serving_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
