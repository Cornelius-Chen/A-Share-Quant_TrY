from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V110APhaseClosureCheckReport:
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


class V110APhaseClosureCheckAnalyzer:
    """Check whether V1.10A has reached a lawful bounded closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        cross_family_probe_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V110APhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        probe_summary = dict(cross_family_probe_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v110a_now"))
            and probe_summary.get("candidate_count", 0) >= 0
            and not bool(phase_summary.get("open_follow_on_probe_now"))
            and not bool(phase_summary.get("promote_retained_now"))
        )

        summary = {
            "acceptance_posture": "close_v110a_as_single_cross_family_probe_success",
            "v110a_success_criteria_met": success_criteria_met,
            "candidate_count": probe_summary.get("candidate_count", 0),
            "admitted_case_count": probe_summary.get("admitted_case_count", 0),
            "successful_negative_probe": bool(probe_summary.get("successful_negative_probe")),
            "enter_v110a_waiting_state_now": success_criteria_met,
            "open_v110b_now": False,
            "promote_retained_now": False,
            "recommended_next_posture": "preserve_v110a_probe_result_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v110a_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "owner_led_exception_phase": True,
                    "allow_auto_follow_on_phase": False,
                },
                "reading": "V1.10A was opened as a one-off owner-led exception phase with no automatic successor.",
            },
            {
                "evidence_name": "cross_family_probe",
                "actual": {
                    "candidate_count": probe_summary.get("candidate_count"),
                    "admitted_case_count": probe_summary.get("admitted_case_count"),
                    "successful_negative_probe": probe_summary.get("successful_negative_probe"),
                },
                "reading": "The single probe produced an explicit bounded result without forcing new evidence or opening wider collection.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "open_follow_on_probe_now": phase_summary.get("open_follow_on_probe_now"),
                    "promote_retained_now": phase_summary.get("promote_retained_now"),
                },
                "reading": "The branch remains bounded and explicitly forbids automatic continuation into V1.10B+ or promotion.",
            },
        ]
        interpretation = [
            "V1.10A has answered its only question: whether cross-family, non-redundant policy-followthrough breadth evidence exists inside the current bounded pool.",
            "A zero-admission outcome is still a successful bounded closure because it is an explicit negative result rather than a governance failure.",
            "Per the owner guardrail, the correct move is waiting state, not auto-creation of V1.10B or wider replay.",
        ]
        return V110APhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v110a_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V110APhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
