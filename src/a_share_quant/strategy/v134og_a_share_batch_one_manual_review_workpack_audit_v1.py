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
class V134OGAShareBatchOneManualReviewWorkpackAuditV1Report:
    summary: dict[str, Any]
    workpack_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "workpack_rows": self.workpack_rows,
            "interpretation": self.interpretation,
        }


class V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer:
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
        self.record_surface_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_manual_review_record_surface_v1.csv"
        )
        self.source_master_path = (
            repo_root / "data" / "reference" / "info_center" / "source_master" / "a_share_source_master_v1.csv"
        )
        self.quality_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "quality_registry"
            / "a_share_source_quality_registry_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_manual_review_workpack_v1.csv"
        )
        self.status_output = (
            repo_root / "data" / "training" / "a_share_batch_one_manual_review_workpack_status_v1.csv"
        )

    def analyze(self) -> V134OGAShareBatchOneManualReviewWorkpackAuditV1Report:
        review_rows = _read_csv(self.review_surface_path)
        record_rows = _read_csv(self.record_surface_path)
        source_rows = _read_csv(self.source_master_path)
        quality_rows = _read_csv(self.quality_path)

        record_by_unit = {row["decision_unit_id"]: row for row in record_rows}
        source_by_id = {row["source_id"]: row for row in source_rows}
        quality_by_id = {row["source_id"]: row for row in quality_rows}

        workpack_rows: list[dict[str, Any]] = []
        for review_row in review_rows:
            decision_unit_id = review_row["review_unit_id"]
            record_row = record_by_unit[decision_unit_id]
            source_ids = review_row["source_ids"].split("|")
            source_names = []
            source_urls = []
            source_tiers = []
            authority_scores = []
            for source_id in source_ids:
                source = source_by_id[source_id]
                quality = quality_by_id[source_id]
                source_names.append(source["source_name"])
                source_urls.append(source["source_url"])
                source_tiers.append(quality["source_tier"])
                authority_scores.append(quality["authority_score"])

            workpack_rows.append(
                {
                    "decision_unit_id": decision_unit_id,
                    "host": review_row["host"],
                    "review_priority_order": record_row["review_priority_order"],
                    "source_ids": review_row["source_ids"],
                    "source_names": " | ".join(source_names),
                    "source_urls": " | ".join(source_urls),
                    "source_tiers": "|".join(source_tiers),
                    "authority_scores": "|".join(authority_scores),
                    "license_terms_checked": record_row["license_terms_checked"],
                    "robots_policy_checked": record_row["robots_policy_checked"],
                    "commercial_use_risk_checked": record_row["commercial_use_risk_checked"],
                    "fetch_scope_restriction_checked": record_row["fetch_scope_restriction_checked"],
                    "manual_license_outcome": record_row["manual_license_outcome"],
                    "manual_runtime_outcome": record_row["manual_runtime_outcome"],
                    "workpack_state": "ready_for_manual_fill",
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(workpack_rows[0].keys()))
            writer.writeheader()
            writer.writerows(workpack_rows)

        status_rows = [
            {
                "component": "batch_one_manual_review_workpack",
                "component_state": "materialized_review_workpack",
                "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
                "coverage_note": f"workpack_row_count = {len(workpack_rows)}",
            }
        ]

        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "workpack_row_count": len(workpack_rows),
            "host_count": len(workpack_rows),
            "pending_manual_field_row_count": sum(
                row["manual_license_outcome"] == "pending" and row["manual_runtime_outcome"] == "pending"
                for row in workpack_rows
            ),
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_batch_one_manual_review_workpack_materialized",
        }
        interpretation = [
            "Batch-one manual closure now has a single workpack surface that combines host unit, source evidence, URLs, authority, and pending review fields.",
            "This reduces future review friction because the manual operator no longer has to traverse multiple registries to fill the next batch-one records.",
        ]
        return V134OGAShareBatchOneManualReviewWorkpackAuditV1Report(
            summary=summary, workpack_rows=workpack_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OGAShareBatchOneManualReviewWorkpackAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134og_a_share_batch_one_manual_review_workpack_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
