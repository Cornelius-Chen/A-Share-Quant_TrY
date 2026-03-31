from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18APhaseClosureCheckReport:
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


class V18APhaseClosureCheckAnalyzer:
    """Check whether V1.8A has reached a lawful bounded closure point."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        breadth_entry_design_payload: dict[str, Any],
        phase_check_payload: dict[str, Any],
    ) -> V18APhaseClosureCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        design_summary = dict(breadth_entry_design_payload.get("summary", {}))
        phase_summary = dict(phase_check_payload.get("summary", {}))

        success_criteria_met = (
            bool(charter_summary.get("do_open_v18a_now"))
            and design_summary.get("entry_row_count", 0) >= 1
            and not bool(phase_summary.get("collect_samples_now"))
        )

        summary = {
            "acceptance_posture": "close_v18a_as_bounded_sample_breadth_expansion_success",
            "v18a_success_criteria_met": success_criteria_met,
            "target_feature_count": charter_summary.get("sample_breadth_target_feature_count", 0),
            "entry_row_count": design_summary.get("entry_row_count", 0),
            "enter_v18a_waiting_state_now": success_criteria_met,
            "collect_samples_now": False,
            "promote_retained_now": False,
            "recommended_next_posture": "preserve_v18a_breadth_entry_design_and_wait_for_owner_phase_switch_or_trigger",
        }
        evidence_rows = [
            {
                "evidence_name": "v18a_charter",
                "actual": {
                    "acceptance_posture": charter_summary.get("acceptance_posture"),
                    "do_open_v18a_now": charter_summary.get("do_open_v18a_now"),
                },
                "reading": "V1.8A opened lawfully as a bounded sample-breadth expansion phase.",
            },
            {
                "evidence_name": "breadth_entry_design",
                "actual": {
                    "entry_row_count": design_summary.get("entry_row_count"),
                    "allow_unbounded_sample_collection_now": design_summary.get("allow_unbounded_sample_collection_now"),
                },
                "reading": "The current review answered what the minimum lawful breadth-entry paths are for the two target features.",
            },
            {
                "evidence_name": "phase_check",
                "actual": {
                    "acceptance_posture": phase_summary.get("acceptance_posture"),
                    "collect_samples_now": phase_summary.get("collect_samples_now"),
                    "promote_retained_now": phase_summary.get("promote_retained_now"),
                },
                "reading": "The branch remains below sample collection and promotion thresholds, so closure should preserve entry design rather than force a wider follow-on action.",
            },
        ]
        interpretation = [
            "V1.8A has now answered its core question: what the minimum lawful breadth-entry design is for the two sample-breadth target features.",
            "That is enough to close the phase successfully without collecting new samples or promoting any feature.",
            "Per the autonomy policy, the correct move is to enter waiting state until a new owner phase switch or trigger appears.",
        ]
        return V18APhaseClosureCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v18a_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18APhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
