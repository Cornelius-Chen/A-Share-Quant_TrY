from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_trading_program_minimal_view_v1 import (
    MaterializeAShareInternalHotNewsTradingProgramMinimalViewV1,
)


@dataclass(slots=True)
class V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsTradingProgramMinimalViewV1(self.repo_root).materialize()
        rows = [
            {
                "component": "minimal_consumer_view",
                "component_state": "read_ready_internal_only",
                "metric": "minimal_view_row_count",
                "value": str(materialized.summary["minimal_view_row_count"]),
            },
            {
                "component": "risk_guardrail",
                "component_state": "materialized",
                "metric": "risk_guardrail_count",
                "value": str(materialized.summary["risk_guardrail_count"]),
            },
            {
                "component": "top_down_guidance",
                "component_state": "materialized",
                "metric": "top_down_guidance_count",
                "value": str(materialized.summary["top_down_guidance_count"]),
            },
            {
                "component": "board_watch_trigger",
                "component_state": "materialized",
                "metric": "board_watch_trigger_count",
                "value": str(materialized.summary["board_watch_trigger_count"]),
            },
            {
                "component": "symbol_focus",
                "component_state": "materialized",
                "metric": "symbol_focus_available_count",
                "value": str(materialized.summary["symbol_focus_available_count"]),
            },
            {
                "component": "timing_gate",
                "component_state": "materialized",
                "metric": "session_handling_mode",
                "value": materialized.summary["session_handling_mode"],
            },
        ]
        interpretation = [
            "The hot-news lane now exposes a compact trading-program view instead of forcing the consumer to read the full ingress surface.",
            "The minimal view keeps only routing-critical fields: priority, action class, focus class, timing window, signal direction, mapping confidence, and current session handling mode.",
        ]
        return V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SCAShareInternalHotNewsTradingProgramMinimalViewAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sc_a_share_internal_hot_news_trading_program_minimal_view_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
