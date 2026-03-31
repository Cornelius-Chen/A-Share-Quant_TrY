from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BAPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BAPhaseCharterAnalyzer:
    def analyze(self, *, v112az_phase_closure_payload: dict[str, Any]) -> V112BAPhaseCharterReport:
        closure_summary = dict(v112az_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112az_success_criteria_met")):
            raise ValueError("V1.12BA requires the completed V1.12AZ closure check.")

        charter = {
            "phase_name": "V1.12BA CPO 10-Row Layer Replacement Review",
            "mission": (
                "Review whether the new 10-row bounded training-facing layer can replace the original "
                "7-row baseline as the default layer for the next bounded pilot."
            ),
            "in_scope": [
                "compare the 7-row baseline and the 10-row bounded extension",
                "preserve guarded posture on the three added branch rows",
                "decide default-layer replacement only within the bounded pilot scope",
            ],
            "out_of_scope": [
                "formal training promotion",
                "formal signal generation",
                "connector/MPO branch admission",
                "broader row-geometry widen",
            ],
            "success_criteria": [
                "a default next-pilot layer can be named explicitly",
                "the replacement decision preserves guarded branch boundaries",
                "the next lawful move becomes an actual pilot on the chosen layer",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ba_10_row_layer_replacement_review",
            "do_open_v112ba_now": True,
            "recommended_first_action": "freeze_v112ba_cpo_10_row_layer_replacement_review_v1",
        }
        interpretation = [
            "V1.12BA is a replacement review, not a new training promotion pass.",
            "This remains bounded, report-only, and non-deployable.",
        ]
        return V112BAPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ba_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BAPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
