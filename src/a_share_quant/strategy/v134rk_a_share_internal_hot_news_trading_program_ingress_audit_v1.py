from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_trading_program_ingress_v1 import (
    MaterializeAShareInternalHotNewsTradingProgramIngressV1,
)


@dataclass(slots=True)
class V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsTradingProgramIngressV1(self.repo_root).materialize()
        rows = [
            {
                "component": "trading_program_ingress",
                "component_state": "read_ready_internal_only",
                "metric": "ingress_row_count",
                "value": str(materialized.summary["ingress_row_count"]),
            },
            {
                "component": "important_ingress",
                "component_state": "materialized",
                "metric": "important_ingress_count",
                "value": str(materialized.summary["important_ingress_count"]),
            },
            {
                "component": "board_specific_ingress",
                "component_state": "materialized",
                "metric": "board_specific_ingress_count",
                "value": str(materialized.summary["board_specific_ingress_count"]),
            },
            {
                "component": "hot_window_status",
                "component_state": "materialized",
                "metric": "active_hot_window_count",
                "value": str(materialized.summary["active_hot_window_count"]),
            },
            {
                "component": "impact_window_attachment",
                "component_state": "materialized",
                "metric": "impact_window_attached_count",
                "value": str(materialized.summary["impact_window_attached_count"]),
            },
            {
                "component": "context_velocity",
                "component_state": "materialized",
                "metric": "accelerating_ingress_count",
                "value": str(materialized.summary["accelerating_ingress_count"]),
            },
            {
                "component": "impact_decay",
                "component_state": "materialized",
                "metric": "late_impact_window_count",
                "value": str(materialized.summary["late_impact_window_count"]),
            },
            {
                "component": "focus_scoring",
                "component_state": "materialized",
                "metric": "focus_scored_ingress_count",
                "value": str(materialized.summary["focus_scored_ingress_count"]),
            },
            {
                "component": "focus_scoring",
                "component_state": "materialized",
                "metric": "top_focus_theme_slug",
                "value": materialized.summary["top_focus_theme_slug"],
            },
        ]
        interpretation = [
            "The hot-news line now emits a single ingress surface for downstream trading programs.",
            "Priority, importance, routing, direction, strength, mapping status, hot-window retention status, rolling context memory, and dynamic velocity/impact-decay states are already folded into one internal-only consumer view.",
            "Focus-cycle scoring is now already folded into ingress, so lower consumers can see persistence, second-wave bias, and tradability before opportunity routing.",
        ]
        return V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RKAShareInternalHotNewsTradingProgramIngressAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rk_a_share_internal_hot_news_trading_program_ingress_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
