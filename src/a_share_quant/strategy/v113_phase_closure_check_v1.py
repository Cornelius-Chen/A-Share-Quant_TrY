from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113PhaseClosureCheckReport:
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


class V113PhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113PhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113_as_template_reentry_success",
            "v113_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v113_waiting_state_now": True,
            "allow_auto_model_open_now": False,
            "recommended_next_posture": "open_bounded_theme_diffusion_state_schema_when_owner_continues",
        }
        evidence_rows = [
            {
                "evidence_name": "v113_phase_check",
                "actual": {
                    "selected_template_family": phase_summary.get("selected_template_family"),
                    "seed_archetype_count": phase_summary.get("seed_archetype_count"),
                    "schema_first_posture": phase_summary.get("schema_first_posture"),
                },
                "reading": "V1.13 closes once the reentry target and bounded archetype basis are frozen cleanly.",
            }
        ]
        interpretation = [
            "V1.13 is a successful reallocation phase.",
            "It does not yet authorize models or execution logic inside the new template line.",
        ]
        return V113PhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V113PhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
