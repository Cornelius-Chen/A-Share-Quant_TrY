from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareServingFoundationV1:
    summary: dict[str, Any]
    research_rows: list[dict[str, Any]]
    shadow_rows: list[dict[str, Any]]
    live_like_rows: list[dict[str, Any]]
    route_rows: list[dict[str, Any]]


class MaterializeAShareServingFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.research_path = self.output_dir / "a_share_research_view_registry_v1.csv"
        self.shadow_path = self.output_dir / "a_share_shadow_view_registry_v1.csv"
        self.live_like_path = self.output_dir / "a_share_live_like_view_registry_v1.csv"
        self.route_path = self.output_dir / "a_share_serving_route_registry_v1.csv"
        self.manifest_path = self.output_dir / "a_share_serving_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareServingFoundationV1:
        research_rows = [
            {
                "view_id": "research_identity_master",
                "consumer_mode": "research",
                "artifact_path": "data/reference/info_center/identity/a_share_security_master_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "research_taxonomy_membership",
                "consumer_mode": "research",
                "artifact_path": "data/reference/info_center/taxonomy/a_share_concept_membership_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "research_event_registry",
                "consumer_mode": "research",
                "artifact_path": "data/reference/info_center/event_registry/a_share_event_registry_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "research_attention_registry",
                "consumer_mode": "research",
                "artifact_path": "data/reference/info_center/attention_registry/a_share_attention_registry_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "research_label_assignment",
                "consumer_mode": "research",
                "artifact_path": "data/reference/info_center/label_registry/a_share_label_assignment_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "research_feature_surface",
                "consumer_mode": "research",
                "artifact_path": "data/reference/info_center/feature_registry/a_share_feature_surface_v1.csv",
                "view_state": "read_ready",
            },
        ]
        shadow_rows = [
            {
                "view_id": "shadow_pti_event_ledger",
                "consumer_mode": "shadow",
                "artifact_path": "data/reference/info_center/event_registry/a_share_pti_event_ledger_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "shadow_time_slice_view",
                "consumer_mode": "shadow",
                "artifact_path": "data/derived/info_center/time_slices/a_share_time_slice_view_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "shadow_state_transition_journal",
                "consumer_mode": "shadow",
                "artifact_path": "data/reference/info_center/state_transition_journal/a_share_state_transition_journal_v1.csv",
                "view_state": "read_ready",
            },
            {
                "view_id": "shadow_replay_surface",
                "consumer_mode": "shadow",
                "artifact_path": "data/derived/info_center/replay/shadow/a_share_shadow_replay_surface_v1.csv",
                "view_state": "read_only_bootstrap",
            },
        ]
        live_like_rows = [
            {
                "view_id": "live_like_event_state_surface",
                "consumer_mode": "live_like",
                "artifact_path": "",
                "view_state": "deferred_backlog",
            },
            {
                "view_id": "live_like_execution_gate",
                "consumer_mode": "live_like",
                "artifact_path": "",
                "view_state": "deferred_backlog",
            },
        ]
        route_rows = [
            {
                "route_id": "research_default_route",
                "route_target": "research",
                "route_state": "active",
            },
            {
                "route_id": "shadow_default_route",
                "route_target": "shadow",
                "route_state": "active_read_only",
            },
            {
                "route_id": "live_like_default_route",
                "route_target": "live_like",
                "route_state": "deferred",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.research_path, research_rows)
        _write(self.shadow_path, shadow_rows)
        _write(self.live_like_path, live_like_rows)
        _write(self.route_path, route_rows)

        summary = {
            "research_view_count": len(research_rows),
            "shadow_view_count": len(shadow_rows),
            "live_like_view_count": len(live_like_rows),
            "active_serving_route_count": sum(row["route_state"] != "deferred" for row in route_rows),
            "research_path": str(self.research_path.relative_to(self.repo_root)),
            "shadow_path": str(self.shadow_path.relative_to(self.repo_root)),
            "live_like_path": str(self.live_like_path.relative_to(self.repo_root)),
            "route_path": str(self.route_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareServingFoundationV1(
            summary=summary,
            research_rows=research_rows,
            shadow_rows=shadow_rows,
            live_like_rows=live_like_rows,
            route_rows=route_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareServingFoundationV1(repo_root).materialize()
    print(result.summary["research_path"])


if __name__ == "__main__":
    main()
