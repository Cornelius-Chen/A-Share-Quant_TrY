from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111APhaseClosureCheckReport:
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


class V111APhaseClosureCheckAnalyzer:
    """Close the first acquisition pilot after one bounded execution cycle."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        screened_first_collection_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V111APhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        collection_summary = dict(screened_first_collection_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v111a_now"))
            and collection_summary.get("admitted_candidate_count", 0) >= 1
            and collection_summary.get("sample_limit_breaches", 0) == 0
            and not bool(phase_summary.get("allow_retained_promotion_now"))
        )
        summary = {
            "acceptance_posture": "close_v111a_as_bounded_first_acquisition_pilot_success",
            "v111a_success_criteria_met": success_criteria_met,
            "admitted_candidate_count": collection_summary.get("admitted_candidate_count", 0),
            "admitted_policy_followthrough_count": collection_summary.get("admitted_policy_followthrough_count", 0),
            "enter_v111a_waiting_state_now": success_criteria_met,
            "allow_auto_follow_on_now": False,
            "recommended_next_posture": "preserve_v111a_candidate_records_and_wait_for_owner_review_or_new_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v111a_charter",
                "actual": {
                    "do_open_v111a_now": charter_summary.get("do_open_v111a_now"),
                },
                "reading": "V1.11A opened as a bounded owner-reviewed exception phase.",
            },
            {
                "evidence_name": "v111a_collection",
                "actual": {
                    "admitted_candidate_count": collection_summary.get("admitted_candidate_count"),
                    "admitted_policy_followthrough_count": collection_summary.get("admitted_policy_followthrough_count"),
                    "sample_limit_breaches": collection_summary.get("sample_limit_breaches"),
                },
                "reading": "The pilot succeeded if it admitted bounded new candidates without breaching caps, even if direct policy-followthrough breadth did not expand yet.",
            },
            {
                "evidence_name": "v111a_phase_check",
                "actual": {
                    "acquisition_path_validated": phase_summary.get("acquisition_path_validated"),
                    "direct_policy_followthrough_breadth_gain_present": phase_summary.get(
                        "direct_policy_followthrough_breadth_gain_present"
                    ),
                },
                "reading": "Closure should preserve the distinction between validating the acquisition path and changing the promotion judgment.",
            },
        ]
        interpretation = [
            "V1.11A has completed one bounded first-pilot cycle and produced real acquisition candidates under the frozen V1.11 rules.",
            "That is enough to close the phase successfully without auto-opening a follow-on pilot or retained-feature review.",
            "Per current governance, the correct posture is waiting state until the owner chooses the next move.",
        ]
        return V111APhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v111a_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111APhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
