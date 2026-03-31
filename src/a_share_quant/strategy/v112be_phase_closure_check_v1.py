from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BEPhaseClosureCheckReport:
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


class V112BEPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BEPhaseClosureCheckReport:
        summary_in = dict(phase_check_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BE closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112be_as_cpo_oracle_upper_bound_benchmark_success",
            "v112be_success_criteria_met": True,
            "enter_v112be_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112be_phase_check",
                "actual": {
                    "trade_count": summary_in.get("trade_count"),
                    "future_information_allowed": summary_in.get("future_information_allowed"),
                },
                "reading": "The phase closes once the hindsight benchmark exists as an explicit upper-bound line and remains outside no-leak training rights.",
            }
        ]
        interpretation = [
            "V1.12BE closes with a hindsight-only upper-bound benchmark for later comparison against aggressive and neutral no-leak tracks.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BEPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112be_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BEPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
