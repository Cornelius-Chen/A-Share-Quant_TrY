from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pr_a_share_shadow_calendar_alignment_candidate_audit_v1 import (
    V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Report:
        report = V134PRAShareShadowCalendarAlignmentCandidateAuditV1Analyzer(self.repo_root).analyze()
        candidate_row = report.rows[0]
        summary = {
            "candidate_row_count": report.summary["candidate_row_count"],
            "candidate_effective_trade_date": candidate_row["candidate_effective_trade_date"],
            "authoritative_status": "shadow_calendar_alignment_should_be_treated_as_auxiliary_shadow_only_candidate_not_timestamp_override",
        }
        triage_rows = [
            {
                "component": "pti_timestamp_policy",
                "direction": "retain_original_visible_event_timestamp_without_rewriting_pti_history",
            },
            {
                "component": "shadow_alignment_candidate",
                "direction": "allow_an_auxiliary_effective_trade_date_candidate_for_shadow_market_context_only",
            },
            {
                "component": "governance_boundary",
                "direction": "keep_calendar_alignment_in_shadow_only_scope_and_do_not_use_it_as_execution_authority",
            },
        ]
        interpretation = [
            "The off-calendar slice can be inspected without corrupting PTI legality.",
            "The cleanest next move is a shadow-only effective-trade-date candidate, not a rewrite of event time history.",
        ]
        return V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ps_a_share_pr_shadow_calendar_alignment_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
