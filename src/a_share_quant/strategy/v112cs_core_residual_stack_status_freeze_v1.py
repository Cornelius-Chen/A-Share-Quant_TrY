from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CSCoreResidualStackStatusFreezeReport:
    summary: dict[str, Any]
    stack_rows: list[dict[str, Any]]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stack_rows": self.stack_rows,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CSCoreResidualStackStatusFreezeAnalyzer:
    def analyze(
        self,
        *,
        ch_payload: dict[str, Any],
        ci_payload: dict[str, Any],
        cn_payload: dict[str, Any],
        cq_payload: dict[str, Any],
        cr_payload: dict[str, Any],
    ) -> V112CSCoreResidualStackStatusFreezeReport:
        ch_summary = dict(ch_payload.get("summary", {}))
        ci_summary = dict(ci_payload.get("summary", {}))
        cn_summary = dict(cn_payload.get("summary", {}))
        cq_summary = dict(cq_payload.get("summary", {}))
        cr_summary = dict(cr_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "freeze_v112cs_core_residual_stack_status_freeze_v1",
            "mainline_asset_count": 1,
            "core_residual_candidate_count": 1,
            "core_residual_sidecar_count": 1,
            "eligibility_only_member_count": 1,
            "joint_promotion_ready": False,
            "recommended_next_posture": "treat_packaging_as_mainline_keep_300308_as_holding_veto_candidate_keep_300502_as_split_derisk_sidecar_and_defer_joint_promotion",
        }
        stack_rows = [
            {
                "stack_item": "packaging_process_enabler",
                "status": "cluster_mainline_template_asset",
                "control_language": ["entry_veto", "de_risk", "eligibility"],
                "evidence": {
                    "path_total_return": ch_summary.get("cd_total_return"),
                    "path_max_drawdown": ch_summary.get("cd_max_drawdown"),
                    "validation_accuracy": ch_summary.get("cf_validation_accuracy"),
                },
            },
            {
                "stack_item": "300308_core_module_leader",
                "status": "holding_veto_candidate",
                "control_language": ["continue", "holding_veto"],
                "evidence": {
                    "selected_total_return": cn_summary.get("selected_total_return"),
                    "selected_max_drawdown": cn_summary.get("selected_max_drawdown"),
                    "neutral_return_delta": cn_summary.get("neutral_return_delta"),
                    "neutral_drawdown_delta": cn_summary.get("neutral_drawdown_delta"),
                },
            },
            {
                "stack_item": "300502_high_beta_core_module",
                "status": "split_derisk_sidecar",
                "control_language": ["neutral_safe_mild_derisk", "evidence_optimizing_stronger_derisk"],
                "evidence": {
                    "mild_band_neutral_safe": cq_summary.get("mild_band_neutral_safe"),
                    "strong_band_beats_evidence_both": cq_summary.get("strong_band_beats_evidence_both"),
                    "preferred_band": cr_summary.get("preferred_band"),
                },
            },
            {
                "stack_item": "laser_chip_component",
                "status": "eligibility_only_template_member",
                "control_language": ["eligibility", "fringe_watch"],
                "evidence": {
                    "clean_eligibility_count": ci_summary.get("clean_eligibility_count"),
                    "de_risk_fringe_watch_count": ci_summary.get("de_risk_fringe_watch_count"),
                },
            },
        ]
        boundary_rows = [
            {
                "boundary_name": "mainline_boundary",
                "reading": "Only packaging_process_enabler is a promoted mainline template asset at the current stage.",
            },
            {
                "boundary_name": "candidate_boundary",
                "reading": "300308 is promotable as a holding-veto candidate but remains separate from packaging's mainline template language.",
            },
            {
                "boundary_name": "sidecar_boundary",
                "reading": "300502 remains a split de-risk sidecar. Mild de-risk is neutral-safe; stronger de-risk stays evidence-optimizing and should not be force-promoted into the default stack.",
            },
            {
                "boundary_name": "joint_promotion_boundary",
                "reading": "Combined core residual replay improves drawdown but gives back return, so joint promotion remains deferred.",
                "combined_return_delta_vs_neutral": -0.0377,
                "combined_drawdown_delta_vs_neutral": 0.028,
            },
        ]
        interpretation = [
            "V1.12CS freezes the current CPO core residual stack into a governed status map instead of continuing to mix mature assets, candidates, and sidecars.",
            "Packaging remains the only promoted mainline refined template; 300308 becomes a holding-veto candidate, 300502 remains a split de-risk sidecar, and laser stays eligibility-only.",
        ]
        return V112CSCoreResidualStackStatusFreezeReport(
            summary=summary,
            stack_rows=stack_rows,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_v112cs_core_residual_stack_status_freeze_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CSCoreResidualStackStatusFreezeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
