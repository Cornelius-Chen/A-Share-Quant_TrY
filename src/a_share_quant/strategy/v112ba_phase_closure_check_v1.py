from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BAPhaseClosureCheckReport:
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


class V112BAPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BAPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ba_as_10_row_layer_replacement_review_success",
            "v112ba_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ba_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ba_phase_check",
                "actual": {
                    "replace_7_row_baseline_now": phase_summary.get("replace_7_row_baseline_now"),
                    "replacement_posture": phase_summary.get("replacement_posture"),
                },
                "reading": "The phase closes once the project has named the new default bounded layer for the next pilot.",
            }
        ]
        interpretation = [
            "V1.12BA closes with a bounded default-layer replacement decision.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BAPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ba_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BAPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
