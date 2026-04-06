from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
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


def _parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.candidate_path = base / "a_share_internal_hot_news_controlled_merge_candidate_surface_v1.csv"
        self.snapshot_path = base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_v1.csv"
        self.summary_path = base / "a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_summary_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1:
        candidate_rows = _read_csv(self.candidate_path)
        snapshot_rows = _read_csv(self.snapshot_path)
        snapshot_row = snapshot_rows[0] if snapshot_rows else {}

        preview_candidates = [
            row
            for row in candidate_rows
            if row.get("primary_theme_slug") != "broad_market" and row.get("top_symbol")
        ]
        ranked = sorted(
            preview_candidates,
            key=lambda row: (
                1 if row["candidate_role"] == "additive_second_source_theme_symbol_candidate" else 0,
                _parse_ts(row["public_ts"]),
                row["source_row_id"],
            ),
            reverse=True,
        )

        preview_rows: list[dict[str, Any]] = []
        for index, row in enumerate(ranked, start=1):
            preview_rows.append(
                {
                    "preview_rank": str(index),
                    "source_family": row["source_family"],
                    "source_row_id": row["source_row_id"],
                    "public_ts": row["public_ts"],
                    "primary_theme_slug": row["primary_theme_slug"],
                    "top_symbol": row["top_symbol"],
                    "candidate_role": row["candidate_role"],
                    "candidate_state": row["candidate_state"],
                    "consumer_preview_action": "review_for_opportunity_lane",
                    "title": row["title"],
                }
            )

        top_candidate = preview_rows[0] if preview_rows else {}
        current_top_theme = snapshot_row.get("top_opportunity_primary_theme_slug", "")
        current_top_watch = snapshot_row.get("top_watch_symbol", "")
        candidate_top_theme = top_candidate.get("primary_theme_slug", "")
        candidate_top_symbol = top_candidate.get("top_symbol", "")
        top_opportunity_change_if_promoted = (
            "stable" if candidate_top_theme == current_top_theme else "would_change"
        )
        top_watch_change_if_promoted = "stable" if candidate_top_symbol == current_top_watch else "would_change"

        summary_row = {
            "preview_id": "internal_hot_news_controlled_merge_candidate_consumer_preview_latest",
            "preview_row_count": str(len(preview_rows)),
            "additive_preview_count": str(
                sum(
                    row["candidate_role"] == "additive_second_source_theme_symbol_candidate"
                    for row in preview_rows
                )
            ),
            "unique_preview_theme_count": str(len({row["primary_theme_slug"] for row in preview_rows})),
            "unique_preview_symbol_count": str(len({row["top_symbol"] for row in preview_rows})),
            "current_top_opportunity_theme": current_top_theme,
            "current_top_watch_symbol": current_top_watch,
            "candidate_top_theme": candidate_top_theme,
            "candidate_top_symbol": candidate_top_symbol,
            "top_opportunity_change_if_promoted": top_opportunity_change_if_promoted,
            "top_watch_change_if_promoted": top_watch_change_if_promoted,
            "consumer_stability_state": (
                "candidate_lane_would_rotate_focus"
                if "would_change" in {top_opportunity_change_if_promoted, top_watch_change_if_promoted}
                else "candidate_lane_stable_against_current_focus"
            ),
        }

        _write_csv(self.output_path, preview_rows)
        _write_csv(self.summary_path, [summary_row])

        summary = {
            "preview_row_count": len(preview_rows),
            "additive_preview_count": sum(
                row["candidate_role"] == "additive_second_source_theme_symbol_candidate" for row in preview_rows
            ),
            "unique_preview_theme_count": len({row["primary_theme_slug"] for row in preview_rows}),
            "unique_preview_symbol_count": len({row["top_symbol"] for row in preview_rows}),
            "current_top_opportunity_theme": current_top_theme,
            "current_top_watch_symbol": current_top_watch,
            "candidate_top_theme": candidate_top_theme,
            "candidate_top_symbol": candidate_top_symbol,
            "top_opportunity_change_if_promoted": top_opportunity_change_if_promoted,
            "top_watch_change_if_promoted": top_watch_change_if_promoted,
            "consumer_stability_state": summary_row["consumer_stability_state"],
            "authoritative_output": "a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_materialized",
        }
        return MaterializedAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1(
            summary=summary,
            rows=preview_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
