from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113PhaseCheckReport:
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


class V113PhaseCheckAnalyzer:
    def analyze(self, *, template_entry_payload: dict[str, Any]) -> V113PhaseCheckReport:
        entry_summary = dict(template_entry_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v113_as_theme_diffusion_template_entry_success",
            "selected_template_family": str(entry_summary.get("selected_template_family", "")),
            "seed_archetype_count": int(entry_summary.get("seed_archetype_count", 0)),
            "schema_first_posture": bool(entry_summary.get("schema_first_posture")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "initialize_bounded_theme_diffusion_state_schema_next",
        }
        evidence_rows = [
            {
                "evidence_name": "v113_template_entry",
                "actual": {
                    "selected_template_family": summary["selected_template_family"],
                    "seed_archetype_count": summary["seed_archetype_count"],
                    "schema_first_posture": summary["schema_first_posture"],
                },
                "reading": "V1.13 succeeds once the project formally reenters a higher-leverage carry template line with bounded seed archetypes.",
            }
        ]
        interpretation = [
            "V1.13 does not yet build the state schema itself.",
            "It resets the effort frontier to the correct higher-leverage template line.",
        ]
        return V113PhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113_phase_check_report(*, reports_dir: Path, report_name: str, result: V113PhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
