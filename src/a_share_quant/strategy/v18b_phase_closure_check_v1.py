from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18BPhaseClosureCheckReport:
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


class V18BPhaseClosureCheckAnalyzer:
    """Check whether V1.8B has reached a lawful bounded closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_admission_gate_review_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V18BPhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_admission_gate_review_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v18b_now"))
            and review_summary.get("reviewed_feature_count", 0) >= 1
            and not bool(phase_summary.get("allow_sample_collection_now"))
        )

        summary = {
            "acceptance_posture": "close_v18b_as_bounded_admission_gate_success",
            "v18b_success_criteria_met": success_criteria_met,
            "reviewed_feature_count": review_summary.get("reviewed_feature_count", 0),
            "admission_gate_ready_count": review_summary.get("admission_gate_ready_count", 0),
            "enter_v18b_waiting_state_now": success_criteria_met,
            "allow_sample_collection_now": False,
            "promote_retained_now": False,
            "recommended_next_posture": "preserve_v18b_admission_gate_results_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v18b_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v18b_now": charter_summary.get("do_open_v18b_now"),
                },
                "reading": "V1.8B opened lawfully as a bounded sample admission-gate phase.",
            },
            {
                "evidence_name": "feature_admission_gate_review",
                "actual": {
                    "reviewed_feature_count": review_summary.get("reviewed_feature_count"),
                    "admission_gate_ready_count": review_summary.get("admission_gate_ready_count"),
                    "allow_sample_collection_now": review_summary.get("allow_sample_collection_now"),
                },
                "reading": "The current review answered whether the two target features now have clean admission gates for future screened breadth collection.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "allow_sample_collection_now": phase_summary.get("allow_sample_collection_now"),
                    "promote_retained_now": phase_summary.get("promote_retained_now"),
                },
                "reading": "The branch remains below collection and promotion thresholds, so closure should preserve admission gating rather than force a wider action.",
            },
        ]
        interpretation = [
            "V1.8B has now answered its core question: what bounded admission gate the two breadth-target features must satisfy before any future screened collection.",
            "That is enough to close the phase successfully without collecting samples or promoting any feature.",
            "Per the autonomy policy, the correct move is to enter waiting state until a new owner phase switch or trigger appears.",
        ]
        return V18BPhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v18b_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18BPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
