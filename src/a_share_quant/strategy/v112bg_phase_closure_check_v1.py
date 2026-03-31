from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BGPhaseClosureCheckReport:
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


class V112BGPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BGPhaseClosureCheckReport:
        if not bool(dict(phase_check_payload.get("summary", {})).get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BG closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bg_as_cpo_oracle_vs_no_leak_gap_review_success",
            "v112bg_success_criteria_met": True,
            "enter_v112bg_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bg_phase_check",
                "actual": {
                    "primary_gap_axis": dict(phase_check_payload.get("summary", {})).get("primary_gap_axis"),
                    "recommended_probability_margin_floor": dict(phase_check_payload.get("summary", {})).get("recommended_probability_margin_floor"),
                },
                "reading": "The phase closes once the gap is decomposed into a concrete neutral-track gate specification.",
            }
        ]
        interpretation = [
            "V1.12BG closes with an explicit oracle-vs-no-leak bottleneck attribution and a neutral selective gate stack.",
        ]
        return V112BGPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bg_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BGPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
