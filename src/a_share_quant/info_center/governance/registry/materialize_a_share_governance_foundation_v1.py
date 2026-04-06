from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareGovernanceFoundationV1:
    summary: dict[str, Any]
    schema_rows: list[dict[str, Any]]
    dataset_rows: list[dict[str, Any]]
    heartbeat_rows: list[dict[str, Any]]
    gate_rows: list[dict[str, Any]]


class MaterializeAShareGovernanceFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "governance_registry"
        self.schema_path = self.output_dir / "a_share_schema_registry_v1.csv"
        self.dataset_path = self.output_dir / "a_share_dataset_registry_v1.csv"
        self.heartbeat_path = self.output_dir / "a_share_workstream_heartbeat_v1.csv"
        self.gate_path = self.output_dir / "a_share_promotion_gate_registry_v1.csv"
        self.manifest_path = self.output_dir / "a_share_governance_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareGovernanceFoundationV1:
        schema_rows = [
            {"schema_id": "identity_v1", "schema_scope": "identity", "schema_state": "active"},
            {"schema_id": "taxonomy_v1", "schema_scope": "taxonomy", "schema_state": "active"},
            {"schema_id": "events_v1", "schema_scope": "events", "schema_state": "active"},
            {"schema_id": "quality_v1", "schema_scope": "quality", "schema_state": "active"},
            {"schema_id": "attention_v1", "schema_scope": "attention", "schema_state": "active"},
            {"schema_id": "labels_v1", "schema_scope": "labels", "schema_state": "active"},
            {"schema_id": "features_v1", "schema_scope": "features", "schema_state": "active"},
            {"schema_id": "market_v1", "schema_scope": "market", "schema_state": "active"},
            {"schema_id": "pti_v1", "schema_scope": "pti", "schema_state": "active"},
            {"schema_id": "replay_v1", "schema_scope": "replay", "schema_state": "active"},
            {"schema_id": "serving_v1", "schema_scope": "serving", "schema_state": "active"},
        ]
        dataset_rows = [
            {
                "dataset_id": "security_master",
                "artifact_path": "data/reference/info_center/identity/a_share_security_master_v1.csv",
                "dataset_state": "source_of_truth",
            },
            {
                "dataset_id": "event_registry",
                "artifact_path": "data/reference/info_center/event_registry/a_share_event_registry_v1.csv",
                "dataset_state": "source_of_truth",
            },
            {
                "dataset_id": "attention_registry",
                "artifact_path": "data/reference/info_center/attention_registry/a_share_attention_registry_v1.csv",
                "dataset_state": "source_of_truth",
            },
            {
                "dataset_id": "feature_surface",
                "artifact_path": "data/reference/info_center/feature_registry/a_share_feature_surface_v1.csv",
                "dataset_state": "source_of_truth",
            },
            {
                "dataset_id": "market_registry",
                "artifact_path": "data/reference/info_center/market_registry/a_share_daily_market_registry_v1.csv",
                "dataset_state": "source_of_truth",
            },
            {
                "dataset_id": "pti_event_ledger",
                "artifact_path": "data/reference/info_center/event_registry/a_share_pti_event_ledger_v1.csv",
                "dataset_state": "source_of_truth",
            },
            {
                "dataset_id": "shadow_replay_surface",
                "artifact_path": "data/derived/info_center/replay/shadow/a_share_shadow_replay_surface_v1.csv",
                "dataset_state": "read_only_surface",
            },
            {
                "dataset_id": "serving_route_registry",
                "artifact_path": "data/reference/info_center/serving_registry/a_share_serving_route_registry_v1.csv",
                "dataset_state": "active_control_surface",
            },
        ]
        heartbeat_rows = [
            {"workstream": "identity", "workstream_state": "frozen_foundation_complete_enough"},
            {"workstream": "taxonomy", "workstream_state": "frozen_foundation_complete_enough_with_backlogs"},
            {"workstream": "events", "workstream_state": "frozen_foundation_complete_enough"},
            {"workstream": "quality", "workstream_state": "frozen_foundation_complete_enough"},
            {"workstream": "attention", "workstream_state": "frozen_bootstrap_complete_enough"},
            {"workstream": "labels", "workstream_state": "frozen_bootstrap_complete_enough_with_backlogs"},
            {"workstream": "features", "workstream_state": "frozen_bootstrap_complete_enough_with_backlogs"},
            {"workstream": "market", "workstream_state": "frozen_storage_aware_foundation_complete_enough"},
            {"workstream": "pti", "workstream_state": "frozen_bootstrap_complete_enough"},
            {"workstream": "replay", "workstream_state": "frozen_read_only_complete_enough"},
            {"workstream": "serving", "workstream_state": "frozen_bootstrap_complete_enough"},
            {"workstream": "governance", "workstream_state": "active_materializing"},
            {"workstream": "automation", "workstream_state": "not_started_beyond_scaffold"},
        ]
        gate_rows = [
            {
                "gate_id": "live_like_opening_gate",
                "gate_state": "closed",
                "gate_reason": "governance and automation bindings must exist before live_like serving opens",
            },
            {
                "gate_id": "execution_authority_gate",
                "gate_state": "closed",
                "gate_reason": "information center remains research-shadow only",
            },
            {
                "gate_id": "board_state_derivation_gate",
                "gate_state": "closed",
                "gate_reason": "market foundation left board-state derivation explicitly backlogged",
            },
            {
                "gate_id": "quality_promotion_gate",
                "gate_state": "partially_open_bootstrap_only",
                "gate_reason": "quality tiering exists but contradiction resolution is still backlog",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.schema_path, schema_rows)
        _write(self.dataset_path, dataset_rows)
        _write(self.heartbeat_path, heartbeat_rows)
        _write(self.gate_path, gate_rows)

        summary = {
            "schema_count": len(schema_rows),
            "dataset_count": len(dataset_rows),
            "heartbeat_count": len(heartbeat_rows),
            "closed_gate_count": sum(row["gate_state"] == "closed" for row in gate_rows),
            "schema_path": str(self.schema_path.relative_to(self.repo_root)),
            "dataset_path": str(self.dataset_path.relative_to(self.repo_root)),
            "heartbeat_path": str(self.heartbeat_path.relative_to(self.repo_root)),
            "gate_path": str(self.gate_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareGovernanceFoundationV1(
            summary=summary,
            schema_rows=schema_rows,
            dataset_rows=dataset_rows,
            heartbeat_rows=heartbeat_rows,
            gate_rows=gate_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareGovernanceFoundationV1(repo_root).materialize()
    print(result.summary["schema_path"])


if __name__ == "__main__":
    main()
