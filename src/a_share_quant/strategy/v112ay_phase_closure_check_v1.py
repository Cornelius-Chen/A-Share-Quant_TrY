from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AYPhaseClosureCheckReport:
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


class V112AYPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AYPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ay_as_guarded_branch_training_layer_review_success",
            "v112ay_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ay_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ay_phase_check",
                "actual": {
                    "guarded_training_layer_admissible_count": phase_summary.get("guarded_training_layer_admissible_count"),
                    "branch_rows_retained_review_only_count": phase_summary.get("branch_rows_retained_review_only_count"),
                },
                "reading": "The phase closes once the branch layer has been cut into admissible guarded rows versus still-review-only rows.",
            }
        ]
        interpretation = [
            "V1.12AY closes with a bounded training-layer admissibility decision for branch rows.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AYPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ay_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AYPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
