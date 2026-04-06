from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


DEFER_HOSTS = {
    "www.jiuyangongshe.com",
    "www.futurephecda.com",
    "www.senn.com.cn",
    "www.forbeschina.com",
}


@dataclass(slots=True)
class V134NIAShareNetworkQueuePriorityAuditV1Report:
    summary: dict[str, Any]
    allowlist_rows: list[dict[str, Any]]
    runtime_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "allowlist_rows": self.allowlist_rows,
            "runtime_rows": self.runtime_rows,
            "interpretation": self.interpretation,
        }


class V134NIAShareNetworkQueuePriorityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.allowlist_queue_path = (
            repo_root / "data" / "temp" / "info_center" / "review_queue" / "a_share_network_allowlist_decision_queue_v1.csv"
        )
        self.runtime_queue_path = (
            repo_root / "data" / "temp" / "info_center" / "review_queue" / "a_share_network_runtime_deployment_queue_v1.csv"
        )
        self.allowlist_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_allowlist_priority_registry_v1.csv"
        )
        self.runtime_output = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_runtime_priority_registry_v1.csv"
        )
        self.status_output = repo_root / "data" / "training" / "a_share_network_queue_priority_status_v1.csv"

    def _materialize_allowlist_rows(self, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
        host_counts: dict[str, int] = {}
        for row in rows:
            host_counts[row["host"]] = host_counts.get(row["host"], 0) + 1

        prioritized_rows: list[dict[str, Any]] = []
        for row in rows:
            tier = row["source_tier"]
            host = row["host"]
            if host in DEFER_HOSTS:
                priority = "deferred_manual_review"
            elif tier == "T2_reliable_media":
                priority = "batch_one_manual_license_review"
            else:
                priority = "batch_two_manual_license_review"
            prioritized_rows.append(
                {
                    "source_id": row["source_id"],
                    "host": host,
                    "source_tier": tier,
                    "host_source_count": host_counts[host],
                    "queue_priority": priority,
                    "decision_scope": row["decision_scope"],
                }
            )
        return prioritized_rows

    def _materialize_runtime_rows(self, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
        prioritized_rows: list[dict[str, Any]] = []
        for row in rows:
            adapter_id = row["adapter_id"]
            if adapter_id == "network_html_article_fetch":
                priority = "first_runtime_candidate_after_batch_one_allowlist"
            elif adapter_id == "network_social_column_fetch":
                priority = "keep_review_only_deferred"
            else:
                priority = "reserve_until_primary_official_hosts_exist"
            prioritized_rows.append(
                {
                    "adapter_id": adapter_id,
                    "flow_id": row["flow_id"],
                    "queue_priority": priority,
                    "deployment_scope": row["deployment_scope"],
                }
            )
        return prioritized_rows

    def analyze(self) -> V134NIAShareNetworkQueuePriorityAuditV1Report:
        allowlist_queue_rows = _read_csv(self.allowlist_queue_path)
        runtime_queue_rows = _read_csv(self.runtime_queue_path)

        allowlist_rows = self._materialize_allowlist_rows(allowlist_queue_rows)
        runtime_rows = self._materialize_runtime_rows(runtime_queue_rows)

        self.allowlist_output.parent.mkdir(parents=True, exist_ok=True)
        with self.allowlist_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(allowlist_rows[0].keys()))
            writer.writeheader()
            writer.writerows(allowlist_rows)

        with self.runtime_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(runtime_rows[0].keys()))
            writer.writeheader()
            writer.writerows(runtime_rows)

        status_rows = [
            {
                "component": "allowlist_batch_one",
                "component_state": "priority_materialized",
                "artifact_path": str(self.allowlist_output.relative_to(self.repo_root)),
                "coverage_note": (
                    f"batch_one_count = {sum(row['queue_priority'] == 'batch_one_manual_license_review' for row in allowlist_rows)}"
                ),
            },
            {
                "component": "allowlist_batch_two",
                "component_state": "priority_materialized",
                "artifact_path": str(self.allowlist_output.relative_to(self.repo_root)),
                "coverage_note": (
                    f"batch_two_count = {sum(row['queue_priority'] == 'batch_two_manual_license_review' for row in allowlist_rows)}"
                ),
            },
            {
                "component": "allowlist_deferred",
                "component_state": "priority_materialized",
                "artifact_path": str(self.allowlist_output.relative_to(self.repo_root)),
                "coverage_note": (
                    f"deferred_count = {sum(row['queue_priority'] == 'deferred_manual_review' for row in allowlist_rows)}"
                ),
            },
            {
                "component": "runtime_priority_surface",
                "component_state": "priority_materialized",
                "artifact_path": str(self.runtime_output.relative_to(self.repo_root)),
                "coverage_note": f"runtime_row_count = {len(runtime_rows)}",
            },
        ]

        self.status_output.parent.mkdir(parents=True, exist_ok=True)
        with self.status_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
            writer.writeheader()
            writer.writerows(status_rows)

        summary = {
            "allowlist_row_count": len(allowlist_rows),
            "allowlist_batch_one_count": sum(
                row["queue_priority"] == "batch_one_manual_license_review" for row in allowlist_rows
            ),
            "allowlist_batch_two_count": sum(
                row["queue_priority"] == "batch_two_manual_license_review" for row in allowlist_rows
            ),
            "allowlist_deferred_count": sum(
                row["queue_priority"] == "deferred_manual_review" for row in allowlist_rows
            ),
            "runtime_row_count": len(runtime_rows),
            "status_csv": str(self.status_output.relative_to(self.repo_root)),
            "authoritative_output": "a_share_network_queue_priority_surface_materialized",
        }
        interpretation = [
            "Source-side queue processing is now ordered rather than flat; not every pending host should be reviewed or activated in the same batch.",
            "Mainstream T2 media hosts form the first manual review batch, secondary hosts form batch two, and a small set of unclear hosts remains deferred.",
            "Runtime deployment should only consider html-article fetch after batch-one allowlist review; social-column and official-source adapters remain deferred or reserved.",
        ]
        return V134NIAShareNetworkQueuePriorityAuditV1Report(
            summary=summary,
            allowlist_rows=allowlist_rows,
            runtime_rows=runtime_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NIAShareNetworkQueuePriorityAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NIAShareNetworkQueuePriorityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ni_a_share_network_queue_priority_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
