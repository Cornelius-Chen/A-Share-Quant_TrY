from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qk_a_share_runtime_scheduler_activation_precondition_audit_v1 import (
    V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Report:
    summary: dict[str, Any]
    checklist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checklist_rows": self.checklist_rows,
            "interpretation": self.interpretation,
        }


class V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_activation_checklist_v1.csv"
        )

    def analyze(self) -> V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Report:
        precondition_report = V134QKAShareRuntimeSchedulerActivationPreconditionAuditV1Analyzer(
            self.repo_root
        ).analyze()
        preconditions = {row["precondition"]: row for row in precondition_report.rows}

        checklist_rows = [
            {
                "checklist_step": "step_1_confirm_single_runtime_candidate_lane",
                "step_state": "completed",
                "blocking_reason": preconditions["single_runtime_candidate_isolated"]["blocking_reason"],
            },
            {
                "checklist_step": "step_2_confirm_policy_and_retry_bindings",
                "step_state": "completed",
                "blocking_reason": (
                    f"{preconditions['activation_policy_bound']['blocking_reason']}; "
                    f"{preconditions['retry_policy_bound']['blocking_reason']}"
                ),
            },
            {
                "checklist_step": "step_3_activate_scheduler_runtime_binding",
                "step_state": "pending",
                "blocking_reason": preconditions["scheduler_runtime_activation"]["blocking_reason"],
            },
            {
                "checklist_step": "step_4_keep_excluded_adapters_outside_first_runtime_lane",
                "step_state": "completed",
                "blocking_reason": "social and reserved official adapters remain outside the first runtime lane",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(checklist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(checklist_rows)

        summary = {
            "checklist_step_count": len(checklist_rows),
            "completed_step_count": sum(row["step_state"] == "completed" for row in checklist_rows),
            "pending_step_count": sum(row["step_state"] == "pending" for row in checklist_rows),
            "ready_to_open_now": False,
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_runtime_scheduler_activation_checklist_materialized",
        }
        interpretation = [
            "Source-side runtime followthrough now has a compact scheduler activation checklist instead of a vague remaining blocker.",
            "Only one step is still pending: activating the scheduler runtime binding for the html-article lane.",
        ]
        return V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Report(
            summary=summary, checklist_rows=checklist_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qm_a_share_runtime_scheduler_activation_checklist_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
