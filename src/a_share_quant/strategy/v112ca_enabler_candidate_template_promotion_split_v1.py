from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CAEnablerCandidateTemplatePromotionSplitReport:
    summary: dict[str, Any]
    promotion_rows: list[dict[str, Any]]
    layer_rows: list[dict[str, Any]]
    diagnostic_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "promotion_rows": self.promotion_rows,
            "layer_rows": self.layer_rows,
            "diagnostic_rows": self.diagnostic_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CAEnablerCandidateTemplatePromotionSplitAnalyzer:
    def analyze(
        self,
        *,
        by_payload: dict[str, Any],
        bz_payload: dict[str, Any],
    ) -> V112CAEnablerCandidateTemplatePromotionSplitReport:
        transfer_rows = {
            str(row["role_family"]): row
            for row in list(by_payload.get("role_level_rows", []))
        }
        calibration_rows = {
            str(row["role_family"]): row
            for row in list(bz_payload.get("role_calibration_rows", []))
        }
        if not transfer_rows or not calibration_rows:
            raise ValueError("V1.12CA requires both V1.12BY transfer rows and V1.12BZ calibration rows.")

        promotion_rows: list[dict[str, Any]] = []
        layer_rows: list[dict[str, Any]] = []
        diagnostic_rows: list[dict[str, Any]] = list(bz_payload.get("diagnostic_rows", []))

        for role_family, transfer_row in sorted(transfer_rows.items()):
            calibration_row = calibration_rows.get(role_family)
            if calibration_row is None:
                raise ValueError(f"Missing calibration row for role family {role_family}.")

            transfer_accuracy = float(transfer_row.get("classification_accuracy", 0.0))
            posture = str(calibration_row.get("calibration_posture", "unknown"))

            direction_layer = self._direction_layer(
                role_family=role_family,
                transfer_accuracy=transfer_accuracy,
                posture=posture,
            )
            band_layer = self._band_layer(
                role_family=role_family,
                transfer_accuracy=transfer_accuracy,
                posture=posture,
            )
            edge_layer = self._edge_layer(posture=posture)
            action_layer = self._action_layer(
                role_family=role_family,
                transfer_accuracy=transfer_accuracy,
                posture=posture,
            )
            promotion_posture = self._promotion_posture(
                role_family=role_family,
                transfer_accuracy=transfer_accuracy,
                posture=posture,
            )

            promotion_rows.append(
                {
                    "role_family": role_family,
                    "transfer_accuracy": round(transfer_accuracy, 4),
                    "direction_layer_status": direction_layer,
                    "band_layer_status": band_layer,
                    "edge_layer_status": edge_layer,
                    "action_layer_status": action_layer,
                    "promotion_posture": promotion_posture,
                }
            )

            for layer_name, layer_status in (
                ("direction_layer", direction_layer),
                ("band_layer", band_layer),
                ("edge_layer", edge_layer),
                ("action_layer", action_layer),
            ):
                layer_rows.append(
                    {
                        "role_family": role_family,
                        "layer_name": layer_name,
                        "layer_status": layer_status,
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v112ca_enabler_candidate_template_promotion_split_v1",
            "role_count": len(promotion_rows),
            "candidate_template_path_count": sum(
                1 for row in promotion_rows if str(row["promotion_posture"]) == "candidate_template_path"
            ),
            "role_specific_template_count": sum(
                1 for row in promotion_rows if str(row["promotion_posture"]) == "candidate_template_path_with_role_specific_edges"
            ),
            "isolated_diagnostic_path_count": sum(
                1 for row in promotion_rows if str(row["promotion_posture"]) == "isolated_diagnostic_path"
            ),
            "recommended_next_posture": "run_action_mapping_review_for_packaging_and_laser_and_isolate_silicon_direction_review",
        }
        interpretation = [
            "V1.12CA splits the enabler-family transfer result into four method layers: direction transfer, band semantics, edge calibration, and action mapping readiness.",
            "The key outcome is that packaging-process-enabler and laser-chip-component can move forward as candidate template paths, while silicon-photonics remains an isolated diagnostic path.",
        ]
        return V112CAEnablerCandidateTemplatePromotionSplitReport(
            summary=summary,
            promotion_rows=promotion_rows,
            layer_rows=layer_rows,
            diagnostic_rows=diagnostic_rows,
            interpretation=interpretation,
        )

    def _direction_layer(self, *, role_family: str, transfer_accuracy: float, posture: str) -> str:
        if role_family == "silicon_photonics_component":
            return "direction_review_required"
        if transfer_accuracy >= 0.9:
            return "transferred_direction_set_confirmed"
        if posture == "adopt_role_specific_band_edges":
            return "transferred_direction_set_supported"
        return "direction_transfer_weak"

    def _band_layer(self, *, role_family: str, transfer_accuracy: float, posture: str) -> str:
        if role_family == "silicon_photonics_component":
            return "band_semantics_not_ready"
        if transfer_accuracy >= 0.9:
            return "three_band_semantics_confirmed"
        if posture == "adopt_role_specific_band_edges":
            return "three_band_semantics_supported_with_local_calibration"
        return "band_semantics_weak"

    def _edge_layer(self, *, posture: str) -> str:
        if posture == "adopt_transferred_band_unchanged":
            return "transferred_edges_unchanged"
        if posture == "adopt_role_specific_band_edges":
            return "role_specific_edge_calibration_required"
        if posture == "do_not_transfer_unmodified":
            return "edge_transfer_blocked"
        return "edge_status_unknown"

    def _action_layer(self, *, role_family: str, transfer_accuracy: float, posture: str) -> str:
        if role_family == "silicon_photonics_component":
            return "do_not_promote_action_mapping"
        if transfer_accuracy >= 0.9:
            return "ready_for_candidate_action_mapping_review"
        if posture == "adopt_role_specific_band_edges":
            return "candidate_action_mapping_review_after_local_edge_binding"
        return "action_mapping_not_ready"

    def _promotion_posture(self, *, role_family: str, transfer_accuracy: float, posture: str) -> str:
        if role_family == "silicon_photonics_component":
            return "isolated_diagnostic_path"
        if posture == "adopt_transferred_band_unchanged" and transfer_accuracy >= 0.9:
            return "candidate_template_path"
        if posture == "adopt_role_specific_band_edges":
            return "candidate_template_path_with_role_specific_edges"
        return "review_only_path"


def write_v112ca_enabler_candidate_template_promotion_split_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CAEnablerCandidateTemplatePromotionSplitReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
