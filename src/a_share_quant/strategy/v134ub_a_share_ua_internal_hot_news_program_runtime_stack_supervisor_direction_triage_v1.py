from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ua_a_share_internal_hot_news_program_runtime_stack_supervisor_surface_audit_v1 import (
    V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UBAShareUAInternalHotNewsProgramRuntimeStackSupervisorDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UBAShareUAInternalHotNewsProgramRuntimeStackSupervisorDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UBAShareUAInternalHotNewsProgramRuntimeStackSupervisorDirectionTriageV1Report:
        report = V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "surface_row_count": report.summary["surface_row_count"],
            "supervisor_mode": report.summary["supervisor_mode"],
            "runtime_consumer_mode": report.summary["runtime_consumer_mode"],
            "scheduler_loop_signal_mode": report.summary["scheduler_loop_signal_mode"],
            "orchestration_loop_signal_mode": report.summary["orchestration_loop_signal_mode"],
            "authoritative_status": "continue_serving_runtime-stack_supervisor_surface_above_runtime_scheduler_and_orchestration_signal_layers",
        }
        triage_rows = [
            {
                "component": "steady_supervision_branch",
                "direction": "keep_the_supervising process on lightweight oversight when supervisor_mode remains steady_supervision",
            },
            {
                "component": "elevated_supervision_branch",
                "direction": "raise_supervision intensity when supervisor_mode rotates into elevated_supervision or tight_supervision",
            },
            {
                "component": "interrupt_supervision_branch",
                "direction": "treat_interrupt_supervision_as_the_highest supervisory state and escalate immediately",
            },
        ]
        interpretation = [
            "This is the top-level compact supervisor card for the hot-news execution stack.",
            "It is meant to stop the infinite outward expansion of loop-specific layers by giving one compact supervisory view.",
        ]
        return V134UBAShareUAInternalHotNewsProgramRuntimeStackSupervisorDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UBAShareUAInternalHotNewsProgramRuntimeStackSupervisorDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UBAShareUAInternalHotNewsProgramRuntimeStackSupervisorDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ub_a_share_ua_internal_hot_news_program_runtime_stack_supervisor_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
