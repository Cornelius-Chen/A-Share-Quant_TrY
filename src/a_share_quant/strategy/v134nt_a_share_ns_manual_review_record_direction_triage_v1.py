from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ns_a_share_batch_one_manual_review_record_surface_audit_v1 import (
    V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NTAShareNSManualReviewRecordDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NTAShareNSManualReviewRecordDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NTAShareNSManualReviewRecordDirectionTriageV1Report:
        report = V134NSAShareBatchOneManualReviewRecordSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "record_row_count": report.summary["record_row_count"],
            "pending_record_count": report.summary["pending_record_count"],
            "authoritative_status": "manual_review_records_should_be_filled_before_any_batch_one_promotion",
        }
        triage_rows = [
            {
                "component": "record_fields",
                "direction": "retain_explicit_terms_robots_risk_scope_and_outcome_fields_for_each_host_unit",
            },
            {
                "component": "record_order",
                "direction": "fill_primary_host_family_record_first_then_follow_priority_order",
            },
            {
                "component": "promotion_dependency",
                "direction": "keep_allowlist_promotion_closed_until_manual_record_fields_stop_being_pending",
            },
        ]
        interpretation = [
            "The next source-side gain now depends on filling standardized manual review records.",
            "This reduces future decision drift because all host reviews must pass through the same fields.",
        ]
        return V134NTAShareNSManualReviewRecordDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NTAShareNSManualReviewRecordDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NTAShareNSManualReviewRecordDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nt_a_share_ns_manual_review_record_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
