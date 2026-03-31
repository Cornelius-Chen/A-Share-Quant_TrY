from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BLPhaseCheckReport:
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


class V112BLPhaseCheckAnalyzer:
    def analyze(self, *, regime_gate_pilot_payload: dict[str, Any]) -> V112BLPhaseCheckReport:
        summary_in = dict(regime_gate_pilot_payload.get("summary", {}))
        if not bool(summary_in.get("no_leak_enforced")):
            raise ValueError("V1.12BL phase check requires explicit no-leak enforcement.")
        if int(summary_in.get("teacher_decision_row_count", 0)) <= 0:
            raise ValueError("V1.12BL requires explicit teacher decision rows.")

        summary = {
            "acceptance_posture": "keep_v112bl_as_cpo_regime_aware_gate_pilot",
            "do_open_v112bl_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "cash_ratio": float(summary_in.get("cash_ratio", 0.0)),
            "teacher_alignment_recall": float(summary_in.get("teacher_alignment_recall", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bl_regime_aware_gate_pilot",
                "actual": {
                    "total_return": summary_in.get("total_return"),
                    "neutral_return_delta": summary_in.get("neutral_return_delta"),
                    "teacher_alignment_recall": summary_in.get("teacher_alignment_recall"),
                },
                "reading": "This phase is only meaningful if regime overlays add information beyond the naive teacher-gate attempt.",
            }
        ]
        interpretation = [
            "V1.12BL is valid because it explicitly tests whether the regime overlay family improves the learnability of the neutral participation policy.",
        ]
        return V112BLPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bl_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BLPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
