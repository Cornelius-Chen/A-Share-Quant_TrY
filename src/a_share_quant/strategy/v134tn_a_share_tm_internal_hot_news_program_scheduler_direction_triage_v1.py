from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134tm_a_share_internal_hot_news_program_scheduler_packet_audit_v1 import (
    V134TMAShareInternalHotNewsProgramSchedulerPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Report:
        report = V134TMAShareInternalHotNewsProgramSchedulerPacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "packet_row_count": report.summary["packet_row_count"],
            "scheduler_mode": report.summary["scheduler_mode"],
            "contract_action": report.summary["contract_action"],
            "sleep_strategy_seconds": report.summary["sleep_strategy_seconds"],
            "contract_change_signal_priority": report.summary["contract_change_signal_priority"],
            "authoritative_status": "continue_serving_scheduler-packet_above_the_runtime-execution_contract",
        }
        triage_rows = [
            {
                "component": "steady_schedule_branch",
                "direction": "keep_the_scheduler_on_steady cadence when scheduler_mode remains steady_schedule",
            },
            {
                "component": "tight_requeue_branch",
                "direction": "shorten_the_scheduler cycle and prioritize this loop when scheduler_mode rotates into tight_requeue",
            },
            {
                "component": "interrupt_and_requeue_branch",
                "direction": "interrupt_the_current scheduler plan and immediately requeue the loop when scheduler_mode rotates into interrupt_and_requeue",
            },
        ]
        interpretation = [
            "This is the topmost scheduler-facing packet in the internal hot-news stack.",
            "A scheduler can stop here without reading the lower execution contract unless it needs deeper detail.",
        ]
        return V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TNAShareTMInternalHotNewsProgramSchedulerDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tn_a_share_tm_internal_hot_news_program_scheduler_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
