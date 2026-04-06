from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qa_a_share_shadow_execution_eligible_subset_audit_v1 import (
    V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Report:
        report = V134QAAShareShadowExecutionEligibleSubsetAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "total_stub_row_count": report.summary["total_stub_row_count"],
            "eligible_subset_count": report.summary["eligible_subset_count"],
            "excluded_boundary_count": report.summary["excluded_boundary_count"],
            "authoritative_status": "shadow_execution_eligible_subset_is_useful_for_internal_replay_build_but_must_not_be_treated_as_execution_opening",
        }
        triage_rows = [
            {
                "component": "shadow_execution_eligible_subset",
                "direction": "retain_as_internal_replay_build_candidate_surface_for_the_15_date_bound_rows",
            },
            {
                "component": "excluded_boundary_rows",
                "direction": "retain_as_external_boundary_exclusions_and_do_not_force_internal_market_context_rebuild_for_them",
            },
            {
                "component": "promotion_boundary",
                "direction": "keep_this_subset_shadow_only_and_do_not_promote_it_into_execution_authority_or_live_like_opening",
            },
        ]
        interpretation = [
            "The eligible subset is useful because it finally separates replay-internal candidate rows from boundary-only exclusions.",
            "That separation improves internal build clarity, but it still does not justify opening live-like or execution.",
        ]
        return V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QBAShareQAShadowExecutionEligibleSubsetDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qb_a_share_qa_shadow_execution_eligible_subset_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
