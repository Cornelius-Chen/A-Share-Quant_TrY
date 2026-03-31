from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V16PhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V16PhaseCharterAnalyzer:
    """Open V1.6 after V1.5 closes and the owner requests provisional-candidacy stability review."""

    def analyze(
        self,
        *,
        v15_phase_closure_payload: dict[str, Any],
        v15_feature_admissibility_review_payload: dict[str, Any],
    ) -> V16PhaseCharterReport:
        closure_summary = dict(v15_phase_closure_payload.get("summary", {}))
        review_summary = dict(v15_feature_admissibility_review_payload.get("summary", {}))

        v15_waiting_ready = bool(closure_summary.get("enter_v15_waiting_state_now"))
        provisional_candidates_ready = review_summary.get("allow_provisional_candidacy_review_count", 0) > 0
        open_v16_now = v15_waiting_ready and provisional_candidates_ready

        charter = {
            "mission": "Review whether current provisional candidacy context features show enough bounded stability to justify continued candidacy attention without promoting them into retained features.",
            "in_scope": [
                "provisional-candidacy stability criteria",
                "bounded cross-artifact consistency review",
                "bounded persistence of admissibility judgments",
                "continued safe-containment review",
            ],
            "out_of_scope": [
                "retained-feature promotion",
                "strategy integration",
                "local regime segmentation",
                "new replay or refresh expansion",
                "formal model work",
            ],
            "success_criteria": [
                "freeze a bounded stability-review protocol",
                "produce stability judgments for the provisional candidacy features",
                "close the phase with a clear continued-candidacy or hold posture",
            ],
            "stop_criteria": [
                "if stability cannot be assessed without reopening data expansion",
                "if the work drifts into promotion or integration",
                "if provisional candidates prove too thin or inconsistent for bounded review",
            ],
            "handoff_condition": "After the charter opens, only replay-independent stability-review artifacts are allowed until the phase-level posture is explicit.",
        }
        summary = {
            "acceptance_posture": (
                "open_v16_provisional_candidacy_stability_review"
                if open_v16_now
                else "hold_v16_charter_until_prerequisites_hold"
            ),
            "v15_waiting_state_present": v15_waiting_ready,
            "provisional_candidate_count": review_summary.get("allow_provisional_candidacy_review_count", 0),
            "do_open_v16_now": open_v16_now,
            "recommended_first_action": "freeze_v16_stability_review_protocol_v1",
        }
        interpretation = [
            "V1.5 already sorted bounded context features into provisional candidacy or hold, but did not answer whether those provisional candidates are stable enough to remain alive.",
            "That makes bounded stability review the next lawful question before any future promotion discussion.",
            "So V1.6 should open as a review-only phase, not as a promotion, integration, or local-model phase.",
        ]
        return V16PhaseCharterReport(
            summary=summary,
            charter=charter,
            interpretation=interpretation,
        )


def write_v16_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V16PhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
