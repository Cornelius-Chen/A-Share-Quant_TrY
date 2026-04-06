from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_orchestration_packet_v1 import (
    MaterializeAShareInternalHotNewsProgramOrchestrationPacketV1,
)


@dataclass(slots=True)
class V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramOrchestrationPacketV1(self.repo_root).materialize()
        rows = [
            {
                "component": "orchestration_packet",
                "component_state": "read_ready_internal_only",
                "metric": "packet_row_count",
                "value": str(materialized.summary["packet_row_count"]),
            },
            {
                "component": "orchestration_mode",
                "component_state": "materialized",
                "metric": "orchestration_mode",
                "value": materialized.summary["orchestration_mode"],
            },
            {
                "component": "scheduler_loop_signal_mode",
                "component_state": "materialized",
                "metric": "scheduler_loop_signal_mode",
                "value": materialized.summary["scheduler_loop_signal_mode"],
            },
            {
                "component": "runtime_consumer_mode",
                "component_state": "materialized",
                "metric": "runtime_consumer_mode",
                "value": materialized.summary["runtime_consumer_mode"],
            },
        ]
        interpretation = [
            "This is the outermost orchestration-facing packet in the internal hot-news stack.",
            "An external orchestrator can use it as a single-row state packet above the scheduler and runtime layers.",
        ]
        return V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ts_a_share_internal_hot_news_program_orchestration_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
