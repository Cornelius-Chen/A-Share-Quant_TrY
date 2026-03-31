from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ARPhaseCharterReport:
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


class V112ARPhaseCharterAnalyzer:
    def analyze(self, *, v112aq_phase_closure_payload: dict[str, Any]) -> V112ARPhaseCharterReport:
        closure_summary = dict(v112aq_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112aq_success_criteria_met")):
            raise ValueError("V1.12AR requires the completed V1.12AQ closure check.")

        charter = {
            "phase_name": "V1.12AR CPO Feature Implementation Patch Spec Freeze",
            "mission": (
                "Freeze the minimum bounded implementation rule set for daily board series and recurring "
                "future catalyst calendar before any row-geometry widen."
            ),
            "in_scope": [
                "freeze board vendor selection rule",
                "freeze breadth formula rule",
                "freeze turnover normalization rule",
                "freeze expected-window fill rule",
                "freeze confidence-tier mapping",
                "freeze calendar rollforward rule",
            ],
            "out_of_scope": [
                "full day-by-day backfill",
                "row-geometry widen",
                "formal training promotion",
                "formal signal generation",
            ],
            "success_criteria": [
                "all 6 bounded patch rules are frozen",
                "each rule has point-in-time and audit posture",
                "next lawful move becomes bounded implementation backfill on current truth rows",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ar_cpo_feature_implementation_patch_spec_freeze",
            "do_open_v112ar_now": True,
            "recommended_first_action": "freeze_v112ar_cpo_feature_implementation_patch_spec_v1",
        }
        interpretation = [
            "V1.12AR exists to stop the project from hiding implementation ambiguity behind broad model wins.",
            "This is the smallest lawful freeze needed before any row-geometry widen.",
        ]
        return V112ARPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ar_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ARPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
