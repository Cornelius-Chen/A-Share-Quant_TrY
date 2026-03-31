from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V16FeatureStabilityReviewReport:
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


class V16FeatureStabilityReviewAnalyzer:
    """Review whether provisional-candidacy features remain stable under bounded evidence."""

    def analyze(
        self,
        *,
        stability_protocol_payload: dict[str, Any],
        feature_admissibility_review_payload: dict[str, Any],
        bounded_discrimination_payload: dict[str, Any],
    ) -> V16FeatureStabilityReviewReport:
        protocol_summary = dict(stability_protocol_payload.get("summary", {}))
        protocol = dict(stability_protocol_payload.get("protocol", {}))
        admissibility_rows = list(feature_admissibility_review_payload.get("review_rows", []))
        discrimination_summary = dict(bounded_discrimination_payload.get("summary", {}))

        if not bool(protocol_summary.get("ready_for_feature_stability_review_next")):
            raise ValueError("V1.6 protocol must explicitly allow per-feature stability review next.")

        provisional_names = set(str(name) for name in protocol.get("provisional_candidate_feature_names", []))
        stable_discrimination_present = bool(discrimination_summary.get("stable_discrimination_present"))

        review_rows: list[dict[str, Any]] = []
        for row in admissibility_rows:
            feature_name = str(row.get("feature_name", ""))
            if feature_name not in provisional_names:
                continue

            cross_artifact_consistency = bool(row.get("admissible_for_candidacy_review")) and stable_discrimination_present
            bounded_definition_stability = bool(row.get("point_in_time_clean_definition")) and bool(
                row.get("binding_rule_stable_and_auditable")
            )
            continued_safe_containment = bool(row.get("safe_containment"))
            no_promotion_dependency = True

            if all([cross_artifact_consistency, bounded_definition_stability, continued_safe_containment, no_promotion_dependency]):
                stability_outcome = "continue_provisional_candidacy"
                review_reading = "Current bounded evidence is stable enough to keep the feature alive inside provisional candidacy review."
            else:
                stability_outcome = "hold_for_more_stability_evidence"
                review_reading = "Current bounded evidence is still too thin or unstable for continued provisional candidacy."

            review_rows.append(
                {
                    "feature_name": feature_name,
                    "cross_artifact_consistency": cross_artifact_consistency,
                    "bounded_definition_stability": bounded_definition_stability,
                    "continued_safe_containment": continued_safe_containment,
                    "no_promotion_dependency": no_promotion_dependency,
                    "stability_outcome": stability_outcome,
                    "review_reading": review_reading,
                }
            )

        summary = {
            "acceptance_posture": "open_v16_feature_stability_review_v1_as_bounded_review",
            "reviewed_feature_count": len(review_rows),
            "continue_provisional_candidacy_count": sum(
                1 for row in review_rows if row.get("stability_outcome") == "continue_provisional_candidacy"
            ),
            "hold_for_more_stability_evidence_count": sum(
                1 for row in review_rows if row.get("stability_outcome") == "hold_for_more_stability_evidence"
            ),
            "drop_from_provisional_candidacy_count": sum(
                1 for row in review_rows if row.get("stability_outcome") == "drop_from_provisional_candidacy"
            ),
            "ready_for_v16_phase_check_next": len(review_rows) > 0,
        }
        interpretation = [
            "V1.6 checks whether provisional candidacy remains stable, not whether features should be promoted.",
            "A positive stability result only means the feature may continue to live inside bounded candidacy review.",
            "The next legal step is a V1.6 phase-level check, not promotion or local-model work.",
        ]
        return V16FeatureStabilityReviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v16_feature_stability_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V16FeatureStabilityReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
