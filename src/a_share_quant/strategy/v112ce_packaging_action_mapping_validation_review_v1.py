from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CEPackagingActionMappingValidationReviewReport:
    summary: dict[str, Any]
    action_confusion_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "action_confusion_rows": self.action_confusion_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CEPackagingActionMappingValidationReviewAnalyzer:
    TARGET_ROLE = "packaging_process_enabler"

    def analyze(
        self,
        *,
        by_payload: dict[str, Any],
        bz_payload: dict[str, Any],
        bp_payload: dict[str, Any],
    ) -> V112CEPackagingActionMappingValidationReviewReport:
        band_specs = self._load_packaging_band_specs(bz_payload=bz_payload)
        actual_rows = [
            row for row in list(by_payload.get("sample_rows", [])) if str(row.get("role_family")) == self.TARGET_ROLE
        ]
        if not actual_rows:
            raise ValueError("V1.12CE requires packaging_process_enabler sample rows from V1.12BY.")

        gate_rows = {
            (str(row["trade_date"]), str(row["symbol"])): row
            for row in list(bp_payload.get("gate_decision_rows", []))
            if str(row.get("symbol")) == "300757"
        }
        if not gate_rows:
            raise ValueError("V1.12CE requires packaging gate decision rows from V1.12BP.")

        sample_rows: list[dict[str, Any]] = []
        confusion: dict[tuple[str, str], int] = {}
        correct = 0
        for actual in actual_rows:
            key = (str(actual.get("trade_date")), str(actual.get("symbol")))
            gate_row = gate_rows.get(key)
            if gate_row is None:
                continue
            predicted_band = self._predict_band(row=gate_row, band_specs=band_specs)
            actual_band = str(actual.get("actual_band"))
            predicted_action = self._band_to_action(predicted_band)
            actual_action = self._band_to_action(actual_band)
            is_correct = predicted_action == actual_action
            if is_correct:
                correct += 1
            confusion[(actual_action, predicted_action)] = confusion.get((actual_action, predicted_action), 0) + 1
            sample_rows.append(
                {
                    "trade_date": key[0],
                    "symbol": key[1],
                    "actual_band": actual_band,
                    "predicted_band": predicted_band,
                    "actual_action": actual_action,
                    "predicted_action": predicted_action,
                    "classification_correct": is_correct,
                }
            )

        if not sample_rows:
            raise ValueError("V1.12CE produced no packaging validation rows.")

        action_confusion_rows = [
            {
                "actual_action": actual_action,
                "predicted_action": predicted_action,
                "count": count,
            }
            for (actual_action, predicted_action), count in sorted(confusion.items())
        ]
        action_count = lambda name: sum(1 for row in sample_rows if str(row["predicted_action"]) == name)
        summary = {
            "acceptance_posture": "freeze_v112ce_packaging_action_mapping_validation_review_v1",
            "sample_count": len(sample_rows),
            "action_mapping_accuracy": round(correct / len(sample_rows), 4),
            "predicted_entry_veto_count": action_count("entry_veto"),
            "predicted_de_risk_count": action_count("de_risk"),
            "predicted_eligibility_count": action_count("eligibility"),
            "recommended_next_posture": "keep_packaging_three_layer_template_as_candidate_if_action_accuracy_remains_material",
        }
        interpretation = [
            "V1.12CE validates the packaging-process-enabler three-layer action mapping on the broader family sample set, not just on the realized baseline path.",
            "The core question is whether role-specific calibrated band edges still produce meaningful action-layer separation across the wider packaging state family.",
        ]
        return V112CEPackagingActionMappingValidationReviewReport(
            summary=summary,
            action_confusion_rows=action_confusion_rows,
            sample_rows=sample_rows,
            interpretation=interpretation,
        )

    def _load_packaging_band_specs(self, *, bz_payload: dict[str, Any]) -> dict[str, tuple[str, float]]:
        band_specs = {}
        for row in list(bz_payload.get("calibrated_band_rows", [])):
            if str(row.get("role_family")) != self.TARGET_ROLE:
                continue
            band_specs[str(row["feature_name"])] = (str(row["direction"]), float(row["calibrated_midpoint"]))
        if not band_specs:
            raise ValueError("V1.12CE requires packaging calibrated band specs from V1.12BZ.")
        return band_specs

    def _predict_band(self, *, row: dict[str, Any], band_specs: dict[str, tuple[str, float]]) -> str:
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

    def _band_to_action(self, band: str) -> str:
        if band == "veto_band":
            return "entry_veto"
        if band == "de_risk_band":
            return "de_risk"
        return "eligibility"


def write_v112ce_packaging_action_mapping_validation_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CEPackagingActionMappingValidationReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
