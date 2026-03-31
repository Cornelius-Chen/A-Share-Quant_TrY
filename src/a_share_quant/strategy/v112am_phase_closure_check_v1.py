from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AMPhaseClosureCheckReport:
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


class V112AMPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AMPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112am_as_extremely_small_core_skeleton_training_pilot_success",
            "v112am_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112am_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112am_phase_check",
                "actual": {
                    "sample_count": phase_summary.get("sample_count"),
                    "best_target_by_gbdt_gain": phase_summary.get("best_target_by_gbdt_gain"),
                    "best_target_gain": phase_summary.get("best_target_gain"),
                },
                "reading": "The project now has bounded pilot evidence and can decide from experiment rather than abstract readiness rhetoric alone.",
            }
        ]
        interpretation = [
            "V1.12AM closes once the first tiny core-skeleton pilot has been exposed and bounded.",
            "The next move should be owner review of the pilot evidence, not automatic scale-up.",
        ]
        return V112AMPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112am_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AMPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
