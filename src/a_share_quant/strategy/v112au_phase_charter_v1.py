from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AUPhaseCharterReport:
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


class V112AUPhaseCharterAnalyzer:
    def analyze(self, *, v112at_phase_closure_payload: dict[str, Any]) -> V112AUPhaseCharterReport:
        closure_summary = dict(v112at_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112at_success_criteria_met")):
            raise ValueError("V1.12AU requires the completed V1.12AT closure check.")
        if not bool(closure_summary.get("allow_row_geometry_widen_now")):
            raise ValueError("V1.12AU only opens once row-geometry widen is explicitly discussable.")

        charter = {
            "phase_name": "V1.12AU CPO Bounded Row-Geometry Widen Pilot",
            "mission": (
                "Widen row geometry in a bounded way by adding branch review rows to the current post-patch "
                "truth stack without opening spillover, pending, formal training, or signal rights."
            ),
            "in_scope": [
                "reuse the current post-patch feature stack",
                "keep the same core and guarded target stack",
                "add only branch review rows as bounded geometry widen",
                "compare widened behavior against V1.12AT",
            ],
            "out_of_scope": [
                "spillover row admission",
                "pending row admission",
                "formal training promotion",
                "formal signal generation",
            ],
            "success_criteria": [
                "core targets remain stable after geometry widen",
                "guarded targets do not collapse under branch-row admission",
                "the widened geometry produces a clearer next move than further abstract review",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112au_bounded_row_geometry_widen_pilot",
            "do_open_v112au_now": True,
            "recommended_first_action": "freeze_v112au_cpo_bounded_row_geometry_widen_pilot_v1",
        }
        interpretation = [
            "V1.12AU moves the live uncertainty from implementation to row geometry.",
            "The widen remains narrow: branch rows only, still under report-only constraints.",
        ]
        return V112AUPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112au_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AUPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
