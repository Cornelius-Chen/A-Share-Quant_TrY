from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BJPhaseCharterReport:
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


class V112BJPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bh_phase_closure_payload: dict[str, Any],
        v112bi_phase_closure_payload: dict[str, Any],
    ) -> V112BJPhaseCharterReport:
        if not bool(dict(v112bh_phase_closure_payload.get("summary", {})).get("v112bh_success_criteria_met")):
            raise ValueError("V1.12BJ requires the completed V1.12BH closure check.")
        if not bool(dict(v112bi_phase_closure_payload.get("summary", {})).get("v112bi_success_criteria_met")):
            raise ValueError("V1.12BJ requires the completed V1.12BI closure check.")

        charter = {
            "phase_name": "V1.12BJ CPO Neutral Teacher Gate Pilot",
            "mission": (
                "Train a no-leak gate model to imitate the entry discipline of the current neutral selective line, "
                "then compare the distilled policy against neutral, aggressive, and ranker tracks."
            ),
            "in_scope": [
                "teacher decision reconstruction from the neutral selective track",
                "point-in-time gate-model training",
                "cash-versus-entry learning on the same lawful 10-row CPO layer",
                "bounded comparison against existing no-leak portfolio lines",
            ],
            "out_of_scope": [
                "formal signal generation",
                "formal training opening",
                "row-geometry widen",
                "model-zoo explosion",
            ],
            "success_criteria": [
                "the teacher-gate line remains no-leak",
                "it emits an explicit portfolio trace",
                "it measures whether neutral-style participation discipline is learnable",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bj_cpo_neutral_teacher_gate_pilot",
            "do_open_v112bj_now": True,
            "recommended_first_action": "freeze_v112bj_cpo_neutral_teacher_gate_pilot_v1",
        }
        interpretation = [
            "V1.12BJ does not search for a new portfolio ideology.",
            "It asks whether the strongest current no-leak line can be partially learned as an explicit teacher-gate policy.",
        ]
        return V112BJPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bj_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BJPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
