from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_governance_tension_packet_v1 import (
    MaterializeAShareInternalHotNewsFocusGovernanceTensionPacketV1,
)


@dataclass(slots=True)
class V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsFocusGovernanceTensionPacketV1(
            self.repo_root
        ).materialize()
        rows = [
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "current_primary_rank",
                "value": str(materialized.summary["current_primary_rank"]),
            },
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "incumbent_is_leader",
                "value": materialized.summary["incumbent_is_leader"],
            },
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "review_state",
                "value": materialized.summary["review_state"],
            },
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "tension_state",
                "value": materialized.summary["tension_state"],
            },
            {
                "component": "focus_governance_tension",
                "component_state": "materialized",
                "metric": "tension_priority",
                "value": materialized.summary["tension_priority"],
            },
        ]
        interpretation = [
            "This packet makes leaderboard-vs-review tension explicit instead of leaving it implicit in separate ranking and review tables.",
            "It helps the top control layer explain why the incumbent may still be held even when it is no longer rank one.",
        ]
        return V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135aq_a_share_internal_hot_news_focus_governance_tension_packet_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
