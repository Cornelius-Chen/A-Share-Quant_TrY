from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(slots=True)
class V112BTPhaseConditionedVetoAndEligibilityExtractionReport:
    summary: dict[str, Any]
    eligibility_rule_rows: list[dict[str, Any]]
    entry_veto_rows: list[dict[str, Any]]
    holding_veto_rows: list[dict[str, Any]]
    risk_off_override_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "eligibility_rule_rows": self.eligibility_rule_rows,
            "entry_veto_rows": self.entry_veto_rows,
            "holding_veto_rows": self.holding_veto_rows,
            "risk_off_override_rows": self.risk_off_override_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BTPhaseConditionedVetoAndEligibilityExtractionAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        bs_refinement_payload: dict[str, Any],
        bp_fusion_payload: dict[str, Any],
    ) -> V112BTPhaseConditionedVetoAndEligibilityExtractionReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bt_now")):
            raise ValueError("V1.12BT must be open before extraction runs.")

        eligibility_rule_rows = self._eligibility_rule_rows(bs_refinement_payload=bs_refinement_payload)
        entry_veto_rows = self._entry_veto_rows(bs_refinement_payload=bs_refinement_payload)
        holding_veto_rows = self._holding_veto_rows(bs_refinement_payload=bs_refinement_payload)
        risk_off_override_rows = self._risk_off_override_rows(
            bs_refinement_payload=bs_refinement_payload,
            bp_fusion_payload=bp_fusion_payload,
        )

        summary = {
            "acceptance_posture": "freeze_v112bt_phase_conditioned_veto_and_eligibility_extraction_v1",
            "eligibility_rule_count": len(eligibility_rule_rows),
            "entry_veto_count": len(entry_veto_rows),
            "holding_veto_count": len(holding_veto_rows),
            "risk_off_override_count": len(risk_off_override_rows),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "test_phase_conditioned_controls_inside_selector_maturity_fusion_baseline",
        }
        interpretation = [
            "V1.12BT treats dangerous regions as first-class control objects instead of waiting for a clean bad cluster that may never naturally appear.",
            "The extraction deliberately separates entry veto, holding veto, and risk-off override so that the system does not collapse back into one blunt global gate.",
        ]
        return V112BTPhaseConditionedVetoAndEligibilityExtractionReport(
            summary=summary,
            eligibility_rule_rows=eligibility_rule_rows,
            entry_veto_rows=entry_veto_rows,
            holding_veto_rows=holding_veto_rows,
            risk_off_override_rows=risk_off_override_rows,
            interpretation=interpretation,
        )

    def _eligibility_rule_rows(self, *, bs_refinement_payload: dict[str, Any]) -> list[dict[str, Any]]:
        bundle_rows = list(bs_refinement_payload.get("candidate_bundle_rows", []))
        cluster_rows = list(bs_refinement_payload.get("penalized_cluster_rows", []))
        rows: list[dict[str, Any]] = []

        for cluster in cluster_rows:
            if str(cluster.get("penalized_posture")) != "offensive_cluster":
                continue
            rows.append(
                {
                    "eligibility_name": "guarded_offensive_core_continuation",
                    "stage_family": str(cluster.get("dominant_stage_family")),
                    "role_family": str(cluster.get("dominant_role_family")),
                    "posture": "guarded_eligibility",
                    "reading": "Offensive region remains usable only if no local veto neighborhood or transition-band warning is active.",
                    "average_forward_return_20d": cluster.get("average_forward_return_20d"),
                    "average_max_drawdown_20d": cluster.get("average_max_drawdown_20d"),
                }
            )

        for bundle in bundle_rows:
            if str(bundle.get("bundle_name")) != "offensive_resonance_direction":
                continue
            rows.append(
                {
                    "eligibility_name": "offensive_resonance_bundle",
                    "feature_1": str(bundle.get("feature_1")),
                    "feature_2": str(bundle.get("feature_2")),
                    "feature_3": str(bundle.get("feature_3")),
                    "posture": "bundle_supported_eligibility",
                    "reading": "Use as an eligibility support bundle, not as standalone authorization.",
                    "average_forward_return_20d": bundle.get("average_forward_return_20d"),
                    "average_max_drawdown_20d": bundle.get("average_max_drawdown_20d"),
                }
            )
        return rows

    def _entry_veto_rows(self, *, bs_refinement_payload: dict[str, Any]) -> list[dict[str, Any]]:
        frame = pd.DataFrame(list(bs_refinement_payload.get("veto_neighborhood_rows", [])))
        if frame.empty:
            return []

        diffusion_frame = frame[frame["stage_family"].astype(str).eq("diffusion")].copy()
        if diffusion_frame.empty:
            return []

        rows: list[dict[str, Any]] = []
        for role_family, group in diffusion_frame.groupby("role_family"):
            rows.append(
                {
                    "entry_veto_name": f"diffusion_{role_family}_entry_veto",
                    "stage_family": "diffusion",
                    "role_family": str(role_family),
                    "bad_trade_density_mean": round(float(group["local_bad_trade_density"].mean()), 4),
                    "penalized_veto_intensity_mean": round(float(group["local_average_penalized_veto_intensity"].mean()), 4),
                    "reading": "Do not open new exposure when local neighborhood looks like this diffusion risk pocket.",
                }
            )
        rows.sort(key=lambda item: float(item["penalized_veto_intensity_mean"]), reverse=True)
        return rows

    def _holding_veto_rows(self, *, bs_refinement_payload: dict[str, Any]) -> list[dict[str, Any]]:
        frame = pd.DataFrame(list(bs_refinement_payload.get("transition_band_rows", [])))
        if frame.empty:
            return []

        core_frame = frame[frame["role_family"].astype(str).eq("high_beta_core_module")].copy()
        if core_frame.empty:
            return []

        rows: list[dict[str, Any]] = []
        for stage_family, group in core_frame.groupby("stage_family"):
            rows.append(
                {
                    "holding_veto_name": f"{stage_family}_core_transition_holding_veto",
                    "stage_family": str(stage_family),
                    "role_family": "high_beta_core_module",
                    "boundary_risk_score_mean": round(float(group["boundary_risk_score"].mean()), 4),
                    "penalized_veto_intensity_mean": round(float(group["penalized_veto_intensity"].mean()), 4),
                    "reading": "This is a de-risk / holding-veto object, not a blanket entry prohibition.",
                }
            )
        rows.sort(key=lambda item: float(item["boundary_risk_score_mean"]), reverse=True)
        return rows

    def _risk_off_override_rows(
        self,
        *,
        bs_refinement_payload: dict[str, Any],
        bp_fusion_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        veto_frame = pd.DataFrame(list(bs_refinement_payload.get("veto_neighborhood_rows", [])))
        band_frame = pd.DataFrame(list(bs_refinement_payload.get("transition_band_rows", [])))
        gate_frame = pd.DataFrame(list(bp_fusion_payload.get("gate_decision_rows", [])))

        rows: list[dict[str, Any]] = []
        if not veto_frame.empty:
            diffusion_count = int(veto_frame["stage_family"].astype(str).eq("diffusion").sum())
            if diffusion_count >= 8:
                rows.append(
                    {
                        "override_name": "diffusion_extension_risk_off_override",
                        "trigger_stage_family": "diffusion",
                        "trigger_reason": "veto neighborhoods are densely concentrated in diffusion extensions and bridge roles",
                        "supporting_count": diffusion_count,
                        "reading": "Shrink new risk expression when diffusion extension pockets dominate the local risk map.",
                    }
                )

        if not band_frame.empty:
            core_transition_count = int(
                (
                    band_frame["role_family"].astype(str).eq("high_beta_core_module")
                    & band_frame["stage_family"].astype(str).isin(["main_markup", "divergence_and_decay"])
                ).sum()
            )
            if core_transition_count >= 3:
                rows.append(
                    {
                        "override_name": "core_transition_instability_override",
                        "trigger_stage_family": "main_markup_to_divergence",
                        "trigger_reason": "core transition bands indicate rising holding instability in the core continuation path",
                        "supporting_count": core_transition_count,
                        "reading": "Prefer de-risking or shorter holding half-life when core transition instability is active.",
                    }
                )

        if not gate_frame.empty:
            risk_dates = set(veto_frame["trade_date"].astype(str).tolist()) | set(band_frame["trade_date"].astype(str).tolist())
            overlap = gate_frame[gate_frame["trade_date"].astype(str).isin(risk_dates)]
            if not overlap.empty:
                rows.append(
                    {
                        "override_name": "risk_surface_overlap_override",
                        "trigger_stage_family": "mixed",
                        "trigger_reason": "selector candidates overlap with identified risk regions",
                        "supporting_count": int(len(overlap)),
                        "reading": "Do not let selector strength automatically override mapped risk regions.",
                    }
                )
        return rows


def write_v112bt_phase_conditioned_veto_and_eligibility_extraction_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BTPhaseConditionedVetoAndEligibilityExtractionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
