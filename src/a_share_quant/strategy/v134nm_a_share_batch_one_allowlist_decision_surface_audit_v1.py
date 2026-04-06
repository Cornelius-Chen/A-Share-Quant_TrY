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
class V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Report:
    summary: dict[str, Any]
    decision_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "decision_rows": self.decision_rows,
            "interpretation": self.interpretation,
        }


class V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.review_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_review_surface_v1.csv"
        )
        self.decision_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_decision_surface_v1.csv"
        )
        self.residual_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_decision_residual_v1.csv"
        )
        self.status_output = (
            repo_root / "data" / "training" / "a_share_batch_one_allowlist_decision_surface_status_v1.csv"
        )

    def analyze(self) -> V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Report:
        review_rows = _read_csv(self.review_surface_path)
        existing_rows = _read_csv_if_exists(self.decision_output)
        existing_by_unit = {row["decision_unit_id"]: row for row in existing_rows}

        priority_order = {
            "primary_batch_one_host_family_review": 1,
            "independent_batch_one_host_review": 2,
            "sibling_host_review_after_primary_sina_family": 3,
        }

        decision_rows: list[dict[str, Any]] = []
        for row in review_rows:
            review_mode = row["review_mode"]
            existing = existing_by_unit.get(row["review_unit_id"], {})
            if review_mode == "primary_batch_one_host_family_review":
                recommended_gate = "review_first"
            elif review_mode == "independent_batch_one_host_review":
                recommended_gate = "review_after_primary_host_family"
            else:
                recommended_gate = "review_after_primary_host_family_outcome"

            decision_rows.append(
                {
                    "decision_unit_id": row["review_unit_id"],
                    "host": row["host"],
                    "review_mode": review_mode,
                    "review_priority_order": priority_order[review_mode],
                    "recommended_review_gate": recommended_gate,
                    "manual_license_decision": existing.get("manual_license_decision", "pending"),
                    "manual_runtime_eligibility": existing.get("manual_runtime_eligibility", "pending"),
                    "manual_notes": existing.get("manual_notes", ""),
                    "promotion_state": existing.get("promotion_state", "closed_pending_manual_decision"),
                }
            )

        decision_rows.sort(key=lambda row: (row["review_priority_order"], row["host"]))
        pending_manual_decision_count = sum(
            row["manual_license_decision"] == "pending" or row["manual_runtime_eligibility"] == "pending"
            for row in decision_rows
        )
        manually_approved_count = sum(
            row["manual_license_decision"] == "allow" and row["manual_runtime_eligibility"] == "allow"
            for row in decision_rows
        )

        residual_rows = [
            {
                "residual_class": "manual_decision_pending",
                "residual_count": pending_manual_decision_count,
            },
            {
                "residual_class": "sibling_host_dependency_pending",
                "residual_count": sum(
                    row["review_mode"] == "sibling_host_review_after_primary_sina_family" for row in decision_rows
                ),
            },
        ]

        self.decision_output.parent.mkdir(parents=True, exist_ok=True)
        with self.decision_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(decision_rows[0].keys()))
            writer.writeheader()
            writer.writerows(decision_rows)

        with self.residual_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(residual_rows[0].keys()))
            writer.writeheader()
            writer.writerows(residual_rows)

        status_rows = [
            {
                "component": "batch_one_allowlist_decision_surface",
                "component_state": "materialized_manual_decision_surface",
                "artifact_path": str(self.decision_output.relative_to(self.repo_root)),
                "coverage_note": f"decision_unit_count = {len(decision_rows)}",
            },
            {
                "component": "batch_one_allowlist_decision_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": str(self.residual_output.relative_to(self.repo_root)),
                "coverage_note": (
                    f"pending_manual_decision_count = {pending_manual_decision_count}; "
                    f"manually_approved_count = {manually_approved_count}"
                ),
            },
        ]

        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "decision_unit_count": len(decision_rows),
            "pending_manual_decision_count": pending_manual_decision_count,
            "manually_approved_count": manually_approved_count,
            "promotable_now_count": 0,
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_batch_one_allowlist_decision_surface_preserved_after_manual_approval",
        }
        interpretation = [
            "Batch-one allowlist keeps an explicit decision surface instead of an informal review package only.",
            "Existing manual outcomes are preserved across reruns rather than being reset to pending.",
            "Manual approval still does not mean runtime promotion is open; it only closes the host-level review stage.",
        ]
        return V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Report(
            summary=summary, decision_rows=decision_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NMAShareBatchOneAllowlistDecisionSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nm_a_share_batch_one_allowlist_decision_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
