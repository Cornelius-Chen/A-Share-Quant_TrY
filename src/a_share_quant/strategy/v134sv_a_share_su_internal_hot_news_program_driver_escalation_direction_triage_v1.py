from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134su_a_share_internal_hot_news_program_driver_escalation_alert_audit_v1 import (
    V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Report:
        report = V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "alert_row_count": report.summary["alert_row_count"],
            "driver_escalation_priority": report.summary["driver_escalation_priority"],
            "program_driver_transition_class": report.summary["program_driver_transition_class"],
            "alert_state": report.summary["alert_state"],
            "authoritative_status": "continue_serving_driver-escalation_alert_above_the_status-change_signal",
        }
        triage_rows = [
            {
                "component": "no_driver_escalation_branch",
                "direction": "keep_the_program_on_lightweight_status_polling_when_driver_escalation_priority_stays_at_p2",
            },
            {
                "component": "activation_rotation_branch",
                "direction": "raise_attention_when_the_driver_mode_rotates_out_of_watch_only_into_prepare_or_live_route",
            },
            {
                "component": "hard_block_rotation_branch",
                "direction": "treat_any_rotation_into_stale_block_as_an_immediate_high-priority_operational_alert",
            },
            {
                "component": "consumer_instruction_branch",
                "direction": "consume_the_alert_state_and_consumer_instruction_directly_without_reinterpreting_the_lower-level_status stack",
            },
        ]
        interpretation = [
            "This is the narrowest top-level alert surface in the internal hot-news stack.",
            "It exists so that only meaningful driver-mode jumps interrupt a consumer that is otherwise happy to stay on passive polling.",
        ]
        return V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sv_a_share_su_internal_hot_news_program_driver_escalation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
