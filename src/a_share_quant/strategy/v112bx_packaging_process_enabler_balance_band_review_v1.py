from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BXPackagingProcessEnablerBalanceBandReviewReport:
    summary: dict[str, Any]
    contrast_rows: list[dict[str, Any]]
    band_rows: list[dict[str, Any]]
    classification_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "contrast_rows": self.contrast_rows,
            "band_rows": self.band_rows,
            "classification_rows": self.classification_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BXPackagingProcessEnablerBalanceBandReviewAnalyzer:
    FEATURE_SPECS = {
        "core_branch_relative_strength_spread_state": "higher_is_better",
        "core_spillover_divergence_state": "higher_is_better",
        "spillover_saturation_overlay_state": "lower_is_better",
        "ai_hardware_cross_board_resonance_state": "higher_is_better",
    }

    def analyze(self, *, bw_payload: dict[str, Any]) -> V112BXPackagingProcessEnablerBalanceBandReviewReport:
        contrast_rows = list(bw_payload.get("contrast_rows", []))
        if len(contrast_rows) < 2:
            raise ValueError("V1.12BX requires the bad/good contrast rows from V1.12BW.")

        bad_row = next((row for row in contrast_rows if str(row.get("contrast_label")) == "bad_trade"), None)
        good_row = next((row for row in contrast_rows if str(row.get("contrast_label")) == "good_trade"), None)
        if bad_row is None or good_row is None:
            raise ValueError("V1.12BX requires both bad_trade and good_trade contrast rows.")

        band_rows: list[dict[str, Any]] = []
        for feature_name, direction in self.FEATURE_SPECS.items():
            bad_value = float(bad_row.get(feature_name, 0.0))
            good_value = float(good_row.get(feature_name, 0.0))
            midpoint = (bad_value + good_value) / 2.0
            band_rows.append(
                {
                    "feature_name": feature_name,
                    "direction": direction,
                    "bad_trade_value": round(bad_value, 6),
                    "good_trade_value": round(good_value, 6),
                    "balance_midpoint": round(midpoint, 6),
                    "veto_side_rule": "< midpoint" if direction == "higher_is_better" else "> midpoint",
                    "eligibility_side_rule": ">= midpoint" if direction == "higher_is_better" else "<= midpoint",
                }
            )

        classification_rows = []
        correct_count = 0
        for row in contrast_rows:
            state = self._classify_row(row=row, band_rows=band_rows)
            expected = "veto_band" if str(row.get("contrast_label")) == "bad_trade" else "eligibility_band"
            is_correct = state == expected
            if is_correct:
                correct_count += 1
            classification_rows.append(
                {
                    "entry_date": str(row.get("entry_date")),
                    "symbol": str(row.get("symbol")),
                    "contrast_label": str(row.get("contrast_label")),
                    "classified_band": state,
                    "expected_band": expected,
                    "classification_correct": is_correct,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112bx_packaging_process_enabler_balance_band_review_v1",
            "feature_count": len(band_rows),
            "contrast_row_count": len(contrast_rows),
            "classification_correct_count": correct_count,
            "classification_accuracy": round(correct_count / len(contrast_rows), 4),
            "balance_band_count": 3,
            "recommended_next_posture": "test_transfer_of_balance_band_to_adjacent_enabler_like_states",
        }
        interpretation = [
            "V1.12BX upgrades the single contrastive veto into a three-band internal state template: veto band, de-risk band, and eligibility band.",
            "The balance object is not a static threshold point; it is a bounded internal state region built from directionally opposed bad/good contributor states.",
        ]
        return V112BXPackagingProcessEnablerBalanceBandReviewReport(
            summary=summary,
            contrast_rows=contrast_rows,
            band_rows=band_rows,
            classification_rows=classification_rows,
            interpretation=interpretation,
        )

    def _classify_row(self, *, row: dict[str, Any], band_rows: list[dict[str, Any]]) -> str:
        healthy_count = 0
        risk_count = 0
        for band in band_rows:
            feature_name = str(band["feature_name"])
            value = float(row.get(feature_name, 0.0))
            midpoint = float(band["balance_midpoint"])
            direction = str(band["direction"])
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


def write_v112bx_packaging_process_enabler_balance_band_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BXPackagingProcessEnablerBalanceBandReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
