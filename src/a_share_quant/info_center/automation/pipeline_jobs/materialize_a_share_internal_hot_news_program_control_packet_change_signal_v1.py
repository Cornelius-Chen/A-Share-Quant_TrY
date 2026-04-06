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
class MaterializedAShareInternalHotNewsProgramControlPacketChangeSignalV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsProgramControlPacketChangeSignalV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.packet_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_v1.csv"
        )
        self.history_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_control_packet_history_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_program_control_packet_change_signal_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_program_control_packet_change_signal_registry_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareInternalHotNewsProgramControlPacketChangeSignalV1:
        current = _read_csv(self.packet_path)[0]
        previous_rows = _read_csv(self.history_path)
        previous = previous_rows[0] if previous_rows else None

        program_health_state_change = _state_change(
            current["program_health_state"],
            previous.get("program_health_state") if previous else None,
        )
        driver_signal_mode_change = _state_change(
            current["program_driver_signal_mode"],
            previous.get("program_driver_signal_mode") if previous else None,
        )
        interrupt_required_change = _state_change(
            current["interrupt_required"],
            previous.get("interrupt_required") if previous else None,
        )
        needs_attention_change = _state_change(
            current["needs_attention"],
            previous.get("needs_attention") if previous else None,
        )
        trading_day_state_change = _state_change(
            current["trading_day_state"],
            previous.get("trading_day_state") if previous else None,
        )
        session_phase_change = _state_change(
            current["session_phase"],
            previous.get("session_phase") if previous else None,
        )
        top_risk_reference_change = _state_change(
            current["top_risk_telegraph_id"],
            previous.get("top_risk_telegraph_id") if previous else None,
        )
        top_opportunity_reference_change = _state_change(
            current["top_opportunity_telegraph_id"],
            previous.get("top_opportunity_telegraph_id") if previous else None,
        )
        top_watch_symbol_change = _state_change(
            current["top_watch_symbol"],
            previous.get("top_watch_symbol") if previous else None,
        )
        top_watch_bundle_change = _state_change(
            current["top_watch_symbols_top5"],
            previous.get("top_watch_symbols_top5") if previous else None,
        )
        primary_focus_match_count_change = _state_change(
            current["primary_focus_match_row_count"],
            previous.get("primary_focus_match_row_count") if previous else None,
        )
        primary_focus_source_present_change = _state_change(
            current["primary_focus_source_present_count"],
            previous.get("primary_focus_source_present_count") if previous else None,
        )
        primary_focus_dual_match_change = _state_change(
            current["primary_focus_dual_match_count"],
            previous.get("primary_focus_dual_match_count") if previous else None,
        )
        top_challenger_theme_change = _state_change(
            current["top_challenger_theme_slug"],
            previous.get("top_challenger_theme_slug") if previous else None,
        )
        top_challenger_symbol_change = _state_change(
            current["top_challenger_symbol"],
            previous.get("top_challenger_symbol") if previous else None,
        )
        top_challenger_support_count_change = _state_change(
            current["top_challenger_support_row_count"],
            previous.get("top_challenger_support_row_count") if previous else None,
        )
        challenger_review_state_change = _state_change(
            current["challenger_review_state"],
            previous.get("challenger_review_state") if previous else None,
        )
        challenger_review_attention_state_change = _state_change(
            current["challenger_review_attention_state"],
            previous.get("challenger_review_attention_state") if previous else None,
        )
        challenger_review_attention_priority_change = _state_change(
            current["challenger_review_attention_priority"],
            previous.get("challenger_review_attention_priority") if previous else None,
        )
        focus_governance_tension_state_change = _state_change(
            current["focus_governance_tension_state"],
            previous.get("focus_governance_tension_state") if previous else None,
        )
        focus_governance_tension_priority_change = _state_change(
            current["focus_governance_tension_priority"],
            previous.get("focus_governance_tension_priority") if previous else None,
        )
        focus_rotation_readiness_state_change = _state_change(
            current["focus_rotation_readiness_state"],
            previous.get("focus_rotation_readiness_state") if previous else None,
        )
        focus_rotation_readiness_priority_change = _state_change(
            current["focus_rotation_readiness_priority"],
            previous.get("focus_rotation_readiness_priority") if previous else None,
        )

        row = {
            "control_packet_change_signal_id": "internal_hot_news_program_control_packet_change_latest",
            "program_health_state_change": program_health_state_change,
            "program_driver_signal_mode_change": driver_signal_mode_change,
            "interrupt_required_change": interrupt_required_change,
            "needs_attention_change": needs_attention_change,
            "trading_day_state_change": trading_day_state_change,
            "session_phase_change": session_phase_change,
            "top_risk_reference_change": top_risk_reference_change,
            "top_opportunity_reference_change": top_opportunity_reference_change,
            "top_watch_symbol_change": top_watch_symbol_change,
            "top_watch_bundle_change": top_watch_bundle_change,
            "primary_focus_match_count_change": primary_focus_match_count_change,
            "primary_focus_source_present_change": primary_focus_source_present_change,
            "primary_focus_dual_match_change": primary_focus_dual_match_change,
            "top_challenger_theme_change": top_challenger_theme_change,
            "top_challenger_symbol_change": top_challenger_symbol_change,
            "top_challenger_support_count_change": top_challenger_support_count_change,
            "challenger_review_state_change": challenger_review_state_change,
            "challenger_review_attention_state_change": challenger_review_attention_state_change,
            "challenger_review_attention_priority_change": challenger_review_attention_priority_change,
            "focus_governance_tension_state_change": focus_governance_tension_state_change,
            "focus_governance_tension_priority_change": focus_governance_tension_priority_change,
            "focus_rotation_readiness_state_change": focus_rotation_readiness_state_change,
            "focus_rotation_readiness_priority_change": focus_rotation_readiness_priority_change,
            "signal_priority": _signal_priority(
                [
                    program_health_state_change,
                    driver_signal_mode_change,
                    interrupt_required_change,
                    needs_attention_change,
                    trading_day_state_change,
                    session_phase_change,
                    top_risk_reference_change,
                    top_opportunity_reference_change,
                    top_watch_symbol_change,
                    top_watch_bundle_change,
                    primary_focus_match_count_change,
                    primary_focus_source_present_change,
                    primary_focus_dual_match_change,
                    top_challenger_theme_change,
                    top_challenger_symbol_change,
                    top_challenger_support_count_change,
                    challenger_review_state_change,
                    challenger_review_attention_state_change,
                    challenger_review_attention_priority_change,
                    focus_governance_tension_state_change,
                    focus_governance_tension_priority_change,
                    focus_rotation_readiness_state_change,
                    focus_rotation_readiness_priority_change,
                ]
            ),
            "program_driver_signal_mode_current": current["program_driver_signal_mode"],
            "interrupt_required_current": current["interrupt_required"],
            "trading_day_state_current": current["trading_day_state"],
            "session_phase_current": current["session_phase"],
            "top_risk_telegraph_id_current": current["top_risk_telegraph_id"],
            "top_opportunity_telegraph_id_current": current["top_opportunity_telegraph_id"],
            "top_watch_symbol_current": current["top_watch_symbol"],
            "top_watch_symbols_top5_current": current["top_watch_symbols_top5"],
            "primary_focus_match_row_count_current": current["primary_focus_match_row_count"],
            "primary_focus_source_present_count_current": current["primary_focus_source_present_count"],
            "primary_focus_dual_match_count_current": current["primary_focus_dual_match_count"],
            "top_challenger_theme_current": current["top_challenger_theme_slug"],
            "top_challenger_symbol_current": current["top_challenger_symbol"],
            "top_challenger_support_row_count_current": current["top_challenger_support_row_count"],
            "challenger_review_state_current": current["challenger_review_state"],
            "challenger_review_attention_state_current": current["challenger_review_attention_state"],
            "challenger_review_attention_priority_current": current["challenger_review_attention_priority"],
            "focus_governance_tension_state_current": current["focus_governance_tension_state"],
            "focus_governance_tension_priority_current": current["focus_governance_tension_priority"],
            "focus_rotation_readiness_state_current": current["focus_rotation_readiness_state"],
            "focus_rotation_readiness_priority_current": current["focus_rotation_readiness_priority"],
            "delivery_state": "program_control_packet_change_signal_ready",
        }

        self._write_csv(self.output_path, [row])
        self._write_csv(self.history_path, [current])
        self._write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_program_control_packet_change_signal",
                    "consumer_mode": "research_shadow",
                    "artifact_path": str(self.output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                }
            ],
        )

        summary = {
            "signal_row_count": 1,
            "program_health_state_change": program_health_state_change,
            "program_driver_signal_mode_change": driver_signal_mode_change,
            "interrupt_required_change": interrupt_required_change,
            "needs_attention_change": needs_attention_change,
            "trading_day_state_change": trading_day_state_change,
            "session_phase_change": session_phase_change,
            "top_risk_reference_change": top_risk_reference_change,
            "top_opportunity_reference_change": top_opportunity_reference_change,
            "top_watch_symbol_change": top_watch_symbol_change,
            "top_watch_bundle_change": top_watch_bundle_change,
            "primary_focus_match_count_change": primary_focus_match_count_change,
            "primary_focus_source_present_change": primary_focus_source_present_change,
            "primary_focus_dual_match_change": primary_focus_dual_match_change,
            "top_challenger_theme_change": top_challenger_theme_change,
            "top_challenger_symbol_change": top_challenger_symbol_change,
            "top_challenger_support_count_change": top_challenger_support_count_change,
            "challenger_review_state_change": challenger_review_state_change,
            "challenger_review_attention_state_change": challenger_review_attention_state_change,
            "challenger_review_attention_priority_change": challenger_review_attention_priority_change,
            "focus_governance_tension_state_change": focus_governance_tension_state_change,
            "focus_governance_tension_priority_change": focus_governance_tension_priority_change,
            "focus_rotation_readiness_state_change": focus_rotation_readiness_state_change,
            "focus_rotation_readiness_priority_change": focus_rotation_readiness_priority_change,
            "signal_priority": row["signal_priority"],
            "authoritative_output": "a_share_internal_hot_news_program_control_packet_change_signal_materialized",
        }
        return MaterializedAShareInternalHotNewsProgramControlPacketChangeSignalV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsProgramControlPacketChangeSignalV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
