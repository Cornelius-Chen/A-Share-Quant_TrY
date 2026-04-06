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
class V134OQAShareSourceInternalManualHandoffPackageV1Report:
    summary: dict[str, Any]
    handoff_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "handoff_rows": self.handoff_rows,
            "interpretation": self.interpretation,
        }


class V134OQAShareSourceInternalManualHandoffPackageV1Analyzer:
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
        self.queue_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_operator_queue_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_handoff_package_v1.csv"
        )

    def analyze(self) -> V134OQAShareSourceInternalManualHandoffPackageV1Report:
        workpack_rows = _read_csv(self.workpack_path)
        queue_rows = _read_csv(self.queue_path)
        queue_by_unit = {row["decision_unit_id"]: row for row in queue_rows}

        handoff_rows: list[dict[str, Any]] = []
        for row in workpack_rows:
            queue = queue_by_unit[row["decision_unit_id"]]
            handoff_rows.append(
                {
                    "decision_unit_id": row["decision_unit_id"],
                    "host": row["host"],
                    "review_priority_order": row["review_priority_order"],
                    "dependency_state": queue["dependency_state"],
                    "next_action": queue["next_action"],
                    "source_ids": row["source_ids"],
                    "source_names": row["source_names"],
                    "source_urls": row["source_urls"],
                    "source_tiers": row["source_tiers"],
                    "authority_scores": row["authority_scores"],
                    "pending_field_count": queue["pending_field_count"],
                    "manual_license_outcome": row["manual_license_outcome"],
                    "manual_runtime_outcome": row["manual_runtime_outcome"],
                    "handoff_state": (
                        "manual_review_completed_pending_runtime_promotion"
                        if queue["operator_queue_state"] == "manual_review_completed"
                        else "ready_for_manual_operator_handoff"
                    ),
                }
            )

        handoff_rows.sort(key=lambda row: (int(row["review_priority_order"]), row["host"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(handoff_rows[0].keys()))
            writer.writeheader()
            writer.writerows(handoff_rows)

        summary = {
            "handoff_row_count": len(handoff_rows),
            "manual_review_completed_count": sum(
                row["handoff_state"] == "manual_review_completed_pending_runtime_promotion"
                for row in handoff_rows
            ),
            "primary_completed_count": sum(
                row["dependency_state"] == "primary_review_completed" for row in handoff_rows
            ),
            "independent_completed_count": sum(
                row["dependency_state"] == "independent_review_completed" for row in handoff_rows
            ),
            "sibling_completed_count": sum(
                row["dependency_state"] == "sibling_review_completed" for row in handoff_rows
            ),
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_source_internal_manual_handoff_package_materialized",
        }
        interpretation = [
            "All source-side closure context now fits in one handoff package with review order, dependency state, evidence URLs, and completed manual outcomes.",
            "This package is now a runtime-promotion handoff rather than a manual-review preparation bundle.",
        ]
        return V134OQAShareSourceInternalManualHandoffPackageV1Report(
            summary=summary,
            handoff_rows=handoff_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OQAShareSourceInternalManualHandoffPackageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OQAShareSourceInternalManualHandoffPackageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oq_a_share_source_internal_manual_handoff_package_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
