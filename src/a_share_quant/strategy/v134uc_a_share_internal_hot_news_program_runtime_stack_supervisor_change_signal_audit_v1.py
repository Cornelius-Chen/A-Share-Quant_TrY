from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_runtime_stack_supervisor_change_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalV1,
)


@dataclass(slots=True)
class V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_stack_supervisor_change_signal",
                "component_state": "read_ready_internal_only",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "supervisor_mode_change",
                "component_state": "materialized",
                "metric": "supervisor_mode_change",
                "value": materialized.summary["supervisor_mode_change"],
            },
            {
                "component": "program_health_state_change",
                "component_state": "materialized",
                "metric": "program_health_state_change",
                "value": materialized.summary["program_health_state_change"],
            },
            {
                "component": "runtime_consumer_mode_change",
                "component_state": "materialized",
                "metric": "runtime_consumer_mode_change",
                "value": materialized.summary["runtime_consumer_mode_change"],
            },
            {
                "component": "scheduler_loop_signal_mode_change",
                "component_state": "materialized",
                "metric": "scheduler_loop_signal_mode_change",
                "value": materialized.summary["scheduler_loop_signal_mode_change"],
            },
            {
                "component": "orchestration_loop_signal_mode_change",
                "component_state": "materialized",
                "metric": "orchestration_loop_signal_mode_change",
                "value": materialized.summary["orchestration_loop_signal_mode_change"],
            },
        ]
        interpretation = [
            "This layer sits above the runtime-stack supervisor card and isolates whether the compact supervision view itself changed.",
            "A supervising process can watch it to avoid reopening the supervisor card unless one of the upper stacks materially changed.",
        ]
        return V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UCAShareInternalHotNewsProgramRuntimeStackSupervisorChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uc_a_share_internal_hot_news_program_runtime_stack_supervisor_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
