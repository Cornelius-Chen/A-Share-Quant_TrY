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
class V134OMAShareSourceInternalManualOperatorQueueAuditV1Report:
    summary: dict[str, Any]
    queue_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "queue_rows": self.queue_rows, "interpretation": self.interpretation}


class V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.workpack_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_manual_review_workpack_v1.csv"
        )
        self.decision_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_decision_surface_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_operator_queue_v1.csv"
        )
        self.status_output = (
            repo_root / "data" / "training" / "a_share_source_internal_manual_operator_queue_status_v1.csv"
        )

    def analyze(self) -> V134OMAShareSourceInternalManualOperatorQueueAuditV1Report:
        workpack_rows = _read_csv(self.workpack_path)
        decision_rows = _read_csv(self.decision_surface_path)
        decision_by_unit = {row["decision_unit_id"]: row for row in decision_rows}

        queue_rows: list[dict[str, Any]] = []
        for row in workpack_rows:
            unit_id = row["decision_unit_id"]
            decision = decision_by_unit[unit_id]
            priority = int(row["review_priority_order"])
            pending_field_count = sum(
                row[field] == "pending"
                for field in (
                    "license_terms_checked",
                    "robots_policy_checked",
                    "commercial_use_risk_checked",
                    "fetch_scope_restriction_checked",
                    "manual_license_outcome",
                    "manual_runtime_outcome",
                )
            )
            approved = (
                pending_field_count == 0
                and decision["manual_license_decision"] == "allow"
                and decision["manual_runtime_eligibility"] == "allow"
            )
            if approved and priority == 1:
                dependency_state = "primary_review_completed"
                next_action = "await_runtime_promotion_binding"
            elif approved and priority == 2:
                dependency_state = "independent_review_completed"
                next_action = "await_runtime_promotion_binding"
            elif approved and priority == 3:
                dependency_state = "sibling_review_completed"
                next_action = "await_runtime_promotion_binding"
            elif priority == 1:
                dependency_state = "ready_primary_review"
                next_action = "fill_primary_host_family_manual_record"
            elif priority == 2:
                dependency_state = "ready_but_should_follow_primary"
                next_action = "prepare_independent_host_review_after_primary"
            else:
                dependency_state = "blocked_by_primary_host_family_dependency"
                next_action = "wait_for_primary_host_family_outcome_before_review"
            queue_rows.append(
                {
                    "decision_unit_id": unit_id,
                    "host": row["host"],
                    "review_priority_order": priority,
                    "dependency_state": dependency_state,
                    "next_action": next_action,
                    "pending_field_count": pending_field_count,
                    "manual_license_decision": decision["manual_license_decision"],
                    "manual_runtime_eligibility": decision["manual_runtime_eligibility"],
                    "operator_queue_state": (
                        "manual_review_completed" if approved else "awaiting_manual_operator"
                    ),
                }
            )

        queue_rows.sort(key=lambda row: (row["review_priority_order"], row["host"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(queue_rows[0].keys()))
            writer.writeheader()
            writer.writerows(queue_rows)

        status_rows = [
            {
                "component": "source_internal_manual_operator_queue",
                "component_state": "materialized_priority_queue",
                "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
                "coverage_note": f"queue_row_count = {len(queue_rows)}",
            }
        ]
        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "queue_row_count": len(queue_rows),
            "ready_primary_review_count": sum(row["dependency_state"] == "ready_primary_review" for row in queue_rows),
            "ready_following_primary_count": sum(
                row["dependency_state"] == "ready_but_should_follow_primary" for row in queue_rows
            ),
            "dependency_blocked_count": sum(
                row["dependency_state"] == "blocked_by_primary_host_family_dependency" for row in queue_rows
            ),
            "manual_review_completed_count": sum(
                row["operator_queue_state"] == "manual_review_completed" for row in queue_rows
            ),
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_source_internal_manual_operator_queue_materialized",
        }
        interpretation = [
            "The source-side manual lane still has an explicit operator queue instead of just a passive workpack.",
            "After manual approval, all four batch-one hosts move from review-pending states into runtime-promotion waiting states.",
        ]
        return V134OMAShareSourceInternalManualOperatorQueueAuditV1Report(
            summary=summary, queue_rows=queue_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OMAShareSourceInternalManualOperatorQueueAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OMAShareSourceInternalManualOperatorQueueAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134om_a_share_source_internal_manual_operator_queue_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
