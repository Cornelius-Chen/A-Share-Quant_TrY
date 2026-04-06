from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.quality.materialize_a_share_quality_foundation_v1 import (
    MaterializeAShareQualityFoundationV1,
)


@dataclass(slots=True)
class V134KIAShareQualityFoundationAuditV1Report:
    summary: dict[str, Any]
    quality_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "quality_rows": self.quality_rows,
            "interpretation": self.interpretation,
        }


class V134KIAShareQualityFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_quality_foundation_status_v1.csv"

    def analyze(self) -> V134KIAShareQualityFoundationAuditV1Report:
        materialized = MaterializeAShareQualityFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        quality_rows = [
            {
                "quality_component": "source_quality_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["source_quality_path"],
                "coverage_note": f"materialized_source_quality_count = {summary['materialized_source_quality_count']}",
            },
            {
                "quality_component": "event_quality_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["event_quality_path"],
                "coverage_note": f"materialized_event_quality_count = {summary['materialized_event_quality_count']}",
            },
            {
                "quality_component": "repost_control_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["repost_control_path"],
                "coverage_note": f"materialized_repost_control_count = {summary['materialized_repost_control_count']}",
            },
            {
                "quality_component": "contradiction_backlog",
                "component_state": "backlog_materialized_not_reviewed",
                "artifact_path": summary["contradiction_backlog_path"],
                "coverage_note": f"contradiction_backlog_count = {summary['contradiction_backlog_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(quality_rows[0].keys()))
            writer.writeheader()
            writer.writerows(quality_rows)

        report_summary = {
            "acceptance_posture": "build_v134ki_a_share_quality_foundation_audit_v1",
            "materialized_source_quality_count": summary["materialized_source_quality_count"],
            "materialized_event_quality_count": summary["materialized_event_quality_count"],
            "high_authority_source_count": summary["high_authority_source_count"],
            "bootstrap_evidence_gate_true_count": summary["bootstrap_evidence_gate_true_count"],
            "quality_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_quality_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KI completes the first quality workstream pass by transforming the bootstrapped event chain into explicit source quality, event quality, repost control, and contradiction backlog registries.",
            "Quality is still heuristic and bootstrap-grade, but it is now explicit and centrally consumable rather than hidden in ad hoc row-by-row interpretation.",
        ]
        return V134KIAShareQualityFoundationAuditV1Report(
            summary=report_summary,
            quality_rows=quality_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KIAShareQualityFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KIAShareQualityFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ki_a_share_quality_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
