from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BLPhaseClosureCheckReport:
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


class V112BLPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BLPhaseClosureCheckReport:
        if not bool(dict(phase_check_payload.get("summary", {})).get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BL closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bl_as_cpo_regime_aware_gate_pilot_success",
            "v112bl_success_criteria_met": True,
            "enter_v112bl_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bl_phase_check",
                "actual": {
                    "trade_count": dict(phase_check_payload.get("summary", {})).get("trade_count"),
                    "teacher_alignment_recall": dict(phase_check_payload.get("summary", {})).get("teacher_alignment_recall"),
                },
                "reading": "The phase closes once the regime-aware gate line exists as a lawful comparison line against the current neutral baseline.",
            }
        ]
        interpretation = [
            "V1.12BL closes with the regime-aware gate attempt derived from the frozen market-regime overlay family.",
        ]
        return V112BLPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bl_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BLPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
