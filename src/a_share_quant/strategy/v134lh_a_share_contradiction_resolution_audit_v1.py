from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.quality.materialize_a_share_contradiction_resolution_v1 import (
    MaterializeAShareContradictionResolutionV1,
)


@dataclass(slots=True)
class V134LHAShareContradictionResolutionAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LHAShareContradictionResolutionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_contradiction_resolution_status_v1.csv"

    def analyze(self) -> V134LHAShareContradictionResolutionAuditV1Report:
        materialized = MaterializeAShareContradictionResolutionV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "contradiction_graph",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["graph_path"],
                "coverage_note": f"registry_group_count = {summary['registry_group_count']}",
            },
            {
                "component": "review_queue",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["review_path"],
                "coverage_note": f"review_queue_count = {summary['review_queue_count']}",
            },
            {
                "component": "residual_backlog",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"residual_count = {summary['residual_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lh_a_share_contradiction_resolution_audit_v1",
            "registry_group_count": summary["registry_group_count"],
            "duplicate_merge_candidate_count": summary["duplicate_merge_candidate_count"],
            "semantic_divergence_count": summary["semantic_divergence_count"],
            "review_queue_count": summary["review_queue_count"],
            "residual_count": summary["residual_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_contradiction_resolution_ready_for_direction_triage",
        }
        interpretation = [
            "This closes the first quality contradiction backlog by separating duplicate-materialization cases from true semantic divergence review.",
            "The result is a reusable contradiction graph and review queue, rather than a flat unreviewed backlog.",
        ]
        return V134LHAShareContradictionResolutionAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LHAShareContradictionResolutionAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LHAShareContradictionResolutionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lh_a_share_contradiction_resolution_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
