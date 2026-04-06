from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134uo_a_share_internal_hot_news_program_runtime_stack_control_packet_change_signal_audit_v1 import (
    V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UPAShareUOInternalHotNewsProgramRuntimeStackControlPacketChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UPAShareUOInternalHotNewsProgramRuntimeStackControlPacketChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UPAShareUOInternalHotNewsProgramRuntimeStackControlPacketChangeDirectionTriageV1Report:
        report = V134UOAShareInternalHotNewsProgramRuntimeStackControlPacketChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "supervisor_mode_change": report.summary["supervisor_mode_change"],
            "supervision_loop_mode_change": report.summary["supervision_loop_mode_change"],
            "contract_action_change": report.summary["contract_action_change"],
            "signal_priority_change": report.summary["signal_priority_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_runtime-stack_control_packet_change_signal_above_the_single-row_runtime-stack_control_packet",
        }
        triage_rows = [
            {
                "component": "stable_runtime_stack_packet_branch",
                "direction": "keep_the_outer controller on lightweight single-row runtime-stack packet polling when the packet-change signal remains stable",
            },
            {
                "component": "supervision_rotation_branch",
                "direction": "treat_supervisor_mode_change_or_supervision_loop_mode_change_as_the_most_important top-level runtime-stack packet flips",
            },
            {
                "component": "contract_rotation_branch",
                "direction": "treat_contract_action_change_as_a_legitimate top-level packet update because it changes the current supervising instruction",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the single-row runtime-stack control packet.",
            "An outer controller can stay on this layer most of the time and only reopen the runtime-stack control packet when it changes.",
        ]
        return V134UPAShareUOInternalHotNewsProgramRuntimeStackControlPacketChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UPAShareUOInternalHotNewsProgramRuntimeStackControlPacketChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UPAShareUOInternalHotNewsProgramRuntimeStackControlPacketChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134up_a_share_uo_internal_hot_news_program_runtime_stack_control_packet_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
