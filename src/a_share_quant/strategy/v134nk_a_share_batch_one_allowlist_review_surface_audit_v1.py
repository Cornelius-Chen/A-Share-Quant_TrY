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
class V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Report:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


class V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.priority_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_allowlist_priority_registry_v1.csv"
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
        self.binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_orchestration_binding_v1.csv"
        )
        self.review_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_review_surface_v1.csv"
        )
        self.residual_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_batch_one_allowlist_review_residual_v1.csv"
        )
        self.status_output = (
            repo_root / "data" / "training" / "a_share_batch_one_allowlist_review_surface_status_v1.csv"
        )

    def analyze(self) -> V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Report:
        priority_rows = _read_csv(self.priority_path)
        source_rows = _read_csv(self.source_master_path)
        quality_rows = _read_csv(self.quality_path)
        binding_rows = _read_csv(self.binding_path)

        source_by_id = {row["source_id"]: row for row in source_rows}
        quality_by_id = {row["source_id"]: row for row in quality_rows}
        binding_by_id = {row["source_id"]: row for row in binding_rows}

        batch_one_rows = [row for row in priority_rows if row["queue_priority"] == "batch_one_manual_license_review"]

        host_groups: dict[str, list[dict[str, str]]] = {}
        for row in batch_one_rows:
            host_groups.setdefault(row["host"], []).append(row)

        review_rows: list[dict[str, Any]] = []
        for host, host_rows in sorted(host_groups.items()):
            source_ids = [row["source_id"] for row in host_rows]
            source_names = [source_by_id[source_id]["source_name"] for source_id in source_ids]
            authority_scores = [int(quality_by_id[source_id]["authority_score"]) for source_id in source_ids]
            adapter_ids = sorted({binding_by_id[source_id]["adapter_id"] for source_id in source_ids})

            if host == "finance.sina.com.cn":
                review_mode = "primary_batch_one_host_family_review"
            elif host == "stock.finance.sina.com.cn":
                review_mode = "sibling_host_review_after_primary_sina_family"
            else:
                review_mode = "independent_batch_one_host_review"

            review_rows.append(
                {
                    "review_unit_id": f"allowlist_review_{host.replace('.', '_')}",
                    "host": host,
                    "source_count": len(source_ids),
                    "source_ids": "|".join(source_ids),
                    "source_names": " | ".join(source_names),
                    "max_authority_score": max(authority_scores),
                    "adapter_ids": "|".join(adapter_ids),
                    "review_mode": review_mode,
                    "review_state": "awaiting_manual_license_review",
                    "promotion_state": "not_promoted",
                }
            )

        residual_rows = [
            {
                "residual_class": "batch_one_review_units_materialized_but_no_allowlist_decision",
                "residual_count": len(review_rows),
            },
            {
                "residual_class": "host_family_dependency_present",
                "residual_count": sum("sibling_host_review" in row["review_mode"] for row in review_rows),
            },
        ]

        self.review_output.parent.mkdir(parents=True, exist_ok=True)
        with self.review_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(review_rows[0].keys()))
            writer.writeheader()
            writer.writerows(review_rows)

        with self.residual_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(residual_rows[0].keys()))
            writer.writeheader()
            writer.writerows(residual_rows)

        status_rows = [
            {
                "component": "batch_one_allowlist_review_surface",
                "component_state": "materialized_host_level_review_units",
                "artifact_path": str(self.review_output.relative_to(self.repo_root)),
                "coverage_note": f"host_review_unit_count = {len(review_rows)}",
            },
            {
                "component": "batch_one_allowlist_review_residual",
                "component_state": "materialized_named_residuals",
                "artifact_path": str(self.residual_output.relative_to(self.repo_root)),
                "coverage_note": "allowlist decisions remain manual and closed",
            },
        ]

        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "batch_one_source_count": len(batch_one_rows),
            "host_review_unit_count": len(review_rows),
            "promotable_now_count": 0,
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_batch_one_allowlist_review_surface_materialized_but_not_promoted",
        }
        interpretation = [
            "Batch-one allowlist work is now shaped as host-level review units rather than six scattered source rows.",
            "This still does not approve any host; it only creates the first disciplined manual review package.",
            "Sina finance is treated as the primary host family, with stock.finance.sina.com.cn retained as a sibling host that should be reviewed after the primary family decision.",
        ]
        return V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Report(
            summary=summary, review_rows=review_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nk_a_share_batch_one_allowlist_review_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
