from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_control_loop_runtime_envelope_v1 import (
    MaterializeAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1,
)


@dataclass(slots=True)
class V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeV1(self.repo_root).materialize()
        rows = [
            {
                "component": "runtime_envelope",
                "component_state": "read_ready_internal_only",
                "metric": "envelope_row_count",
                "value": str(materialized.summary["envelope_row_count"]),
            },
            {
                "component": "runtime_consumer_mode",
                "component_state": "materialized",
                "metric": "runtime_consumer_mode",
                "value": materialized.summary["runtime_consumer_mode"],
            },
            {
                "component": "runtime_attention_level",
                "component_state": "materialized",
                "metric": "runtime_attention_level",
                "value": materialized.summary["runtime_attention_level"],
            },
            {
                "component": "suggested_poll_interval",
                "component_state": "materialized",
                "metric": "suggested_poll_interval_seconds",
                "value": materialized.summary["suggested_poll_interval_seconds"],
            },
        ]
        interpretation = [
            "This runtime envelope converts the narrow control-loop signal into an execution-facing polling and reopening envelope.",
            "A consumer can stop here when it wants explicit polling cadence and attention level rather than raw signal semantics.",
        ]
        return V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134TEAShareInternalHotNewsProgramControlLoopRuntimeEnvelopeAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134te_a_share_internal_hot_news_program_control_loop_runtime_envelope_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
