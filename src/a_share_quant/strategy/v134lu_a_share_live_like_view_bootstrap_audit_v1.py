from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.serving.live_like.materialize_a_share_live_like_view_bootstrap_v1 import (
    MaterializeAShareLiveLikeViewBootstrapV1,
)


@dataclass(slots=True)
class V134LUAShareLiveLikeViewBootstrapAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LUAShareLiveLikeViewBootstrapAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_live_like_view_bootstrap_status_v1.csv"

    def analyze(self) -> V134LUAShareLiveLikeViewBootstrapAuditV1Report:
        materialized = MaterializeAShareLiveLikeViewBootstrapV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "live_like_view_registry",
                "component_state": "materialized_but_blocked",
                "artifact_path": summary["registry_path"],
                "coverage_note": f"closed_gate_count = {summary['closed_gate_count']}",
            },
            {
                "component": "live_like_event_state_surface",
                "component_state": "materialized_but_blocked",
                "artifact_path": summary["event_state_path"],
                "coverage_note": f"event_state_row_count = {summary['event_state_row_count']}",
            },
            {
                "component": "live_like_gate_view",
                "component_state": "materialized_but_blocked",
                "artifact_path": summary["gate_view_path"],
                "coverage_note": f"candidate_context_blocked_count = {summary['candidate_context_blocked_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lu_a_share_live_like_view_bootstrap_audit_v1",
            "event_state_row_count": summary["event_state_row_count"],
            "candidate_intraday_only_watch_count": summary["candidate_intraday_only_watch_count"],
            "candidate_context_blocked_count": summary["candidate_context_blocked_count"],
            "closed_gate_count": summary["closed_gate_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_live_like_views_materialized_but_still_blocked",
        }
        interpretation = [
            "Live-like no longer lacks views; it now has a concrete event-state surface and gate surface.",
            "Those views are still blocked by closed gates, but the blocker is now policy and readiness, not missing materialization.",
        ]
        return V134LUAShareLiveLikeViewBootstrapAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LUAShareLiveLikeViewBootstrapAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LUAShareLiveLikeViewBootstrapAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lu_a_share_live_like_view_bootstrap_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
