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
class V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.runtime_dependency_path = (
            repo_root / "data" / "training" / "a_share_runtime_candidate_dependency_status_v1.csv"
        )
        self.runtime_priority_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_runtime_priority_registry_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_runtime_promotion_candidate_surface_v1.csv"
        )
        self.status_output = (
            repo_root / "data" / "training" / "a_share_runtime_promotion_candidate_surface_status_v1.csv"
        )

    def analyze(self) -> V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Report:
        dependency_rows = _read_csv(self.runtime_dependency_path)
        priority_rows = _read_csv(self.runtime_priority_path)
        priority_by_adapter = {row["adapter_id"]: row for row in priority_rows}

        rows: list[dict[str, Any]] = []
        for row in dependency_rows:
            adapter_id = row["adapter_id"]
            priority = priority_by_adapter[adapter_id]
            if adapter_id == "network_html_article_fetch":
                candidate_class = "priority_runtime_candidate"
                candidate_state = "manual_review_cleared_pending_scheduler_activation"
                excluded_from_first_runtime_lane = "False"
            elif adapter_id == "network_social_column_fetch":
                candidate_class = "review_only_excluded"
                candidate_state = "nonpromotive_review_only"
                excluded_from_first_runtime_lane = "True"
            else:
                candidate_class = "reserved_primary_source_excluded"
                candidate_state = "reserved_until_primary_official_hosts_exist"
                excluded_from_first_runtime_lane = "True"

            rows.append(
                {
                    "adapter_id": adapter_id,
                    "queue_priority": priority["queue_priority"],
                    "dependency_state": row["dependency_state"],
                    "candidate_class": candidate_class,
                    "candidate_state": candidate_state,
                    "promotable_now": row["promotable_now"],
                    "excluded_from_first_runtime_lane": excluded_from_first_runtime_lane,
                    "blocking_reason": row["blocking_reason"],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        status_rows = [
            {
                "component": "runtime_promotion_candidate_surface",
                "component_state": "materialized_runtime_candidate_partition",
                "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
                "coverage_note": f"runtime_row_count = {len(rows)}",
            }
        ]
        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "runtime_row_count": len(rows),
            "priority_runtime_candidate_count": sum(
                row["candidate_class"] == "priority_runtime_candidate" for row in rows
            ),
            "excluded_runtime_row_count": sum(
                row["excluded_from_first_runtime_lane"] == "True" for row in rows
            ),
            "promotable_now_count": sum(row["promotable_now"] == "True" for row in rows),
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_runtime_promotion_candidate_surface_materialized",
        }
        interpretation = [
            "Runtime promotion is no longer one flat blocked set; it is partitioned into one first candidate and two excluded adapters.",
            "The only meaningful first runtime lane is html-article fetch after completed manual approval, but scheduler activation still keeps it non-promotive.",
        ]
        return V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qg_a_share_runtime_promotion_candidate_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
