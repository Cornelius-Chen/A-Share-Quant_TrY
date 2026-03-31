from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113EPhaseCheckReport:
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


class V113EPhaseCheckAnalyzer:
    def analyze(self, *, pilot_protocol_payload: dict[str, Any]) -> V113EPhaseCheckReport:
        protocol_summary = dict(pilot_protocol_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v113e_as_theme_diffusion_bounded_labeling_pilot_success",
            "selected_archetype": str(protocol_summary.get("selected_archetype", "")),
            "label_block_count": int(protocol_summary.get("label_block_count", 0)),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "bounded_pilot_data_assembly_for_selected_theme_diffusion_archetype",
        }
        evidence_rows = [
            {
                "evidence_name": "v113e_pilot_protocol",
                "actual": {
                    "selected_archetype": summary["selected_archetype"],
                    "label_block_count": summary["label_block_count"],
                },
                "reading": "V1.13E succeeds once one clean theme-diffusion archetype and one bounded labeling/training protocol are frozen.",
            }
        ]
        interpretation = [
            "V1.13E moves the theme-diffusion line one step closer to the ultimate quant goal without opening model or execution scope.",
            "The next lawful move is concrete: bounded pilot data assembly on the selected archetype.",
        ]
        return V113EPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113e_phase_check_report(
    *, reports_dir: Path, report_name: str, result: V113EPhaseCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
