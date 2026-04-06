from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134nk_a_share_batch_one_allowlist_review_surface_audit_v1 import (
    V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NLAShareNKBatchOneAllowlistDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NLAShareNKBatchOneAllowlistDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NLAShareNKBatchOneAllowlistDirectionTriageV1Report:
        report = V134NKAShareBatchOneAllowlistReviewSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "batch_one_source_count": report.summary["batch_one_source_count"],
            "host_review_unit_count": report.summary["host_review_unit_count"],
            "authoritative_status": "batch_one_allowlist_should_be_reviewed_by_host_units_not_promoted_yet",
        }
        triage_rows = [
            {
                "component": "primary_sina_family",
                "direction": "review_finance_sina_com_cn_first_as_primary_batch_one_host_family",
            },
            {
                "component": "sibling_sina_host",
                "direction": "keep_stock_finance_sina_com_cn_as_follow_on_review_after_primary_sina_family_outcome",
            },
            {
                "component": "independent_t2_hosts",
                "direction": "review_yicai_and_stcn_as_independent_batch_one_hosts_after_primary_sina_family",
            },
            {
                "component": "promotion_gate",
                "direction": "keep_all_batch_one_hosts_not_promoted_until_manual_license_review_records_exist",
            },
        ]
        interpretation = [
            "Batch-one now has a disciplined host-level review order, but still no automatic allowlist promotion.",
            "The next source-side gain should come from manual review records, not from reclassifying more hosts.",
        ]
        return V134NLAShareNKBatchOneAllowlistDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NLAShareNKBatchOneAllowlistDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NLAShareNKBatchOneAllowlistDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nl_a_share_nk_batch_one_allowlist_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
