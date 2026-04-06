from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _importance_tier(row: dict[str, str], score: float) -> str:
    if row["guidance_class"] == "guidance_event" and row["guidance_priority"] == "p0":
        return "tier_1_market_guidance"
    if row["guidance_class"] == "risk_event" and abs(score) >= 1.0:
        return "tier_1_risk_shock"
    if row["guidance_class"] in {"trigger_event", "watch_only_guidance"} and row["target_theme_slug"] != "broad_market":
        return "tier_2_board_signal"
    return "tier_3_watch_only"


def _promotion_reason(row: dict[str, str], score: float) -> str:
    if row["guidance_class"] == "guidance_event":
        return "top_down_guidance"
    if row["guidance_class"] == "risk_event" and abs(score) >= 1.0:
        return "market_risk_shock"
    if row["target_theme_slug"] != "broad_market":
        return "board_specific_signal"
    return "watchlist_candidate"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsImportantPromotionV1:
    summary: dict[str, Any]
    promotion_rows: list[dict[str, Any]]
    queue_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsImportantPromotionV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.deduped_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_deduped_event_stream_v1.csv"
        )
        self.guidance_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_guidance_surface_v1.csv"
        )
        self.promotion_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "event_registry"
            / "a_share_internal_hot_news_important_promotion_registry_v1.csv"
        )
        self.queue_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_important_trading_queue_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        fieldnames = list(materialized_rows[0].keys())
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsImportantPromotionV1:
        deduped_rows = _read_csv(self.deduped_path)
        guidance_rows = _read_csv(self.guidance_path)
        guidance_map = {row["telegraph_id"]: row for row in guidance_rows}

        promotion_rows: list[dict[str, Any]] = []
        queue_rows: list[dict[str, Any]] = []

        for row in deduped_rows:
            score = _to_float(row["decision_signal_score"])
            tier = _importance_tier(row, score)
            reason = _promotion_reason(row, score)
            guidance_row = guidance_map[row["telegraph_id"]]

            if tier == "tier_3_watch_only":
                continue

            promotion_rows.append(
                {
                    "important_event_id": f"cls_refined_{row['telegraph_id']}",
                    "cluster_id": row["cluster_id"],
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "guidance_class": row["guidance_class"],
                    "event_direction": row["event_direction"],
                    "event_strength": row["event_strength"],
                    "guidance_priority": row["guidance_priority"],
                    "decision_signal_score": row["decision_signal_score"],
                    "importance_tier": tier,
                    "promotion_reason": reason,
                    "title": row["title"],
                }
            )

            queue_rows.append(
                {
                    "important_event_id": f"cls_refined_{row['telegraph_id']}",
                    "cluster_id": row["cluster_id"],
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "routing_bucket": guidance_row["routing_bucket"],
                    "target_scope": row["target_scope"],
                    "target_board": row["target_board"],
                    "target_theme_slug": row["target_theme_slug"],
                    "importance_tier": tier,
                    "decision_signal_score": row["decision_signal_score"],
                    "action_bias": row["action_bias"],
                    "delivery_state": "important_trading_queue_ready",
                    "title": row["title"],
                }
            )

        self._write_csv(self.promotion_path, promotion_rows)
        self._write_csv(self.queue_path, queue_rows)

        summary = {
            "deduped_row_count": len(deduped_rows),
            "important_promotion_row_count": len(promotion_rows),
            "important_queue_row_count": len(queue_rows),
            "tier_1_count": sum(row["importance_tier"].startswith("tier_1") for row in promotion_rows),
            "tier_2_count": sum(row["importance_tier"] == "tier_2_board_signal" for row in promotion_rows),
            "authoritative_output": "a_share_internal_hot_news_important_promotion_registry_materialized",
        }
        return MaterializedAShareInternalHotNewsImportantPromotionV1(
            summary=summary,
            promotion_rows=promotion_rows,
            queue_rows=queue_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsImportantPromotionV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
