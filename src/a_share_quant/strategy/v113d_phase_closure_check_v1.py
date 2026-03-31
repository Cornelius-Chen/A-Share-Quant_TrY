from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113DPhaseClosureCheckReport:
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


class V113DPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V113DPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v113d_as_bounded_archetype_usage_pass_success",
            "v113d_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v113d_waiting_state_now": True,
            "allow_auto_model_open_now": False,
            "allow_auto_execution_schema_now": False,
            "allow_auto_template_promotion_now": False,
            "recommended_next_posture": "preserve_archetype_review_assets_and_wait_for_owner_direction",
        }
        evidence_rows = [
            {
                "evidence_name": "v113d_phase_check",
                "actual": {
                    "archetype_count_reviewed": phase_summary.get("archetype_count_reviewed"),
                    "clean_template_review_asset_count": phase_summary.get("clean_template_review_asset_count"),
                },
                "reading": "V1.13D closes once the bounded archetypes have been reviewed cleanly under the new grammar without over-promotion.",
            }
        ]
        interpretation = [
            "V1.13D is a template review success, not a model readiness signal.",
            "The theme-diffusion grammar now has bounded archetype-level validation and should pause before any deeper escalation.",
        ]
        return V113DPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113d_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V113DPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
