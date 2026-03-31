from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BCPhaseClosureCheckReport:
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


class V112BCPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BCPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112bc_as_cpo_portfolio_objective_protocol_success",
            "v112bc_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112bc_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bc_phase_check",
                "actual": {
                    "objective_track_count": phase_summary.get("objective_track_count"),
                    "marginal_stop_threshold": phase_summary.get("marginal_stop_threshold"),
                },
                "reading": "The phase closes once the objective tracks and search stop rule are frozen.",
            }
        ]
        interpretation = [
            "V1.12BC closes with a reusable objective protocol for later portfolio experiments.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BCPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bc_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BCPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
