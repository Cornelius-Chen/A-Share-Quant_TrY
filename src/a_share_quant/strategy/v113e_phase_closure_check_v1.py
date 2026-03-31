from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113EPhaseClosureCheckReport:
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


class V113EPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113EPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113e_as_theme_diffusion_bounded_labeling_pilot_success",
            "v113e_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v113e_waiting_state_now": True,
            "allow_auto_execution_now": False,
            "allow_auto_signal_now": False,
            "allow_auto_multi_archetype_expansion_now": False,
            "recommended_next_posture": "open_bounded_pilot_data_assembly_when_owner_continues",
        }
        evidence_rows = [
            {
                "evidence_name": "v113e_phase_check",
                "actual": {
                    "selected_archetype": phase_summary.get("selected_archetype"),
                    "label_block_count": phase_summary.get("label_block_count"),
                },
                "reading": "V1.13E closes once the first theme-diffusion labeling/training pilot basis is frozen cleanly.",
            }
        ]
        interpretation = [
            "V1.13E is still above dataset assembly, model training, and execution.",
            "The project now has a lawful entry point for a first theme-diffusion pilot if owner wants to continue.",
        ]
        return V113EPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113e_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V113EPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
