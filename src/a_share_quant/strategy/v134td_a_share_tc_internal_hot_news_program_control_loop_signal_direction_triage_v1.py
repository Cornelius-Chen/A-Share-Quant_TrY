from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134tc_a_share_internal_hot_news_program_control_loop_signal_feed_audit_v1 import (
    V134TCAShareInternalHotNewsProgramControlLoopSignalFeedAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TDAShareTCInternalHotNewsProgramControlLoopSignalDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TDAShareTCInternalHotNewsProgramControlLoopSignalDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TDAShareTCInternalHotNewsProgramControlLoopSignalDirectionTriageV1Report:
        report = V134TCAShareInternalHotNewsProgramControlLoopSignalFeedAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "loop_signal_mode": report.summary["loop_signal_mode"],
            "interrupt_required": report.summary["interrupt_required"],
            "reopen_target": report.summary["reopen_target"],
            "authoritative_status": "continue_serving_control-loop_signal-feed_above_the_control-packet_change_layer",
        }
        triage_rows = [
            {
                "component": "passive_branch",
                "direction": "stay_on_passive_polling_when_loop_signal_mode_remains_passive_polling",
            },
            {
                "component": "elevate_attention_branch",
                "direction": "raise_attention_and_reopen_the_target_surface_when_loop_signal_mode_rotates_to_elevate_attention",
            },
            {
                "component": "interrupt_branch",
                "direction": "interrupt_the_control_loop_immediately_when_loop_signal_mode_rotates_to_interrupt",
            },
        ]
        interpretation = [
            "This is the narrowest control-loop routing surface for the internal hot-news program.",
            "A consumer can stop here unless it is explicitly told to reopen the control packet or interrupt itself.",
        ]
        return V134TDAShareTCInternalHotNewsProgramControlLoopSignalDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TDAShareTCInternalHotNewsProgramControlLoopSignalDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TDAShareTCInternalHotNewsProgramControlLoopSignalDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134td_a_share_tc_internal_hot_news_program_control_loop_signal_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
