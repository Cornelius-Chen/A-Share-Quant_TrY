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


def _join_top(rows: list[dict[str, str]], key: str, limit: int = 5) -> str:
    values = [row.get(key, "").strip() for row in rows[:limit]]
    return ",".join([value for value in values if value])


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSymbolWatchSummaryV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.watchlist_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watchlist_packet_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watch_summary_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_symbol_watch_summary_registry_v1.csv"
        )
        self.rotation_acceptance_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSymbolWatchSummaryV1:
        watch_rows = _read_csv(self.watchlist_packet_path)
        top_rows = watch_rows[:5]
        acceptance_rows = _read_csv(self.rotation_acceptance_path)
        acceptance = acceptance_rows[0] if acceptance_rows else None

        row = {
            "summary_id": "internal_hot_news_program_symbol_watch_summary_latest",
            "watchlist_row_count": str(len(watch_rows)),
            "top_watch_symbol": top_rows[0]["beneficiary_symbol"] if top_rows else "",
            "top_watch_primary_theme_slug": top_rows[0]["primary_theme_slug"] if top_rows else "none",
            "top_watch_mapping_confidence": top_rows[0]["beneficiary_mapping_confidence"] if top_rows else "unknown",
            "top_watch_linkage_class": top_rows[0]["beneficiary_linkage_class"] if top_rows else "unknown",
            "top_watch_symbols_top5": _join_top(top_rows, "beneficiary_symbol"),
            "top_watch_primary_themes_top5": _join_top(top_rows, "primary_theme_slug"),
            "watch_summary_state": "symbol_watch_summary_ready",
        }
        if acceptance and acceptance.get("acceptance_state") == "accepted":
            accepted_symbol = acceptance["accepted_top_watch_symbol"]
            accepted_theme = acceptance["accepted_top_opportunity_theme"]
            existing_symbols = [value for value in row["top_watch_symbols_top5"].split(",") if value]
            merged_symbols = [accepted_symbol] + [value for value in existing_symbols if value != accepted_symbol]
            row["top_watch_symbol"] = accepted_symbol
            row["top_watch_primary_theme_slug"] = accepted_theme
            row["top_watch_mapping_confidence"] = "medium"
            row["top_watch_linkage_class"] = "direct_beneficiary"
            row["top_watch_symbols_top5"] = ",".join(merged_symbols[:5])
            existing_themes = [value for value in row["top_watch_primary_themes_top5"].split(",") if value]
            merged_themes = [accepted_theme] + [value for value in existing_themes if value != accepted_theme]
            row["top_watch_primary_themes_top5"] = ",".join(merged_themes[:5])
            row["watch_summary_state"] = "symbol_watch_summary_ready_after_rotation_acceptance"

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_symbol_watch_summary",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "summary_row_count": 1,
            "watchlist_row_count": len(watch_rows),
            "top_watch_symbol": row["top_watch_symbol"],
            "top_watch_primary_theme_slug": row["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": row["top_watch_mapping_confidence"],
            "top_watch_linkage_class": row["top_watch_linkage_class"],
            "top_watch_symbols_top5": row["top_watch_symbols_top5"],
            "authoritative_output": "a_share_internal_hot_news_program_symbol_watch_summary_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSymbolWatchSummaryV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
