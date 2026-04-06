from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_controlled_merge_candidate_consumer_preview_v1 import (
    MaterializeAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsControlledMergeCandidatePromotionGateV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsControlledMergeCandidatePromotionGateV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.output_path = base / "a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_v1.csv"
        self.summary_path = base / "a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_summary_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsControlledMergeCandidatePromotionGateV1:
        preview = MaterializeAShareInternalHotNewsControlledMergeCandidateConsumerPreviewV1(self.repo_root).materialize()
        summary = preview.summary

        top_opportunity_gate = (
            "promotion_rotation_gate_triggered"
            if summary["top_opportunity_change_if_promoted"] == "would_change"
            else "promotion_rotation_gate_clear"
        )
        top_watch_gate = (
            "promotion_rotation_gate_triggered"
            if summary["top_watch_change_if_promoted"] == "would_change"
            else "promotion_rotation_gate_clear"
        )
        promotable_now = top_opportunity_gate == "promotion_rotation_gate_clear" and top_watch_gate == "promotion_rotation_gate_clear"
        gate_rows = [
            {
                "gate_component": "top_opportunity_rotation",
                "current_focus": summary["current_top_opportunity_theme"],
                "candidate_focus": summary["candidate_top_theme"],
                "change_state": summary["top_opportunity_change_if_promoted"],
                "gate_state": top_opportunity_gate,
            },
            {
                "gate_component": "top_watch_rotation",
                "current_focus": summary["current_top_watch_symbol"],
                "candidate_focus": summary["candidate_top_symbol"],
                "change_state": summary["top_watch_change_if_promoted"],
                "gate_state": top_watch_gate,
            },
            {
                "gate_component": "promotion_readiness",
                "current_focus": "current_primary_consumers",
                "candidate_focus": "controlled_merge_candidate_lane",
                "change_state": summary["consumer_stability_state"],
                "gate_state": "promotable_now" if promotable_now else "promotion_hold_explicit_review_required",
            },
        ]

        summary_row = {
            "gate_id": "internal_hot_news_controlled_merge_candidate_promotion_gate_latest",
            "preview_row_count": str(summary["preview_row_count"]),
            "additive_preview_count": str(summary["additive_preview_count"]),
            "top_opportunity_change_if_promoted": summary["top_opportunity_change_if_promoted"],
            "top_watch_change_if_promoted": summary["top_watch_change_if_promoted"],
            "promotable_now": "true" if promotable_now else "false",
            "promotion_gate_state": "promotion_gate_clear" if promotable_now else "promotion_gate_hold",
        }

        _write_csv(self.output_path, gate_rows)
        _write_csv(self.summary_path, [summary_row])

        result_summary = {
            "preview_row_count": summary["preview_row_count"],
            "additive_preview_count": summary["additive_preview_count"],
            "top_opportunity_change_if_promoted": summary["top_opportunity_change_if_promoted"],
            "top_watch_change_if_promoted": summary["top_watch_change_if_promoted"],
            "promotable_now": promotable_now,
            "promotion_gate_state": summary_row["promotion_gate_state"],
            "authoritative_output": "a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_materialized",
        }
        return MaterializedAShareInternalHotNewsControlledMergeCandidatePromotionGateV1(
            summary=result_summary,
            rows=gate_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsControlledMergeCandidatePromotionGateV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
