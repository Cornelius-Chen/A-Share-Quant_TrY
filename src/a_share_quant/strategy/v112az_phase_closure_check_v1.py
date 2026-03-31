from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AZPhaseClosureCheckReport:
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


class V112AZPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AZPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112az_as_bounded_training_layer_extension_success",
            "v112az_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112az_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112az_phase_check",
                "actual": {
                    "row_count_after_extension": phase_summary.get("row_count_after_extension"),
                    "guarded_branch_row_count": phase_summary.get("guarded_branch_row_count"),
                },
                "reading": "The phase closes once the 10-row bounded training-facing layer has been assembled under the guarded branch rules.",
            }
        ]
        interpretation = [
            "V1.12AZ closes with a bounded training-layer extension asset.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AZPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112az_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AZPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
