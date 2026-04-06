from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135as_a_share_internal_hot_news_focus_governance_tension_change_signal_audit_v1 import (
    V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer,
)


@dataclass(slots=True)
class V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Report:
        report = V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer(
            self.repo_root
        ).analyze()
        summary = {
            "current_primary_rank_change": report.summary["current_primary_rank_change"],
            "incumbent_is_leader_change": report.summary["incumbent_is_leader_change"],
            "review_state_change": report.summary["review_state_change"],
            "tension_state_change": report.summary["tension_state_change"],
            "tension_priority_change": report.summary["tension_priority_change"],
            "signal_priority": report.summary["signal_priority"],
            "authoritative_status": "focus_governance_tension_change_signal_materialized",
        }
        triage_rows = [
            {
                "component": "tension_monitoring",
                "direction": "watch this layer when you care about governance friction changing even if the incumbent symbol itself has not rotated.",
            },
            {
                "component": "review_triggering",
                "direction": "treat tension-state changes as a separate escalation path from direct focus rotation signals.",
            },
            {
                "component": "top_level_routing",
                "direction": "promote p1 tension changes upward; keep p2/p3 tension changes in review-aware polling.",
            },
        ]
        interpretation = [
            "This signal separates governance friction changes from direct focus swaps.",
            "It helps avoid conflating 'the focus changed' with 'the policy around the focus became unstable'.",
        ]
        return V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ATAShareASInternalHotNewsFocusGovernanceTensionChangeDirectionTriageV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135at_a_share_as_internal_hot_news_focus_governance_tension_change_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
