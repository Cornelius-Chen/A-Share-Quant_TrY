from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134um_a_share_internal_hot_news_program_runtime_stack_control_packet_audit_v1 import (
    V134UMAShareInternalHotNewsProgramRuntimeStackControlPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134UNAShareUMInternalHotNewsProgramRuntimeStackControlPacketDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134UNAShareUMInternalHotNewsProgramRuntimeStackControlPacketDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134UNAShareUMInternalHotNewsProgramRuntimeStackControlPacketDirectionTriageV1Report:
        report = V134UMAShareInternalHotNewsProgramRuntimeStackControlPacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "packet_row_count": report.summary["packet_row_count"],
            "supervisor_mode": report.summary["supervisor_mode"],
            "supervision_loop_mode": report.summary["supervision_loop_mode"],
            "contract_action": report.summary["contract_action"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_single-row_runtime-stack_control_packet_above_the_supervision_contract_layers",
        }
        triage_rows = [
            {
                "component": "steady_control_packet_branch",
                "direction": "keep_the_outer controller on lightweight polling when the packet stays in keep_steady_supervision and steady_supervision_loop",
            },
            {
                "component": "tight_control_packet_branch",
                "direction": "escalate_attention and tighten the supervising cadence when the packet rotates into tighten_supervision_loop or elevate_supervision_only",
            },
            {
                "component": "interrupt_control_packet_branch",
                "direction": "interrupt_and reopen the requested target immediately when the packet rotates into interrupt_supervision_loop_and_reopen_target",
            },
        ]
        interpretation = [
            "This is the single-row topmost control surface for the internal hot-news runtime stack.",
            "An external top controller can stop here unless it needs to open lower supervision tables for deeper diagnostics.",
        ]
        return V134UNAShareUMInternalHotNewsProgramRuntimeStackControlPacketDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134UNAShareUMInternalHotNewsProgramRuntimeStackControlPacketDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134UNAShareUMInternalHotNewsProgramRuntimeStackControlPacketDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134un_a_share_um_internal_hot_news_program_runtime_stack_control_packet_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
