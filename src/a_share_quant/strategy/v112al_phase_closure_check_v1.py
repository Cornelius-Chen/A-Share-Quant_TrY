from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ALPhaseClosureCheckReport:
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


class V112ALPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ALPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112al_as_bounded_training_readiness_review_success",
            "v112al_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112al_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_label_freeze_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112al_phase_check",
                "actual": {
                    "bounded_training_pilot_lawful_now": phase_summary.get("bounded_training_pilot_lawful_now"),
                    "bounded_training_pilot_scope": phase_summary.get("bounded_training_pilot_scope"),
                    "primary_bottleneck_layer": phase_summary.get("primary_bottleneck_layer"),
                },
                "reading": (
                    "The project now knows the lawful upper bound of any immediate pilot and the layer that still constrains it most."
                ),
            }
        ]
        interpretation = [
            "V1.12AL closes once the lawful upper bound of a first pilot is explicit.",
            "The next move is a very small bounded pilot only if the project chooses to open it deliberately.",
        ]
        return V112ALPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112al_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ALPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
