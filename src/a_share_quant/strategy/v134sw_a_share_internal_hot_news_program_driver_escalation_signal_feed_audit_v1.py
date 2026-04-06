from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_driver_escalation_signal_feed_v1 import (
    MaterializeAShareInternalHotNewsProgramDriverEscalationSignalFeedV1,
)


@dataclass(slots=True)
class V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramDriverEscalationSignalFeedV1(self.repo_root).materialize()
        rows = [
            {
                "component": "driver_escalation_signal_feed",
                "component_state": "read_ready_internal_only",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "signal_feed_mode",
                "component_state": "materialized",
                "metric": "signal_feed_mode",
                "value": materialized.summary["signal_feed_mode"],
            },
            {
                "component": "interrupt_required",
                "component_state": "materialized",
                "metric": "interrupt_required",
                "value": materialized.summary["interrupt_required"],
            },
            {
                "component": "alert_state",
                "component_state": "materialized",
                "metric": "alert_state",
                "value": materialized.summary["alert_state"],
            },
        ]
        interpretation = [
            "This is the narrowest program-facing alert feed in the internal hot-news stack.",
            "A consumer that only cares about whether it should stay passive, elevate attention, or interrupt can stop at this layer.",
        ]
        return V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SWAShareInternalHotNewsProgramDriverEscalationSignalFeedAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sw_a_share_internal_hot_news_program_driver_escalation_signal_feed_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
