from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lh_a_share_contradiction_resolution_audit_v1 import (
    V134LHAShareContradictionResolutionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LIAShareLHContradictionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LIAShareLHContradictionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LIAShareLHContradictionDirectionTriageV1Report:
        audit = V134LHAShareContradictionResolutionAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "duplicate_merge_candidates",
                "direction": "freeze_as_current_deduplication_resolution_surface",
            },
            {
                "component": "semantic_divergence",
                "direction": "retain_review_queue_for_future_real_conflict_sources",
            },
            {
                "component": "residual_backlog",
                "direction": "retain_only_for_events_not_yet_promoted_through_graph_resolution",
            },
        ]
        summary = {
            "duplicate_merge_candidate_count": audit.summary["duplicate_merge_candidate_count"],
            "semantic_divergence_count": audit.summary["semantic_divergence_count"],
            "review_queue_count": audit.summary["review_queue_count"],
            "authoritative_status": "contradiction_resolution_complete_enough_to_freeze_as_bootstrap",
        }
        interpretation = [
            "The quality layer now has a first-pass contradiction graph, which removes pure duplication noise from future review work.",
            "Real semantic contradiction handling remains open, but the backlog is now structured instead of flat.",
        ]
        return V134LIAShareLHContradictionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LIAShareLHContradictionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LIAShareLHContradictionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134li_a_share_lh_contradiction_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
