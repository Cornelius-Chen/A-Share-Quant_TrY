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
class V134OUAShareSourceInternalManualOperatorChecklistAuditV1Report:
    summary: dict[str, Any]
    checklist_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checklist_rows": self.checklist_rows,
            "interpretation": self.interpretation,
        }


class V134OUAShareSourceInternalManualOperatorChecklistAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.handoff_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_handoff_package_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_operator_checklist_v1.csv"
        )

    def analyze(self) -> V134OUAShareSourceInternalManualOperatorChecklistAuditV1Report:
        handoff_rows = _read_csv(self.handoff_path)
        checklist_rows: list[dict[str, Any]] = []
        for row in handoff_rows:
            if row["review_priority_order"] == "1":
                checklist_stage = "stage_1_primary_host_family_review"
            elif row["review_priority_order"] == "2":
                checklist_stage = "stage_2_independent_host_review_after_primary"
            else:
                checklist_stage = "stage_3_sibling_host_review_after_primary_outcome"

            checklist_rows.append(
                {
                    "decision_unit_id": row["decision_unit_id"],
                    "host": row["host"],
                    "checklist_stage": checklist_stage,
                    "dependency_state": row["dependency_state"],
                    "required_checks": "license_terms|robots_policy|commercial_use_risk|fetch_scope_restriction",
                    "required_decisions": "manual_license_outcome|manual_runtime_outcome",
                    "source_url_count": str(len(row["source_urls"].split(" | "))),
                    "authority_scores": row["authority_scores"],
                    "operator_action_state": (
                        "manual_checklist_completed_pending_runtime_promotion"
                        if row["handoff_state"] == "manual_review_completed_pending_runtime_promotion"
                        else "pending_manual_checklist_execution"
                    ),
                }
            )

        checklist_rows.sort(key=lambda row: (row["checklist_stage"], row["host"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(checklist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(checklist_rows)

        summary = {
            "checklist_row_count": len(checklist_rows),
            "stage_1_count": sum(row["checklist_stage"] == "stage_1_primary_host_family_review" for row in checklist_rows),
            "stage_2_count": sum(
                row["checklist_stage"] == "stage_2_independent_host_review_after_primary" for row in checklist_rows
            ),
            "stage_3_count": sum(
                row["checklist_stage"] == "stage_3_sibling_host_review_after_primary_outcome"
                for row in checklist_rows
            ),
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_source_internal_manual_operator_checklist_materialized",
        }
        interpretation = [
            "The source-side manual lane still has a compact operator checklist with explicit staged ordering instead of only status cards and handoff bundles.",
            "Batch-one checklist stages are now completed and preserved, while runtime promotion remains a later gate.",
        ]
        return V134OUAShareSourceInternalManualOperatorChecklistAuditV1Report(
            summary=summary,
            checklist_rows=checklist_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OUAShareSourceInternalManualOperatorChecklistAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OUAShareSourceInternalManualOperatorChecklistAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ou_a_share_source_internal_manual_operator_checklist_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
