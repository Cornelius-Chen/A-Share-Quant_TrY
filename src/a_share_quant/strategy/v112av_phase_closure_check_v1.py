from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AVPhaseClosureCheckReport:
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


class V112AVPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AVPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112av_as_branch_role_geometry_patch_pilot_success",
            "v112av_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112av_waiting_state_now": True,
            "allow_formal_training_now": False,
            "allow_formal_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112av_phase_check",
                "actual": {
                    "role_state_patch_gain": phase_summary.get("role_state_patch_gain"),
                    "core_targets_stable_after_branch_patch": phase_summary.get("core_targets_stable_after_branch_patch"),
                    "guarded_targets_stable_after_branch_patch": phase_summary.get("guarded_targets_stable_after_branch_patch"),
                },
                "reading": "The branch patch closes once the widened geometry has a clear post-patch posture.",
            }
        ]
        interpretation = [
            "V1.12AV closes with branch-role geometry either repaired or explicitly still blocked.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AVPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112av_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AVPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
