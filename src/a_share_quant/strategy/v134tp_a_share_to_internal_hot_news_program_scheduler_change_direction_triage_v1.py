from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134to_a_share_internal_hot_news_program_scheduler_packet_change_signal_audit_v1 import (
    V134TOAShareInternalHotNewsProgramSchedulerPacketChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TPAShareTOInternalHotNewsProgramSchedulerChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TPAShareTOInternalHotNewsProgramSchedulerChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TPAShareTOInternalHotNewsProgramSchedulerChangeDirectionTriageV1Report:
        report = V134TOAShareInternalHotNewsProgramSchedulerPacketChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "scheduler_mode_change": report.summary["scheduler_mode_change"],
            "contract_action_change": report.summary["contract_action_change"],
            "sleep_strategy_change": report.summary["sleep_strategy_change"],
            "interrupt_required_change": report.summary["interrupt_required_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_scheduler-packet_change_signal_above_the_scheduler-packet",
        }
        triage_rows = [
            {
                "component": "stable_scheduler_branch",
                "direction": "keep_the_existing_scheduler cadence when the scheduler-packet change signal remains stable",
            },
            {
                "component": "cadence_rotation_branch",
                "direction": "reconfigure_the_scheduler cadence immediately when scheduler_mode_change or sleep_strategy_change flips state",
            },
            {
                "component": "interrupt_rotation_branch",
                "direction": "promote_the_change_to_high_attention_when interrupt_required_change flips state",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the scheduler-facing packet.",
            "A scheduler can watch it to know whether scheduling behavior really changed without reparsing the packet every cycle.",
        ]
        return V134TPAShareTOInternalHotNewsProgramSchedulerChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TPAShareTOInternalHotNewsProgramSchedulerChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TPAShareTOInternalHotNewsProgramSchedulerChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tp_a_share_to_internal_hot_news_program_scheduler_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
