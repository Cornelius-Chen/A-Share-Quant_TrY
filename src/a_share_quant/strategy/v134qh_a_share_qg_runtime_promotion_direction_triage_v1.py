from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qg_a_share_runtime_promotion_candidate_surface_audit_v1 import (
    V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QHAShareQGRuntimePromotionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QHAShareQGRuntimePromotionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QHAShareQGRuntimePromotionDirectionTriageV1Report:
        report = V134QGAShareRuntimePromotionCandidateSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "priority_runtime_candidate_count": report.summary["priority_runtime_candidate_count"],
            "excluded_runtime_row_count": report.summary["excluded_runtime_row_count"],
            "authoritative_status": "runtime_promotion_should_follow_a_single_candidate_lane_not_flat_activation",
        }
        triage_rows = [
            {
                "component": "network_html_article_fetch",
                "direction": "treat_as_the_only_first_runtime_promotion_candidate_after_completed_manual_review",
            },
            {
                "component": "network_social_column_fetch",
                "direction": "retain_as_review_only_excluded_adapter",
            },
            {
                "component": "network_official_source_fetch",
                "direction": "retain_as_reserved_until_primary_official_hosts_exist",
            },
        ]
        interpretation = [
            "Runtime followthrough should now continue through a single candidate lane rather than through all adapters equally.",
            "This still does not open runtime promotion; it only narrows the remaining source-side work to one adapter family.",
        ]
        return V134QHAShareQGRuntimePromotionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134QHAShareQGRuntimePromotionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QHAShareQGRuntimePromotionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qh_a_share_qg_runtime_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
