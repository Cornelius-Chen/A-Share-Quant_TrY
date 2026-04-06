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
class V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.record_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_manual_review_record_surface_v1.csv"
        )
        self.runtime_dependency_path = (
            repo_root / "data" / "training" / "a_share_runtime_candidate_dependency_status_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_allowlist_promotion_precondition_surface_status_v1.csv"
        )

    def analyze(self) -> V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Report:
        record_rows = _read_csv(self.record_surface_path)
        runtime_rows = _read_csv(self.runtime_dependency_path)

        pending_record_count = sum(row["record_state"] != "manual_review_completed" for row in record_rows)
        pending_license_count = sum(row["manual_license_outcome"] == "pending" for row in record_rows)
        pending_runtime_outcome_count = sum(row["manual_runtime_outcome"] == "pending" for row in record_rows)
        runtime_blocked_count = sum(row["promotable_now"] == "False" for row in runtime_rows)

        rows = [
            {
                "precondition": "manual_review_records_filled",
                "precondition_state": "satisfied" if pending_record_count == 0 else "unsatisfied",
                "supporting_count": pending_record_count,
                "blocking_reason": (
                    "batch-one manual review records are complete"
                    if pending_record_count == 0
                    else "batch-one manual review records remain unfilled"
                ),
            },
            {
                "precondition": "manual_license_outcomes_non_pending",
                "precondition_state": "satisfied" if pending_license_count == 0 else "unsatisfied",
                "supporting_count": pending_license_count,
                "blocking_reason": (
                    "all manual license outcomes are non-pending"
                    if pending_license_count == 0
                    else "manual license outcomes remain pending"
                ),
            },
            {
                "precondition": "manual_runtime_outcomes_non_pending",
                "precondition_state": "satisfied" if pending_runtime_outcome_count == 0 else "unsatisfied",
                "supporting_count": pending_runtime_outcome_count,
                "blocking_reason": (
                    "all manual runtime outcomes are non-pending"
                    if pending_runtime_outcome_count == 0
                    else "manual runtime outcomes remain pending"
                ),
            },
            {
                "precondition": "runtime_candidate_promotable",
                "precondition_state": "unsatisfied",
                "supporting_count": runtime_blocked_count,
                "blocking_reason": "runtime candidate dependency surface still reports zero promotable adapters",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "precondition_count": len(rows),
            "unsatisfied_count": sum(row["precondition_state"] == "unsatisfied" for row in rows),
            "promotable_now_count": 0,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_allowlist_promotion_preconditions_reaudited_after_manual_approval",
        }
        interpretation = [
            "Allowlist promotion preconditions are now explicit instead of being spread across multiple registries.",
            "Manual review preconditions are now satisfied; the remaining unsatisfied precondition is runtime promotability.",
        ]
        return V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
