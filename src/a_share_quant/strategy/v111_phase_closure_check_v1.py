from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111PhaseClosureCheckReport:
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


class V111PhaseClosureCheckAnalyzer:
    """Close V1.11 once the acquisition infrastructure basis is explicit."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        infrastructure_plan_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V111PhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        plan_summary = dict(infrastructure_plan_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v111_now"))
            and bool(plan_summary.get("ready_for_bounded_first_pilot_next"))
            and not bool(phase_summary.get("allow_strategy_integration_now"))
        )

        summary = {
            "acceptance_posture": "close_v111_as_sustained_acquisition_infrastructure_success",
            "v111_success_criteria_met": success_criteria_met,
            "ready_for_bounded_first_pilot_next": bool(plan_summary.get("ready_for_bounded_first_pilot_next")),
            "enter_v111_waiting_state_now": success_criteria_met,
            "allow_auto_first_pilot_now": False,
            "recommended_next_posture": "preserve_v111_infrastructure_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v111_charter",
                "actual": {"do_open_v111_now": charter_summary.get("do_open_v111_now")},
                "reading": "V1.11 opened lawfully as an exploration-layer infrastructure phase.",
            },
            {
                "evidence_name": "v111_infrastructure_plan",
                "actual": {
                    "acquisition_scope_count": plan_summary.get("acquisition_scope_count"),
                    "family_novelty_rule_count": plan_summary.get("family_novelty_rule_count"),
                    "ready_for_bounded_first_pilot_next": plan_summary.get("ready_for_bounded_first_pilot_next"),
                },
                "reading": "The phase produced a repeatable upstream acquisition basis that changes the future decision basis.",
            },
            {
                "evidence_name": "v111_phase_check",
                "actual": {"allow_auto_strategy_or_promotion": False},
                "reading": "The phase remains below admission and strategy layers, so closure preserves the design basis rather than auto-opening a pilot.",
            },
        ]
        interpretation = [
            "V1.11 has completed its exploration-layer mission by defining how sustained catalyst evidence should be acquired and recorded.",
            "That is enough to close the design phase successfully without auto-opening another phase.",
            "Per current governance, the correct next posture is waiting state until an owner-authorized pilot or trigger appears.",
        ]
        return V111PhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v111_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111PhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
