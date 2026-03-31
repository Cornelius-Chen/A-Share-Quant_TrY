from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AUPhaseClosureCheckReport:
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


class V112AUPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AUPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112au_as_bounded_row_geometry_widen_pilot_success",
            "v112au_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112au_waiting_state_now": True,
            "allow_formal_training_now": False,
            "allow_formal_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112au_phase_check",
                "actual": {
                    "core_targets_stable_after_row_widen": phase_summary.get("core_targets_stable_after_row_widen"),
                    "guarded_targets_stable_after_row_widen": phase_summary.get("guarded_targets_stable_after_row_widen"),
                    "row_count_after_widen": phase_summary.get("row_count_after_widen"),
                },
                "reading": "The phase closes once branch-row admission has been tested under the same report-only boundary.",
            }
        ]
        interpretation = [
            "V1.12AU closes with bounded row-geometry evidence added.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AUPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112au_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AUPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
