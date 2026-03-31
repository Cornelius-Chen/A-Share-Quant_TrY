from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112LPhaseClosureCheckReport:
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


class V112LPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112LPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112l_as_review_only_preservation_success",
            "v112l_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112l_waiting_state_now": True,
            "allow_auto_inner_drafting_now": False,
            "allow_formal_label_split_now": False,
            "recommended_next_posture": "keep_two_review_only_substates_and_one_mixed_target_frozen_until_explicit_owner_decision",
        }
        evidence_rows = [
            {
                "evidence_name": "v112l_phase_check",
                "actual": {
                    "preserved_review_only_count": phase_summary.get("preserved_review_only_count"),
                    "mixed_inner_drafting_target_count": phase_summary.get("mixed_inner_drafting_target_count"),
                    "formal_label_split_now": phase_summary.get("formal_label_split_now"),
                },
                "reading": (
                    "V1.12L closes once the owner review preserves the usable review-only substates and blocks automatic "
                    "next-step escalation."
                ),
            }
        ]
        interpretation = [
            "V1.12L ends in a cleaner review-only state than V1.12K.",
            "Any future inner-drafting move remains optional and must be explicitly reopened.",
        ]
        return V112LPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112l_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V112LPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
