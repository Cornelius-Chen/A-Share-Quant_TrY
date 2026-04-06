from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_runtime_stack_supervisor_surface_v1 import (
    MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1,
)


@dataclass(slots=True)
class V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_stack_supervisor_surface",
                "component_state": "read_ready_internal_only",
                "metric": "surface_row_count",
                "value": str(materialized.summary["surface_row_count"]),
            },
            {
                "component": "supervisor_mode",
                "component_state": "materialized",
                "metric": "supervisor_mode",
                "value": materialized.summary["supervisor_mode"],
            },
            {
                "component": "runtime_consumer_mode",
                "component_state": "materialized",
                "metric": "runtime_consumer_mode",
                "value": materialized.summary["runtime_consumer_mode"],
            },
            {
                "component": "scheduler_loop_signal_mode",
                "component_state": "materialized",
                "metric": "scheduler_loop_signal_mode",
                "value": materialized.summary["scheduler_loop_signal_mode"],
            },
            {
                "component": "orchestration_loop_signal_mode",
                "component_state": "materialized",
                "metric": "orchestration_loop_signal_mode",
                "value": materialized.summary["orchestration_loop_signal_mode"],
            },
        ]
        interpretation = [
            "This surface is the top-level supervisor card above runtime, scheduler, and orchestration layers.",
            "A human or supervising process can use it as a compact readout instead of separately reading the three upper stacks.",
        ]
        return V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UAAShareInternalHotNewsProgramRuntimeStackSupervisorSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ua_a_share_internal_hot_news_program_runtime_stack_supervisor_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
