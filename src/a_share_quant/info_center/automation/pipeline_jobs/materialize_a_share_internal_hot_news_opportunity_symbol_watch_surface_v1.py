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


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _split_symbols(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.opportunity_feed_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_opportunity_feed_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_opportunity_symbol_watch_surface_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_opportunity_symbol_watch_surface_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1:
        opportunity_rows = _read_csv(self.opportunity_feed_path)
        rows: list[dict[str, Any]] = []

        for opportunity_row in opportunity_rows:
            symbols = _split_symbols(opportunity_row.get("beneficiary_symbols_top5", ""))
            for rank, symbol in enumerate(symbols, start=1):
                rows.append(
                    {
                        "telegraph_id": opportunity_row["telegraph_id"],
                        "public_ts": opportunity_row["public_ts"],
                        "program_priority_score": opportunity_row["program_priority_score"],
                        "priority_band": opportunity_row["priority_band"],
                        "target_board": opportunity_row["target_board"],
                        "target_theme_slug": opportunity_row["target_theme_slug"],
                        "primary_theme_slug": opportunity_row.get("primary_theme_slug", opportunity_row["target_theme_slug"]),
                        "secondary_theme_slug": opportunity_row.get("secondary_theme_slug", ""),
                        "theme_governance_state": opportunity_row.get("theme_governance_state", "unknown"),
                        "consumer_action_class": opportunity_row["consumer_action_class"],
                        "consumer_focus_class": opportunity_row["consumer_focus_class"],
                        "board_hit_state": opportunity_row["board_hit_state"],
                        "beneficiary_mapping_confidence": opportunity_row["beneficiary_mapping_confidence"],
                        "beneficiary_linkage_class": opportunity_row.get("beneficiary_linkage_class", "unknown"),
                        "beneficiary_symbol_rank": str(rank),
                        "beneficiary_symbol": symbol,
                        "opportunity_consumer_gate": opportunity_row["opportunity_consumer_gate"],
                        "opportunity_action_bias": opportunity_row["opportunity_action_bias"],
                        "window_state": opportunity_row["window_state"],
                        "trading_day_state": opportunity_row["trading_day_state"],
                        "session_phase": opportunity_row["session_phase"],
                        "session_handling_mode": opportunity_row["session_handling_mode"],
                        "title": opportunity_row["title"],
                        "delivery_state": "opportunity_symbol_watch_ready",
                    }
                )

        rows.sort(
            key=lambda row: (
                -_to_float(row["program_priority_score"]),
                row["beneficiary_symbol_rank"],
                row["telegraph_id"],
            )
        )

        self._write_csv(self.output_path, rows)
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_opportunity_symbol_watch_surface",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "symbol_watch_row_count": len(rows),
            "unique_symbol_count": len({row["beneficiary_symbol"] for row in rows}),
            "opportunity_event_count": len({row["telegraph_id"] for row in rows}),
            "top_symbol": rows[0]["beneficiary_symbol"] if rows else "",
            "top_theme": rows[0]["primary_theme_slug"] if rows else "none",
            "top_mapping_confidence": rows[0]["beneficiary_mapping_confidence"] if rows else "unknown",
            "top_linkage_class": rows[0]["beneficiary_linkage_class"] if rows else "unknown",
            "authoritative_output": "a_share_internal_hot_news_opportunity_symbol_watch_surface_materialized",
        }
        return MaterializedAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsOpportunitySymbolWatchSurfaceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
