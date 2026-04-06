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


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsProgramControlPacketV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramControlPacketV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.status_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_status_surface_v1.csv"
        )
        self.snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_snapshot_v1.csv"
        )
        self.driver_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_driver_escalation_signal_feed_v1.csv"
        )
        self.symbol_watch_change_signal_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_symbol_watch_summary_change_signal_v1.csv"
        )
        self.primary_focus_replay_tracker_summary_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_primary_focus_replay_tracker_summary_v1.csv"
        )
        self.challenger_focus_comparison_summary_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_challenger_focus_comparison_summary_v1.csv"
        )
        self.focus_competition_leaderboard_summary_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_focus_competition_leaderboard_summary_v1.csv"
        )
        self.focus_governance_tension_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_focus_governance_tension_packet_v1.csv"
        )
        self.focus_rotation_readiness_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_focus_rotation_readiness_packet_v1.csv"
        )
        self.challenger_review_attention_packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_challenger_review_attention_packet_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_control_packet_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramControlPacketV1:
        status_row = _read_csv(self.status_path)[0]
        snapshot_row = _read_csv(self.snapshot_path)[0]
        driver_signal_row = _read_csv(self.driver_signal_path)[0]
        symbol_watch_change_row = _read_csv(self.symbol_watch_change_signal_path)[0]
        primary_focus_replay_row = _read_csv(self.primary_focus_replay_tracker_summary_path)[0]
        challenger_focus_row = _read_csv(self.challenger_focus_comparison_summary_path)[0]
        focus_competition_row = _read_csv(self.focus_competition_leaderboard_summary_path)[0]
        focus_governance_tension_row = _read_csv(self.focus_governance_tension_packet_path)[0]
        focus_rotation_readiness_row = _read_csv(self.focus_rotation_readiness_packet_path)[0]
        challenger_review_attention_row = _read_csv(self.challenger_review_attention_packet_path)[0]

        row = {
            "program_control_packet_id": "internal_hot_news_program_control_packet_latest",
            "program_health_state": status_row["program_health_state"],
            "program_mode": status_row["program_mode"],
            "global_program_action_mode": status_row["global_program_action_mode"],
            "program_consumer_gate_mode": status_row["program_consumer_gate_mode"],
            "program_driver_action_mode": status_row["program_driver_action_mode"],
            "program_driver_signal_mode": driver_signal_row["signal_feed_mode"],
            "interrupt_required": driver_signal_row["interrupt_required"],
            "driver_consumer_instruction": driver_signal_row["consumer_instruction"],
            "change_signal_priority": status_row["change_signal_priority"],
            "needs_attention": status_row["needs_attention"],
            "freshness_state": status_row["freshness_state"],
            "heartbeat_timeout_state": status_row["heartbeat_timeout_state"],
            "stale_alert_level": status_row["stale_alert_level"],
            "force_refresh": status_row["force_refresh"],
            "trading_day_state": status_row["trading_day_state"],
            "session_phase": status_row["session_phase"],
            "session_handling_mode": status_row["session_handling_mode"],
            "top_risk_telegraph_id": snapshot_row["top_risk_telegraph_id"],
            "top_risk_score": snapshot_row["top_risk_score"],
            "top_risk_theme": snapshot_row["top_risk_theme"],
            "top_opportunity_telegraph_id": snapshot_row["top_opportunity_telegraph_id"],
            "top_opportunity_score": snapshot_row["top_opportunity_score"],
            "top_opportunity_theme": snapshot_row["top_opportunity_theme"],
            "top_opportunity_primary_theme_slug": snapshot_row["top_opportunity_primary_theme_slug"],
            "top_opportunity_secondary_theme_slug": snapshot_row["top_opportunity_secondary_theme_slug"],
            "top_opportunity_theme_governance_state": snapshot_row["top_opportunity_theme_governance_state"],
            "top_opportunity_focus_class": snapshot_row["top_opportunity_focus_class"],
            "top_opportunity_board_hit_state": snapshot_row["top_opportunity_board_hit_state"],
            "top_opportunity_mapping_confidence": snapshot_row["top_opportunity_mapping_confidence"],
            "top_opportunity_linkage_class": snapshot_row["top_opportunity_linkage_class"],
            "top_opportunity_beneficiary_symbols_top5": snapshot_row["top_opportunity_beneficiary_symbols_top5"],
            "top_watch_symbol": snapshot_row["top_watch_symbol"],
            "top_watch_primary_theme_slug": snapshot_row["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": snapshot_row["top_watch_mapping_confidence"],
            "top_watch_linkage_class": snapshot_row["top_watch_linkage_class"],
            "top_watch_symbols_top5": snapshot_row["top_watch_symbols_top5"],
            "top_watch_symbol_change": symbol_watch_change_row["top_watch_symbol_change"],
            "top_watch_bundle_change": symbol_watch_change_row["top_watch_bundle_change"],
            "top_watch_theme_change": symbol_watch_change_row["top_watch_theme_change"],
            "symbol_watch_change_signal_priority": symbol_watch_change_row["signal_priority"],
            "primary_focus_match_row_count": primary_focus_replay_row["focus_match_row_count"],
            "primary_focus_source_present_count": primary_focus_replay_row["focus_source_present_count"],
            "primary_focus_dual_match_count": primary_focus_replay_row["dual_match_count"],
            "primary_focus_source_family_count": primary_focus_replay_row["unique_source_family_count"],
            "focus_leader_theme_slug": focus_competition_row["leader_theme_slug"],
            "focus_leader_symbol": focus_competition_row["leader_watch_symbol"],
            "focus_leader_support_row_count": focus_competition_row["leader_support_row_count"],
            "current_primary_rank": focus_competition_row["current_primary_rank"],
            "incumbent_is_focus_leader": focus_competition_row["incumbent_is_leader"],
            "focus_governance_tension_state": focus_governance_tension_row["tension_state"],
            "focus_governance_tension_priority": focus_governance_tension_row["tension_priority"],
            "focus_governance_tension_instruction": focus_governance_tension_row["tension_instruction"],
            "focus_rotation_readiness_state": focus_rotation_readiness_row["rotation_readiness_state"],
            "focus_rotation_readiness_priority": focus_rotation_readiness_row["rotation_readiness_priority"],
            "focus_rotation_readiness_instruction": focus_rotation_readiness_row["rotation_readiness_instruction"],
            "top_challenger_theme_slug": challenger_focus_row["top_challenger_theme_slug"],
            "top_challenger_symbol": challenger_focus_row["top_challenger_symbol"],
            "top_challenger_support_row_count": challenger_focus_row["top_challenger_support_row_count"],
            "top_challenger_source_family_count": challenger_focus_row["top_challenger_source_family_count"],
            "challenger_review_state": challenger_review_attention_row["review_state"],
            "challenger_review_attention_state": challenger_review_attention_row["attention_state"],
            "challenger_review_attention_priority": challenger_review_attention_row["attention_priority"],
            "challenger_review_instruction": challenger_review_attention_row["attention_instruction"],
            "snapshot_consumer_gate_mode": snapshot_row["snapshot_consumer_gate_mode"],
            "risk_consumer_gate": snapshot_row["risk_consumer_gate"],
            "opportunity_consumer_gate": snapshot_row["opportunity_consumer_gate"],
            "delivery_state": "program_control_packet_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_control_packet",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "packet_row_count": 1,
            "program_health_state": row["program_health_state"],
            "program_driver_signal_mode": row["program_driver_signal_mode"],
            "interrupt_required": row["interrupt_required"],
            "change_signal_priority": row["change_signal_priority"],
            "trading_day_state": row["trading_day_state"],
            "session_phase": row["session_phase"],
            "top_risk_telegraph_id": row["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id": row["top_opportunity_telegraph_id"],
            "top_opportunity_primary_theme_slug": row["top_opportunity_primary_theme_slug"],
            "top_opportunity_theme_governance_state": row["top_opportunity_theme_governance_state"],
            "top_opportunity_focus_class": row["top_opportunity_focus_class"],
            "top_opportunity_mapping_confidence": row["top_opportunity_mapping_confidence"],
            "top_opportunity_linkage_class": row["top_opportunity_linkage_class"],
            "top_opportunity_beneficiary_symbols_top5": row["top_opportunity_beneficiary_symbols_top5"],
            "top_watch_symbol": row["top_watch_symbol"],
            "top_watch_primary_theme_slug": row["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": row["top_watch_mapping_confidence"],
            "top_watch_linkage_class": row["top_watch_linkage_class"],
            "top_watch_symbols_top5": row["top_watch_symbols_top5"],
            "top_watch_symbol_change": row["top_watch_symbol_change"],
            "top_watch_bundle_change": row["top_watch_bundle_change"],
            "top_watch_theme_change": row["top_watch_theme_change"],
            "symbol_watch_change_signal_priority": row["symbol_watch_change_signal_priority"],
            "primary_focus_match_row_count": row["primary_focus_match_row_count"],
            "primary_focus_source_present_count": row["primary_focus_source_present_count"],
            "primary_focus_dual_match_count": row["primary_focus_dual_match_count"],
            "primary_focus_source_family_count": row["primary_focus_source_family_count"],
            "focus_leader_theme_slug": row["focus_leader_theme_slug"],
            "focus_leader_symbol": row["focus_leader_symbol"],
            "focus_leader_support_row_count": row["focus_leader_support_row_count"],
            "current_primary_rank": row["current_primary_rank"],
            "incumbent_is_focus_leader": row["incumbent_is_focus_leader"],
            "focus_governance_tension_state": row["focus_governance_tension_state"],
            "focus_governance_tension_priority": row["focus_governance_tension_priority"],
            "focus_governance_tension_instruction": row["focus_governance_tension_instruction"],
            "focus_rotation_readiness_state": row["focus_rotation_readiness_state"],
            "focus_rotation_readiness_priority": row["focus_rotation_readiness_priority"],
            "focus_rotation_readiness_instruction": row["focus_rotation_readiness_instruction"],
            "top_challenger_theme_slug": row["top_challenger_theme_slug"],
            "top_challenger_symbol": row["top_challenger_symbol"],
            "top_challenger_support_row_count": row["top_challenger_support_row_count"],
            "top_challenger_source_family_count": row["top_challenger_source_family_count"],
            "challenger_review_state": row["challenger_review_state"],
            "challenger_review_attention_state": row["challenger_review_attention_state"],
            "challenger_review_attention_priority": row["challenger_review_attention_priority"],
            "challenger_review_instruction": row["challenger_review_instruction"],
            "authoritative_output": "a_share_internal_hot_news_program_control_packet_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramControlPacketV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramControlPacketV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
