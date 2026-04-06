from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134te_a_share_internal_hot_news_program_control_loop_runtime_envelope_audit_v1 import (
    V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer,
)


@dataclass(slots=True)
class V134TFAShareTEInternalHotNewsProgramControlLoopRuntimeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134TFAShareTEInternalHotNewsProgramControlLoopRuntimeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TFAShareTEInternalHotNewsProgramControlLoopRuntimeDirectionTriageV1Report:
        report = V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "envelope_row_count": report.summary["envelope_row_count"],
            "runtime_consumer_mode": report.summary["runtime_consumer_mode"],
            "runtime_attention_level": report.summary["runtime_attention_level"],
            "suggested_poll_interval_seconds": report.summary["suggested_poll_interval_seconds"],
            "reopen_target": report.summary["reopen_target"],
            "authoritative_status": "continue_serving_control-loop_runtime-envelope_above_the_narrow_control-loop_signal",
        }
        triage_rows = [
            {
                "component": "passive_runtime_branch",
                "direction": "keep_longer_polling_intervals_when_runtime_consumer_mode_stays_passive_polling_only",
            },
            {
                "component": "elevated_runtime_branch",
                "direction": "shorten_polling_and_reopen_the_requested_target_when_runtime_consumer_mode_rotates_into_elevate_and_reopen_or_elevate_polling",
            },
            {
                "component": "interrupt_runtime_branch",
                "direction": "drop_poll_interval_to_zero_and_interrupt_the_current_loop_when_runtime_consumer_mode_rotates_into_interrupt_and_reopen",
            },
        ]
        interpretation = [
            "This is the execution-facing runtime envelope above the narrow control-loop signal.",
            "A consumer can use it to derive polling cadence and escalation behavior without reinterpreting lower layers.",
        ]
        return V134TFAShareTEInternalHotNewsProgramControlLoopRuntimeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TFAShareTEInternalHotNewsProgramControlLoopRuntimeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TFAShareTEInternalHotNewsProgramControlLoopRuntimeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134tf_a_share_te_internal_hot_news_program_control_loop_runtime_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
