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
class MaterializedAShareContradictionResolutionV1:
    summary: dict[str, Any]
    graph_rows: list[dict[str, Any]]
    review_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareContradictionResolutionV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.event_path = repo_root / "data" / "reference" / "info_center" / "event_registry" / "a_share_event_registry_v1.csv"
        self.backlog_path = (
            repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_contradiction_backlog_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "quality_registry"
        self.graph_path = self.output_dir / "a_share_contradiction_graph_v1.csv"
        self.review_path = self.output_dir / "a_share_contradiction_review_queue_v1.csv"
        self.residual_path = self.output_dir / "a_share_contradiction_resolution_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_contradiction_resolution_manifest_v1.json"

    def materialize(self) -> MaterializedAShareContradictionResolutionV1:
        event_rows = _read_csv(self.event_path)
        backlog_rows = _read_csv(self.backlog_path)

        grouped: dict[str, list[dict[str, str]]] = {}
        for row in event_rows:
            grouped.setdefault(row["registry_id"], []).append(row)

        graph_rows: list[dict[str, Any]] = []
        review_rows: list[dict[str, Any]] = []
        residual_rows: list[dict[str, Any]] = []

        for registry_id, rows in sorted(grouped.items()):
            if len(rows) == 1:
                row = rows[0]
                graph_rows.append(
                    {
                        "registry_id": registry_id,
                        "node_count": 1,
                        "resolution_class": "single_event_no_internal_conflict",
                        "resolved_event_id": row["event_id"],
                        "semantic_conflict": False,
                    }
                )
                if row["timestamp_resolution_status"] != "resolved":
                    review_rows.append(
                        {
                            "review_target": row["event_id"],
                            "review_class": "timestamp_resolution_followup",
                            "review_reason": row["timestamp_resolution_status"],
                        }
                    )
                continue

            unique_signatures = {
                (
                    row["event_id"],
                    row["claim_id"],
                    row["layer"],
                    row["event_scope"],
                    row["event_occurred_ts"],
                    row["public_ts"],
                    row["system_visible_ts"],
                    row["timestamp_resolution_status"],
                )
                for row in rows
            }
            retained_rows = [row for row in rows if str(row.get("decisive_retained", "")).lower() == "true"]
            if len(unique_signatures) == 1:
                resolved_event_id = retained_rows[0]["event_id"] if retained_rows else rows[0]["event_id"]
                graph_rows.append(
                    {
                        "registry_id": registry_id,
                        "node_count": len(rows),
                        "resolution_class": "duplicate_materialization_merge_candidate",
                        "resolved_event_id": resolved_event_id,
                        "semantic_conflict": False,
                    }
                )
            else:
                graph_rows.append(
                    {
                        "registry_id": registry_id,
                        "node_count": len(rows),
                        "resolution_class": "semantic_divergence_review_required",
                        "resolved_event_id": "",
                        "semantic_conflict": True,
                    }
                )
                review_rows.append(
                    {
                        "review_target": registry_id,
                        "review_class": "semantic_divergence",
                        "review_reason": "multiple non-identical events under one registry_id",
                    }
                )

        backlog_event_ids = {row["event_id"] for row in backlog_rows}
        resolved_event_ids = {row["resolved_event_id"] for row in graph_rows if row["resolved_event_id"]}
        for event_id in sorted(backlog_event_ids - resolved_event_ids):
            residual_rows.append(
                {
                    "event_id": event_id,
                    "residual_reason": "backlog_event_not_promoted_to_resolved_event_id",
                }
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.graph_path, graph_rows)
        _write(self.review_path, review_rows or [{"review_target": "", "review_class": "", "review_reason": ""}])
        _write(self.residual_path, residual_rows or [{"event_id": "", "residual_reason": ""}])

        summary = {
            "registry_group_count": len(graph_rows),
            "duplicate_merge_candidate_count": sum(
                row["resolution_class"] == "duplicate_materialization_merge_candidate" for row in graph_rows
            ),
            "semantic_divergence_count": sum(str(row["semantic_conflict"]) == "True" for row in graph_rows),
            "review_queue_count": 0 if (len(review_rows) == 0) else len(review_rows),
            "residual_count": 0 if (len(residual_rows) == 0) else len(residual_rows),
            "graph_path": str(self.graph_path.relative_to(self.repo_root)),
            "review_path": str(self.review_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareContradictionResolutionV1(
            summary=summary, graph_rows=graph_rows, review_rows=review_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareContradictionResolutionV1(repo_root).materialize()
    print(result.summary["graph_path"])


if __name__ == "__main__":
    main()
