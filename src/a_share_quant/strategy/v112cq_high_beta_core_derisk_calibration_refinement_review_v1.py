from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CQHighBetaCoreDeriskCalibrationRefinementReviewReport:
    summary: dict[str, Any]
    band_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "band_rows": self.band_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CQHighBetaCoreDeriskCalibrationRefinementReviewAnalyzer:
    def analyze(
        self,
        *,
        co_payload: dict[str, Any],
        cp_payload: dict[str, Any],
    ) -> V112CQHighBetaCoreDeriskCalibrationRefinementReviewReport:
        candidate_rows = list(co_payload.get("candidate_rule_rows", []))
        if not candidate_rows:
            raise ValueError("V1.12CQ requires V1.12CO candidate rule rows.")

        mild_band = max(
            (
                row
                for row in candidate_rows
                if float(row.get("neutral_symbol_return_delta", -1.0)) >= 0.0
                and bool(row.get("beats_evidence_baseline_drawdown")) is True
            ),
            key=lambda row: (
                float(row["evidence_total_return"]),
                float(row["evidence_max_drawdown"]),
                -float(row["reduced_exposure"]),
            ),
        )
        strong_band = max(
            (
                row
                for row in candidate_rows
                if bool(row.get("beats_evidence_baseline_return")) is True
                and bool(row.get("beats_evidence_baseline_drawdown")) is True
            ),
            key=lambda row: (
                float(row["neutral_symbol_return_delta"]),
                float(row["evidence_total_return"]),
                float(row["evidence_max_drawdown"]),
            ),
        )

        band_rows = [
            {
                "band_name": "neutral_safe_mild_derisk_band",
                "band_role": "de-risk without harming the current neutral 300502 path",
                **mild_band,
            },
            {
                "band_name": "evidence_optimizing_stronger_derisk_band",
                "band_role": "stronger late-state de-risk that beats evidence baseline on both return and drawdown",
                **strong_band,
            },
        ]

        cp_summary = dict(cp_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "freeze_v112cq_high_beta_core_derisk_calibration_refinement_review_v1",
            "band_count": len(band_rows),
            "mild_band_neutral_safe": float(mild_band["neutral_symbol_return_delta"]) >= 0.0,
            "strong_band_beats_evidence_both": bool(strong_band["beats_evidence_baseline_return"])
            and bool(strong_band["beats_evidence_baseline_drawdown"]),
            "combined_replay_ready_after_split": False,
            "cp_combined_return_delta_vs_neutral": float(cp_summary.get("return_delta_vs_neutral", 0.0)),
            "cp_combined_drawdown_delta_vs_neutral": float(cp_summary.get("drawdown_delta_vs_neutral", 0.0)),
            "recommended_next_posture": "keep_300502_on_split_derisk_bands_and_defer_joint_promotion_until_neutral_safe_calibration_improves",
        }
        comparison_rows = [
            {
                "comparison_name": "mild_vs_strong_neutral_symbol_return_delta",
                "baseline_value": round(float(mild_band["neutral_symbol_return_delta"]), 4),
                "pilot_value": round(float(strong_band["neutral_symbol_return_delta"]), 4),
                "delta": round(
                    float(strong_band["neutral_symbol_return_delta"]) - float(mild_band["neutral_symbol_return_delta"]), 4
                ),
            },
            {
                "comparison_name": "mild_vs_strong_evidence_total_return",
                "baseline_value": round(float(mild_band["evidence_total_return"]), 4),
                "pilot_value": round(float(strong_band["evidence_total_return"]), 4),
                "delta": round(
                    float(strong_band["evidence_total_return"]) - float(mild_band["evidence_total_return"]), 4
                ),
            },
            {
                "comparison_name": "mild_vs_strong_evidence_max_drawdown",
                "baseline_value": round(float(mild_band["evidence_max_drawdown"]), 4),
                "pilot_value": round(float(strong_band["evidence_max_drawdown"]), 4),
                "delta": round(
                    float(strong_band["evidence_max_drawdown"]) - float(mild_band["evidence_max_drawdown"]), 4
                ),
            },
        ]
        interpretation = [
            "V1.12CQ stops searching for a single 300502 de-risk point and instead extracts a calibration frontier.",
            "The mild band preserves the current neutral 300502 path, while the stronger band improves the evidence bundle on both return and drawdown at the cost of a small neutral-path giveback.",
            "This means 300502 now reads as a split-band de-risk problem rather than as a single-rule promotion candidate.",
        ]
        return V112CQHighBetaCoreDeriskCalibrationRefinementReviewReport(
            summary=summary,
            band_rows=band_rows,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )


def write_v112cq_high_beta_core_derisk_calibration_refinement_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CQHighBetaCoreDeriskCalibrationRefinementReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
