from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.review_jobs.materialize_a_share_review_activation_v1 import (
    MaterializeAShareReviewActivationV1,
)


@dataclass(slots=True)
class V134LQAShareReviewActivationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LQAShareReviewActivationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_review_activation_status_v1.csv"

    def analyze(self) -> V134LQAShareReviewActivationAuditV1Report:
        materialized = MaterializeAShareReviewActivationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "review_activation_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["registry_path"],
                "coverage_note": f"review_registry_count = {summary['review_registry_count']}",
            },
            {
                "component": "low_confidence_event_queue",
                "component_state": "active_bootstrap_queue",
                "artifact_path": summary["low_conf_path"],
                "coverage_note": f"low_confidence_queue_count = {summary['low_confidence_queue_count']}",
            },
            {
                "component": "contradiction_queue",
                "component_state": "active_bootstrap_queue",
                "artifact_path": summary["contradiction_path"],
                "coverage_note": f"contradiction_queue_count = {summary['contradiction_queue_count']}",
            },
            {
                "component": "attention_soft_candidate_queue",
                "component_state": "active_bootstrap_queue",
                "artifact_path": summary["attention_queue_path"],
                "coverage_note": f"attention_soft_queue_count = {summary['attention_soft_queue_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lq_a_share_review_activation_audit_v1",
            "review_registry_count": summary["review_registry_count"],
            "low_confidence_queue_count": summary["low_confidence_queue_count"],
            "contradiction_queue_count": summary["contradiction_queue_count"],
            "attention_soft_queue_count": summary["attention_soft_queue_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_review_activation_ready_for_direction_triage",
        }
        interpretation = [
            "Review is no longer just a job contract. The information center now materializes real bootstrap queues for low-confidence events, contradictions, and soft attention candidates.",
            "This is the minimum human-in-the-loop layer needed before more aggressive source activation and live-like gates can be considered.",
        ]
        return V134LQAShareReviewActivationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LQAShareReviewActivationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LQAShareReviewActivationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lq_a_share_review_activation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
