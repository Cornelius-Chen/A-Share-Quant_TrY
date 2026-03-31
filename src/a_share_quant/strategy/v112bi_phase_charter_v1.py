from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BIPhaseCharterReport:
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


class V112BIPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bh_phase_closure_payload: dict[str, Any],
        v112bc_phase_closure_payload: dict[str, Any],
    ) -> V112BIPhaseCharterReport:
        if not bool(dict(v112bh_phase_closure_payload.get("summary", {})).get("v112bh_success_criteria_met")):
            raise ValueError("V1.12BI requires the completed V1.12BH closure check.")
        if not bool(dict(v112bc_phase_closure_payload.get("summary", {})).get("v112bc_success_criteria_met")):
            raise ValueError("V1.12BI requires the completed V1.12BC closure check.")

        charter = {
            "phase_name": "V1.12BI CPO Cross-Sectional Ranker Pilot",
            "mission": (
                "Test whether a no-leak direct-return ranker can outperform the existing classifier-style "
                "aggressive and neutral lines on the same lawful 10-row CPO layer."
            ),
            "in_scope": [
                "point-in-time only training cutoff",
                "direct future-return regression score",
                "top-ranked symbol or cash",
                "comparison versus oracle, aggressive, and neutral tracks",
            ],
            "out_of_scope": [
                "formal signal generation",
                "deployment",
                "large model-zoo expansion",
            ],
            "success_criteria": [
                "the ranker remains no-leak",
                "it produces an explicit portfolio trace",
                "it reports whether ranking adds value beyond current classifier tracks",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bi_cpo_cross_sectional_ranker_pilot",
            "do_open_v112bi_now": True,
            "recommended_first_action": "freeze_v112bi_cpo_cross_sectional_ranker_pilot_v1",
        }
        interpretation = [
            "V1.12BI is the first direct ranking experiment after the aggressive and neutral classifier lines were established.",
            "It tests target-function alignment rather than simply adding a heavier model family.",
        ]
        return V112BIPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bi_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BIPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
