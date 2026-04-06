from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134uc_a_share_internal_hot_news_program_runtime_stack_supervisor_change_signal_audit_v1 import (
    V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Report:
        report = V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "supervisor_mode_change": report.summary["supervisor_mode_change"],
            "program_health_state_change": report.summary["program_health_state_change"],
            "runtime_consumer_mode_change": report.summary["runtime_consumer_mode_change"],
            "scheduler_loop_signal_mode_change": report.summary["scheduler_loop_signal_mode_change"],
            "orchestration_loop_signal_mode_change": report.summary["orchestration_loop_signal_mode_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_runtime-stack_supervisor_change_signal_above_the_supervisor_surface",
        }
        triage_rows = [
            {
                "component": "stable_supervisor_branch",
                "direction": "keep_the_existing_supervision posture when the supervisor-change layer remains stable",
            },
            {
                "component": "mode_change_branch",
                "direction": "escalate_supervision attention when supervisor_mode_change or orchestration_loop_signal_mode_change flips state",
            },
            {
                "component": "stack_rotation_branch",
                "direction": "reopen_the_compact_supervisor card when runtime or scheduler loop modes flip even if the top-level supervisor_mode has not yet rotated",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the compact runtime-stack supervisor card.",
            "A supervising process can watch it to know when the runtime/scheduler/orchestration stack materially changed without rereading the supervisor card every cycle.",
        ]
        return V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UDAShareUCInternalHotNewsProgramRuntimeStackSupervisorChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ud_a_share_uc_internal_hot_news_program_runtime_stack_supervisor_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
