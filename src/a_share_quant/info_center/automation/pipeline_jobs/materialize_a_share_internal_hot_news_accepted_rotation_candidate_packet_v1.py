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
class MaterializedAShareInternalHotNewsAcceptedRotationCandidatePacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsAcceptedRotationCandidatePacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.preview_summary_path = base / "a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_summary_v1.csv"
        self.preview_path = base / "a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_v1.csv"
        self.snapshot_path = base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_accepted_rotation_candidate_packet_v1.csv"
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_accepted_rotation_candidate_packet_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsAcceptedRotationCandidatePacketV1:
        preview_summary = _read_csv(self.preview_summary_path)[0]
        preview_rows = _read_csv(self.preview_path)
        snapshot = _read_csv(self.snapshot_path)[0]
        top_candidate = preview_rows[0] if preview_rows else {}

        row = {
            "accepted_rotation_candidate_id": "internal_hot_news_accepted_rotation_candidate_latest",
            "current_top_opportunity_theme": preview_summary["current_top_opportunity_theme"],
            "current_top_watch_symbol": preview_summary["current_top_watch_symbol"],
            "accepted_top_opportunity_theme": preview_summary["candidate_top_theme"],
            "accepted_top_watch_symbol": preview_summary["candidate_top_symbol"],
            "accepted_source_family": top_candidate.get("source_family", ""),
            "accepted_source_row_id": top_candidate.get("source_row_id", ""),
            "accepted_public_ts": top_candidate.get("public_ts", ""),
            "accepted_candidate_role": top_candidate.get("candidate_role", ""),
            "accepted_rotation_state": "rotation_preview_ready",
            "rotation_impact_state": preview_summary["consumer_stability_state"],
            "top_opportunity_change_if_accepted": preview_summary["top_opportunity_change_if_promoted"],
            "top_watch_change_if_accepted": preview_summary["top_watch_change_if_promoted"],
            "current_snapshot_consumer_gate_mode": snapshot.get("snapshot_consumer_gate_mode", ""),
            "accepted_rotation_consumer_mode": "accepted_rotation_preview_only",
            "accepted_title": top_candidate.get("title", ""),
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_accepted_rotation_candidate_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "current_top_opportunity_theme": row["current_top_opportunity_theme"],
            "accepted_top_opportunity_theme": row["accepted_top_opportunity_theme"],
            "current_top_watch_symbol": row["current_top_watch_symbol"],
            "accepted_top_watch_symbol": row["accepted_top_watch_symbol"],
            "accepted_source_family": row["accepted_source_family"],
            "top_opportunity_change_if_accepted": row["top_opportunity_change_if_accepted"],
            "top_watch_change_if_accepted": row["top_watch_change_if_accepted"],
            "authoritative_output": "a_share_internal_hot_news_accepted_rotation_candidate_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsAcceptedRotationCandidatePacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsAcceptedRotationCandidatePacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
