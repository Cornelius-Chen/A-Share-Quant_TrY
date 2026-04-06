from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134og_a_share_batch_one_manual_review_workpack_audit_v1 import (
    V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OHAShareOGManualReviewWorkpackDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134OHAShareOGManualReviewWorkpackDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134OHAShareOGManualReviewWorkpackDirectionTriageV1Report:
        report = V134OGAShareBatchOneManualReviewWorkpackAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "workpack_row_count": report.summary["workpack_row_count"],
            "pending_manual_field_row_count": report.summary["pending_manual_field_row_count"],
            "authoritative_status": "batch_one_manual_closure_should_now_use_consolidated_workpack_surface",
        }
        triage_rows = [
            {
                "component": "workpack_usage",
                "direction": "use_single_workpack_surface_as_the_entrypoint_for_batch_one_manual_review",
            },
            {
                "component": "record_fill",
                "direction": "fill_review_record_fields_from_workpack_without_reopening_source_lookup",
            },
            {
                "component": "promotion_gate",
                "direction": "keep_allowlist_promotion_closed_until_workpack_backed_records_are_completed",
            },
        ]
        interpretation = [
            "Batch-one manual review no longer needs new structure; it needs record filling against the consolidated workpack.",
            "This is the most concrete remaining internal source-side artifact before actual manual decisions.",
        ]
        return V134OHAShareOGManualReviewWorkpackDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OHAShareOGManualReviewWorkpackDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OHAShareOGManualReviewWorkpackDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oh_a_share_og_manual_review_workpack_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
