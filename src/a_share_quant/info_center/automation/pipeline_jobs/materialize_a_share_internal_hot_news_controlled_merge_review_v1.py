from __future__ import annotations

import csv
import re
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


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return text


def _title_stem(text: str) -> str:
    normalized = _normalize_text(text)
    return normalized[:18] if normalized else "empty"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsControlledMergeReviewV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsControlledMergeReviewV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.cls_path = base / "a_share_internal_hot_news_theme_symbol_hit_replay_surface_v1.csv"
        self.sina_path = base / "a_share_internal_hot_news_sina_theme_probe_surface_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_controlled_merge_review_surface_v1.csv"
        self.summary_path = base / "a_share_internal_hot_news_controlled_merge_review_summary_v1.csv"

    @staticmethod
    def _to_merge_rows(rows: list[dict[str, str]], *, source_family: str) -> list[dict[str, str]]:
        merge_rows: list[dict[str, str]] = []
        for row in rows:
            if source_family == "cls":
                merge_rows.append(
                    {
                        "source_family": "cls",
                        "source_row_id": row["telegraph_id"],
                        "public_ts": row["public_ts"],
                        "title": row["title"],
                        "primary_theme_slug": row["primary_theme_slug"],
                        "top_symbol": row["top_watch_symbol"],
                        "route_state": row["replay_hit_state"],
                    }
                )
            else:
                merge_rows.append(
                    {
                        "source_family": "sina",
                        "source_row_id": row["telegraph_id"],
                        "public_ts": row["public_ts"],
                        "title": row["title"],
                        "primary_theme_slug": row["primary_theme_slug"],
                        "top_symbol": row["top_symbol"],
                        "route_state": row["probe_state"],
                    }
                )
        return merge_rows

    def materialize(self) -> MaterializedAShareInternalHotNewsControlledMergeReviewV1:
        cls_rows = self._to_merge_rows(_read_csv(self.cls_path), source_family="cls")
        sina_rows = self._to_merge_rows(_read_csv(self.sina_path), source_family="sina")
        all_rows = cls_rows + sina_rows

        grouped: dict[str, list[dict[str, str]]] = {}
        for row in all_rows:
            key = "|".join([row["primary_theme_slug"], _title_stem(row["title"])])
            grouped.setdefault(key, []).append(row)

        review_rows: list[dict[str, Any]] = []
        cross_source_duplicate_candidate_count = 0
        additive_sina_candidate_count = 0

        for merge_cluster_key, members in sorted(grouped.items()):
            source_families = {row["source_family"] for row in members}
            cross_source_state = (
                "cross_source_duplicate_candidate" if len(source_families) > 1 else "single_source_cluster"
            )
            if cross_source_state == "cross_source_duplicate_candidate":
                cross_source_duplicate_candidate_count += 1

            ranked = sorted(
                members,
                key=lambda row: (
                    1 if row["source_family"] == "cls" else 0,
                    1 if row["route_state"] in {"theme_hit_with_symbol_watch", "theme_hit_with_symbol_route"} else 0,
                    1 if row["primary_theme_slug"] != "broad_market" else 0,
                    row["public_ts"],
                ),
                reverse=True,
            )
            primary = ranked[0]

            for row in ranked:
                merge_recommendation = "retain_as_primary_candidate" if row == primary else "hold_as_secondary_candidate"
                if (
                    row["source_family"] == "sina"
                    and cross_source_state == "single_source_cluster"
                    and row["primary_theme_slug"] != "broad_market"
                    and row["route_state"] == "theme_hit_with_symbol_route"
                ):
                    merge_recommendation = "additive_second_source_candidate"
                    additive_sina_candidate_count += 1

                review_rows.append(
                    {
                        "merge_cluster_key": merge_cluster_key,
                        "merge_cluster_size": str(len(ranked)),
                        "cross_source_state": cross_source_state,
                        "source_family": row["source_family"],
                        "source_row_id": row["source_row_id"],
                        "public_ts": row["public_ts"],
                        "primary_theme_slug": row["primary_theme_slug"],
                        "top_symbol": row["top_symbol"],
                        "route_state": row["route_state"],
                        "merge_recommendation": merge_recommendation,
                        "title": row["title"],
                        "review_state": "controlled_merge_review_ready",
                    }
                )

        summary_row = {
            "review_id": "internal_hot_news_controlled_merge_review_latest",
            "cls_row_count": str(len(cls_rows)),
            "sina_row_count": str(len(sina_rows)),
            "combined_row_count": str(len(all_rows)),
            "merge_cluster_count": str(len(grouped)),
            "cross_source_duplicate_candidate_count": str(cross_source_duplicate_candidate_count),
            "additive_sina_candidate_count": str(additive_sina_candidate_count),
            "review_summary_state": "controlled_merge_review_summarized",
        }

        _write_csv(self.output_path, review_rows)
        _write_csv(self.summary_path, [summary_row])

        summary = {
            "cls_row_count": len(cls_rows),
            "sina_row_count": len(sina_rows),
            "combined_row_count": len(all_rows),
            "merge_cluster_count": len(grouped),
            "cross_source_duplicate_candidate_count": cross_source_duplicate_candidate_count,
            "additive_sina_candidate_count": additive_sina_candidate_count,
            "authoritative_output": "a_share_internal_hot_news_controlled_merge_review_materialized",
        }
        return MaterializedAShareInternalHotNewsControlledMergeReviewV1(summary=summary, rows=review_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsControlledMergeReviewV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
