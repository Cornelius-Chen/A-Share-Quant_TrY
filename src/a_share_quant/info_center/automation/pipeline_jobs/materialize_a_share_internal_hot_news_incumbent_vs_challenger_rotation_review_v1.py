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
class MaterializedAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.primary_focus_summary_path = (
            derived_base / "a_share_internal_hot_news_primary_focus_replay_tracker_summary_v1.csv"
        )
        self.leaderboard_summary_path = (
            derived_base / "a_share_internal_hot_news_focus_competition_leaderboard_summary_v1.csv"
        )
        self.challenger_summary_path = (
            derived_base / "a_share_internal_hot_news_challenger_focus_comparison_summary_v1.csv"
        )
        self.output_path = (
            derived_base / "a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1:
        incumbent_row = _read_csv(self.primary_focus_summary_path)[0]
        leaderboard_row = _read_csv(self.leaderboard_summary_path)[0]
        challenger_row = _read_csv(self.challenger_summary_path)[0]

        incumbent_support = int(incumbent_row["focus_match_row_count"])
        incumbent_dual_match = int(incumbent_row["dual_match_count"])
        incumbent_focus_score = float(leaderboard_row["current_primary_focus_total_score"])
        challenger_support = int(challenger_row["top_challenger_support_row_count"])
        challenger_focus_score = float(challenger_row["top_challenger_focus_total_score"])
        support_delta = challenger_support - incumbent_support
        focus_score_delta = round(challenger_focus_score - incumbent_focus_score, 4)
        focus_score_ratio = (
            round(challenger_focus_score / incumbent_focus_score, 4) if incumbent_focus_score > 0 else 0.0
        )

        if focus_score_delta >= 1.25 or focus_score_ratio >= 1.35:
            review_state = "open_next_rotation_review"
            recommendation = "challenger_focus_score_materially_exceeds_incumbent"
        elif focus_score_delta >= 0.35 or focus_score_ratio >= 1.10 or challenger_support > incumbent_support:
            review_state = "keep_incumbent_but_raise_review_attention"
            recommendation = "challenger_focus_score_exceeds_incumbent_but_not_by_open_threshold"
        else:
            review_state = "hold_incumbent_focus"
            recommendation = "incumbent_focus_score_not_weaker_than_challenger_threshold"

        row = {
            "review_id": "internal_hot_news_incumbent_vs_challenger_rotation_review_latest",
            "incumbent_theme_slug": incumbent_row["current_primary_theme_slug"],
            "incumbent_watch_symbol": incumbent_row["current_primary_watch_symbol"],
            "incumbent_support_row_count": incumbent_row["focus_match_row_count"],
            "incumbent_dual_match_count": incumbent_row["dual_match_count"],
            "incumbent_focus_total_score": f"{incumbent_focus_score:.4f}",
            "challenger_theme_slug": challenger_row["top_challenger_theme_slug"],
            "challenger_watch_symbol": challenger_row["top_challenger_symbol"],
            "challenger_support_row_count": challenger_row["top_challenger_support_row_count"],
            "challenger_source_family_count": challenger_row["top_challenger_source_family_count"],
            "challenger_focus_total_score": f"{challenger_focus_score:.4f}",
            "support_delta_vs_incumbent": str(support_delta),
            "focus_score_delta_vs_incumbent": f"{focus_score_delta:.4f}",
            "focus_score_ratio_vs_incumbent": f"{focus_score_ratio:.4f}",
            "review_state": review_state,
            "review_recommendation": recommendation,
            "review_delivery_state": "incumbent_vs_challenger_rotation_review_ready",
        }

        _write_csv(self.output_path, [row])

        summary = {
            "incumbent_theme_slug": row["incumbent_theme_slug"],
            "incumbent_watch_symbol": row["incumbent_watch_symbol"],
            "incumbent_support_row_count": incumbent_support,
            "incumbent_dual_match_count": incumbent_dual_match,
            "incumbent_focus_total_score": incumbent_focus_score,
            "challenger_theme_slug": row["challenger_theme_slug"],
            "challenger_watch_symbol": row["challenger_watch_symbol"],
            "challenger_support_row_count": challenger_support,
            "challenger_source_family_count": int(row["challenger_source_family_count"]),
            "challenger_focus_total_score": challenger_focus_score,
            "support_delta_vs_incumbent": support_delta,
            "focus_score_delta_vs_incumbent": focus_score_delta,
            "focus_score_ratio_vs_incumbent": focus_score_ratio,
            "review_state": review_state,
            "review_recommendation": recommendation,
            "authoritative_output": "a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_materialized",
        }
        return MaterializedAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsIncumbentVsChallengerRotationReviewV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
