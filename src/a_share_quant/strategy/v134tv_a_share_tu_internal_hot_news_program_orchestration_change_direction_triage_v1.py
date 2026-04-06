from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134tu_a_share_internal_hot_news_program_orchestration_packet_change_signal_audit_v1 import (
    V134TUAShareInternalHotNewsProgramOrchestrationPacketChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TVAShareTUInternalHotNewsProgramOrchestrationChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TVAShareTUInternalHotNewsProgramOrchestrationChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TVAShareTUInternalHotNewsProgramOrchestrationChangeDirectionTriageV1Report:
        report = V134TUAShareInternalHotNewsProgramOrchestrationPacketChangeSignalAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "orchestration_mode_change": report.summary["orchestration_mode_change"],
            "scheduler_loop_signal_mode_change": report.summary["scheduler_loop_signal_mode_change"],
            "runtime_consumer_mode_change": report.summary["runtime_consumer_mode_change"],
            "sleep_strategy_change": report.summary["sleep_strategy_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "continue_serving_orchestration-packet_change_signal_above_the_orchestration-packet",
        }
        triage_rows = [
            {
                "component": "steady_orchestration_branch",
                "direction": "keep_the_outer orchestrator on the existing supervision plan when the orchestration-packet change signal remains stable",
            },
            {
                "component": "mode_rotation_branch",
                "direction": "reconfigure_outer orchestration immediately when orchestration_mode_change or scheduler_loop_signal_mode_change flips state",
            },
            {
                "component": "cadence_rotation_branch",
                "direction": "update_outer supervision cadence when runtime_consumer_mode_change or sleep_strategy_change flips state",
            },
        ]
        interpretation = [
            "This is the topmost change detector for the orchestration-facing packet.",
            "An orchestrator can watch it to know whether orchestration behavior really changed without rereading the packet every cycle.",
        ]
        return V134TVAShareTUInternalHotNewsProgramOrchestrationChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TVAShareTUInternalHotNewsProgramOrchestrationChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TVAShareTUInternalHotNewsProgramOrchestrationChangeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tv_a_share_tu_internal_hot_news_program_orchestration_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
