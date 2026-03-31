from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APhaseClosureCheckReport:
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


class V112APhaseClosureCheckAnalyzer:
    """Close bounded pilot data assembly once the owner-correction sheet exists."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V112APhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v112a_now"))
            and bool(phase_summary.get("ready_for_owner_correction_next"))
            and not bool(phase_summary.get("allow_training_now"))
        )
        summary = {
            "acceptance_posture": "close_v112a_as_owner_correction_ready_pilot_data_assembly_success",
            "v112a_success_criteria_met": success_criteria_met,
            "ready_for_owner_correction_next": phase_summary.get("ready_for_owner_correction_next"),
            "enter_v112a_waiting_state_now": success_criteria_met,
            "allow_auto_training_now": False,
            "recommended_next_posture": "preserve_v112a_review_sheet_and_wait_for_owner_corrections",
        }
        evidence_rows = [
            {
                "evidence_name": "v112a_charter",
                "actual": {"do_open_v112a_now": charter_summary.get("do_open_v112a_now")},
                "reading": "V1.12A opened as a bounded pilot data assembly phase.",
            },
            {
                "evidence_name": "v112a_phase_check",
                "actual": {
                    "ready_for_owner_correction_next": phase_summary.get("ready_for_owner_correction_next"),
                    "allow_training_now": phase_summary.get("allow_training_now"),
                },
                "reading": "The phase succeeds once the owner can correct a concrete pilot sheet before any training begins.",
            },
        ]
        interpretation = [
            "V1.12A has completed its bounded assembly mission once a reviewable pilot sheet exists.",
            "That is enough to close the phase without auto-opening training.",
            "The correct next move is owner correction of the pilot dataset draft.",
        ]
        return V112APhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112a_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
