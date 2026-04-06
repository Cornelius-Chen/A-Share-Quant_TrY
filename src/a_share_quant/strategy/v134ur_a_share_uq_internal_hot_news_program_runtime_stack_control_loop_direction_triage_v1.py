from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134uq_a_share_internal_hot_news_program_runtime_stack_control_loop_signal_feed_audit_v1 import (
    V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer,
)


@dataclass(slots=True)
class V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Report:
        report = V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "runtime_stack_control_loop_signal_mode": report.summary["runtime_stack_control_loop_signal_mode"],
            "signal_priority": report.summary["signal_priority"],
            "reopen_target": report.summary["reopen_target"],
            "authoritative_status": "continue_serving_runtime-stack_control_loop_signal_feed_above_the_single-row_runtime-stack_control_packet",
        }
        triage_rows = [
            {
                "component": "steady_runtime_stack_control_loop_branch",
                "direction": "keep_the_outer controller on steady lightweight polling when the runtime-stack control loop signal remains steady",
            },
            {
                "component": "tight_runtime_stack_control_loop_branch",
                "direction": "tighten_the_outer controller polling and reopen the requested target when the loop signal rotates into tight_runtime_stack_control_loop",
            },
            {
                "component": "interrupt_runtime_stack_control_loop_branch",
                "direction": "interrupt_the_outer controller immediately when the loop signal rotates into interrupt_runtime_stack_control_loop",
            },
        ]
        interpretation = [
            "This is the topmost loop-facing routing surface for the single-row runtime-stack control packet.",
            "An outer controller can stop here without rereading the control packet unless it needs deeper diagnostics.",
        ]
        return V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134URAShareUQInternalHotNewsProgramRuntimeStackControlLoopDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ur_a_share_uq_internal_hot_news_program_runtime_stack_control_loop_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
