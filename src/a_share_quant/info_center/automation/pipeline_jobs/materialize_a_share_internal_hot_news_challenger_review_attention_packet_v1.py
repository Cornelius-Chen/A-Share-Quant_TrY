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


def _attention_payload(review_state: str) -> tuple[str, str, str]:
    if review_state == "open_next_rotation_review":
        return (
            "open_rotation_review_now",
            "p1",
            "prepare_next_rotation_shadow_and_review",
        )
    if review_state == "keep_incumbent_but_raise_review_attention":
        return (
            "raise_review_attention_hold_incumbent",
            "p2",
            "keep_incumbent_and_monitor_challenger_compounding",
        )
    return (
        "background_monitor_only",
        "p3",
        "hold_incumbent_background_monitor_only",
    )


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsChallengerReviewAttentionPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsChallengerReviewAttentionPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving_base = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.review_path = (
            derived_base / "a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_v1.csv"
        )
        self.output_path = (
            derived_base / "a_share_internal_hot_news_challenger_review_attention_packet_v1.csv"
        )
        self.registry_path = (
            serving_base / "a_share_internal_hot_news_challenger_review_attention_packet_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsChallengerReviewAttentionPacketV1:
        review_row = _read_csv(self.review_path)[0]
        attention_state, attention_priority, attention_instruction = _attention_payload(
            review_row["review_state"]
        )

        row = {
            "challenger_review_attention_packet_id": "internal_hot_news_challenger_review_attention_latest",
            "incumbent_theme_slug": review_row["incumbent_theme_slug"],
            "incumbent_watch_symbol": review_row["incumbent_watch_symbol"],
            "incumbent_support_row_count": review_row["incumbent_support_row_count"],
            "challenger_theme_slug": review_row["challenger_theme_slug"],
            "challenger_watch_symbol": review_row["challenger_watch_symbol"],
            "challenger_support_row_count": review_row["challenger_support_row_count"],
            "challenger_source_family_count": review_row["challenger_source_family_count"],
            "support_delta_vs_incumbent": review_row["support_delta_vs_incumbent"],
            "review_state": review_row["review_state"],
            "review_recommendation": review_row["review_recommendation"],
            "attention_state": attention_state,
            "attention_priority": attention_priority,
            "attention_instruction": attention_instruction,
            "delivery_state": "challenger_review_attention_packet_ready",
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_challenger_review_attention_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "incumbent_theme_slug": row["incumbent_theme_slug"],
            "incumbent_watch_symbol": row["incumbent_watch_symbol"],
            "challenger_theme_slug": row["challenger_theme_slug"],
            "challenger_watch_symbol": row["challenger_watch_symbol"],
            "support_delta_vs_incumbent": int(row["support_delta_vs_incumbent"]),
            "review_state": row["review_state"],
            "attention_state": row["attention_state"],
            "attention_priority": row["attention_priority"],
            "attention_instruction": row["attention_instruction"],
            "authoritative_output": "a_share_internal_hot_news_challenger_review_attention_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsChallengerReviewAttentionPacketV1(
            summary=summary,
            rows=[row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsChallengerReviewAttentionPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
