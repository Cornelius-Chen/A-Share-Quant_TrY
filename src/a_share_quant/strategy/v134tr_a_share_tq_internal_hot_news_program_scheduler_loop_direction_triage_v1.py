from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134tq_a_share_internal_hot_news_program_scheduler_loop_signal_feed_audit_v1 import (
    V134TQAShareInternalHotNewsProgramSchedulerLoopSignalFeedAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TRAShareTQInternalHotNewsProgramSchedulerLoopDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TRAShareTQInternalHotNewsProgramSchedulerLoopDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TRAShareTQInternalHotNewsProgramSchedulerLoopDirectionTriageV1Report:
        report = V134TQAShareInternalHotNewsProgramSchedulerLoopSignalFeedAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "scheduler_loop_signal_mode": report.summary["scheduler_loop_signal_mode"],
            "signal_priority": report.summary["signal_priority"],
            "reschedule_target": report.summary["reschedule_target"],
            "authoritative_status": "continue_serving_scheduler-loop_signal-feed_above_the_scheduler-packet_and_change-signal",
        }
        triage_rows = [
            {
                "component": "steady_loop_branch",
                "direction": "keep_the_scheduler_loop_on_steady polling when scheduler_loop_signal_mode remains steady_polling",
            },
            {
                "component": "tight_loop_branch",
                "direction": "tighten_the_scheduler loop and reschedule the queue when scheduler_loop_signal_mode rotates into tight_poll_requeue",
            },
            {
                "component": "interrupt_loop_branch",
                "direction": "interrupt_the_scheduler loop immediately when scheduler_loop_signal_mode rotates into interrupt_requeue",
            },
        ]
        interpretation = [
            "This is the narrowest scheduler-loop routing surface in the internal hot-news stack.",
            "An outer scheduler can stop here without reading lower scheduler packet layers unless it wants deeper detail.",
        ]
        return V134TRAShareTQInternalHotNewsProgramSchedulerLoopDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TRAShareTQInternalHotNewsProgramSchedulerLoopDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TRAShareTQInternalHotNewsProgramSchedulerLoopDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tr_a_share_tq_internal_hot_news_program_scheduler_loop_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
