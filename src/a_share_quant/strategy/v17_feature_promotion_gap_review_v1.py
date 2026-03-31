from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V17FeaturePromotionGapReviewReport:
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


class V17FeaturePromotionGapReviewAnalyzer:
    """State per-feature promotion shortfalls for the current provisional candidates."""

    def analyze(
        self,
        *,
        promotion_evidence_protocol_payload: dict[str, Any],
        feature_stability_review_payload: dict[str, Any],
        feature_admissibility_review_payload: dict[str, Any],
    ) -> V17FeaturePromotionGapReviewReport:
        protocol_summary = dict(promotion_evidence_protocol_payload.get("summary", {}))
        protocol = dict(promotion_evidence_protocol_payload.get("protocol", {}))
        stability_rows = list(feature_stability_review_payload.get("review_rows", []))
        admissibility_rows = list(feature_admissibility_review_payload.get("review_rows", []))

        if not bool(protocol_summary.get("ready_for_per_feature_promotion_gap_review_next")):
            raise ValueError("V1.7 protocol must explicitly allow per-feature promotion-gap review next.")

        admissibility_by_name = {
            str(row.get("feature_name", "")): row for row in admissibility_rows
        }
        provisional_names = set(str(name) for name in protocol.get("provisional_candidate_feature_names", []))

        review_rows: list[dict[str, Any]] = []
        for row in stability_rows:
            feature_name = str(row.get("feature_name", ""))
            if feature_name not in provisional_names:
                continue
            if row.get("stability_outcome") != "continue_provisional_candidacy":
                continue

            admissibility_row = dict(admissibility_by_name.get(feature_name, {}))
            sample_breadth_gap = True
            cross_pocket_or_cross_regime_gap = True
            non_redundancy_stress_gap = True
            safe_consumption_beyond_report_only_gap = True

            if feature_name == "concept_confirmation_depth":
                primary_shortfall = "cross_pocket_or_cross_regime_gap"
                minimum_evidence_path = "bounded_cross_theme_or_cross_regime_consistency_review"
            elif feature_name == "policy_followthrough_support":
                primary_shortfall = "sample_breadth_gap"
                minimum_evidence_path = "bounded_additional_followthrough_case_review"
            elif feature_name == "multi_day_reinforcement_support":
                primary_shortfall = "safe_consumption_beyond_report_only_gap"
                minimum_evidence_path = "bounded_safe_consumption_extension_review"
            else:
                primary_shortfall = "sample_breadth_gap"
                minimum_evidence_path = "bounded_multi_sample_review"

            review_rows.append(
                {
                    "feature_name": feature_name,
                    "sample_breadth_gap": sample_breadth_gap,
                    "cross_pocket_or_cross_regime_gap": cross_pocket_or_cross_regime_gap,
                    "non_redundancy_stress_gap": non_redundancy_stress_gap,
                    "safe_consumption_beyond_report_only_gap": safe_consumption_beyond_report_only_gap,
                    "primary_shortfall": primary_shortfall,
                    "minimum_evidence_path": minimum_evidence_path,
                    "promotion_readiness_now": False,
                    "review_reading": (
                        "The feature remains alive inside provisional candidacy, but promotion still needs explicit new evidence "
                        "beyond current bounded admissibility and stability review."
                    ),
                    "admissibility_basis_present": bool(admissibility_row.get("admissible_for_candidacy_review")),
                }
            )

        summary = {
            "acceptance_posture": "open_v17_feature_promotion_gap_review_v1_as_bounded_review",
            "reviewed_feature_count": len(review_rows),
            "promotion_ready_now_count": sum(1 for row in review_rows if row.get("promotion_readiness_now")),
            "needs_additional_promotion_evidence_count": sum(
                1 for row in review_rows if not row.get("promotion_readiness_now")
            ),
            "ready_for_v17_phase_check_next": len(review_rows) > 0,
        }
        interpretation = [
            "V1.7 asks what evidence is still missing, not whether the current provisional candidates should already be promoted.",
            "Each current provisional feature still has explicit promotion shortfalls even though it remains alive under bounded review.",
            "The next legal step is a V1.7 phase check, not retained-feature promotion itself.",
        ]
        return V17FeaturePromotionGapReviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v17_feature_promotion_gap_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V17FeaturePromotionGapReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
