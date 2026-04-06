from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ue_a_share_internal_hot_news_program_runtime_stack_supervisor_loop_signal_feed_audit_v1 import (
    V134UEAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UFAShareUEInternalHotNewsProgramRuntimeStackSupervisorLoopDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UFAShareUEInternalHotNewsProgramRuntimeStackSupervisorLoopDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UFAShareUEInternalHotNewsProgramRuntimeStackSupervisorLoopDirectionTriageV1Report:
        report = V134UEAShareInternalHotNewsProgramRuntimeStackSupervisorLoopSignalFeedAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "supervision_loop_mode": report.summary["supervision_loop_mode"],
            "signal_priority": report.summary["signal_priority"],
            "reopen_target": report.summary["reopen_target"],
            "authoritative_status": "continue_serving_runtime-stack_supervisor_loop_signal_feed_above_the_supervisor_surface_and_change-signal",
        }
        triage_rows = [
            {
                "component": "steady_supervision_loop_branch",
                "direction": "keep_the_supervising_loop_on_steady polling when supervision_loop_mode remains steady_supervision_loop",
            },
            {
                "component": "tight_supervision_loop_branch",
                "direction": "tighten_the_supervising_loop and reopen the requested supervisor target when supervision_loop_mode rotates into tight_supervision_loop",
            },
            {
                "component": "interrupt_supervision_loop_branch",
                "direction": "interrupt_the_supervising_loop immediately when supervision_loop_mode rotates into interrupt_supervision_loop",
            },
        ]
        interpretation = [
            "This is the narrowest loop-facing routing surface above the compact runtime-stack supervisor card.",
            "A supervising loop can stop here without rereading the supervisor surface unless it needs deeper context.",
        ]
        return V134UFAShareUEInternalHotNewsProgramRuntimeStackSupervisorLoopDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UFAShareUEInternalHotNewsProgramRuntimeStackSupervisorLoopDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UFAShareUEInternalHotNewsProgramRuntimeStackSupervisorLoopDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uf_a_share_ue_internal_hot_news_program_runtime_stack_supervisor_loop_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
