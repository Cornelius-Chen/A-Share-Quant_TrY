from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BTPhaseClosureCheckReport:
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


class V112BTPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BTPhaseClosureCheckReport:
        if not bool(dict(phase_check_payload.get("summary", {})).get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BT closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bt_as_phase_conditioned_veto_and_eligibility_extraction_success",
            "v112bt_success_criteria_met": True,
            "enter_v112bt_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bt_phase_check",
                "actual": {
                    "eligibility_rule_count": dict(phase_check_payload.get("summary", {})).get("eligibility_rule_count"),
                    "entry_veto_count": dict(phase_check_payload.get("summary", {})).get("entry_veto_count"),
                    "holding_veto_count": dict(phase_check_payload.get("summary", {})).get("holding_veto_count"),
                    "risk_off_override_count": dict(phase_check_payload.get("summary", {})).get("risk_off_override_count"),
                },
                "reading": "The phase closes once dangerous regions have been translated into explicit control-layer candidates.",
            }
        ]
        interpretation = [
            "V1.12BT closes with the first explicit phase-conditioned eligibility and veto extraction layer for CPO.",
        ]
        return V112BTPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bt_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BTPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
