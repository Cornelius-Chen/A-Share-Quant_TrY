from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112PhaseClosureCheckReport:
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


class V112PhaseClosureCheckAnalyzer:
    """Close the single-cycle training design phase after definition is frozen."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V112PhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v112_now"))
            and bool(phase_summary.get("ready_for_bounded_pilot_data_assembly_next"))
            and not bool(phase_summary.get("allow_strategy_integration_now"))
            and not bool(phase_summary.get("allow_black_box_deployment_now"))
        )
        summary = {
            "acceptance_posture": "close_v112_as_single_cycle_training_pilot_definition_success",
            "v112_success_criteria_met": success_criteria_met,
            "ready_for_bounded_pilot_data_assembly_next": phase_summary.get("ready_for_bounded_pilot_data_assembly_next"),
            "enter_v112_waiting_state_now": success_criteria_met,
            "allow_auto_training_now": False,
            "recommended_next_posture": "preserve_v112_protocol_and_wait_for_owner_review_of_bounded_pilot_data_assembly",
        }
        evidence_rows = [
            {
                "evidence_name": "v112_charter",
                "actual": {"do_open_v112_now": charter_summary.get("do_open_v112_now")},
                "reading": "V1.12 opened lawfully as a bounded one-cycle training design phase.",
            },
            {
                "evidence_name": "v112_phase_check",
                "actual": {
                    "ready_for_bounded_pilot_data_assembly_next": phase_summary.get("ready_for_bounded_pilot_data_assembly_next"),
                    "allow_strategy_integration_now": phase_summary.get("allow_strategy_integration_now"),
                    "allow_black_box_deployment_now": phase_summary.get("allow_black_box_deployment_now"),
                },
                "reading": "The phase succeeds when the first cycle experiment is sharply defined without slipping into deployment.",
            },
        ]
        interpretation = [
            "V1.12 is successful once one clean price-cycle experiment is defined and ready for bounded data assembly.",
            "That is enough to close the phase without auto-training or widening to many objects.",
            "Per governance, the correct next posture is waiting state until the owner authorizes the next bounded step.",
        ]
        return V112PhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112PhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
