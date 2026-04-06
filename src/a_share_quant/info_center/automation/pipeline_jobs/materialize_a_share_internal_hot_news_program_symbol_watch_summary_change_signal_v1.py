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


def _state_change(current: str, previous: str | None) -> str:
    if previous is None:
        return "no_previous_baseline"
    if current != previous:
        return "state_changed"
    return "stable"


def _signal_priority(states: list[str]) -> str:
    if "state_changed" in states:
        return "p1"
    return "p2"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.summary_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watch_summary_v1.csv"
        )
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_symbol_watch_summary_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watch_summary_change_signal_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_symbol_watch_summary_change_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1:
        current = _read_csv(self.summary_path)[0]
        history_rows = _read_csv(self.history_path)
        previous = history_rows[0] if history_rows else None

        top_watch_symbol_change = _state_change(
            current["top_watch_symbol"],
            previous.get("top_watch_symbol") if previous else None,
        )
        top_watch_bundle_change = _state_change(
            current["top_watch_symbols_top5"],
            previous.get("top_watch_symbols_top5") if previous else None,
        )
        top_watch_theme_change = _state_change(
            current["top_watch_primary_theme_slug"],
            previous.get("top_watch_primary_theme_slug") if previous else None,
        )

        row = {
            "change_signal_id": "internal_hot_news_program_symbol_watch_summary_change_latest",
            "top_watch_symbol_change": top_watch_symbol_change,
            "top_watch_symbol_current": current["top_watch_symbol"],
            "top_watch_bundle_change": top_watch_bundle_change,
            "top_watch_symbols_top5_current": current["top_watch_symbols_top5"],
            "top_watch_theme_change": top_watch_theme_change,
            "top_watch_primary_theme_slug_current": current["top_watch_primary_theme_slug"],
            "signal_priority": _signal_priority(
                [top_watch_symbol_change, top_watch_bundle_change, top_watch_theme_change]
            ),
            "watch_summary_state": current["watch_summary_state"],
            "delivery_state": "symbol_watch_summary_change_signal_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_symbol_watch_summary_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "change_row_count": 1,
            "top_watch_symbol_change": top_watch_symbol_change,
            "top_watch_bundle_change": top_watch_bundle_change,
            "top_watch_theme_change": top_watch_theme_change,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_symbol_watch_summary_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramSymbolWatchSummaryChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
