from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareAutomationFoundationV1:
    summary: dict[str, Any]
    ingest_rows: list[dict[str, Any]]
    pipeline_rows: list[dict[str, Any]]
    review_rows: list[dict[str, Any]]
    retention_rows: list[dict[str, Any]]
    orchestration_rows: list[dict[str, Any]]


class MaterializeAShareAutomationFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "automation_registry"
        self.ingest_path = self.output_dir / "a_share_ingest_job_registry_v1.csv"
        self.pipeline_path = self.output_dir / "a_share_pipeline_job_registry_v1.csv"
        self.review_path = self.output_dir / "a_share_review_job_registry_v1.csv"
        self.retention_path = self.output_dir / "a_share_retention_job_registry_v1.csv"
        self.orchestration_path = self.output_dir / "a_share_orchestration_registry_v1.csv"
        self.manifest_path = self.output_dir / "a_share_automation_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareAutomationFoundationV1:
        ingest_rows = [
            {
                "job_id": "ingest_identity_source_refresh",
                "job_class": "ingest",
                "job_state": "bootstrap_defined",
                "target_layer": "identity",
            },
            {
                "job_id": "ingest_event_source_refresh",
                "job_class": "ingest",
                "job_state": "bootstrap_defined",
                "target_layer": "events",
            },
            {
                "job_id": "ingest_market_coverage_refresh",
                "job_class": "ingest",
                "job_state": "bootstrap_defined",
                "target_layer": "market",
            },
        ]
        pipeline_rows = [
            {
                "job_id": "pipeline_event_claim_event_materialization",
                "job_class": "pipeline",
                "job_state": "bootstrap_defined",
                "target_layer": "events",
            },
            {
                "job_id": "pipeline_label_feature_refresh",
                "job_class": "pipeline",
                "job_state": "bootstrap_defined",
                "target_layer": "labels_features",
            },
            {
                "job_id": "pipeline_pti_replay_refresh",
                "job_class": "pipeline",
                "job_state": "bootstrap_defined",
                "target_layer": "pti_replay",
            },
        ]
        review_rows = [
            {
                "job_id": "review_low_confidence_event_queue",
                "job_class": "review",
                "job_state": "bootstrap_defined",
                "target_layer": "quality",
            },
            {
                "job_id": "review_contradiction_queue",
                "job_class": "review",
                "job_state": "bootstrap_defined",
                "target_layer": "quality",
            },
            {
                "job_id": "review_attention_soft_candidate_queue",
                "job_class": "review",
                "job_state": "bootstrap_defined",
                "target_layer": "attention",
            },
        ]
        retention_rows = [
            {
                "job_id": "retention_temp_candidate_search_ttl",
                "job_class": "retention",
                "job_state": "bootstrap_defined",
                "target_layer": "temp",
            },
            {
                "job_id": "retention_review_queue_cleanup",
                "job_class": "retention",
                "job_state": "bootstrap_defined",
                "target_layer": "review_queue",
            },
            {
                "job_id": "retention_raw_document_compaction",
                "job_class": "retention",
                "job_state": "bootstrap_defined",
                "target_layer": "raw_documents",
            },
        ]
        orchestration_rows = [
            {
                "flow_id": "daily_bootstrap_cycle",
                "flow_state": "bootstrap_defined",
                "flow_sequence": "ingest->pipeline->review->retention",
            },
            {
                "flow_id": "manual_rebuild_cycle",
                "flow_state": "bootstrap_defined",
                "flow_sequence": "pipeline->governance_check->publish",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.ingest_path, ingest_rows)
        _write(self.pipeline_path, pipeline_rows)
        _write(self.review_path, review_rows)
        _write(self.retention_path, retention_rows)
        _write(self.orchestration_path, orchestration_rows)

        summary = {
            "ingest_job_count": len(ingest_rows),
            "pipeline_job_count": len(pipeline_rows),
            "review_job_count": len(review_rows),
            "retention_job_count": len(retention_rows),
            "orchestration_flow_count": len(orchestration_rows),
            "ingest_path": str(self.ingest_path.relative_to(self.repo_root)),
            "pipeline_path": str(self.pipeline_path.relative_to(self.repo_root)),
            "review_path": str(self.review_path.relative_to(self.repo_root)),
            "retention_path": str(self.retention_path.relative_to(self.repo_root)),
            "orchestration_path": str(self.orchestration_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareAutomationFoundationV1(
            summary=summary,
            ingest_rows=ingest_rows,
            pipeline_rows=pipeline_rows,
            review_rows=review_rows,
            retention_rows=retention_rows,
            orchestration_rows=orchestration_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareAutomationFoundationV1(repo_root).materialize()
    print(result.summary["ingest_path"])


if __name__ == "__main__":
    main()
