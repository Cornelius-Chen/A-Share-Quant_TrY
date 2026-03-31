from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V16PhaseCheckReport:
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


class V16PhaseCheckAnalyzer:
    """Check the bounded posture of V1.6 after the first stability-review cycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_stability_review_payload: dict[str, Any],
    ) -> V16PhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_stability_review_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v16_active_but_bounded_as_stability_review",
            "v16_open": bool(charter_summary.get("do_open_v16_now")),
            "continue_provisional_candidacy_count": review_summary.get("continue_provisional_candidacy_count", 0),
            "hold_for_more_stability_evidence_count": review_summary.get("hold_for_more_stability_evidence_count", 0),
            "promote_retained_now": False,
            "do_integrate_into_strategy_now": False,
            "recommended_next_posture": "prepare_v16_phase_closure_or_waiting_state_not_promotion",
        }
        evidence_rows = [
            {
                "evidence_name": "v16_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "recommended_first_action": charter_summary.get("recommended_first_action"),
                },
                "reading": "V1.6 opened lawfully as stability review, not promotion.",
            },
            {
                "evidence_name": "feature_stability_review",
                "actual": {
                    "continue_provisional_candidacy_count": review_summary.get("continue_provisional_candidacy_count"),
                    "hold_for_more_stability_evidence_count": review_summary.get("hold_for_more_stability_evidence_count"),
                    "drop_from_provisional_candidacy_count": review_summary.get("drop_from_provisional_candidacy_count"),
                },
                "reading": "The bounded review already answers whether current provisional candidates remain alive under stability scrutiny.",
            },
        ]
        interpretation = [
            "V1.6 has produced bounded stability judgments without crossing into promotion.",
            "That means the phase now has a clear continued-candidacy posture and does not need wider expansion to justify itself.",
            "The next legal step is a closure check, not integration or local-model work.",
        ]
        return V16PhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v16_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V16PhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
