from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_status_change_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramStatusChangeSignalV1,
)


@dataclass(slots=True)
class V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramStatusChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_status_change_signal",
                "component_state": "read_ready_internal_only",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "program_health_change",
                "component_state": "materialized",
                "metric": "program_health_state_change",
                "value": materialized.summary["program_health_state_change"],
            },
            {
                "component": "action_mode_change",
                "component_state": "materialized",
                "metric": "global_program_action_mode_change",
                "value": materialized.summary["global_program_action_mode_change"],
            },
            {
                "component": "session_change",
                "component_state": "materialized",
                "metric": "session_phase_change",
                "value": materialized.summary["session_phase_change"],
            },
            {
                "component": "consumer_gate_change",
                "component_state": "materialized",
                "metric": "program_consumer_gate_mode_change",
                "value": materialized.summary["program_consumer_gate_mode_change"],
            },
            {
                "component": "driver_action_change",
                "component_state": "materialized",
                "metric": "program_driver_action_mode_change",
                "value": materialized.summary["program_driver_action_mode_change"],
            },
            {
                "component": "driver_transition",
                "component_state": "materialized",
                "metric": "program_driver_transition_class",
                "value": materialized.summary["program_driver_transition_class"],
            },
            {
                "component": "driver_escalation",
                "component_state": "materialized",
                "metric": "driver_escalation_priority",
                "value": materialized.summary["driver_escalation_priority"],
            },
            {
                "component": "signal_priority",
                "component_state": "materialized",
                "metric": "signal_priority",
                "value": materialized.summary["signal_priority"],
            },
        ]
        interpretation = [
            "The outermost program status row now has its own change signal above it.",
            "This lets a consumer react only when top-level program state, session timing, or the outer driver mode meaningfully changes.",
            "Driver-mode rotations are now split into a dedicated transition class so that watch_only-to-prepare/live_route/stale_block can be escalated above ordinary stable-state churn.",
        ]
        return V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SQAShareInternalHotNewsProgramStatusChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sq_a_share_internal_hot_news_program_status_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
