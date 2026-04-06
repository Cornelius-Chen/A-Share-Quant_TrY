from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qc_a_share_shadow_execution_candidate_journal_overlay_audit_v1 import (
    V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer,
)


@dataclass(slots=True)
class V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Report:
        report = V134QCAShareShadowExecutionCandidateJournalOverlayAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "overlay_row_count": report.summary["overlay_row_count"],
            "excluded_boundary_count": report.summary["excluded_boundary_count"],
            "authoritative_status": "shadow_execution_candidate_journal_overlay_is_useful_for_internal_replay_build_but_must_remain_shadow_only",
        }
        triage_rows = [
            {
                "component": "candidate_journal_overlay",
                "direction": "retain_as_shadow_only_candidate_journal_surface_for_the_15_eligible_rows",
            },
            {
                "component": "boundary_exclusions",
                "direction": "retain_as_external_boundary_exclusions_outside_the_candidate_journal_overlay",
            },
            {
                "component": "promotion_boundary",
                "direction": "do_not_treat_the_candidate_journal_overlay_as_execution_opening_or_live_like_authority",
            },
        ]
        interpretation = [
            "The overlay is the first journal-shaped replay surface that excludes only the two external boundary rows.",
            "That improves internal replay build clarity, but it remains a shadow-only construct and not an execution permission layer.",
        ]
        return V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134QDAShareQCShadowExecutionCandidateJournalDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134qd_a_share_qc_shadow_execution_candidate_journal_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
