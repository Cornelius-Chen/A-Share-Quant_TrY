from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CXCoreLeaderHoldingVetoPromotionReviewReport:
    summary: dict[str, Any]
    promotion_rows: list[dict[str, Any]]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "promotion_rows": self.promotion_rows,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CXCoreLeaderHoldingVetoPromotionReviewAnalyzer:
    def analyze(
        self,
        *,
        cn_payload: dict[str, Any],
        cw_payload: dict[str, Any],
        cs_payload: dict[str, Any],
    ) -> V112CXCoreLeaderHoldingVetoPromotionReviewReport:
        cn_summary = dict(cn_payload.get("summary", {}))
        cn_selected_rule = dict(cn_payload.get("selected_rule", {}))
        cw_summary = dict(cw_payload.get("summary", {}))
        cs_summary = dict(cs_payload.get("summary", {}))

        promotion_ready = bool(cn_summary.get("beats_neutral_return")) and bool(cn_summary.get("beats_neutral_drawdown"))

        summary = {
            "acceptance_posture": "freeze_v112cx_core_leader_holding_veto_promotion_review_v1",
            "promotion_ready": promotion_ready,
            "promotion_posture": (
                "core_residual_promotable_holding_veto_candidate"
                if promotion_ready
                else "retain_as_holding_veto_candidate_only"
            ),
            "packaging_mainline_surface_frozen": bool(cw_summary.get("mainline_extension_count", 0) == 1),
            "joint_core_promotion_ready": bool(cs_summary.get("joint_promotion_ready", False)),
            "recommended_next_posture": (
                "freeze_300308_as_promotable_holding_veto_candidate_but_keep_separate_from_joint_core_promotion"
                if promotion_ready
                else "retain_300308_as_candidate_only"
            ),
        }
        promotion_rows = [
            {
                "promotion_target": "300308_core_module_leader_holding_veto",
                "posture": (
                    "core_residual_promotable_holding_veto_candidate"
                    if promotion_ready
                    else "holding_veto_candidate_only"
                ),
                "selected_rule_name": cn_selected_rule.get("rule_name"),
                "min_holding_day": cn_selected_rule.get("min_holding_day"),
                "drawdown_threshold": cn_selected_rule.get("drawdown_threshold"),
                "retained_gain_buffer": cn_selected_rule.get("retained_gain_buffer"),
                "require_ma5_break": cn_selected_rule.get("require_ma5_break"),
                "beats_neutral_return": bool(cn_summary.get("beats_neutral_return")),
                "beats_neutral_drawdown": bool(cn_summary.get("beats_neutral_drawdown")),
                "neutral_return_delta": cn_summary.get("neutral_return_delta"),
                "neutral_drawdown_delta": cn_summary.get("neutral_drawdown_delta"),
                "holding_veto_count": cn_summary.get("holding_veto_count"),
                "continue_count": cn_summary.get("continue_count"),
            }
        ]
        boundary_rows = [
            {
                "boundary_name": "packaging_surface_boundary",
                "reading": "300308 holding-veto promotion remains outside the already frozen packaging mainline surface.",
                "packaging_mainline_surface_frozen": bool(cw_summary.get("mainline_extension_count", 0) == 1),
            },
            {
                "boundary_name": "joint_core_boundary",
                "reading": "300308 may be promotable on its own while joint 300308/300502 core residual promotion remains deferred.",
                "joint_core_promotion_ready": bool(cs_summary.get("joint_promotion_ready", False)),
            },
            {
                "boundary_name": "blunt_exit_boundary",
                "reading": "The promotion is justified because the selected state-conditioned holding veto beats both neutral and the blunt uniform half-life cut.",
                "beats_uniform_10d_return": bool(cn_summary.get("beats_uniform_10d_return")),
            },
        ]
        interpretation = [
            "V1.12CX converts 300308's late-stage main-markup holding-veto from a residual candidate into a governed promotion decision.",
            "The review supports promotion of 300308 as a standalone holding-veto candidate while preserving separation from packaging's frozen mainline surface and the deferred joint core stack.",
        ]
        return V112CXCoreLeaderHoldingVetoPromotionReviewReport(
            summary=summary,
            promotion_rows=promotion_rows,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_v112cx_core_leader_holding_veto_promotion_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CXCoreLeaderHoldingVetoPromotionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
