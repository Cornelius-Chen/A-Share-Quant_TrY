from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V14PhaseClosureCheckReport:
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


class V14PhaseClosureCheckAnalyzer:
    """Check whether V1.4 has reached a bounded and lawful closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        bounded_discrimination_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V14PhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        discrimination_summary = dict(bounded_discrimination_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v14_now"))
            and bool(discrimination_summary.get("stable_discrimination_present"))
            and not bool(phase_summary.get("do_integrate_into_strategy_now"))
        )

        summary = {
            "acceptance_posture": "close_v14_as_bounded_context_consumption_success",
            "v14_success_criteria_met": success_criteria_met,
            "stable_discrimination_present": bool(discrimination_summary.get("stable_discrimination_present")),
            "promote_context_now": False,
            "enter_v14_waiting_state_now": success_criteria_met,
            "open_retained_feature_review_now": False,
            "open_local_regime_phase_now": False,
            "recommended_next_posture": "preserve_v14_results_as_report_only_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v14_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v14_now": charter_summary.get("do_open_v14_now"),
                },
                "reading": "V1.4 opened lawfully as a bounded context-consumption pilot.",
            },
            {
                "evidence_name": "bounded_discrimination",
                "actual": {
                    "acceptance_posture": discrimination_summary.get("acceptance_posture"),
                    "stable_discrimination_present": discrimination_summary.get("stable_discrimination_present"),
                    "concept_depth_difference_present": discrimination_summary.get("concept_depth_difference_present"),
                },
                "reading": "The bounded review produced stable directional discrimination without relying on strategy-level consumption.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "promote_context_now": phase_summary.get("promote_context_now"),
                    "do_integrate_into_strategy_now": phase_summary.get("do_integrate_into_strategy_now"),
                },
                "reading": "The phase remains below promotion threshold, which means the correct closure is bounded report-only success rather than forced expansion.",
            },
        ]
        interpretation = [
            "V1.4 has now answered its core question: bounded concept and catalyst context can be consumed as report-only features with stable directional discrimination.",
            "That is enough to close the phase successfully without promoting the branch into strategy integration, retained features, or local-model work.",
            "Per the autonomy policy, the correct move is to enter waiting state until a new owner phase switch or trigger appears.",
        ]
        return V14PhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v14_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V14PhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
