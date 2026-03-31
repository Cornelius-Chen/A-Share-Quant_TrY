from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V19FeatureBreadthRereviewReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V19FeatureBreadthRereviewAnalyzer:
    """Refresh promotion judgment after bounded breadth evidence arrives."""

    def analyze(
        self,
        *,
        breadth_rereview_protocol_payload: dict[str, Any],
        feature_promotion_gap_review_payload: dict[str, Any],
        screened_collection_payload: dict[str, Any],
    ) -> V19FeatureBreadthRereviewReport:
        protocol_summary = dict(breadth_rereview_protocol_payload.get("summary", {}))
        protocol = dict(breadth_rereview_protocol_payload.get("protocol", {}))
        prior_gap_rows = list(feature_promotion_gap_review_payload.get("review_rows", []))
        collection_rows = list(screened_collection_payload.get("collection_rows", []))

        if not bool(protocol_summary.get("ready_for_per_feature_breadth_rereview_next")):
            raise ValueError("V1.9 protocol must explicitly allow per-feature breadth re-review next.")

        prior_gap_by_name = {str(row.get("feature_name", "")): row for row in prior_gap_rows}
        admitted_rows_by_feature: dict[str, list[dict[str, Any]]] = {}
        for row in collection_rows:
            if row.get("admission_status") != "admit":
                continue
            feature_name = str(row.get("feature_name", ""))
            admitted_rows_by_feature.setdefault(feature_name, []).append(dict(row))

        review_rows: list[dict[str, Any]] = []
        for target_row in list(protocol.get("target_feature_rows", [])):
            feature_name = str(target_row.get("feature_name", ""))
            prior_row = dict(prior_gap_by_name.get(feature_name, {}))
            admitted_rows = admitted_rows_by_feature.get(feature_name, [])
            admitted_symbols = sorted({str(row.get("symbol", "")) for row in admitted_rows if row.get("symbol")})
            admitted_lane_ids = [
                str(row.get("lane_id", "")) for row in admitted_rows if row.get("lane_id")
            ]

            if feature_name == "single_pulse_support":
                breadth_gap_reduction = "material"
                updated_primary_shortfall = "non_redundancy_stress_gap"
                rereview_outcome = "continue_provisional_with_breadth_improvement"
                review_reading = (
                    "The new breadth cases materially reduce the original sample-breadth shortfall, but the feature "
                    "still looks too entangled with opening-led structure to support promotion."
                )
            elif feature_name == "policy_followthrough_support":
                breadth_gap_reduction = "partial"
                updated_primary_shortfall = "sample_breadth_gap"
                rereview_outcome = "continue_provisional_but_breadth_still_thin"
                review_reading = (
                    "The new breadth cases help, but they remain concentrated inside one symbol-family, so the original "
                    "sample-breadth shortfall is reduced only partially and does not justify promotion."
                )
            else:
                breadth_gap_reduction = "none"
                updated_primary_shortfall = str(target_row.get("prior_primary_shortfall"))
                rereview_outcome = "outside_v19_scope"
                review_reading = "The feature was not a breadth target for V1.9."

            review_rows.append(
                {
                    "feature_name": feature_name,
                    "prior_primary_shortfall": prior_row.get("primary_shortfall"),
                    "new_admitted_case_count": len(admitted_rows),
                    "new_admitted_symbol_count": len(admitted_symbols),
                    "new_admitted_symbols": admitted_symbols,
                    "new_admitted_lane_ids": admitted_lane_ids,
                    "breadth_gap_reduction": breadth_gap_reduction,
                    "updated_primary_shortfall": updated_primary_shortfall,
                    "promotion_ready_now": False,
                    "rereview_outcome": rereview_outcome,
                    "review_reading": review_reading,
                }
            )

        summary = {
            "acceptance_posture": "open_v19_feature_breadth_rereview_v1_as_bounded_rereview",
            "reviewed_feature_count": len(review_rows),
            "shortfall_changed_count": sum(
                1
                for row in review_rows
                if row.get("updated_primary_shortfall") != row.get("prior_primary_shortfall")
            ),
            "breadth_gap_materially_reduced_count": sum(
                1 for row in review_rows if row.get("breadth_gap_reduction") == "material"
            ),
            "breadth_gap_partially_reduced_count": sum(
                1 for row in review_rows if row.get("breadth_gap_reduction") == "partial"
            ),
            "promotion_ready_now_count": 0,
            "ready_for_v19_phase_check_next": len(review_rows) > 0,
        }
        interpretation = [
            "V1.9 does not ask whether these features should be promoted today; it asks whether new bounded breadth evidence changes the shortfall ordering.",
            "single_pulse_support now has meaningfully broader support, but not enough orthogonality for promotion.",
            "policy_followthrough_support improved, but the new evidence is still too concentrated to remove the breadth constraint entirely.",
        ]
        return V19FeatureBreadthRereviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v19_feature_breadth_rereview_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V19FeatureBreadthRereviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
