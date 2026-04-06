from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_status_surface_v1 import (
    MaterializeAShareInternalHotNewsProgramStatusSurfaceV1,
)


@dataclass(slots=True)
class V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramStatusSurfaceV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_status_surface",
                "component_state": "read_ready_internal_only",
                "metric": "status_row_count",
                "value": str(materialized.summary["status_row_count"]),
            },
            {
                "component": "program_health",
                "component_state": "materialized",
                "metric": "program_health_state",
                "value": materialized.summary["program_health_state"],
            },
            {
                "component": "global_action_mode",
                "component_state": "materialized",
                "metric": "global_program_action_mode",
                "value": materialized.summary["global_program_action_mode"],
            },
            {
                "component": "attention_gate",
                "component_state": "materialized",
                "metric": "needs_attention",
                "value": materialized.summary["needs_attention"],
            },
            {
                "component": "session_gate",
                "component_state": "materialized",
                "metric": "session_phase",
                "value": materialized.summary["session_phase"],
            },
            {
                "component": "session_confidence_gate",
                "component_state": "materialized",
                "metric": "session_phase_confidence",
                "value": materialized.summary["session_phase_confidence"],
            },
            {
                "component": "program_consumer_gate",
                "component_state": "materialized",
                "metric": "program_consumer_gate_mode",
                "value": materialized.summary["program_consumer_gate_mode"],
            },
            {
                "component": "program_driver_action",
                "component_state": "materialized",
                "metric": "program_driver_action_mode",
                "value": materialized.summary["program_driver_action_mode"],
            },
            {
                "component": "freshness_gate",
                "component_state": "materialized",
                "metric": "freshness_state",
                "value": materialized.summary["freshness_state"],
            },
            {
                "component": "heartbeat_timeout_gate",
                "component_state": "materialized",
                "metric": "heartbeat_timeout_state",
                "value": materialized.summary["heartbeat_timeout_state"],
            },
            {
                "component": "stale_alert_gate",
                "component_state": "materialized",
                "metric": "stale_alert_level",
                "value": materialized.summary["stale_alert_level"],
            },
        ]
        interpretation = [
            "The program now has a single health/status row above snapshot, action surface, and change signal.",
            "A downstream consumer can check one row first before deciding whether to inspect deeper feeds.",
            "The status row now exposes trade-calendar-backed timing plus freshness, timeout state, stale-alert level, one top-level consumer gate mode, and one program-driver action mode so the consumer can react without descending.",
        ]
        return V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SOAShareInternalHotNewsProgramStatusSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134so_a_share_internal_hot_news_program_status_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
