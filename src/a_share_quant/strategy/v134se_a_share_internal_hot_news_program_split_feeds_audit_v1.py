from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_split_feeds_v1 import (
    MaterializeAShareInternalHotNewsProgramSplitFeedsV1,
)


@dataclass(slots=True)
class V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramSplitFeedsV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_risk_feed",
                "component_state": "read_ready_internal_only",
                "metric": "risk_feed_row_count",
                "value": str(materialized.summary["risk_feed_row_count"]),
            },
            {
                "component": "program_opportunity_feed",
                "component_state": "read_ready_internal_only",
                "metric": "opportunity_feed_row_count",
                "value": str(materialized.summary["opportunity_feed_row_count"]),
            },
            {
                "component": "critical_risk_feed",
                "component_state": "materialized",
                "metric": "critical_risk_count",
                "value": str(materialized.summary["critical_risk_count"]),
            },
            {
                "component": "critical_opportunity_feed",
                "component_state": "materialized",
                "metric": "critical_opportunity_count",
                "value": str(materialized.summary["critical_opportunity_count"]),
            },
            {
                "component": "timing_gate",
                "component_state": "materialized",
                "metric": "session_handling_mode",
                "value": materialized.summary["session_handling_mode"],
            },
            {
                "component": "risk_consumer_gate",
                "component_state": "materialized",
                "metric": "risk_consumer_gate",
                "value": materialized.summary["risk_consumer_gate"],
            },
            {
                "component": "opportunity_consumer_gate",
                "component_state": "materialized",
                "metric": "opportunity_consumer_gate",
                "value": materialized.summary["opportunity_consumer_gate"],
            },
            {
                "component": "opportunity_focus_scoring",
                "component_state": "materialized",
                "metric": "top_opportunity_theme_slug",
                "value": materialized.summary["top_opportunity_theme_slug"],
            },
            {
                "component": "opportunity_focus_scoring",
                "component_state": "materialized",
                "metric": "top_opportunity_focus_total_score",
                "value": materialized.summary["top_opportunity_focus_total_score"],
            },
        ]
        interpretation = [
            "The trading program no longer needs to split risk and opportunity messages itself.",
            "The minimal consumer view is now further decomposed into two narrower feeds: risk first and opportunity first, both with explicit session-handling context and direct consumer gates.",
            "Opportunity feed ordering now also reflects focus-cycle scoring, not just the earlier generic program-priority field.",
        ]
        return V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SEAShareInternalHotNewsProgramSplitFeedsAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134se_a_share_internal_hot_news_program_split_feeds_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
