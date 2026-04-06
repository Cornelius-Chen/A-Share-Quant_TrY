from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134uw_a_share_internal_hot_news_program_runtime_stack_control_loop_runtime_envelope_change_signal_audit_v1 import (
    V134UWAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UXAShareUWInternalHotNewsProgramRuntimeStackControlLoopRuntimeChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UXAShareUWInternalHotNewsProgramRuntimeStackControlLoopRuntimeChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UXAShareUWInternalHotNewsProgramRuntimeStackControlLoopRuntimeChangeDirectionTriageV1Report:
        report = V134UWAShareInternalHotNewsProgramRuntimeStackControlLoopRuntimeEnvelopeChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "runtime_consumer_mode_change": report.summary["runtime_consumer_mode_change"],
            "runtime_attention_level_change": report.summary["runtime_attention_level_change"],
            "suggested_poll_interval_change": report.summary["suggested_poll_interval_change"],
            "reopen_target_change": report.summary["reopen_target_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_runtime-stack_control-loop_runtime-envelope_change_signal_above_the_runtime-envelope",
        }
        triage_rows = [
            {
                "component": "stable_runtime_envelope_branch",
                "direction": "keep_the_outer controller on_the_existing_polling cadence when the runtime-envelope change signal remains stable",
            },
            {
                "component": "poll_interval_rotation_branch",
                "direction": "update_the_outer scheduler cadence immediately when suggested_poll_interval_change flips state",
            },
            {
                "component": "reopen_target_rotation_branch",
                "direction": "refresh_the_requested upper target when reopen_target_change flips state",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the runtime-stack control-loop runtime envelope.",
            "An outer controller can watch it to know when polling cadence or reopening targets changed without reparsing the runtime envelope itself.",
        ]
        return V134UXAShareUWInternalHotNewsProgramRuntimeStackControlLoopRuntimeChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UXAShareUWInternalHotNewsProgramRuntimeStackControlLoopRuntimeChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UXAShareUWInternalHotNewsProgramRuntimeStackControlLoopRuntimeChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ux_a_share_uw_internal_hot_news_program_runtime_stack_control_loop_runtime_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
