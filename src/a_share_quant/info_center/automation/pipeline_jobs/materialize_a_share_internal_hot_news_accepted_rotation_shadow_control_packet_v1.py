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
class MaterializedAShareInternalHotNewsAcceptedRotationShadowControlPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsAcceptedRotationShadowControlPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        self.control_packet_path = base / "a_share_internal_hot_news_program_control_packet_v1.csv"
        self.shadow_snapshot_path = base / "a_share_internal_hot_news_accepted_rotation_shadow_snapshot_v1.csv"
        self.output_path = base / "a_share_internal_hot_news_accepted_rotation_shadow_control_packet_v1.csv"
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_accepted_rotation_shadow_control_packet_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsAcceptedRotationShadowControlPacketV1:
        control_packet = _read_csv(self.control_packet_path)[0]
        shadow_snapshot = _read_csv(self.shadow_snapshot_path)[0]

        row = {
            "accepted_rotation_shadow_control_packet_id": "internal_hot_news_accepted_rotation_shadow_control_packet_latest",
            "program_health_state": control_packet["program_health_state"],
            "program_driver_signal_mode": control_packet["program_driver_signal_mode"],
            "interrupt_required": control_packet["interrupt_required"],
            "trading_day_state": control_packet["trading_day_state"],
            "session_phase": control_packet["session_phase"],
            "current_top_opportunity_theme": shadow_snapshot["current_top_opportunity_theme"],
            "current_top_watch_symbol": shadow_snapshot["current_top_watch_symbol"],
            "shadow_top_opportunity_theme": shadow_snapshot["shadow_top_opportunity_theme"],
            "shadow_top_watch_symbol": shadow_snapshot["shadow_top_watch_symbol"],
            "shadow_source_family": shadow_snapshot["shadow_source_family"],
            "shadow_source_row_id": shadow_snapshot["shadow_source_row_id"],
            "shadow_rotation_state": shadow_snapshot["shadow_rotation_state"],
            "shadow_control_mode": "accepted_rotation_shadow_control_only",
            "shadow_control_state": "accepted_rotation_shadow_control_packet_ready",
        }

        _write_csv(self.output_path, [row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_accepted_rotation_shadow_control_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "program_health_state": row["program_health_state"],
            "current_top_opportunity_theme": row["current_top_opportunity_theme"],
            "shadow_top_opportunity_theme": row["shadow_top_opportunity_theme"],
            "current_top_watch_symbol": row["current_top_watch_symbol"],
            "shadow_top_watch_symbol": row["shadow_top_watch_symbol"],
            "shadow_rotation_state": row["shadow_rotation_state"],
            "authoritative_output": "a_share_internal_hot_news_accepted_rotation_shadow_control_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsAcceptedRotationShadowControlPacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsAcceptedRotationShadowControlPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
