from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123XCpoUvwControlIntegrationTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V123XCpoUvwControlIntegrationTriageAnalyzer:
    def analyze(self) -> V123XCpoUvwControlIntegrationTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "downgrade_riskoff_execution_use",
                "reason": "combination_is_massively_over_defensive_and_heat_only_remains_best_tradeoff",
                "recommended_next_step": "keep_heat_replay_facing_and_push_riskoff_back_to_soft_or_explanatory_gating",
            },
            {
                "reviewer": "Tesla",
                "verdict": "downgrade_riskoff_execution_use",
                "reason": "riskoff_prior_compresses_drawdown_but_destroys_return_too_hard_for_execution_use",
                "recommended_next_step": "retain_only_as_narrower_non_replay_reduce_prior_until_misfire_rate_falls",
            },
            {
                "reviewer": "James",
                "verdict": "downgrade_riskoff_execution_use",
                "reason": "heat_only_still_wins_objective_while_riskoff_execution_variants_collapse_final_equity",
                "recommended_next_step": "keep_heat_primary_and_demote_riskoff_execution_back_to_non_replay_soft_use",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v123x_cpo_uvw_control_integration_triage_v1",
            "related_runs": ["V123U", "V123V", "V123W"],
            "authoritative_status": "downgrade_riskoff_execution_use",
            "majority_vote": {"downgrade_riskoff_execution_use": 3},
            "heat_replay_facing_allowed": True,
            "riskoff_replay_facing_allowed": False,
            "recommended_next_posture": "keep_heat_as_primary_execution_control_and_return_board_risk_off_to_non_replay_soft_prior_status",
        }
        interpretation = [
            "V1.23X freezes the first explicit execution integration verdict for the ordered risk-control stack.",
            "The result is unambiguous: heat guardrails remain the only replay-facing control worth keeping, while board_risk_off_reduce_prior is too broad and over-defensive in execution form.",
            "Future downside work should narrow risk-off further before trying execution attachment again.",
        ]
        return V123XCpoUvwControlIntegrationTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123XCpoUvwControlIntegrationTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123XCpoUvwControlIntegrationTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123x_cpo_uvw_control_integration_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
