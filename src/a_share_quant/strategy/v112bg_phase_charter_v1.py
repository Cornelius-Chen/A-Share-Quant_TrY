from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BGPhaseCharterReport:
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


class V112BGPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112be_phase_closure_payload: dict[str, Any],
        v112bf_phase_closure_payload: dict[str, Any],
        v112bc_phase_closure_payload: dict[str, Any],
    ) -> V112BGPhaseCharterReport:
        if not bool(dict(v112be_phase_closure_payload.get("summary", {})).get("v112be_success_criteria_met")):
            raise ValueError("V1.12BG requires the completed V1.12BE closure check.")
        if not bool(dict(v112bf_phase_closure_payload.get("summary", {})).get("v112bf_success_criteria_met")):
            raise ValueError("V1.12BG requires the completed V1.12BF closure check.")
        if not bool(dict(v112bc_phase_closure_payload.get("summary", {})).get("v112bc_success_criteria_met")):
            raise ValueError("V1.12BG requires the completed V1.12BC closure check.")

        charter = {
            "phase_name": "V1.12BG CPO Oracle-vs-No-Leak Gap Review",
            "mission": (
                "Decompose the current gap between the hindsight oracle benchmark and the aggressive no-leak track "
                "into actionable bottlenecks before opening the neutral selective track."
            ),
            "in_scope": [
                "oracle versus aggressive return-gap attribution",
                "negative-trade concentration by stage, role, and catalyst",
                "probability-margin quality review",
                "neutral selective gate recommendations",
            ],
            "out_of_scope": [
                "formal feature promotion",
                "formal training rights",
                "deployment",
            ],
            "success_criteria": [
                "the review outputs an explicit bottleneck attribution",
                "the review freezes concrete neutral-track gate recommendations",
                "the review does not open formal training or signal rights",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bg_cpo_oracle_vs_no_leak_gap_review",
            "do_open_v112bg_now": True,
            "recommended_first_action": "freeze_v112bg_cpo_oracle_vs_no_leak_gap_review_v1",
        }
        interpretation = [
            "V1.12BG exists to prevent blind imitation of the aggressive track in the next no-leak portfolio line.",
            "It should identify whether the current shortfall is mostly a selection problem, a drawdown-control problem, or a stage-maturity problem.",
        ]
        return V112BGPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bg_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BGPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
