from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ts_a_share_internal_hot_news_program_orchestration_packet_audit_v1 import (
    V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Report:
        report = V134TSAShareInternalHotNewsProgramOrchestrationPacketAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "packet_row_count": report.summary["packet_row_count"],
            "orchestration_mode": report.summary["orchestration_mode"],
            "scheduler_loop_signal_mode": report.summary["scheduler_loop_signal_mode"],
            "runtime_consumer_mode": report.summary["runtime_consumer_mode"],
            "sleep_strategy_seconds": report.summary["sleep_strategy_seconds"],
            "authoritative_status": "continue_serving_orchestration-packet_above_scheduler-and-runtime_layers",
        }
        triage_rows = [
            {
                "component": "steady_orchestration_branch",
                "direction": "keep_the_outer_orchestrator_on_steady supervision when orchestration_mode remains steady_orchestration",
            },
            {
                "component": "tight_orchestration_branch",
                "direction": "tighten_outer supervision and shorten orchestration cadence when orchestration_mode rotates into tight_orchestration",
            },
            {
                "component": "interrupt_orchestration_branch",
                "direction": "interrupt_the_outer orchestration loop immediately when orchestration_mode rotates into interrupt_orchestration",
            },
        ]
        interpretation = [
            "This is the highest orchestration-facing packet in the internal hot-news stack.",
            "An external orchestrator can stop here without reading lower scheduler or runtime layers unless it needs detail.",
        ]
        return V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TTAShareTSInternalHotNewsProgramOrchestrationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tt_a_share_ts_internal_hot_news_program_orchestration_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
