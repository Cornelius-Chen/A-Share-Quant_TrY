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
class MaterializedAShareInternalHotNewsChallengerRotationShadowChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsChallengerRotationShadowChangeSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        serving = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.control_packet_path = base / "a_share_internal_hot_news_program_control_packet_v1.csv"
        self.shadow_control_packet_path = base / "a_share_internal_hot_news_challenger_rotation_shadow_control_packet_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_challenger_rotation_shadow_change_signal_v1.csv"
        self.registry_path = serving / "a_share_internal_hot_news_challenger_rotation_shadow_change_signal_registry_v1.csv"

    def materialize(self) -> MaterializedAShareInternalHotNewsChallengerRotationShadowChangeSignalV1:
        control_packet = _read_csv(self.control_packet_path)[0]
        shadow_packet = _read_csv(self.shadow_control_packet_path)[0]

        top_opportunity_theme_change = (
            "would_change"
            if control_packet["top_opportunity_primary_theme_slug"] != shadow_packet["shadow_top_opportunity_theme"]
            else "stable"
        )
        top_watch_symbol_change = (
            "would_change"
            if control_packet["top_watch_symbol"] != shadow_packet["shadow_top_watch_symbol"]
            else "stable"
        )
        signal_priority = "p1" if "would_change" in {top_opportunity_theme_change, top_watch_symbol_change} else "p2"

        row = {
            "challenger_rotation_shadow_change_signal_id": "internal_hot_news_challenger_rotation_shadow_change_signal_latest",
            "current_top_opportunity_theme": control_packet["top_opportunity_primary_theme_slug"],
            "shadow_top_opportunity_theme": shadow_packet["shadow_top_opportunity_theme"],
            "top_opportunity_theme_change": top_opportunity_theme_change,
            "current_top_watch_symbol": control_packet["top_watch_symbol"],
            "shadow_top_watch_symbol": shadow_packet["shadow_top_watch_symbol"],
            "top_watch_symbol_change": top_watch_symbol_change,
            "signal_priority": signal_priority,
            "rotation_change_state": "challenger_shadow_rotation_delta",
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_challenger_rotation_shadow_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "top_opportunity_theme_change": top_opportunity_theme_change,
            "top_watch_symbol_change": top_watch_symbol_change,
            "signal_priority": signal_priority,
            "authoritative_output": "a_share_internal_hot_news_challenger_rotation_shadow_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsChallengerRotationShadowChangeSignalV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsChallengerRotationShadowChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
