from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AGPhaseClosureCheckReport:
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


class V112AGPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AGPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ag_as_bounded_label_draft_integrity_success",
            "v112ag_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ag_waiting_state_now": True,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ag_phase_check",
                "actual": {
                    "label_skeleton_count": phase_summary.get("label_skeleton_count"),
                    "family_support_mapping_count": phase_summary.get("family_support_mapping_count"),
                    "anti_leakage_review_count": phase_summary.get("anti_leakage_review_count"),
                    "ambiguity_preservation_count": phase_summary.get("ambiguity_preservation_count"),
                },
                "reading": "The CPO label draft now has a bounded skeleton, support matrix, leakage review, and ambiguity guards, but still no training rights.",
            }
        ]
        interpretation = [
            "V1.12AG closes when the draft becomes structurally reviewable without collapsing ambiguity or leaking future information.",
            "The next lawful move is owner review of draft integrity, not automatic training.",
        ]
        return V112AGPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ag_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AGPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
