from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135aq_a_share_internal_hot_news_focus_governance_tension_packet_audit_v1 import (
    V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer,
)


@dataclass(slots=True)
class V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Report:
        report = V135AQAShareInternalHotNewsFocusGovernanceTensionPacketAuditV1Analyzer(
            self.repo_root
        ).analyze()
        summary = {
            "current_primary_theme_slug": report.summary["current_primary_theme_slug"],
            "current_primary_rank": report.summary["current_primary_rank"],
            "leader_theme_slug": report.summary["leader_theme_slug"],
            "review_state": report.summary["review_state"],
            "tension_state": report.summary["tension_state"],
            "tension_priority": report.summary["tension_priority"],
            "authoritative_status": "focus_governance_tension_packet_materialized",
        }
        triage_rows = [
            {
                "component": "governance_explanation",
                "direction": "use the tension packet to explain when leaderboard rank and review policy disagree, instead of treating that mismatch as a silent inconsistency.",
            },
            {
                "component": "rotation_discipline",
                "direction": "keep rotation gated by review policy even when the incumbent is no longer leader, unless the tension state itself escalates.",
            },
            {
                "component": "attention_routing",
                "direction": "route p2 or above tension states to higher-level review surfaces; keep p3 tension in background monitoring.",
            },
        ]
        interpretation = [
            "This packet turns an implicit governance nuance into an explicit top-level state.",
            "It is especially useful when support counts are tied or near-tied and rank ordering alone would overstate the need to rotate.",
        ]
        return V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ARAShareAQInternalHotNewsFocusGovernanceTensionDirectionTriageV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ar_a_share_aq_internal_hot_news_focus_governance_tension_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
