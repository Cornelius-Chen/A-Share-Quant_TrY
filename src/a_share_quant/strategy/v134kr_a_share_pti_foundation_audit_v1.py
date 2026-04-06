from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.pti.ledger.materialize_a_share_pti_foundation_v1 import (
    MaterializeASharePTIFoundationV1,
)


@dataclass(slots=True)
class V134KRASharePTIFoundationAuditV1Report:
    summary: dict[str, Any]
    pti_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "pti_rows": self.pti_rows,
            "interpretation": self.interpretation,
        }


class V134KRASharePTIFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_pti_foundation_status_v1.csv"

    def analyze(self) -> V134KRASharePTIFoundationAuditV1Report:
        materialized = MaterializeASharePTIFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        pti_rows = [
            {
                "pti_component": "event_ledger",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["event_ledger_path"],
                "coverage_note": f"event_ledger_count = {summary['event_ledger_count']}",
            },
            {
                "pti_component": "time_slice_view",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["time_slice_path"],
                "coverage_note": f"time_slice_count = {summary['time_slice_count']}",
            },
            {
                "pti_component": "state_transition_journal",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["state_transition_path"],
                "coverage_note": f"state_transition_count = {summary['state_transition_count']}",
            },
            {
                "pti_component": "transition_backlog",
                "component_state": "backlog_materialized_not_bound_to_replay",
                "artifact_path": summary["transition_backlog_path"],
                "coverage_note": f"transition_backlog_count = {summary['transition_backlog_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(pti_rows[0].keys()))
            writer.writeheader()
            writer.writerows(pti_rows)

        report_summary = {
            "acceptance_posture": "build_v134kr_a_share_pti_foundation_audit_v1",
            "event_ledger_count": summary["event_ledger_count"],
            "time_slice_count": summary["time_slice_count"],
            "state_transition_count": summary["state_transition_count"],
            "pti_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_pti_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KR completes the first PTI workstream pass by materializing a visible-time event ledger, a time-slice surface, and a bootstrap state transition journal.",
            "This is intentionally narrower than a full trading state machine: it captures legal visibility and bootstrap semantic transitions without pretending execution states already exist.",
        ]
        return V134KRASharePTIFoundationAuditV1Report(
            summary=report_summary,
            pti_rows=pti_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KRASharePTIFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KRASharePTIFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kr_a_share_pti_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
