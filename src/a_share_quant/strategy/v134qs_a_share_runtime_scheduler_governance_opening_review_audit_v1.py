from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Report:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


class V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.deployment_candidate_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_deployment_candidate_view_v1.csv"
        )
        self.scheduler_checklist_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_activation_checklist_v1.csv"
        )
        self.governance_gate_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "governance_registry"
            / "a_share_promotion_gate_registry_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_scheduler_governance_opening_review_surface_v1.csv"
        )

    def analyze(self) -> V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Report:
        deployment_rows = _read_csv(self.deployment_candidate_path)
        checklist_rows = _read_csv(self.scheduler_checklist_path)
        gate_rows = _read_csv(self.governance_gate_path)
        checklist_by_step = {row["checklist_step"]: row for row in checklist_rows}
        gates_by_id = {row["gate_id"]: row for row in gate_rows}

        review_rows: list[dict[str, Any]] = []
        for row in deployment_rows:
            scheduler_step = checklist_by_step["step_3_activate_scheduler_runtime_binding"]
            live_like_gate = gates_by_id["live_like_opening_gate"]
            execution_gate = gates_by_id["execution_authority_gate"]
            review_rows.append(
                {
                    "adapter_id": row["adapter_id"],
                    "deployment_candidate_state": row["deployment_candidate_state"],
                    "scheduler_step_state": scheduler_step["step_state"],
                    "live_like_gate_state": live_like_gate["gate_state"],
                    "execution_gate_state": execution_gate["gate_state"],
                    "opening_review_state": "single_candidate_pending_scheduler_and_governance_manual_opening",
                    "ready_to_open_now": "False",
                    "silent_opening_allowed": "False",
                    "next_controlled_movement": "activate_scheduler_runtime_binding_then_reaudit_live_like_governance_opening",
                    "blocking_reason": (
                        f"{scheduler_step['blocking_reason']}; "
                        f"{live_like_gate['gate_reason']}; "
                        f"{execution_gate['gate_reason']}"
                    ),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(review_rows[0].keys()))
            writer.writeheader()
            writer.writerows(review_rows)

        summary = {
            "review_row_count": len(review_rows),
            "scheduler_pending_count": sum(row["scheduler_step_state"] == "pending" for row in review_rows),
            "governance_closed_count": sum(
                row["live_like_gate_state"] == "closed" and row["execution_gate_state"] == "closed"
                for row in review_rows
            ),
            "ready_to_open_now_count": sum(row["ready_to_open_now"] == "True" for row in review_rows),
            "silent_opening_allowed_count": sum(row["silent_opening_allowed"] == "True" for row in review_rows),
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_runtime_scheduler_governance_opening_review_surface_materialized",
        }
        interpretation = [
            "Source-side opening work is now reduced to a single combined scheduler-plus-governance review surface for the html-article deployment candidate.",
            "The candidate is not silently promotable: scheduler binding remains pending and both live_like and execution governance gates stay closed.",
        ]
        return V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Report(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
