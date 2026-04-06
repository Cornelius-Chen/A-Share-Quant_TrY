from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_csv_if_exists(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return _read_csv(path)


@dataclass(slots=True)
class V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Report:
    summary: dict[str, Any]
    record_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "record_rows": self.record_rows,
            "interpretation": self.interpretation,
        }


class V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.decision_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_decision_surface_v1.csv"
        )
        self.record_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_manual_review_record_surface_v1.csv"
        )
        self.residual_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_manual_review_record_residual_v1.csv"
        )
        self.status_output = (
            repo_root / "data" / "training" / "a_share_batch_one_manual_review_record_surface_status_v1.csv"
        )

    def analyze(self) -> V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Report:
        decision_rows = _read_csv(self.decision_surface_path)
        existing_rows = _read_csv_if_exists(self.record_output)
        existing_by_unit = {row["decision_unit_id"]: row for row in existing_rows}

        record_rows: list[dict[str, Any]] = []
        for row in decision_rows:
            existing = existing_by_unit.get(row["decision_unit_id"], {})
            record_rows.append(
                {
                    "decision_unit_id": row["decision_unit_id"],
                    "host": row["host"],
                    "review_priority_order": row["review_priority_order"],
                    "review_started_ts": existing.get("review_started_ts", ""),
                    "review_completed_ts": existing.get("review_completed_ts", ""),
                    "review_operator": existing.get("review_operator", ""),
                    "license_terms_checked": existing.get("license_terms_checked", "pending"),
                    "robots_policy_checked": existing.get("robots_policy_checked", "pending"),
                    "commercial_use_risk_checked": existing.get("commercial_use_risk_checked", "pending"),
                    "fetch_scope_restriction_checked": existing.get("fetch_scope_restriction_checked", "pending"),
                    "manual_license_outcome": existing.get("manual_license_outcome", row["manual_license_decision"]),
                    "manual_runtime_outcome": existing.get(
                        "manual_runtime_outcome", row["manual_runtime_eligibility"]
                    ),
                    "review_notes": existing.get("review_notes", ""),
                    "record_state": existing.get("record_state", "awaiting_manual_record_fill"),
                }
            )
        pending_record_count = sum(row["record_state"] == "awaiting_manual_record_fill" for row in record_rows)
        completed_record_count = sum(row["record_state"] == "manual_review_completed" for row in record_rows)

        residual_rows = [
            {
                "residual_class": "manual_review_records_unfilled",
                "residual_count": pending_record_count,
            }
        ]

        self.record_output.parent.mkdir(parents=True, exist_ok=True)
        with self.record_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(record_rows[0].keys()))
            writer.writeheader()
            writer.writerows(record_rows)

        with self.residual_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(residual_rows[0].keys()))
            writer.writeheader()
            writer.writerows(residual_rows)

        status_rows = [
            {
                "component": "batch_one_manual_review_record_surface",
                "component_state": "materialized_manual_review_record_surface",
                "artifact_path": str(self.record_output.relative_to(self.repo_root)),
                "coverage_note": f"record_row_count = {len(record_rows)}",
            },
            {
                "component": "batch_one_manual_review_record_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": str(self.residual_output.relative_to(self.repo_root)),
                "coverage_note": (
                    f"pending_record_count = {pending_record_count}; "
                    f"completed_record_count = {completed_record_count}"
                ),
            },
        ]

        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "record_row_count": len(record_rows),
            "pending_record_count": pending_record_count,
            "completed_record_count": completed_record_count,
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_batch_one_manual_review_record_surface_preserved_after_manual_completion",
        }
        interpretation = [
            "Batch-one manual review keeps a fixed record format instead of relying on free-form notes.",
            "Existing operator-filled records are preserved across reruns instead of being overwritten back to pending.",
        ]
        return V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Report(
            summary=summary, record_rows=record_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ns_a_share_batch_one_manual_review_record_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
