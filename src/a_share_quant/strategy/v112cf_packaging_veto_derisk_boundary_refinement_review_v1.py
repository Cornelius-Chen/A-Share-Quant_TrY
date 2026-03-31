from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CFPackagingVetoDeRiskBoundaryRefinementReviewReport:
    summary: dict[str, Any]
    refinement_rule_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "refinement_rule_rows": self.refinement_rule_rows,
            "sample_rows": self.sample_rows,
            "residual_rows": self.residual_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CFPackagingVetoDeRiskBoundaryRefinementReviewAnalyzer:
    TARGET_ROLE = "packaging_process_enabler"

    VETO_TO_DERISK_RULE = {
        "core_branch_relative_strength_spread_state": -0.15,
        "core_spillover_divergence_state": -0.20,
        "spillover_saturation_overlay_state": 0.16,
        "ai_hardware_cross_board_resonance_state": -0.08,
    }
    STRICT_ELIGIBILITY_RULE = {
        "core_branch_relative_strength_spread_state": 0.0,
        "core_spillover_divergence_state": 0.15,
        "spillover_saturation_overlay_state": 0.10,
        "ai_hardware_cross_board_resonance_state": 0.0,
    }

    def analyze(
        self,
        *,
        by_payload: dict[str, Any],
        bz_payload: dict[str, Any],
        bp_payload: dict[str, Any],
        ce_payload: dict[str, Any],
    ) -> V112CFPackagingVetoDeRiskBoundaryRefinementReviewReport:
        band_specs = self._load_packaging_band_specs(bz_payload=bz_payload)
        base_rows = [
            row for row in list(by_payload.get("sample_rows", [])) if str(row.get("role_family")) == self.TARGET_ROLE
        ]
        gate_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in list(bp_payload.get("gate_decision_rows", []))
            if str(row.get("symbol")) == "300757"
        }
        if not base_rows or not gate_rows:
            raise ValueError("V1.12CF requires packaging sample rows and gate rows.")

        previous_accuracy = float(ce_payload.get("summary", {}).get("action_mapping_accuracy", 0.0))

        sample_rows: list[dict[str, Any]] = []
        correct = 0
        for row in base_rows:
            key = (str(row["trade_date"]), str(row["symbol"]))
            gate_row = gate_rows[key]
            base_band = self._base_predict_band(row=gate_row, band_specs=band_specs)
            refined_band = self._refined_predict_band(row=gate_row, base_band=base_band)
            actual_band = str(row["actual_band"])
            if refined_band == actual_band:
                correct += 1
            sample_rows.append(
                {
                    "trade_date": key[0],
                    "symbol": key[1],
                    "actual_band": actual_band,
                    "base_band": base_band,
                    "refined_band": refined_band,
                    "classification_correct": refined_band == actual_band,
                }
            )

        refined_accuracy = correct / len(sample_rows)
        residual_rows = [row for row in sample_rows if not bool(row["classification_correct"])]

        summary = {
            "acceptance_posture": "freeze_v112cf_packaging_veto_derisk_boundary_refinement_review_v1",
            "sample_count": len(sample_rows),
            "previous_action_mapping_accuracy": round(previous_accuracy, 4),
            "refined_action_mapping_accuracy": round(refined_accuracy, 4),
            "accuracy_delta": round(refined_accuracy - previous_accuracy, 4),
            "residual_count": len(residual_rows),
            "recommended_next_posture": "promote_refined_packaging_boundary_as_candidate_and_rerun_template_pilot_if_material",
        }
        refinement_rule_rows = [
            {
                "rule_name": "veto_to_derisk_relaxation",
                "trigger_reading": "If base band is veto but the state is only moderately negative and still shows saturated-weak drift, downgrade to de-risk.",
                "thresholds": self.VETO_TO_DERISK_RULE,
            },
            {
                "rule_name": "strict_eligibility_confirmation",
                "trigger_reading": "Only keep eligibility when all positive directions are clearly constructive and spillover saturation remains subdued.",
                "thresholds": self.STRICT_ELIGIBILITY_RULE,
            },
        ]
        interpretation = [
            "V1.12CF refines the packaging three-layer template by separating true veto states from over-suppressed de-risk states.",
            "The refinement is intentionally local: it upgrades the de-risk/veto boundary without changing the broader cluster-level control grammar.",
        ]
        return V112CFPackagingVetoDeRiskBoundaryRefinementReviewReport(
            summary=summary,
            refinement_rule_rows=refinement_rule_rows,
            sample_rows=sample_rows,
            residual_rows=residual_rows,
            interpretation=interpretation,
        )

    def _load_packaging_band_specs(self, *, bz_payload: dict[str, Any]) -> dict[str, tuple[str, float]]:
        band_specs = {}
        for row in list(bz_payload.get("calibrated_band_rows", [])):
            if str(row.get("role_family")) != self.TARGET_ROLE:
                continue
            band_specs[str(row["feature_name"])] = (str(row["direction"]), float(row["calibrated_midpoint"]))
        if not band_specs:
            raise ValueError("V1.12CF requires packaging calibrated band specs from V1.12BZ.")
        return band_specs

    def _base_predict_band(self, *, row: dict[str, Any], band_specs: dict[str, tuple[str, float]]) -> str:
        risk_count = 0
        healthy_count = 0
        for feature_name, (direction, midpoint) in band_specs.items():
            value = float(row.get(feature_name, 0.0))
            if direction == "higher_is_better":
                if value < midpoint:
                    risk_count += 1
                else:
                    healthy_count += 1
            else:
                if value > midpoint:
                    risk_count += 1
                else:
                    healthy_count += 1
        if risk_count >= 3:
            return "veto_band"
        if healthy_count >= 3:
            return "eligibility_band"
        return "de_risk_band"

    def _refined_predict_band(self, *, row: dict[str, Any], base_band: str) -> str:
        if base_band == "veto_band":
            if (
                float(row["core_branch_relative_strength_spread_state"]) > self.VETO_TO_DERISK_RULE["core_branch_relative_strength_spread_state"]
                and float(row["core_spillover_divergence_state"]) > self.VETO_TO_DERISK_RULE["core_spillover_divergence_state"]
                and float(row["spillover_saturation_overlay_state"]) > self.VETO_TO_DERISK_RULE["spillover_saturation_overlay_state"]
                and float(row["ai_hardware_cross_board_resonance_state"]) > self.VETO_TO_DERISK_RULE["ai_hardware_cross_board_resonance_state"]
            ):
                return "de_risk_band"
            return "veto_band"

        if base_band == "eligibility_band":
            if (
                float(row["core_branch_relative_strength_spread_state"]) >= self.STRICT_ELIGIBILITY_RULE["core_branch_relative_strength_spread_state"]
                and float(row["core_spillover_divergence_state"]) >= self.STRICT_ELIGIBILITY_RULE["core_spillover_divergence_state"]
                and float(row["spillover_saturation_overlay_state"]) <= self.STRICT_ELIGIBILITY_RULE["spillover_saturation_overlay_state"]
                and float(row["ai_hardware_cross_board_resonance_state"]) >= self.STRICT_ELIGIBILITY_RULE["ai_hardware_cross_board_resonance_state"]
            ):
                return "eligibility_band"
            return "de_risk_band"

        return "de_risk_band"


def write_v112cf_packaging_veto_derisk_boundary_refinement_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CFPackagingVetoDeRiskBoundaryRefinementReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
