from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_review_v1 import (
    MaterializeAShareInternalHotNewsControlledMergeReviewV1,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsControlledMergeCandidateSurfaceV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsControlledMergeCandidateSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.output_path = base / "a_share_internal_hot_news_controlled_merge_candidate_surface_v1.csv"
        self.summary_path = base / "a_share_internal_hot_news_controlled_merge_candidate_summary_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsControlledMergeCandidateSurfaceV1:
        review = MaterializeAShareInternalHotNewsControlledMergeReviewV1(self.repo_root).materialize()
        candidate_rows: list[dict[str, Any]] = []

        for row in review.rows:
            recommendation = row["merge_recommendation"]
            keep_cls_primary = recommendation == "retain_as_primary_candidate" and row["source_family"] == "cls"
            keep_sina_additive = recommendation == "additive_second_source_candidate"
            if not (keep_cls_primary or keep_sina_additive):
                continue

            candidate_role = (
                "primary_fastlane_anchor" if keep_cls_primary else "additive_second_source_theme_symbol_candidate"
            )

            candidate_rows.append(
                {
                    "merge_cluster_key": row["merge_cluster_key"],
                    "source_family": row["source_family"],
                    "source_row_id": row["source_row_id"],
                    "public_ts": row["public_ts"],
                    "primary_theme_slug": row["primary_theme_slug"],
                    "top_symbol": row["top_symbol"],
                    "route_state": row["route_state"],
                    "candidate_role": candidate_role,
                    "candidate_state": "controlled_merge_candidate_only",
                    "merge_recommendation": recommendation,
                    "title": row["title"],
                }
            )

        cls_primary_count = sum(1 for row in candidate_rows if row["source_family"] == "cls")
        sina_additive_count = sum(
            1
            for row in candidate_rows
            if row["source_family"] == "sina"
            and row["candidate_role"] == "additive_second_source_theme_symbol_candidate"
        )
        unique_theme_count = len(
            {row["primary_theme_slug"] for row in candidate_rows if row["primary_theme_slug"] != "broad_market"}
        )
        unique_symbol_count = len({row["top_symbol"] for row in candidate_rows if row["top_symbol"]})

        summary_row = {
            "candidate_id": "internal_hot_news_controlled_merge_candidate_latest",
            "candidate_row_count": str(len(candidate_rows)),
            "cls_primary_count": str(cls_primary_count),
            "sina_additive_count": str(sina_additive_count),
            "unique_theme_count": str(unique_theme_count),
            "unique_symbol_count": str(unique_symbol_count),
            "candidate_summary_state": "controlled_merge_candidate_summarized",
        }

        _write_csv(self.output_path, candidate_rows)
        _write_csv(self.summary_path, [summary_row])

        summary = {
            "candidate_row_count": len(candidate_rows),
            "cls_primary_count": cls_primary_count,
            "sina_additive_count": sina_additive_count,
            "unique_theme_count": unique_theme_count,
            "unique_symbol_count": unique_symbol_count,
            "authoritative_output": "a_share_internal_hot_news_controlled_merge_candidate_surface_materialized",
        }
        return MaterializedAShareInternalHotNewsControlledMergeCandidateSurfaceV1(
            summary=summary,
            rows=candidate_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsControlledMergeCandidateSurfaceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
