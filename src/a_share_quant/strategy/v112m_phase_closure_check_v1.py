from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112MPhaseClosureCheckReport:
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


class V112MPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112MPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112m_as_inner_draft_success",
            "v112m_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112m_waiting_state_now": True,
            "allow_auto_schema_change_now": False,
            "allow_auto_follow_up_now": False,
            "recommended_next_posture": "preserve_inner_draft_pieces_and_pause_before_any_label_or_schema decision",
        }
        evidence_rows = [
            {
                "evidence_name": "v112m_phase_check",
                "actual": {
                    "preservable_review_only_inner_candidate_count": phase_summary.get(
                        "preservable_review_only_inner_candidate_count"
                    ),
                    "unresolved_inner_residue_count": phase_summary.get("unresolved_inner_residue_count"),
                    "formal_label_split_now": phase_summary.get("formal_label_split_now"),
                },
                "reading": "V1.12M closes once one bounded inner-drafting pass has been completed and still remains review-only.",
            }
        ]
        interpretation = [
            "V1.12M adds detail inside the mixed stall cluster without changing the formal schema.",
            "Any future move remains optional and must be explicitly reopened.",
        ]
        return V112MPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112m_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V112MPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
