from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_driver_escalation_alert_v1 import (
    MaterializeAShareInternalHotNewsProgramDriverEscalationAlertV1,
)


@dataclass(slots=True)
class V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramDriverEscalationAlertV1(self.repo_root).materialize()
        rows = [
            {
                "component": "driver_escalation_alert",
                "component_state": "read_ready_internal_only",
                "metric": "alert_row_count",
                "value": str(materialized.summary["alert_row_count"]),
            },
            {
                "component": "driver_transition",
                "component_state": "materialized",
                "metric": "program_driver_transition_class",
                "value": materialized.summary["program_driver_transition_class"],
            },
            {
                "component": "driver_escalation_priority",
                "component_state": "materialized",
                "metric": "driver_escalation_priority",
                "value": materialized.summary["driver_escalation_priority"],
            },
            {
                "component": "alert_state",
                "component_state": "materialized",
                "metric": "alert_state",
                "value": materialized.summary["alert_state"],
            },
        ]
        interpretation = [
            "This layer sits above the outermost status-change signal and isolates only driver-mode escalation semantics.",
            "A consumer can subscribe here when it only cares about operating-mode jumps such as entering prepare, live_route, or stale_block.",
        ]
        return V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134su_a_share_internal_hot_news_program_driver_escalation_alert_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
