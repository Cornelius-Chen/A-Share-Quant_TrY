from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AQPhaseCharterReport:
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


class V112AQPhaseCharterAnalyzer:
    def analyze(self, *, v112ap_phase_closure_payload: dict[str, Any]) -> V112AQPhaseCharterReport:
        closure_summary = dict(v112ap_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ap_success_criteria_met")):
            raise ValueError("V1.12AQ requires the completed V1.12AP closure check.")

        charter = {
            "phase_name": "V1.12AQ CPO Feature Implementation Patch Review",
            "mission": (
                "Resolve whether bounded feature-implementation patching should precede any "
                "row-geometry widen, and narrow the required patch scope to the smallest lawful set."
            ),
            "in_scope": [
                "compare current implementation gaps against the stable V1.12AP widen result",
                "attribute the next bottleneck between feature implementation and row geometry",
                "identify the minimum board/calendar patch domains that should be frozen next",
            ],
            "out_of_scope": [
                "new row admission",
                "formal training promotion",
                "formal signal generation",
                "broad model search",
            ],
            "success_criteria": [
                "produce a yes/no conclusion on whether implementation patching must precede row widen",
                "name the minimum bounded patch domains",
                "keep the project out of both infinite audit and premature widen",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112aq_cpo_feature_implementation_patch_review",
            "do_open_v112aq_now": True,
            "recommended_first_action": "freeze_v112aq_cpo_feature_implementation_patch_review_v1",
        }
        interpretation = [
            "V1.12AQ is a decision phase, not another generic readiness loop.",
            "Its job is to tell the project whether implementation patching is now the narrowest lawful move.",
        ]
        return V112AQPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112aq_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AQPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
