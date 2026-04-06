from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134so_a_share_internal_hot_news_program_status_surface_audit_v1 import (
    V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Report:
        report = V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "status_row_count": report.summary["status_row_count"],
            "program_health_state": report.summary["program_health_state"],
            "global_program_action_mode": report.summary["global_program_action_mode"],
            "change_signal_priority": report.summary["change_signal_priority"],
            "needs_attention": report.summary["needs_attention"],
            "trading_day_state": report.summary["trading_day_state"],
            "session_phase": report.summary["session_phase"],
            "session_phase_confidence": report.summary["session_phase_confidence"],
            "freshness_state": report.summary["freshness_state"],
            "heartbeat_timeout_state": report.summary["heartbeat_timeout_state"],
            "stale_alert_level": report.summary["stale_alert_level"],
            "force_refresh": report.summary["force_refresh"],
            "program_consumer_gate_mode": report.summary["program_consumer_gate_mode"],
            "program_driver_action_mode": report.summary["program_driver_action_mode"],
            "authoritative_status": "continue_serving_single_program_status_row_as_the_outermost_consumer_entry",
        }
        triage_rows = [
            {
                "component": "outermost_entry",
                "direction": "prefer_the_program_status_surface_as_the_first_polling_target_for_any_downstream_consumer",
            },
            {
                "component": "attention_branch",
                "direction": "only_descend_into_change_signal_action_surface_or_split_feeds_when_needs_attention_is_true_or_when_deeper_context_is_required",
            },
            {
                "component": "steady_state_branch",
                "direction": "when_program_health_is_healthy_needs_attention_is_false_and_freshness_state_is_fresh_keep_the_consumer_in_lightweight_polling_mode",
            },
            {
                "component": "consumer_gate_branch",
                "direction": "respect_program_consumer_gate_mode_first_so_the_consumer_can_decide_between_live_routing_prepare_only_break_hold_review_only_non_trading_day_watch_or_stale_block_behavior_from_one_row",
            },
            {
                "component": "driver_action_branch",
                "direction": "prefer_program_driver_action_mode_when_the_consumer_wants_a_direct_machine-actionable_enum_such_as_watch_prepare_live_route_break_hold_review_degraded_watch_or_stale_block",
            },
            {
                "component": "session_branch",
                "direction": "respect_trade_calendar_backed_trading_day_state_and_session_phase_when_deciding_whether_the_consumer_should_treat_the_same_status_as_pre_open_call_auction_continuous_session_lunch_break_post_close_or_non_trading_day_logic",
            },
            {
                "component": "freshness_branch",
                "direction": "when_freshness_state_is_warming_stale_or_stale_treat_the_status_row_as_low-confidence_and_force_a_refresh_before_trusting_it",
            },
            {
                "component": "timeout_alert_branch",
                "direction": "when_heartbeat_timeout_state_is_timed_out_or_stale_alert_level_is_critical_raise_a_stale-alert_and_stop_trusting_the_status_row_until_refreshed",
            },
        ]
        interpretation = [
            "This is the outermost consumer entry built on top of the internal hot-news pipeline.",
            "The deeper layers remain available, but the status row should be enough for first-pass orchestration.",
        ]
        return V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SPAShareSOInternalHotNewsProgramStatusDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sp_a_share_so_internal_hot_news_program_status_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
