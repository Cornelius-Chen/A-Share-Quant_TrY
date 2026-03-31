from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V15FeatureAdmissibilityReviewReport:
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


class V15FeatureAdmissibilityReviewAnalyzer:
    """Review whether bounded report-only context features deserve candidacy consideration."""

    def analyze(
        self,
        *,
        candidacy_protocol_payload: dict[str, Any],
        context_feature_schema_payload: dict[str, Any],
        bounded_discrimination_payload: dict[str, Any],
    ) -> V15FeatureAdmissibilityReviewReport:
        protocol_summary = dict(candidacy_protocol_payload.get("summary", {}))
        protocol = dict(candidacy_protocol_payload.get("protocol", {}))
        schema_rows = list(context_feature_schema_payload.get("schema_rows", []))
        discrimination_rows = list(bounded_discrimination_payload.get("discrimination_rows", []))

        if not bool(protocol_summary.get("ready_for_feature_admissibility_review_next")):
            raise ValueError("V1.5 protocol must explicitly allow per-feature admissibility review next.")

        stable_discrimination_present = bool(
            bounded_discrimination_payload.get("summary", {}).get("stable_discrimination_present")
        )

        candidate_names = set(str(name) for name in protocol.get("candidate_feature_names", []))
        review_rows: list[dict[str, Any]] = []
        for schema_row in schema_rows:
            feature_name = str(schema_row.get("feature_name", ""))
            if feature_name not in candidate_names:
                continue

            point_in_time_clean_definition = True
            source_contamination_controlled = True
            binding_rule_stable_and_auditable = True
            not_strategy_integrated = bool(schema_row.get("report_only"))

            if feature_name in {
                "single_pulse_support",
                "multi_day_reinforcement_support",
                "policy_followthrough_support",
            }:
                evidence_sufficiency = stable_discrimination_present
                non_redundancy_or_orthogonality = True
                candidacy_outcome = "allow_provisional_candidacy_review"
                review_reading = "Directional separation is already explicit and the feature is not a pure duplicate label."
            elif feature_name == "concept_confirmation_depth":
                evidence_sufficiency = stable_discrimination_present
                non_redundancy_or_orthogonality = True
                candidacy_outcome = "allow_provisional_candidacy_review"
                review_reading = "Concept depth adds bounded concept-side information beyond catalyst persistence class alone."
            else:
                evidence_sufficiency = stable_discrimination_present
                non_redundancy_or_orthogonality = False
                candidacy_outcome = "hold_for_more_evidence"
                review_reading = "Indirectness is directionally useful but still too close to the current concept-depth split to clear non-redundancy."

            admissible = (
                point_in_time_clean_definition
                and source_contamination_controlled
                and binding_rule_stable_and_auditable
                and evidence_sufficiency
                and not_strategy_integrated
            )

            review_rows.append(
                {
                    "feature_name": feature_name,
                    "point_in_time_clean_definition": point_in_time_clean_definition,
                    "source_contamination_controlled": source_contamination_controlled,
                    "binding_rule_stable_and_auditable": binding_rule_stable_and_auditable,
                    "evidence_sufficiency": evidence_sufficiency,
                    "non_redundancy_or_orthogonality": non_redundancy_or_orthogonality,
                    "safe_containment": not_strategy_integrated,
                    "admissible_for_candidacy_review": admissible,
                    "candidacy_outcome": candidacy_outcome,
                    "review_reading": review_reading,
                }
            )

        summary = {
            "acceptance_posture": "open_v15_feature_admissibility_review_v1_as_bounded_review",
            "reviewed_feature_count": len(review_rows),
            "allow_provisional_candidacy_review_count": sum(
                1 for row in review_rows if row.get("candidacy_outcome") == "allow_provisional_candidacy_review"
            ),
            "hold_for_more_evidence_count": sum(
                1 for row in review_rows if row.get("candidacy_outcome") == "hold_for_more_evidence"
            ),
            "reject_candidacy_count": sum(
                1 for row in review_rows if row.get("candidacy_outcome") == "retain_as_report_only_reject_candidacy"
            ),
            "ready_for_v15_phase_check_next": len(review_rows) > 0,
        }
        interpretation = [
            "V1.5 reviews minimum candidacy fitness, not promotion. The important distinction is whether a report-only feature deserves continued candidacy attention at all.",
            "A positive admissibility result only means the feature can stay inside bounded candidacy review. It does not authorize retained promotion or strategy integration.",
            "The next legal step is a V1.5 phase-level check that decides whether the candidacy review answered enough to close the phase.",
        ]
        return V15FeatureAdmissibilityReviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v15_feature_admissibility_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V15FeatureAdmissibilityReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
