from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ARPhaseClosureCheckReport:
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


class V112ARPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ARPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112ar_as_bounded_feature_implementation_patch_spec_freeze_success",
            "v112ar_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112ar_waiting_state_now": True,
            "allow_row_geometry_widen_now": phase_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("next_lawful_move"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ar_phase_check",
                "actual": {
                    "total_patch_rule_count": phase_summary.get("total_patch_rule_count"),
                    "next_lawful_move": phase_summary.get("next_lawful_move"),
                },
                "reading": "The phase closes once the project has a frozen bounded patch rule set and a concrete bounded backfill target.",
            }
        ]
        interpretation = [
            "V1.12AR closes with a concrete bounded implementation move, not a return to broad review.",
            "Formal training and signal rights remain closed.",
        ]
        return V112ARPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ar_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ARPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
