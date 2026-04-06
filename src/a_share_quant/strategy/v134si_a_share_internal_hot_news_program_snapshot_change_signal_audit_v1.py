from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_snapshot_change_signal_v1 import (
    MaterializeAShareInternalHotNewsProgramSnapshotChangeSignalV1,
)


@dataclass(slots=True)
class V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramSnapshotChangeSignalV1(self.repo_root).materialize()
        rows = [
            {
                "component": "snapshot_change_signal",
                "component_state": "read_ready_internal_only",
                "metric": "change_row_count",
                "value": str(materialized.summary["change_row_count"]),
            },
            {
                "component": "top_risk_change",
                "component_state": "materialized",
                "metric": "top_risk_change_state",
                "value": materialized.summary["top_risk_change_state"],
            },
            {
                "component": "top_opportunity_change",
                "component_state": "materialized",
                "metric": "top_opportunity_change_state",
                "value": materialized.summary["top_opportunity_change_state"],
            },
            {
                "component": "session_change",
                "component_state": "materialized",
                "metric": "session_handling_mode_change",
                "value": materialized.summary["session_handling_mode_change"],
            },
            {
                "component": "signal_priority",
                "component_state": "materialized",
                "metric": "signal_priority",
                "value": materialized.summary["signal_priority"],
            },
        ]
        interpretation = [
            "The program can now distinguish a stable snapshot from a real top-risk or top-opportunity change.",
            "This change layer now also treats trading-day and session-handling transitions as first-class snapshot changes.",
        ]
        return V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134si_a_share_internal_hot_news_program_snapshot_change_signal_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
