from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18CPhaseClosureCheckReport:
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


class V18CPhaseClosureCheckAnalyzer:
    """Check whether V1.8C has reached a lawful bounded closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        screened_collection_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V18CPhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        collection_summary = dict(screened_collection_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v18c_now"))
            and collection_summary.get("targets_with_admitted_cases_count", 0) >= 1
            and collection_summary.get("sample_limit_breaches", 0) == 0
            and not bool(phase_summary.get("promote_retained_now"))
        )

        summary = {
            "acceptance_posture": "close_v18c_as_bounded_screened_collection_success",
            "v18c_success_criteria_met": success_criteria_met,
            "admitted_case_count": collection_summary.get("admitted_case_count", 0),
            "targets_with_admitted_cases_count": collection_summary.get("targets_with_admitted_cases_count", 0),
            "enter_v18c_waiting_state_now": success_criteria_met,
            "promote_retained_now": False,
            "open_new_refresh_now": False,
            "recommended_next_posture": "preserve_v18c_collection_results_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v18c_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v18c_now": charter_summary.get("do_open_v18c_now"),
                },
                "reading": "V1.8C opened lawfully as a screened bounded collection phase.",
            },
            {
                "evidence_name": "screened_collection",
                "actual": {
                    "admitted_case_count": collection_summary.get("admitted_case_count"),
                    "targets_with_admitted_cases_count": collection_summary.get("targets_with_admitted_cases_count"),
                    "sample_limit_breaches": collection_summary.get("sample_limit_breaches"),
                },
                "reading": "The current collection answered whether new lawful breadth evidence could actually be gathered under the frozen rules.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "promote_retained_now": phase_summary.get("promote_retained_now"),
                    "do_integrate_into_strategy_now": phase_summary.get("do_integrate_into_strategy_now"),
                },
                "reading": "The branch remains below promotion and integration thresholds, so closure should preserve collected breadth evidence rather than force promotion.",
            },
        ]
        interpretation = [
            "V1.8C has now answered its core question: whether lawful screened bounded collection can produce real additional breadth evidence for the two target features.",
            "That is enough to close the phase successfully without promoting any feature into retained status.",
            "Per the autonomy policy, the correct move is to enter waiting state until a new owner phase switch or trigger appears.",
        ]
        return V18CPhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v18c_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18CPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
