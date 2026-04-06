from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_runtime_stack_control_packet_change_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalV1,
)


@dataclass(slots=True)
class V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_stack_control_packet_change_signal",
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
                "component": "supervision_loop_mode_change",
                "component_state": "materialized",
                "metric": "supervision_loop_mode_change",
                "value": materialized.summary["supervision_loop_mode_change"],
            },
            {
                "component": "contract_action_change",
                "component_state": "materialized",
                "metric": "contract_action_change",
                "value": materialized.summary["contract_action_change"],
            },
            {
                "component": "signal_priority_change",
                "component_state": "materialized",
                "metric": "signal_priority_change",
                "value": materialized.summary["signal_priority_change"],
            },
        ]
        interpretation = [
            "This change signal sits directly above the single-row runtime-stack control packet.",
            "An outer controller can watch this layer to know whether the topmost runtime-stack packet itself materially changed without reopening lower packet fields every cycle.",
        ]
        return V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134uo_a_share_internal_hot_news_program_runtime_stack_control_packet_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
