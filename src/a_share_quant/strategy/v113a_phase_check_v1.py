from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113APhaseCheckReport:
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


class V113APhaseCheckAnalyzer:
    def analyze(self, *, state_schema_payload: dict[str, Any]) -> V113APhaseCheckReport:
        schema_summary = dict(state_schema_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v113a_as_theme_diffusion_state_schema_success",
            "phase_state_count": int(schema_summary.get("phase_state_count", 0)),
            "stock_role_count": int(schema_summary.get("stock_role_count", 0)),
            "strength_dimension_count": int(schema_summary.get("strength_dimension_count", 0)),
            "driver_dimension_count": int(schema_summary.get("driver_dimension_count", 0)),
            "review_only_candidate_driver_count": int(schema_summary.get("review_only_candidate_driver_count", 0)),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "candidate_driver_discovery_or_bounded_state_usage_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v113a_theme_diffusion_state_schema",
                "actual": {
                    "phase_state_count": summary["phase_state_count"],
                    "stock_role_count": summary["stock_role_count"],
                    "strength_dimension_count": summary["strength_dimension_count"],
                    "driver_dimension_count": summary["driver_dimension_count"],
                    "review_only_candidate_driver_count": summary["review_only_candidate_driver_count"],
                },
                "reading": "V1.13A succeeds once the theme-diffusion carry grammar is frozen into states, roles, strength, and drivers.",
            }
        ]
        interpretation = [
            "V1.13A now gives the project a proper schema language for theme-diffusion carry.",
            "The next lawful move can either review candidate drivers or begin bounded state usage.",
        ]
        return V113APhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113a_phase_check_report(
    *, reports_dir: Path, report_name: str, result: V113APhaseCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
