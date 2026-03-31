from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BJPhaseCheckReport:
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


class V112BJPhaseCheckAnalyzer:
    def analyze(self, *, teacher_gate_pilot_payload: dict[str, Any]) -> V112BJPhaseCheckReport:
        summary_in = dict(teacher_gate_pilot_payload.get("summary", {}))
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BJ phase check requires explicit no-leak enforcement.")
        if int(summary_in.get("teacher_decision_row_count", 0)) <= 0:
            raise ValueError("V1.12BJ requires explicit teacher decision rows.")

        summary = {
            "acceptance_posture": "keep_v112bj_as_cpo_neutral_teacher_gate_pilot",
            "do_open_v112bj_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "cash_ratio": float(summary_in.get("cash_ratio", 0.0)),
            "teacher_alignment_recall": float(summary_in.get("teacher_alignment_recall", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bj_teacher_gate_pilot",
                "actual": {
                    "total_return": summary_in.get("total_return"),
                    "neutral_return_delta": summary_in.get("neutral_return_delta"),
                    "teacher_alignment_recall": summary_in.get("teacher_alignment_recall"),
                },
                "reading": "The phase is only meaningful if the teacher-gate line both remains lawful and reveals whether neutral-style participation can be learned.",
            }
        ]
        interpretation = [
            "V1.12BJ is valid because it turns the strongest current no-leak line into a learnable teacher instead of adding an unrelated objective.",
        ]
        return V112BJPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bj_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BJPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
