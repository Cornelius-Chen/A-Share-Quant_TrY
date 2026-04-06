from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsChallengerRotationShadowSnapshotV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsChallengerRotationShadowSnapshotV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.snapshot_path = base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.candidate_packet_path = base / "a_share_internal_hot_news_challenger_rotation_candidate_packet_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_challenger_rotation_shadow_snapshot_v1.csv"
        self.registry_path = serving / "a_share_internal_hot_news_challenger_rotation_shadow_snapshot_registry_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsChallengerRotationShadowSnapshotV1:
        current_snapshot = _read_csv(self.snapshot_path)[0]
        challenger_packet = _read_csv(self.candidate_packet_path)[0]

        row = {
            "shadow_snapshot_id": "internal_hot_news_challenger_rotation_shadow_snapshot_latest",
            "current_top_opportunity_theme": current_snapshot["top_opportunity_primary_theme_slug"],
            "current_top_watch_symbol": current_snapshot["top_watch_symbol"],
            "shadow_top_opportunity_theme": challenger_packet["challenger_top_opportunity_theme"],
            "shadow_top_watch_symbol": challenger_packet["challenger_top_watch_symbol"],
            "shadow_source_family": challenger_packet["challenger_source_family"],
            "shadow_source_row_id": challenger_packet["challenger_source_row_id"],
            "shadow_rotation_state": challenger_packet["rotation_impact_state"],
            "shadow_snapshot_consumer_gate_mode": current_snapshot["snapshot_consumer_gate_mode"],
            "shadow_program_mode": "research_shadow_internal_only",
            "shadow_snapshot_state": "challenger_rotation_shadow_snapshot_ready",
            "challenger_title": challenger_packet["challenger_title"],
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_challenger_rotation_shadow_snapshot",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "shadow_snapshot_row_count": 1,
            "current_top_opportunity_theme": row["current_top_opportunity_theme"],
            "shadow_top_opportunity_theme": row["shadow_top_opportunity_theme"],
            "current_top_watch_symbol": row["current_top_watch_symbol"],
            "shadow_top_watch_symbol": row["shadow_top_watch_symbol"],
            "shadow_source_family": row["shadow_source_family"],
            "shadow_rotation_state": row["shadow_rotation_state"],
            "authoritative_output": "a_share_internal_hot_news_challenger_rotation_shadow_snapshot_materialized",
        }
        return MaterializedAShareInternalHotNewsChallengerRotationShadowSnapshotV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsChallengerRotationShadowSnapshotV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
