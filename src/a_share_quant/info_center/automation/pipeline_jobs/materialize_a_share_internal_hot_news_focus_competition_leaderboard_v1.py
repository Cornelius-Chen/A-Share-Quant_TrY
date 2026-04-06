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
class MaterializedAShareInternalHotNewsFocusCompetitionLeaderboardV1:
    summary: dict[str, Any]
    detail_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsFocusCompetitionLeaderboardV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving_base = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.snapshot_path = derived_base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.focus_scoring_surface_path = (
            derived_base / "a_share_internal_hot_news_focus_scoring_surface_v1.csv"
        )
        self.detail_output_path = (
            derived_base / "a_share_internal_hot_news_focus_competition_leaderboard_v1.csv"
        )
        self.summary_output_path = (
            derived_base / "a_share_internal_hot_news_focus_competition_leaderboard_summary_v1.csv"
        )
        self.registry_path = (
            serving_base / "a_share_internal_hot_news_focus_competition_leaderboard_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsFocusCompetitionLeaderboardV1:
        snapshot = _read_csv(self.snapshot_path)[0]
        scoring_rows = _read_csv(self.focus_scoring_surface_path)

        incumbent_theme = snapshot["top_opportunity_primary_theme_slug"]
        incumbent_symbol = snapshot["top_watch_symbol"]
        incumbent_score = 0.0
        incumbent_support = 0
        rows: list[dict[str, Any]] = []
        for scored in scoring_rows:
            theme_slug = scored["theme_slug"]
            watch_symbol = scored["watch_symbol"]
            focus_total_score = float(scored["focus_total_score"])
            support_row_count = int(scored["support_row_count"])
            focus_role = (
                "incumbent"
                if theme_slug == incumbent_theme and watch_symbol == incumbent_symbol
                else "challenger"
            )
            if focus_role == "incumbent":
                incumbent_score = focus_total_score
                incumbent_support = support_row_count
            rows.append(
                {
                    "theme_slug": theme_slug,
                    "watch_symbol": watch_symbol,
                    "support_row_count": scored["support_row_count"],
                    "support_source_family_count": scored["support_source_family_count"],
                    "focus_total_score": scored["focus_total_score"],
                    "focus_score_density": scored["focus_score_density"],
                    "cycle_state": scored["cycle_state"],
                    "focus_bias_class": scored["focus_bias_class"],
                    "focus_role": focus_role,
                    "relative_support_gap_vs_incumbent": "0",
                    "relative_focus_score_gap_vs_incumbent": "0.0000",
                    "leaderboard_state": "focus_competition_scored_candidate_ready",
                }
            )

        for row in rows:
            row["relative_support_gap_vs_incumbent"] = str(int(row["support_row_count"]) - incumbent_support)
            row["relative_focus_score_gap_vs_incumbent"] = (
                f"{float(row['focus_total_score']) - incumbent_score:.4f}"
            )

        rows.sort(
            key=lambda row: (
                -float(row["focus_total_score"]),
                -float(row["focus_score_density"]),
                -int(row["support_row_count"]),
                row["theme_slug"],
                row["watch_symbol"],
            )
        )

        detail_rows: list[dict[str, Any]] = []
        current_rank = 0
        for index, row in enumerate(rows, start=1):
            ranked_row = {"leaderboard_rank": str(index), **row}
            if row["focus_role"] == "incumbent":
                current_rank = index
            detail_rows.append(ranked_row)

        top_row = detail_rows[0]
        summary_row = {
            "leaderboard_id": "internal_hot_news_focus_competition_leaderboard_latest",
            "current_primary_theme_slug": incumbent_theme,
            "current_primary_watch_symbol": incumbent_symbol,
            "current_primary_support_row_count": str(incumbent_support),
            "current_primary_focus_total_score": f"{incumbent_score:.4f}",
            "current_primary_rank": str(current_rank),
            "leader_theme_slug": top_row["theme_slug"],
            "leader_watch_symbol": top_row["watch_symbol"],
            "leader_support_row_count": top_row["support_row_count"],
            "leader_focus_total_score": top_row["focus_total_score"],
            "incumbent_is_leader": "true" if current_rank == 1 else "false",
            "challenger_count": str(max(len(detail_rows) - 1, 0)),
            "leaderboard_summary_state": "focus_competition_leaderboard_summarized",
        }

        _write_csv(self.detail_output_path, detail_rows)
        _write_csv(self.summary_output_path, [summary_row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_focus_competition_leaderboard",
                    "artifact_path": str(self.detail_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
                {
                    "view_id": "internal_hot_news_focus_competition_leaderboard_summary",
                    "artifact_path": str(self.summary_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
            ],
        )

        summary = {
            "leaderboard_row_count": len(detail_rows),
            "current_primary_theme_slug": summary_row["current_primary_theme_slug"],
            "current_primary_watch_symbol": summary_row["current_primary_watch_symbol"],
            "current_primary_support_row_count": int(summary_row["current_primary_support_row_count"]),
            "current_primary_focus_total_score": float(summary_row["current_primary_focus_total_score"]),
            "current_primary_rank": int(summary_row["current_primary_rank"]),
            "leader_theme_slug": summary_row["leader_theme_slug"],
            "leader_watch_symbol": summary_row["leader_watch_symbol"],
            "leader_support_row_count": int(summary_row["leader_support_row_count"]),
            "leader_focus_total_score": float(summary_row["leader_focus_total_score"]),
            "incumbent_is_leader": summary_row["incumbent_is_leader"],
            "challenger_count": int(summary_row["challenger_count"]),
            "authoritative_output": "a_share_internal_hot_news_focus_competition_leaderboard_materialized",
        }
        return MaterializedAShareInternalHotNewsFocusCompetitionLeaderboardV1(
            summary=summary,
            detail_rows=detail_rows,
            summary_rows=[summary_row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsFocusCompetitionLeaderboardV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
