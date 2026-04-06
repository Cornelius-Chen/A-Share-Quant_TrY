from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sw_a_share_internal_hot_news_program_driver_escalation_signal_feed_audit_v1 import (
    V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Report:
        report = V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "signal_row_count": report.summary["signal_row_count"],
            "signal_feed_mode": report.summary["signal_feed_mode"],
            "interrupt_required": report.summary["interrupt_required"],
            "alert_state": report.summary["alert_state"],
            "authoritative_status": "continue_serving_driver-escalation_signal-feed_above_the_driver-alert_surface",
        }
        triage_rows = [
            {
                "component": "passive_polling_branch",
                "direction": "stay_on_passive_polling_when_signal_feed_mode_remains_passive_polling",
            },
            {
                "component": "elevate_attention_branch",
                "direction": "raise_operator_or_program_attention_when_signal_feed_mode_rotates_to_elevate_attention",
            },
            {
                "component": "interrupt_branch",
                "direction": "interrupt_the_current_consumer_loop_immediately_when_signal_feed_mode_rotates_to_interrupt",
            },
        ]
        interpretation = [
            "This feed compresses driver escalation semantics into the smallest program-facing branch surface.",
            "A consumer can use it as a direct switch between passive polling, elevated attention, and interruption.",
        ]
        return V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SXAShareSWInternalHotNewsProgramDriverSignalFeedDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sx_a_share_sw_internal_hot_news_program_driver_signal_feed_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
