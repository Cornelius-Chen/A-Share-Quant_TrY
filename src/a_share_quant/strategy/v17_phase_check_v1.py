from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V17PhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V17PhaseCheckAnalyzer:
    """Check the bounded posture of V1.7 after the first promotion-gap review cycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_promotion_gap_review_payload: dict[str, Any],
    ) -> V17PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_promotion_gap_review_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v17_active_but_bounded_as_promotion_evidence_generation",
            "v17_open": bool(charter_summary.get("do_open_v17_now")),
            "reviewed_feature_count": review_summary.get("reviewed_feature_count", 0),
            "promotion_ready_now_count": review_summary.get("promotion_ready_now_count", 0),
            "needs_additional_promotion_evidence_count": review_summary.get("needs_additional_promotion_evidence_count", 0),
            "promote_retained_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "prepare_v17_phase_closure_or_waiting_state_not_promotion",
        }
        evidence_rows = [
            {
                "evidence_name": "v17_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "recommended_first_action": charter_summary.get("recommended_first_action"),
                },
                "reading": "V1.7 opened lawfully as promotion-evidence generation, not as a promotion phase.",
            },
            {
                "evidence_name": "feature_promotion_gap_review",
                "actual": {
                    "reviewed_feature_count": review_summary.get("reviewed_feature_count"),
                    "promotion_ready_now_count": review_summary.get("promotion_ready_now_count"),
                    "needs_additional_promotion_evidence_count": review_summary.get("needs_additional_promotion_evidence_count"),
                },
                "reading": "The bounded review already states what evidence is missing for current provisional candidates.",
            },
        ]
        interpretation = [
            "V1.7 has produced bounded promotion-gap judgments without crossing into promotion.",
            "That means the phase now has a clear evidence-shortfall posture and does not need wider expansion to justify itself.",
            "The next legal step is a closure check, not retained-feature promotion or local-model work.",
        ]
        return V17PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v17_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V17PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
