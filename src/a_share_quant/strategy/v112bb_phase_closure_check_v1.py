from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BBPhaseClosureCheckReport:
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


class V112BBPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BBPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112bb_as_default_10_row_guarded_layer_pilot_success",
            "v112bb_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112bb_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112bb_phase_check",
                "actual": {
                    "default_10_row_pilot_established": phase_summary.get("default_10_row_pilot_established"),
                    "core_targets_stable_vs_7_row_baseline": phase_summary.get("core_targets_stable_vs_7_row_baseline"),
                    "guarded_targets_stable_vs_7_row_guarded_baseline": phase_summary.get("guarded_targets_stable_vs_7_row_guarded_baseline"),
                },
                "reading": "The phase closes once the 10-row layer has been proven stable enough to serve as the default bounded pilot baseline.",
            }
        ]
        interpretation = [
            "V1.12BB closes with a frozen default experimental baseline on the 10-row guarded layer.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BBPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bb_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BBPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
