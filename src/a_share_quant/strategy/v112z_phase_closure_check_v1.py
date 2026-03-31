from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ZPhaseClosureCheckReport:
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


class V112ZPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ZPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112z_as_bounded_cycle_reconstruction_entry_success",
            "v112z_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112z_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112z_phase_check",
                "actual": {
                    "foundation_ready_for_bounded_cycle_reconstruction": phase_summary.get(
                        "foundation_ready_for_bounded_cycle_reconstruction"
                    ),
                    "split_ready_adjacent_asset_count": phase_summary.get("split_ready_adjacent_asset_count"),
                    "bounded_spillover_factor_candidate_count": phase_summary.get("bounded_spillover_factor_candidate_count"),
                },
                "reading": "The reconstruction experiment is now lawfully opened with explicit ambiguity-preserving guardrails.",
            }
        ]
        interpretation = [
            "V1.12Z closes successfully once the reconstruction entry conditions and protocol are frozen.",
            "The next action is the actual bounded reconstruction pass, not training.",
        ]
        return V112ZPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112z_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ZPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
