from __future__ import annotations

import csv
from collections import defaultdict
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


def _join_top(values: list[str], limit: int = 5) -> str:
    deduped: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)
    return ",".join(deduped[:limit])


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsChallengerFocusComparisonV1:
    summary: dict[str, Any]
    detail_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsChallengerFocusComparisonV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving_base = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.candidate_surface_path = (
            derived_base / "a_share_internal_hot_news_controlled_merge_candidate_surface_v1.csv"
        )
        self.snapshot_path = derived_base / "a_share_internal_hot_news_program_snapshot_v1.csv"
        self.leaderboard_detail_path = (
            derived_base / "a_share_internal_hot_news_focus_competition_leaderboard_v1.csv"
        )
        self.detail_output_path = (
            derived_base / "a_share_internal_hot_news_challenger_focus_comparison_surface_v1.csv"
        )
        self.summary_output_path = (
            derived_base / "a_share_internal_hot_news_challenger_focus_comparison_summary_v1.csv"
        )
        self.registry_path = (
            serving_base / "a_share_internal_hot_news_challenger_focus_comparison_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsChallengerFocusComparisonV1:
        candidate_rows = _read_csv(self.candidate_surface_path)
        leaderboard_rows = _read_csv(self.leaderboard_detail_path)
        snapshot_rows = _read_csv(self.snapshot_path)
        snapshot = snapshot_rows[0] if snapshot_rows else {}

        current_theme = snapshot.get("top_opportunity_primary_theme_slug", "")
        current_symbol = snapshot.get("top_watch_symbol", "")

        grouped_candidates: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in candidate_rows:
            theme = row.get("primary_theme_slug", "")
            symbol = row.get("top_symbol", "")
            if theme and symbol:
                grouped_candidates[(theme, symbol)].append(row)

        detail_rows: list[dict[str, Any]] = []
        for row in leaderboard_rows:
            theme = row.get("theme_slug", "")
            symbol = row.get("watch_symbol", "")
            if theme in {"", "broad_market"}:
                continue
            if theme == current_theme and symbol == current_symbol:
                continue
            supporting_rows = grouped_candidates.get((theme, symbol), [])
            source_families = [supporting_row["source_family"] for supporting_row in supporting_rows]
            source_row_ids = [supporting_row["source_row_id"] for supporting_row in supporting_rows]
            candidate_roles = [supporting_row["candidate_role"] for supporting_row in supporting_rows]
            route_states = [supporting_row["route_state"] for supporting_row in supporting_rows]
            detail_rows.append(
                {
                    "challenger_theme_slug": theme,
                    "challenger_top_symbol": symbol,
                    "support_row_count": row["support_row_count"],
                    "support_source_family_count": row["support_source_family_count"],
                    "focus_total_score": row["focus_total_score"],
                    "focus_score_density": row["focus_score_density"],
                    "cycle_state": row["cycle_state"],
                    "focus_bias_class": row["focus_bias_class"],
                    "support_source_families_top5": _join_top(source_families),
                    "support_source_row_ids_top5": _join_top(source_row_ids),
                    "candidate_roles_top5": _join_top(candidate_roles) if candidate_roles else row["focus_role"],
                    "route_states_top5": _join_top(route_states) if route_states else row["leaderboard_state"],
                    "challenger_state": "challenger_focus_candidate_ready_from_scored_leaderboard",
                }
            )

        detail_rows.sort(
            key=lambda row: (
                -float(row["focus_total_score"]),
                -float(row["focus_score_density"]),
                -int(row["support_row_count"]),
                row["challenger_theme_slug"],
                row["challenger_top_symbol"],
            )
        )

        top_row = detail_rows[0] if detail_rows else {}
        summary_row = {
            "comparison_id": "internal_hot_news_challenger_focus_comparison_latest",
            "current_primary_theme_slug": current_theme or "none",
            "current_primary_watch_symbol": current_symbol or "",
            "challenger_row_count": str(len(detail_rows)),
            "top_challenger_theme_slug": top_row.get("challenger_theme_slug", "none"),
            "top_challenger_symbol": top_row.get("challenger_top_symbol", ""),
            "top_challenger_support_row_count": top_row.get("support_row_count", "0"),
            "top_challenger_source_family_count": top_row.get("support_source_family_count", "0"),
            "top_challenger_focus_total_score": top_row.get("focus_total_score", "0.0000"),
            "comparison_summary_state": "challenger_focus_comparison_summarized",
        }

        _write_csv(self.detail_output_path, detail_rows)
        _write_csv(self.summary_output_path, [summary_row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_challenger_focus_comparison_surface",
                    "artifact_path": str(self.detail_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
                {
                    "view_id": "internal_hot_news_challenger_focus_comparison_summary",
                    "artifact_path": str(self.summary_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
            ],
        )

        summary = {
            "challenger_row_count": len(detail_rows),
            "current_primary_theme_slug": current_theme or "none",
            "current_primary_watch_symbol": current_symbol or "",
            "top_challenger_theme_slug": summary_row["top_challenger_theme_slug"],
            "top_challenger_symbol": summary_row["top_challenger_symbol"],
            "top_challenger_support_row_count": int(summary_row["top_challenger_support_row_count"]),
            "top_challenger_source_family_count": int(summary_row["top_challenger_source_family_count"]),
            "top_challenger_focus_total_score": float(summary_row["top_challenger_focus_total_score"]),
            "authoritative_output": "a_share_internal_hot_news_challenger_focus_comparison_materialized",
        }
        return MaterializedAShareInternalHotNewsChallengerFocusComparisonV1(
            summary=summary,
            detail_rows=detail_rows,
            summary_rows=[summary_row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsChallengerFocusComparisonV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
