from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ug_a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_change_audit_v1 import (
    V134UGAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UHAShareUGInternalHotNewsProgramRuntimeStackSupervisorLoopChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UHAShareUGInternalHotNewsProgramRuntimeStackSupervisorLoopChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UHAShareUGInternalHotNewsProgramRuntimeStackSupervisorLoopChangeDirectionTriageV1Report:
        report = V134UGAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalChangeAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "supervision_loop_mode_change": report.summary["supervision_loop_mode_change"],
            "signal_priority_change": report.summary["signal_priority_change"],
            "reopen_target_change": report.summary["reopen_target_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_runtime-stack_supervisor_loop_signal_change_above_the_runtime-stack_supervisor_loop_signal_feed",
        }
        triage_rows = [
            {
                "component": "stable_loop_signal_branch",
                "direction": "keep_the_existing_supervision loop routing when the supervisor-loop change layer remains stable",
            },
            {
                "component": "loop_mode_rotation_branch",
                "direction": "reconfigure_supervision loop routing immediately when supervision_loop_mode_change flips state",
            },
            {
                "component": "reopen_rotation_branch",
                "direction": "refresh_the_requested supervisor target when reopen_target_change flips state",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the narrow runtime-stack supervisor loop signal feed.",
            "A supervising loop can watch it to know when supervisor-loop routing semantics changed without rereading the signal feed every cycle.",
        ]
        return V134UHAShareUGInternalHotNewsProgramRuntimeStackSupervisorLoopChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UHAShareUGInternalHotNewsProgramRuntimeStackSupervisorLoopChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UHAShareUGInternalHotNewsProgramRuntimeStackSupervisorLoopChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uh_a_share_ug_internal_hot_news_program_runtime_stack_supervisor_loop_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
