from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_change_action_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramChangeActionSignalV1,
)


@dataclass(slots=True)
class V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramChangeActionSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_change_action_signal",
                "component_state": "read_ready_internal_only",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "top_risk_action_state",
                "component_state": "materialized",
                "metric": "top_risk_action_state",
                "value": materialized.summary["top_risk_action_state"],
            },
            {
                "component": "top_opportunity_action_state",
                "component_state": "materialized",
                "metric": "top_opportunity_action_state",
                "value": materialized.summary["top_opportunity_action_state"],
            },
            {
                "component": "global_program_action_mode_state",
                "component_state": "materialized",
                "metric": "global_program_action_mode_state",
                "value": materialized.summary["global_program_action_mode_state"],
            },
            {
                "component": "session_action_gate_state",
                "component_state": "materialized",
                "metric": "session_action_gate_state",
                "value": materialized.summary["session_action_gate_state"],
            },
        ]
        interpretation = [
            "The consumer can now distinguish unchanged action guidance from a real action-level rotation.",
            "This signal is thinner than the full action surface and now also reflects session-gate changes such as pre-open to live-session rotation.",
        ]
        return V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SMAShareInternalHotNewsProgramChangeActionSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sm_a_share_internal_hot_news_program_change_action_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
