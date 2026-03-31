from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BIPhaseClosureCheckReport:
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


class V112BIPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BIPhaseClosureCheckReport:
        if not bool(dict(phase_check_payload.get("summary", {})).get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BI closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bi_as_cpo_cross_sectional_ranker_pilot_success",
            "v112bi_success_criteria_met": True,
            "enter_v112bi_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bi_phase_check",
                "actual": {
                    "trade_count": dict(phase_check_payload.get("summary", {})).get("trade_count"),
                    "cash_ratio": dict(phase_check_payload.get("summary", {})).get("cash_ratio"),
                },
                "reading": "The phase closes once the ranker exists as a lawful comparison line on the same 10-row CPO layer.",
            }
        ]
        interpretation = [
            "V1.12BI closes with the first direct-return ranking portfolio pilot on the lawful 10-row CPO layer.",
        ]
        return V112BIPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bi_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BIPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
