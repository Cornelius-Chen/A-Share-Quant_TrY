from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134tw_a_share_internal_hot_news_program_orchestration_loop_signal_feed_audit_v1 import (
    V134TWAShareInternalHotNewsProgramOrchestrationLoopSignalFeedAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TXAShareTWInternalHotNewsProgramOrchestrationLoopDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TXAShareTWInternalHotNewsProgramOrchestrationLoopDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TXAShareTWInternalHotNewsProgramOrchestrationLoopDirectionTriageV1Report:
        report = V134TWAShareInternalHotNewsProgramOrchestrationLoopSignalFeedAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "orchestration_loop_signal_mode": report.summary["orchestration_loop_signal_mode"],
            "signal_priority": report.summary["signal_priority"],
            "reopen_target": report.summary["reopen_target"],
            "authoritative_status": "continue_serving_orchestration-loop_signal-feed_above_the_orchestration-packet_and_change-signal",
        }
        triage_rows = [
            {
                "component": "steady_loop_branch",
                "direction": "keep_the_outer_orchestration_loop_on_steady polling when orchestration_loop_signal_mode remains steady_orchestration_loop",
            },
            {
                "component": "tight_loop_branch",
                "direction": "tighten_the_outer_orchestration_loop and reopen the requested target when orchestration_loop_signal_mode rotates into tight_orchestration_loop",
            },
            {
                "component": "interrupt_loop_branch",
                "direction": "interrupt_the_outer_orchestration_loop immediately when orchestration_loop_signal_mode rotates into interrupt_orchestration_loop",
            },
        ]
        interpretation = [
            "This is the narrowest orchestration-loop routing surface in the internal hot-news stack.",
            "An outer orchestrator can stop here without reading lower orchestration packet layers unless it needs deeper detail.",
        ]
        return V134TXAShareTWInternalHotNewsProgramOrchestrationLoopDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TXAShareTWInternalHotNewsProgramOrchestrationLoopDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TXAShareTWInternalHotNewsProgramOrchestrationLoopDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tx_a_share_tw_internal_hot_news_program_orchestration_loop_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
