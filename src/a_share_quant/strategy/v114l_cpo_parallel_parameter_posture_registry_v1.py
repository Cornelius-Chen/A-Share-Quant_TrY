from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114LCpoParallelParameterPostureRegistryReport:
    summary: dict[str, Any]
    posture_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "posture_rows": self.posture_rows,
            "interpretation": self.interpretation,
        }


class V114LCpoParallelParameterPostureRegistryAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114d_payload: dict[str, Any],
        v114e_payload: dict[str, Any],
        v114k_payload: dict[str, Any],
    ) -> V114LCpoParallelParameterPostureRegistryReport:
        summary_d = dict(v114d_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        summary_k = dict(v114k_payload.get("summary", {}))
        if str(summary_d.get("acceptance_posture")) != "freeze_v114d_cpo_stable_zone_replay_injection_v1":
            raise ValueError("V1.14L expects V1.14D stable-zone replay injection.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14L expects V1.14E default sizing replay promotion.")
        if str(summary_k.get("acceptance_posture")) != "freeze_v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1":
            raise ValueError("V1.14L expects V1.14K candidate audit replay.")

        d_rows = {str(row.get("candidate_name")): dict(row) for row in list(v114d_payload.get("candidate_rows", []))}
        default_row = dict(v114e_payload.get("promoted_default_row", {}))

        posture_rows = [
            {
                "posture_name": "default_expectancy_mainline",
                "status": "default_promoted",
                "source_run": "V114E",
                "curve": round(float(default_row.get("final_curve", 0.0)), 4),
                "max_drawdown": round(float(default_row.get("max_drawdown", 0.0)), 4),
                "capture_ratio_vs_board": round(float(default_row.get("capture_ratio_vs_board", 0.0)), 4),
                "config": dict(default_row.get("config", {})),
                "usage_rule": "current_default_cpo_sizing_surface",
            },
            {
                "posture_name": "conservative_guardrail",
                "status": "parallel_retained",
                "source_run": "V114D",
                "curve": round(float(d_rows.get("conservative_stable_injection", {}).get("final_curve", 0.0)), 4),
                "max_drawdown": round(float(d_rows.get("conservative_stable_injection", {}).get("max_drawdown", 0.0)), 4),
                "capture_ratio_vs_board": round(float(d_rows.get("conservative_stable_injection", {}).get("capture_ratio_vs_board", 0.0)), 4),
                "config": dict(d_rows.get("conservative_stable_injection", {}).get("config", {})),
                "usage_rule": "future_lower_drawdown_cross_board_candidate",
            },
            {
                "posture_name": "balanced_shadow",
                "status": "parallel_retained",
                "source_run": "V114D",
                "curve": round(float(d_rows.get("balanced_injection", {}).get("final_curve", 0.0)), 4),
                "max_drawdown": round(float(d_rows.get("balanced_injection", {}).get("max_drawdown", 0.0)), 4),
                "capture_ratio_vs_board": round(float(d_rows.get("balanced_injection", {}).get("capture_ratio_vs_board", 0.0)), 4),
                "config": dict(d_rows.get("balanced_injection", {}).get("config", {})),
                "usage_rule": "tie_case_reference_not_default",
            },
            {
                "posture_name": "vector_overlay_experimental",
                "status": "candidate_only",
                "source_run": "V114K",
                "curve": round(float(summary_k.get("candidate_curve", 0.0)), 4),
                "max_drawdown": round(float(summary_k.get("candidate_max_drawdown", 0.0)), 4),
                "capture_ratio_vs_board": None,
                "config": {
                    **dict(default_row.get("config", {})),
                    "candidate_add_threshold": round(float(v114k_payload.get("candidate_policy_summary", {}).get("candidate_add_threshold", 0.0)), 6),
                    "candidate_extra_uplift": round(float(v114k_payload.get("candidate_policy_summary", {}).get("candidate_extra_uplift", 0.0)), 6),
                    "candidate_floor": round(float(v114k_payload.get("candidate_policy_summary", {}).get("candidate_floor", 0.0)), 6),
                    "max_expression_weight": round(float(v114k_payload.get("candidate_policy_summary", {}).get("candidate_max_expression_weight", default_row.get("config", {}).get("max_expression_weight", 0.0))), 6),
                },
                "usage_rule": "do_not_promote_until_cross_board_or_harsher_environment_judgement",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v114l_cpo_parallel_parameter_posture_registry_v1",
            "retained_posture_count": len(posture_rows),
            "default_posture_name": "default_expectancy_mainline",
            "parallel_retained_count": len([row for row in posture_rows if row["status"] == "parallel_retained"]),
            "candidate_only_count": len([row for row in posture_rows if row["status"] == "candidate_only"]),
            "recommended_next_posture": "carry_multiple_parameter_postures_forward_for_future_board_judgement_instead_of_collapsing_to_single_cpo_winner",
        }
        interpretation = [
            "V1.14L freezes multiple CPO sizing postures in parallel instead of pretending one local winner is the only useful parameterization.",
            "The default posture stays the replay-promoted expectancy-max surface, while conservative and balanced variants are retained as future cross-board judgement candidates.",
            "The vector-overlay posture remains candidate-only because its replay gain is real but too expensive in drawdown to promote without harsher judgement.",
        ]
        return V114LCpoParallelParameterPostureRegistryReport(
            summary=summary,
            posture_rows=posture_rows,
            interpretation=interpretation,
        )


def write_v114l_cpo_parallel_parameter_posture_registry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114LCpoParallelParameterPostureRegistryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
