from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_focus_governance_tension_change_signal_v1 import (
    MaterializeAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1,
)


@dataclass(slots=True)
class V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsFocusGovernanceTensionChangeSignalV1(
            self.repo_root
        ).materialize()
        rows = [
            {
                "component": "tension_change_signal",
                "component_state": "materialized",
                "metric": "signal_row_count",
                "value": str(materialized.summary["signal_row_count"]),
            },
            {
                "component": "tension_change_signal",
                "component_state": "materialized",
                "metric": "current_primary_rank_change",
                "value": materialized.summary["current_primary_rank_change"],
            },
            {
                "component": "tension_change_signal",
                "component_state": "materialized",
                "metric": "tension_state_change",
                "value": materialized.summary["tension_state_change"],
            },
            {
                "component": "tension_change_signal",
                "component_state": "materialized",
                "metric": "tension_priority_change",
                "value": materialized.summary["tension_priority_change"],
            },
        ]
        interpretation = [
            "This change layer lets the top stack react when governance tension itself changes, not only when raw focus references rotate.",
            "It is useful for detecting when ranking-vs-policy disagreement begins, escalates, or resolves.",
        ]
        return V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer(
        repo_root
    ).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135as_a_share_internal_hot_news_focus_governance_tension_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
