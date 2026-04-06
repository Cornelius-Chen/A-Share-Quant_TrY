from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123VCpoDrawdownControlPriorityFreezeReport:
    summary: dict[str, Any]
    priority_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "priority_rows": self.priority_rows,
            "interpretation": self.interpretation,
        }


class V123VCpoDrawdownControlPriorityFreezeAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v123u_payload: dict[str, Any]) -> V123VCpoDrawdownControlPriorityFreezeReport:
        heat_intervals = [row for row in v123u_payload["interval_rows"] if row["primary_driver"] == "position_heat"]
        residual_intervals = [
            row for row in v123u_payload["interval_rows"] if row["primary_driver"] == "held_pair_residual_deterioration"
        ]

        priority_rows = [
            {
                "priority_rank": 1,
                "control_layer": "position_heat_guardrail",
                "why_now": "dominates_two_of_three_major_drawdowns_and_already_has_real_interval_improvement",
                "authoritative_posture": "keep_balanced_and_strict_as_primary_control_refs",
            },
            {
                "priority_rank": 2,
                "control_layer": "board_risk_off_reduce_prior",
                "why_now": "still_the_only_live_reduce_side_candidate_even_if_broad",
                "authoritative_posture": "candidate_only_non_replay",
            },
            {
                "priority_rank": 3,
                "control_layer": "held_pair_residual_soft_penalty",
                "why_now": "explains_the_non_overheated_third_drawdown_but_is_too_narrow_for_candidate_budget",
                "authoritative_posture": "soft_component_only",
            },
            {
                "priority_rank": 4,
                "control_layer": "market_regime_overlay",
                "why_now": "helps_explain_risk_but_is_not_evaluable_enough_for_execution_use",
                "authoritative_posture": "explanatory_only",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v123v_cpo_drawdown_control_priority_freeze_v1",
            "heat_dominated_interval_count": len(heat_intervals),
            "residual_dominated_interval_count": len(residual_intervals),
            "top_control_priority": "position_heat_guardrail",
            "recommended_next_posture": "focus_next_execution_work_on_heat_plus_reduce_prior_not_on_new_family_discovery",
        }
        interpretation = [
            "V1.23V freezes a control-layer priority order after the drawdown attribution matrix.",
            "This is meant to stop the project from opening more side branches before the main risk-control stack is ordered correctly.",
            "The order is driven by what actually explains the three largest research-baseline drawdowns, not by pooled factor aesthetics.",
        ]
        return V123VCpoDrawdownControlPriorityFreezeReport(
            summary=summary,
            priority_rows=priority_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123VCpoDrawdownControlPriorityFreezeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123u_cpo_drawdown_risk_layer_attribution_matrix_v1.json").read_text(
            encoding="utf-8"
        )
    )
    analyzer = V123VCpoDrawdownControlPriorityFreezeAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v123u_payload=payload)
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123v_cpo_drawdown_control_priority_freeze_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
