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
class V134OOAShareSourceInternalManualLatestStatusCardV1Report:
    summary: dict[str, Any]
    status_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "status_rows": self.status_rows,
            "interpretation": self.interpretation,
        }


class V134OOAShareSourceInternalManualLatestStatusCardV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.queue_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_source_internal_manual_operator_queue_v1.csv"
        )
        self.precondition_path = (
            repo_root
            / "data"
            / "training"
            / "a_share_allowlist_promotion_precondition_surface_status_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "a_share_source_internal_manual_latest_status_card_v1.csv"
        )

    def analyze(self) -> V134OOAShareSourceInternalManualLatestStatusCardV1Report:
        queue_rows = _read_csv(self.queue_path)
        precondition_rows = _read_csv(self.precondition_path)
        unsatisfied = sum(row["precondition_state"] == "unsatisfied" for row in precondition_rows)
        manual_review_completed_count = sum(
            row["operator_queue_state"] == "manual_review_completed" for row in queue_rows
        )

        status_rows = [
            {
                "component": "source_internal_manual_lane",
                "component_state": "manual_review_completed_pending_runtime_promotion",
                "metric": "queue_row_count",
                "value": str(len(queue_rows)),
            },
            {
                "component": "manual_review_completed",
                "component_state": "all_batch_one_hosts_manually_approved",
                "metric": "manual_review_completed_count",
                "value": str(manual_review_completed_count),
            },
            {
                "component": "primary_host_family_completed",
                "component_state": "primary_manual_review_completed",
                "metric": "primary_completed_count",
                "value": str(sum(row["dependency_state"] == "primary_review_completed" for row in queue_rows)),
            },
            {
                "component": "independent_hosts_completed",
                "component_state": "independent_manual_reviews_completed",
                "metric": "independent_completed_count",
                "value": str(sum(row["dependency_state"] == "independent_review_completed" for row in queue_rows)),
            },
            {
                "component": "sibling_host_completed",
                "component_state": "sibling_manual_review_completed",
                "metric": "sibling_completed_count",
                "value": str(sum(row["dependency_state"] == "sibling_review_completed" for row in queue_rows)),
            },
            {
                "component": "promotion_preconditions",
                "component_state": "runtime_only_unsatisfied_after_manual_closure",
                "metric": "unsatisfied_count",
                "value": str(unsatisfied),
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "queue_row_count": len(queue_rows),
            "manual_review_completed_count": manual_review_completed_count,
            "primary_completed_count": sum(
                row["dependency_state"] == "primary_review_completed" for row in queue_rows
            ),
            "independent_completed_count": sum(
                row["dependency_state"] == "independent_review_completed" for row in queue_rows
            ),
            "sibling_completed_count": sum(
                row["dependency_state"] == "sibling_review_completed" for row in queue_rows
            ),
            "unsatisfied_precondition_count": unsatisfied,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_status": "source_internal_manual_now_at_manual_approval_complete_pending_runtime_promotion_stopline",
        }
        interpretation = [
            "The only internally actionable source lane is no longer waiting on manual filling; manual closure is complete for batch-one.",
            "What remains on the source side is runtime promotion gating, not another round of operator review scaffolding.",
        ]
        return V134OOAShareSourceInternalManualLatestStatusCardV1Report(
            summary=summary,
            status_rows=status_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OOAShareSourceInternalManualLatestStatusCardV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OOAShareSourceInternalManualLatestStatusCardV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oo_a_share_source_internal_manual_latest_status_card_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
