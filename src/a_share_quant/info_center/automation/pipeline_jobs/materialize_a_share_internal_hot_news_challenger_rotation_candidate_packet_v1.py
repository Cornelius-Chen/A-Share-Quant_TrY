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
class MaterializedAShareInternalHotNewsChallengerRotationCandidatePacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsChallengerRotationCandidatePacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.comparison_summary_path = base / "a_share_internal_hot_news_challenger_focus_comparison_summary_v1.csv"
        self.comparison_surface_path = base / "a_share_internal_hot_news_challenger_focus_comparison_surface_v1.csv"
        self.snapshot_path = base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_challenger_rotation_candidate_packet_v1.csv"
        self.registry_path = serving / "a_share_internal_hot_news_challenger_rotation_candidate_packet_registry_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsChallengerRotationCandidatePacketV1:
        comparison_summary = _read_csv(self.comparison_summary_path)[0]
        comparison_rows = _read_csv(self.comparison_surface_path)
        snapshot = _read_csv(self.snapshot_path)[0]
        top_challenger = comparison_rows[0] if comparison_rows else {}

        challenger_theme = comparison_summary["top_challenger_theme_slug"]
        challenger_symbol = comparison_summary["top_challenger_symbol"]

        row = {
            "challenger_rotation_candidate_id": "internal_hot_news_challenger_rotation_candidate_latest",
            "current_top_opportunity_theme": snapshot["top_opportunity_primary_theme_slug"],
            "current_top_watch_symbol": snapshot["top_watch_symbol"],
            "challenger_top_opportunity_theme": challenger_theme,
            "challenger_top_watch_symbol": challenger_symbol,
            "challenger_source_family": top_challenger.get("support_source_families_top5", "").split(",")[0],
            "challenger_source_row_id": top_challenger.get("support_source_row_ids_top5", "").split(",")[0],
            "challenger_candidate_role": top_challenger.get("candidate_roles_top5", "").split(",")[0],
            "challenger_route_state": top_challenger.get("route_states_top5", "").split(",")[0],
            "challenger_support_row_count": comparison_summary["top_challenger_support_row_count"],
            "challenger_source_family_count": comparison_summary["top_challenger_source_family_count"],
            "challenger_rotation_state": "challenger_rotation_preview_ready",
            "rotation_impact_state": "challenger_would_rotate_primary_focus",
            "top_opportunity_change_if_accepted": "would_change",
            "top_watch_change_if_accepted": "would_change",
            "current_snapshot_consumer_gate_mode": snapshot.get("snapshot_consumer_gate_mode", ""),
            "challenger_rotation_consumer_mode": "challenger_rotation_preview_only",
            "challenger_title": top_challenger.get("support_source_row_ids_top5", ""),
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_challenger_rotation_candidate_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "current_top_opportunity_theme": row["current_top_opportunity_theme"],
            "challenger_top_opportunity_theme": row["challenger_top_opportunity_theme"],
            "current_top_watch_symbol": row["current_top_watch_symbol"],
            "challenger_top_watch_symbol": row["challenger_top_watch_symbol"],
            "challenger_source_family": row["challenger_source_family"],
            "challenger_support_row_count": int(row["challenger_support_row_count"]),
            "top_opportunity_change_if_accepted": row["top_opportunity_change_if_accepted"],
            "top_watch_change_if_accepted": row["top_watch_change_if_accepted"],
            "authoritative_output": "a_share_internal_hot_news_challenger_rotation_candidate_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsChallengerRotationCandidatePacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsChallengerRotationCandidatePacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
