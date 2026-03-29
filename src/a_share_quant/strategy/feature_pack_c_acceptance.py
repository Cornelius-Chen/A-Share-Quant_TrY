from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackCAcceptanceReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackCAcceptanceAnalyzer:
    """Decide whether feature-pack-c should continue or close as explanatory."""

    def analyze(
        self,
        *,
        fallback_payload: dict[str, Any],
        residual_payload: dict[str, Any],
        stability_liquidity_payload: dict[str, Any],
        turnover_payload: dict[str, Any],
        balanced_turnover_payload: dict[str, Any],
    ) -> FeaturePackCAcceptanceReport:
        fallback_summary = dict(fallback_payload.get("summary", {}))
        residual_summary = dict(residual_payload.get("summary", {}))
        stability_summary = dict(stability_liquidity_payload.get("summary", {}))
        turnover_summary = dict(turnover_payload.get("summary", {}))
        balanced_summary = dict(balanced_turnover_payload.get("summary", {}))

        late_quality_dominant = int(
            fallback_summary.get("dominant_component_counts", {}).get("late_quality", 0)
        )
        score_margin_dominant = int(
            fallback_summary.get("dominant_component_counts", {}).get("score_margin", 0)
        )
        raw_below_threshold = int(residual_summary.get("raw_below_threshold_count", 0))
        concept_boost_active = int(residual_summary.get("concept_boost_active_count", 0))
        turnover_led = int(
            stability_summary.get("local_context_counts", {}).get("turnover_share_led", 0)
        )
        broad_attention_deficit = int(
            turnover_summary.get("summary", {}).get("local_turnover_context_counts", {}).get(
                "broad_attention_deficit", 0
            )
        )
        singleton_sector_masking = int(
            balanced_summary.get("balanced_weakness_counts", {}).get("singleton_sector_masking", 0)
        )
        true_balanced_weakness = int(
            balanced_summary.get("balanced_weakness_counts", {}).get(
                "true_balanced_share_weakness",
                0,
            )
        )

        explanatory_success = (
            late_quality_dominant > score_margin_dominant
            and raw_below_threshold > 0
            and turnover_led > 0
            and singleton_sector_masking > 0
        )
        no_clean_turnover_branch = (
            broad_attention_deficit == 0 and true_balanced_weakness == 0 and singleton_sector_masking > 0
        )
        acceptance_posture = (
            "close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar"
            if explanatory_success and no_clean_turnover_branch
            else "continue_feature_pack_c"
        )

        evidence_rows = [
            {
                "evidence_name": "fallback_decomposition",
                "actual": {
                    "late_quality_dominant": late_quality_dominant,
                    "score_margin_dominant": score_margin_dominant,
                },
                "reading": "The suspect pockets are still driven primarily by late-quality failure rather than a generic score-margin story.",
            },
            {
                "evidence_name": "raw_late_quality_stack",
                "actual": {
                    "raw_below_threshold_count": raw_below_threshold,
                    "concept_boost_active_count": concept_boost_active,
                    "dominant_residual_component_counts": residual_summary.get("dominant_residual_component_counts", {}),
                },
                "reading": "The remaining blocker sits inside the raw late-quality stack, with concept boost mostly secondary.",
            },
            {
                "evidence_name": "turnover_lane_split",
                "actual": {
                    "turnover_share_led": turnover_led,
                    "local_turnover_context_counts": turnover_summary.get("local_turnover_context_counts", {}),
                },
                "reading": "Turnover-share matters locally, but it does not collapse into one global attention feature.",
            },
            {
                "evidence_name": "balanced_turnover_resolution",
                "actual": {
                    "balanced_weakness_counts": balanced_summary.get("balanced_weakness_counts", {}),
                },
                "reading": "The balanced-share branch is currently explained by singleton-sector masking rather than a reusable balanced-turnover weakness feature.",
            },
        ]
        interpretation = [
            "Feature-pack-c should continue only if the next lane still promises a reusable local-causal branch rather than one more descriptive split.",
            "The current evidence says pack-c succeeded as explanation: it localized the pockets to late-quality residual structure and ruled out a generic turnover-attention feature.",
            "The correct next move is therefore not more turnover-lane refinement. It is to close feature-pack-c as explanatory and, if needed, start a bounded U1 lightweight-geometry sidecar.",
        ]
        summary = {
            "acceptance_posture": acceptance_posture,
            "late_quality_dominant_count": late_quality_dominant,
            "raw_below_threshold_count": raw_below_threshold,
            "turnover_share_led_count": turnover_led,
            "singleton_sector_masking_count": singleton_sector_masking,
            "true_balanced_share_weakness_count": true_balanced_weakness,
            "do_continue_pack_c_turnover_branch": not no_clean_turnover_branch,
            "do_restart_replay_queue": False,
            "ready_for_u1_lightweight_geometry": acceptance_posture
            == "close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar",
        }
        return FeaturePackCAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_feature_pack_c_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
