from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qm_a_share_runtime_scheduler_activation_checklist_audit_v1 import (
    V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Report:
        report = V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "completed_step_count": report.summary["completed_step_count"],
            "pending_step_count": report.summary["pending_step_count"],
            "authoritative_status": "source_runtime_followthrough_should_continue_only_through_scheduler_activation",
        }
        triage_rows = [
            {
                "component": "completed_prework",
                "direction": "retain_completed candidate-selection and policy-binding steps without reopening them",
            },
            {
                "component": "remaining_step",
                "direction": "treat scheduler runtime binding as the only remaining source-side followthrough step",
            },
            {
                "component": "excluded_adapters",
                "direction": "keep non-html adapters outside this lane during scheduler followthrough",
            },
        ]
        interpretation = [
            "Source-side runtime followthrough is now a checklist problem with one remaining pending step, not a multi-branch activation problem.",
            "This keeps the lane narrow and avoids reopening excluded adapters.",
        ]
        return V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qn_a_share_qm_runtime_scheduler_checklist_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
