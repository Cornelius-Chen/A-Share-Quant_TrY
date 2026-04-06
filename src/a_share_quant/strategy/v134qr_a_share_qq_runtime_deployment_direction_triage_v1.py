from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qq_a_share_runtime_scheduler_deployment_candidate_view_audit_v1 import (
    V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QRAShareQQRuntimeDeploymentDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QRAShareQQRuntimeDeploymentDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QRAShareQQRuntimeDeploymentDirectionTriageV1Report:
        report = V134QQAShareRuntimeSchedulerDeploymentCandidateViewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "candidate_row_count": report.summary["candidate_row_count"],
            "promotable_now_count": report.summary["promotable_now_count"],
            "authoritative_status": "runtime_deployment_followthrough_should_continue_from_single_candidate_view_only",
        }
        triage_rows = [
            {
                "component": "deployment_candidate_view",
                "direction": "use_the_single_row_candidate_view_as_the_only_runtime_deployment_followthrough_surface",
            },
            {
                "component": "remaining_gate",
                "direction": "retain_scheduler_and_governance_opening_as_the_next_real movement",
            },
        ]
        interpretation = [
            "The source-side runtime path is now compact enough to follow through from one candidate deployment view.",
            "No additional adapter expansion is justified before scheduler and governance movement.",
        ]
        return V134QRAShareQQRuntimeDeploymentDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QRAShareQQRuntimeDeploymentDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QRAShareQQRuntimeDeploymentDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qr_a_share_qq_runtime_deployment_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
