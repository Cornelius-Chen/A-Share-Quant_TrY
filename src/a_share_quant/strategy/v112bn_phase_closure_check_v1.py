from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BNPhaseClosureCheckReport:
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


class V112BNPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BNPhaseClosureCheckReport:
        summary_in = dict(phase_check_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BN closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bn_as_teacher_decomposition_gate_search_success",
            "v112bn_success_criteria_met": True,
            "enter_v112bn_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bn_phase_check",
                "actual": {
                    "candidate_row_count": summary_in.get("candidate_row_count"),
                    "best_candidate_non_cash": summary_in.get("best_candidate_non_cash"),
                    "teacher_alignment_f1": summary_in.get("teacher_alignment_f1"),
                },
                "reading": "The phase closes once the bounded rule search produces an auditable best candidate or a proof that no non-cash candidate survives.",
            }
        ]
        interpretation = [
            "V1.12BN closes the teacher decomposition search branch without opening formal training or signaling.",
        ]
        return V112BNPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bn_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BNPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
