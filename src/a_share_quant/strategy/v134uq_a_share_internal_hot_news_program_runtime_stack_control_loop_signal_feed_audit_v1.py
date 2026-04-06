from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_runtime_stack_control_loop_signal_feed_v1 import (
    MaterializeAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedV1,
)


@dataclass(slots=True)
class V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_stack_control_loop_signal_feed",
                "component_state": "read_ready_internal_only",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "runtime_stack_control_loop_signal_mode",
                "component_state": "materialized",
                "metric": "runtime_stack_control_loop_signal_mode",
                "value": materialized.summary["runtime_stack_control_loop_signal_mode"],
            },
            {
                "component": "signal_priority",
                "component_state": "materialized",
                "metric": "signal_priority",
                "value": materialized.summary["signal_priority"],
            },
            {
                "component": "reopen_target",
                "component_state": "materialized",
                "metric": "reopen_target",
                "value": materialized.summary["reopen_target"],
            },
        ]
        interpretation = [
            "This is the narrowest loop-facing signal above the single-row runtime-stack control packet.",
            "An outer controller loop can use it to stay steady, tighten polling, or interrupt immediately without rereading the full control packet.",
        ]
        return V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UQAShareInternalHotNewsProgramRuntimeStackControlLoopSignalFeedAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uq_a_share_internal_hot_news_program_runtime_stack_control_loop_signal_feed_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
