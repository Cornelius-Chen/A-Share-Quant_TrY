from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V16StabilityReviewProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V16StabilityReviewProtocolAnalyzer:
    """Freeze the bounded protocol for provisional-candidacy stability review."""

    def analyze(
        self,
        *,
        v16_phase_charter_payload: dict[str, Any],
        v15_feature_admissibility_review_payload: dict[str, Any],
    ) -> V16StabilityReviewProtocolReport:
        charter_summary = dict(v16_phase_charter_payload.get("summary", {}))
        review_rows = list(v15_feature_admissibility_review_payload.get("review_rows", []))

        if not bool(charter_summary.get("do_open_v16_now")):
            raise ValueError("V1.6 charter must be open before the stability-review protocol can be frozen.")

        provisional_candidates = [
            str(row.get("feature_name", ""))
            for row in review_rows
            if row.get("candidacy_outcome") == "allow_provisional_candidacy_review"
        ]
        protocol = {
            "provisional_candidate_feature_names": provisional_candidates,
            "review_axes": [
                "cross_artifact_consistency",
                "bounded_definition_stability",
                "continued_safe_containment",
                "hold_or_continue_decision",
            ],
            "minimum_stability_requirements": [
                "admissibility_result_remains_consistent",
                "feature_definition_has_not drifted",
                "report_only boundary still holds",
                "no promotion dependency is required to keep the feature alive",
            ],
            "stability_outcomes": [
                "continue_provisional_candidacy",
                "hold_for_more_stability_evidence",
                "drop_from_provisional_candidacy",
            ],
            "forbidden_actions": [
                "retained_feature_promotion",
                "strategy_integration",
                "new replay or refresh expansion",
                "local_model_opening",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v16_stability_review_protocol_v1",
            "provisional_candidate_count": len(provisional_candidates),
            "review_axis_count": len(protocol["review_axes"]),
            "allow_retained_promotion_now": False,
            "ready_for_feature_stability_review_next": len(provisional_candidates) > 0,
        }
        interpretation = [
            "V1.6 does not reopen admissibility; it tests whether provisional candidacy is stable enough to remain alive under bounded review.",
            "The protocol is still review-only and keeps all promotion and integration actions forbidden.",
            "The next legal action is per-feature stability review, not a jump to retained features or local models.",
        ]
        return V16StabilityReviewProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v16_stability_review_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V16StabilityReviewProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
