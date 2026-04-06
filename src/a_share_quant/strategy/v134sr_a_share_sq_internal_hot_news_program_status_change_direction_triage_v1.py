from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sq_a_share_internal_hot_news_program_status_change_signal_audit_v1 import (
    V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Report:
        report = V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "program_health_state_change": report.summary["program_health_state_change"],
            "global_program_action_mode_change": report.summary["global_program_action_mode_change"],
            "needs_attention_change": report.summary["needs_attention_change"],
            "trading_day_state_change": report.summary["trading_day_state_change"],
            "session_phase_change": report.summary["session_phase_change"],
            "program_consumer_gate_mode_change": report.summary["program_consumer_gate_mode_change"],
            "program_driver_action_mode_change": report.summary["program_driver_action_mode_change"],
            "program_driver_transition_class": report.summary["program_driver_transition_class"],
            "driver_escalation_priority": report.summary["driver_escalation_priority"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_status-level_change_signal_above_the_program_status_surface",
        }
        triage_rows = [
            {
                "component": "stable_outer_state",
                "direction": "when_the_status-level_change_signal_is_stable_keep_the_consumer_on_lightweight_status_polling_only",
            },
            {
                "component": "state_changed_outer_state",
                "direction": "when_any_outer_state_changes_treat_it_as_a_higher-priority_consumer_event_than_inner_feed_noise",
            },
            {
                "component": "signal_priority_branch",
                "direction": "use_signal_priority_as_the_switch_between_passive_polling_and_active_reaction_or_alerting",
            },
            {
                "component": "session_timing_branch",
                "direction": "treat_session_phase_change_or_trading_day_state_change_as_a_legitimate_outer-state_rotation_even_if_the_message_content_stack_itself_is_stable",
            },
            {
                "component": "driver_action_branch",
                "direction": "treat_program_driver_action_mode_change_as_a_top-level_operational_rotation_because_it_directly_changes_how_the_program_should_consume_the_hot-news_stack",
            },
            {
                "component": "driver_transition_escalation_branch",
                "direction": "escalate_watch_only-to-prepare_or_live_route_and_any_rotation_into_stale_block_above_ordinary_outer-state_changes_because_these_transitions directly alter whether the program should stay passive, prepare, route live, or block itself",
            },
        ]
        interpretation = [
            "This is now the topmost change detector in the internal hot-news program stack.",
            "A consumer can stay on this layer most of the time and only descend when it changes.",
            "The driver-transition branch separates meaningful operating-mode jumps from ordinary stable-state refresh noise.",
        ]
        return V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SRAShareSQInternalHotNewsProgramStatusChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sr_a_share_sq_internal_hot_news_program_status_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
