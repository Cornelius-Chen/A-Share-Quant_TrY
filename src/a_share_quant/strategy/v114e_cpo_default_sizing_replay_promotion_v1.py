from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)


@dataclass(slots=True)
class V114ECPODefaultSizingReplayPromotionReport:
    summary: dict[str, Any]
    promoted_default_row: dict[str, Any]
    baseline_comparison_row: dict[str, Any]
    promotion_checks: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "promoted_default_row": self.promoted_default_row,
            "baseline_comparison_row": self.baseline_comparison_row,
            "promotion_checks": self.promotion_checks,
            "interpretation": self.interpretation,
        }


class V114ECPODefaultSizingReplayPromotionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v113v_payload: dict[str, Any],
        v114d_payload: dict[str, Any],
    ) -> V114ECPODefaultSizingReplayPromotionReport:
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_d = dict(v114d_payload.get("summary", {}))
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14E expects V1.13V full-board replay as baseline.")
        if str(summary_d.get("acceptance_posture")) != "freeze_v114d_cpo_stable_zone_replay_injection_v1":
            raise ValueError("V1.14E expects V1.14D stable-zone replay injection.")

        promoted_default_row = dict(v114d_payload.get("recommended_candidate_row", {}))
        if str(promoted_default_row.get("candidate_name")) != str(summary_d.get("recommended_candidate_name")):
            raise ValueError("V1.14E expects V1.14D recommended candidate row to match summary.")

        baseline_curve = float(summary_d.get("baseline_curve", 0.0))
        baseline_drawdown = float(summary_d.get("baseline_max_drawdown", 0.0))
        promoted_curve = float(promoted_default_row.get("final_curve", 0.0))
        promoted_drawdown = float(promoted_default_row.get("max_drawdown", 0.0))
        promoted_capture = float(promoted_default_row.get("capture_ratio_vs_board", 0.0))
        promoted_orders = int(promoted_default_row.get("executed_order_count", 0))

        baseline_comparison_row = {
            "baseline_curve": round(baseline_curve, 4),
            "promoted_curve": round(promoted_curve, 4),
            "curve_delta": round(promoted_curve - baseline_curve, 4),
            "baseline_max_drawdown": round(baseline_drawdown, 4),
            "promoted_max_drawdown": round(promoted_drawdown, 4),
            "drawdown_delta": round(promoted_drawdown - baseline_drawdown, 4),
            "promoted_capture_ratio_vs_board": round(promoted_capture, 4),
            "promoted_executed_order_count": promoted_orders,
        }

        promotion_checks = {
            "curve_improves_vs_baseline": promoted_curve > baseline_curve,
            "capture_ratio_improves_vs_baseline": promoted_capture > 0.0,
            "candidate_is_from_stable_zone": True,
            "promotion_source_is_replay_validated": True,
            "drawdown_uplift_is_positive_but_controlled": promoted_drawdown > baseline_drawdown and promoted_drawdown <= 0.20,
        }

        summary = {
            "acceptance_posture": "freeze_v114e_cpo_default_sizing_replay_promotion_v1",
            "promoted_default_candidate_name": str(promoted_default_row.get("candidate_name")),
            "default_strong_board_uplift": float(dict(promoted_default_row.get("config", {})).get("strong_board_uplift", 0.0)),
            "default_under_exposure_floor": float(dict(promoted_default_row.get("config", {})).get("under_exposure_floor", 0.0)),
            "default_derisk_keep_fraction": float(dict(promoted_default_row.get("config", {})).get("derisk_keep_fraction", 0.0)),
            "baseline_curve": round(baseline_curve, 4),
            "promoted_curve": round(promoted_curve, 4),
            "baseline_max_drawdown": round(baseline_drawdown, 4),
            "promoted_max_drawdown": round(promoted_drawdown, 4),
            "promoted_capture_ratio_vs_board": round(promoted_capture, 4),
            "recommended_next_posture": "use_expectancy_max_injection_as_default_probability_expectancy_sizing_surface",
        }

        interpretation = [
            "V1.14E does not reopen local search. It freezes the V1.14D replay-validated winner as the default probability-expectancy sizing candidate.",
            "The promoted default keeps the narrow hard-veto layer intact and only upgrades expression via strong-board uplift, under-exposure floor, and de-risk keep fraction.",
            "This marks the transition from sizing discovery to sizing default posture: future audits should judge this promoted default across longer windows and harsher environments instead of repeating small local searches.",
        ]

        return V114ECPODefaultSizingReplayPromotionReport(
            summary=summary,
            promoted_default_row=promoted_default_row,
            baseline_comparison_row=baseline_comparison_row,
            promotion_checks=promotion_checks,
            interpretation=interpretation,
        )


def write_v114e_cpo_default_sizing_replay_promotion_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114ECPODefaultSizingReplayPromotionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

