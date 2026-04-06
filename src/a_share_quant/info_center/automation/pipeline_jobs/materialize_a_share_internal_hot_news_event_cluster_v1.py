from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"【[^】]*】", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return text


def _cluster_stem(title: str) -> str:
    normalized = _normalize_text(title)
    return normalized[:18] if normalized else "empty"


def _cluster_key(fastlane_row: dict[str, str], guidance_row: dict[str, str]) -> str:
    subject = fastlane_row.get("subject_names") or "none"
    event_domain = guidance_row.get("event_domain") or "general_market_news"
    target_theme_slug = guidance_row.get("target_theme_slug") or "broad_market"
    stem = _cluster_stem(fastlane_row.get("title", ""))
    return "|".join([subject, event_domain, target_theme_slug, stem])


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsEventClusterV1:
    summary: dict[str, Any]
    cluster_rows: list[dict[str, Any]]
    deduped_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsEventClusterV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.fastlane_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_fastlane_surface_v1.csv"
        )
        self.guidance_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_trading_guidance_surface_v1.csv"
        )
        self.decision_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_decision_signal_surface_v1.csv"
        )
        self.cluster_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_event_cluster_surface_v1.csv"
        )
        self.deduped_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_deduped_event_stream_v1.csv"
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

    def materialize(self) -> MaterializedAShareInternalHotNewsEventClusterV1:
        fastlane_rows = _read_csv(self.fastlane_path)
        guidance_rows = _read_csv(self.guidance_path)
        decision_rows = _read_csv(self.decision_signal_path)

        fastlane_map = {row["telegraph_id"]: row for row in fastlane_rows}
        guidance_map = {row["telegraph_id"]: row for row in guidance_rows}
        decision_map = {row["telegraph_id"]: row for row in decision_rows}

        grouped: dict[str, list[str]] = {}
        for telegraph_id, fastlane_row in fastlane_map.items():
            guidance_row = guidance_map[telegraph_id]
            key = _cluster_key(fastlane_row, guidance_row)
            grouped.setdefault(key, []).append(telegraph_id)

        cluster_rows: list[dict[str, Any]] = []
        deduped_rows: list[dict[str, Any]] = []

        for index, (cluster_key, telegraph_ids) in enumerate(sorted(grouped.items()), start=1):
            ranked_ids = sorted(
                telegraph_ids,
                key=lambda item: (
                    abs(_to_float(decision_map[item].get("decision_signal_score"))),
                    guidance_map[item]["guidance_priority"],
                    fastlane_map[item]["public_ts"],
                ),
                reverse=True,
            )
            primary_id = ranked_ids[0]
            primary_fastlane = fastlane_map[primary_id]
            primary_guidance = guidance_map[primary_id]
            primary_decision = decision_map[primary_id]
            cluster_id = f"cls_event_cluster_{index:03d}"
            member_scores = [_to_float(decision_map[item].get("decision_signal_score")) for item in ranked_ids]

            cluster_rows.append(
                {
                    "cluster_id": cluster_id,
                    "cluster_key": cluster_key,
                    "cluster_size": str(len(ranked_ids)),
                    "primary_telegraph_id": primary_id,
                    "latest_public_ts": max(fastlane_map[item]["public_ts"] for item in ranked_ids),
                    "event_domain": primary_guidance["event_domain"],
                    "target_board": primary_guidance["target_board"],
                    "target_theme_slug": primary_guidance["target_theme_slug"],
                    "guidance_class": primary_guidance["guidance_class"],
                    "event_direction": primary_guidance["event_direction"],
                    "event_strength": primary_guidance["event_strength"],
                    "guidance_priority": primary_guidance["guidance_priority"],
                    "cluster_abs_signal_max": f"{max(abs(score) for score in member_scores):.4f}",
                    "member_telegraph_ids": "|".join(ranked_ids),
                    "cluster_state": "cluster_materialized",
                    "primary_title": primary_fastlane["title"],
                }
            )

            deduped_rows.append(
                {
                    "cluster_id": cluster_id,
                    "telegraph_id": primary_id,
                    "public_ts": primary_fastlane["public_ts"],
                    "event_domain": primary_guidance["event_domain"],
                    "target_scope": primary_guidance["target_scope"],
                    "target_board": primary_guidance["target_board"],
                    "target_theme_slug": primary_guidance["target_theme_slug"],
                    "guidance_class": primary_guidance["guidance_class"],
                    "event_direction": primary_guidance["event_direction"],
                    "event_strength": primary_guidance["event_strength"],
                    "guidance_priority": primary_guidance["guidance_priority"],
                    "action_bias": primary_guidance["action_bias"],
                    "routing_bucket": primary_guidance["routing_bucket"],
                    "decision_signal_score": primary_decision["decision_signal_score"],
                    "cluster_size": str(len(ranked_ids)),
                    "delivery_state": "deduped_event_stream_ready",
                    "title": primary_fastlane["title"],
                }
            )

        self._write_csv(self.cluster_path, cluster_rows)
        self._write_csv(self.deduped_path, deduped_rows)

        summary = {
            "fastlane_row_count": len(fastlane_rows),
            "cluster_row_count": len(cluster_rows),
            "deduped_row_count": len(deduped_rows),
            "duplicate_reduction_count": len(fastlane_rows) - len(deduped_rows),
            "authoritative_output": "a_share_internal_hot_news_event_cluster_and_deduped_stream_materialized",
        }
        return MaterializedAShareInternalHotNewsEventClusterV1(
            summary=summary,
            cluster_rows=cluster_rows,
            deduped_rows=deduped_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsEventClusterV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
