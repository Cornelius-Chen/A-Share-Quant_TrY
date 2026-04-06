from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pc_a_share_limit_halt_derivation_review_audit_v1 import (
    V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PDASharePCLimitHaltDerivationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PDASharePCLimitHaltDerivationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PDASharePCLimitHaltDerivationDirectionTriageV1Report:
        report = V134PCAShareLimitHaltDerivationReviewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "blocked_by_limit_halt_derivation_count": report.summary["blocked_by_limit_halt_derivation_count"],
            "promotable_now_count": report.summary["promotable_now_count"],
            "authoritative_status": "limit_halt_semantic_materialization_has_reopened_replay_promotion_recheck",
        }
        triage_rows = [
            {
                "component": "limit_halt_candidate_surface",
                "direction": "retain_raw_daily_candidate_surface_as_background_support_not_as_the_primary_replay_story",
            },
            {
                "component": "limit_halt_derivation",
                "direction": "retire_limit_halt_as_primary_blocker_and_use_the_semantic_surface_for_replay_recheck",
            },
            {
                "component": "daily_market_promotion",
                "direction": "treat_promotable_subset_as_the_new_replay-facing_entry_surface_while_keeping_named_residuals_explicit",
            },
        ]
        interpretation = [
            "The replay frontier has moved past the old index-daily source gap and past the old limit-halt derivation blocker.",
            "The next valid move is replay-side precondition recheck from the promotable subset, not more semantic source hunting on the limit-halt side.",
        ]
        return V134PDASharePCLimitHaltDerivationDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PDASharePCLimitHaltDerivationDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PDASharePCLimitHaltDerivationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pd_a_share_pc_limit_halt_derivation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
