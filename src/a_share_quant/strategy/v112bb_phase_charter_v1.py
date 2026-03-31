from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BBPhaseCharterReport:
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


class V112BBPhaseCharterAnalyzer:
    def analyze(self, *, v112ba_phase_closure_payload: dict[str, Any]) -> V112BBPhaseCharterReport:
        closure_summary = dict(v112ba_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ba_success_criteria_met")):
            raise ValueError("V1.12BB requires the completed V1.12BA closure check.")

        charter = {
            "phase_name": "V1.12BB CPO Default 10-Row Guarded-Layer Pilot",
            "mission": (
                "Run the next bounded pilot directly on the new default 10-row guarded training-facing layer, "
                "and compare it against the old 7-row baseline and prior guarded-branch pilot results."
            ),
            "in_scope": [
                "use the 10-row guarded layer as the single default pilot layer",
                "evaluate the three core targets and the currently lawful guarded targets",
                "compare current pilot behavior against prior 7-row and guarded-branch results",
            ],
            "out_of_scope": [
                "formal training promotion",
                "formal signal generation",
                "spillover or pending-row admission",
                "mixed connector/MPO branch admission",
            ],
            "success_criteria": [
                "the 10-row default layer produces a stable bounded pilot result",
                "core targets stay stable relative to the old 7-row baseline",
                "guarded targets stay stable relative to the 7-row guarded baseline",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bb_default_10_row_guarded_layer_pilot",
            "do_open_v112bb_now": True,
            "recommended_first_action": "freeze_v112bb_cpo_default_10_row_guarded_layer_pilot_v1",
        }
        interpretation = [
            "V1.12BB is the first real pilot that treats the 10-row guarded layer as the project default, not as an optional branch add-on.",
            "This remains bounded, report-only, and non-deployable.",
        ]
        return V112BBPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bb_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BBPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
