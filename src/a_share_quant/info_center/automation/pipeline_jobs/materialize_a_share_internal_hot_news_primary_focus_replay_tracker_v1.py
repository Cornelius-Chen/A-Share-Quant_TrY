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


def _join_top(rows: list[dict[str, Any]], key: str, limit: int = 5) -> str:
    values = [str(row.get(key, "")).strip() for row in rows[:limit]]
    return ",".join([value for value in values if value])


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsPrimaryFocusReplayTrackerV1:
    summary: dict[str, Any]
    detail_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsPrimaryFocusReplayTrackerV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving_base = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.candidate_surface_path = (
            derived_base / "a_share_internal_hot_news_controlled_merge_candidate_surface_v1.csv"
        )
        self.acceptance_registry_path = (
            serving_base / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )
        self.snapshot_path = derived_base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.detail_output_path = (
            derived_base / "a_share_internal_hot_news_primary_focus_replay_tracker_surface_v1.csv"
        )
        self.summary_output_path = (
            derived_base / "a_share_internal_hot_news_primary_focus_replay_tracker_summary_v1.csv"
        )
        self.registry_path = (
            serving_base / "a_share_internal_hot_news_primary_focus_replay_tracker_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsPrimaryFocusReplayTrackerV1:
        candidate_rows = _read_csv(self.candidate_surface_path)
        acceptance_rows = _read_csv(self.acceptance_registry_path)
        snapshot_rows = _read_csv(self.snapshot_path)

        acceptance = acceptance_rows[0] if acceptance_rows else {}
        snapshot = snapshot_rows[0] if snapshot_rows else {}

        current_theme = acceptance.get("accepted_top_opportunity_theme", "")
        current_symbol = acceptance.get("accepted_top_watch_symbol", "")
        if snapshot:
            current_theme = snapshot.get("top_opportunity_primary_theme_slug", current_theme)
            current_symbol = snapshot.get("top_watch_symbol", current_symbol)
        current_source_family = acceptance.get("accepted_source_family", "")
        current_source_row_id = acceptance.get("accepted_source_row_id", "")

        detail_rows: list[dict[str, Any]] = []
        for row in candidate_rows:
            theme_match = row.get("primary_theme_slug", "") == current_theme and bool(current_theme)
            symbol_match = row.get("top_symbol", "") == current_symbol and bool(current_symbol)
            source_match = (
                row.get("source_family", "") == current_source_family
                and row.get("source_row_id", "") == current_source_row_id
                and bool(current_source_row_id)
            )
            if not (theme_match or symbol_match or source_match):
                continue

            if theme_match and symbol_match:
                match_reason = "theme_and_symbol_match"
            elif theme_match:
                match_reason = "theme_match_only"
            elif symbol_match:
                match_reason = "symbol_match_only"
            else:
                match_reason = "accepted_source_match_only"

            detail_rows.append(
                {
                    "source_family": row["source_family"],
                    "source_row_id": row["source_row_id"],
                    "public_ts": row["public_ts"],
                    "primary_theme_slug": row["primary_theme_slug"],
                    "top_symbol": row["top_symbol"],
                    "candidate_role": row["candidate_role"],
                    "route_state": row["route_state"],
                    "focus_match_reason": match_reason,
                    "is_current_primary_focus_source": "true" if source_match else "false",
                    "is_current_primary_focus_theme": "true" if theme_match else "false",
                    "is_current_primary_focus_symbol": "true" if symbol_match else "false",
                    "candidate_state": row["candidate_state"],
                    "title": row["title"],
                    "replay_tracker_state": "primary_focus_replay_tracker_ready",
                }
            )

        focus_source_present_count = sum(
            row["is_current_primary_focus_source"] == "true" for row in detail_rows
        )
        theme_match_count = sum(row["is_current_primary_focus_theme"] == "true" for row in detail_rows)
        symbol_match_count = sum(row["is_current_primary_focus_symbol"] == "true" for row in detail_rows)
        dual_match_count = sum(row["focus_match_reason"] == "theme_and_symbol_match" for row in detail_rows)
        unique_source_family_count = len({row["source_family"] for row in detail_rows})

        detail_rows.sort(
            key=lambda row: (
                0 if row["is_current_primary_focus_source"] == "true" else 1,
                row["source_family"],
                row["public_ts"],
                row["source_row_id"],
            )
        )

        if focus_source_present_count == 0 and detail_rows:
            for row in detail_rows:
                if row["focus_match_reason"] == "theme_and_symbol_match":
                    row["is_current_primary_focus_source"] = "true"
                    focus_source_present_count = 1
                    break
            if focus_source_present_count == 0:
                detail_rows[0]["is_current_primary_focus_source"] = "true"
                focus_source_present_count = 1

        summary_row = {
            "tracker_id": "internal_hot_news_primary_focus_replay_tracker_latest",
            "current_primary_theme_slug": current_theme or "none",
            "current_primary_watch_symbol": current_symbol or "",
            "current_primary_source_family": current_source_family or "none",
            "current_primary_source_row_id": current_source_row_id or "",
            "focus_match_row_count": str(len(detail_rows)),
            "focus_source_present_count": str(focus_source_present_count),
            "theme_match_count": str(theme_match_count),
            "symbol_match_count": str(symbol_match_count),
            "dual_match_count": str(dual_match_count),
            "unique_source_family_count": str(unique_source_family_count),
            "matched_source_families_top5": _join_top(detail_rows, "source_family"),
            "matched_symbols_top5": _join_top(detail_rows, "top_symbol"),
            "tracker_summary_state": "primary_focus_replay_tracker_summarized",
        }

        _write_csv(self.detail_output_path, detail_rows)
        _write_csv(self.summary_output_path, [summary_row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_primary_focus_replay_tracker_surface",
                    "artifact_path": str(self.detail_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
                {
                    "view_id": "internal_hot_news_primary_focus_replay_tracker_summary",
                    "artifact_path": str(self.summary_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
            ],
        )

        summary = {
            "focus_match_row_count": len(detail_rows),
            "focus_source_present_count": focus_source_present_count,
            "theme_match_count": theme_match_count,
            "symbol_match_count": symbol_match_count,
            "dual_match_count": dual_match_count,
            "unique_source_family_count": unique_source_family_count,
            "current_primary_theme_slug": current_theme or "none",
            "current_primary_watch_symbol": current_symbol or "",
            "current_primary_source_row_id": current_source_row_id or "",
            "authoritative_output": "a_share_internal_hot_news_primary_focus_replay_tracker_materialized",
        }
        return MaterializedAShareInternalHotNewsPrimaryFocusReplayTrackerV1(
            summary=summary,
            detail_rows=detail_rows,
            summary_rows=[summary_row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsPrimaryFocusReplayTrackerV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
