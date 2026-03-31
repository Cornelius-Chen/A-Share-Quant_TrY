from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BFPhaseCharterReport:
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


class V112BFPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112be_phase_closure_payload: dict[str, Any],
        v112bb_phase_closure_payload: dict[str, Any],
        v112bc_phase_closure_payload: dict[str, Any],
    ) -> V112BFPhaseCharterReport:
        if not bool(dict(v112be_phase_closure_payload.get("summary", {})).get("v112be_success_criteria_met")):
            raise ValueError("V1.12BF requires the completed V1.12BE closure check.")
        if not bool(dict(v112bb_phase_closure_payload.get("summary", {})).get("v112bb_success_criteria_met")):
            raise ValueError("V1.12BF requires the completed V1.12BB closure check.")
        if not bool(dict(v112bc_phase_closure_payload.get("summary", {})).get("v112bc_success_criteria_met")):
            raise ValueError("V1.12BF requires the completed V1.12BC closure check.")

        charter = {
            "phase_name": "V1.12BF CPO Aggressive No-Leak Black-Box Portfolio Pilot",
            "mission": (
                "Run the first no-leak aggressive black-box portfolio pilot on the default 10-row guarded CPO layer "
                "and compare its realized bounded portfolio quality against the oracle upper-bound benchmark."
            ),
            "in_scope": [
                "point-in-time only training cutoff",
                "aggressive total-return objective",
                "single-position or cash selection",
                "equity and drawdown trace",
                "oracle-gap comparison",
            ],
            "out_of_scope": [
                "oracle hindsight logic",
                "formal signal generation",
                "deployment",
            ],
            "success_criteria": [
                "all model decisions use only point-in-time visible information",
                "the pilot produces an explicit trade trace and equity curve",
                "the pilot reports its gap versus the oracle benchmark",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot",
            "do_open_v112bf_now": True,
            "recommended_first_action": "freeze_v112bf_cpo_aggressive_no_leak_black_box_portfolio_pilot_v1",
        }
        interpretation = [
            "V1.12BF is the first true no-leak portfolio experiment on top of the frozen 10-row CPO layer.",
            "The aggressive track maximizes return first, but still remains bounded and non-deployable.",
        ]
        return V112BFPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bf_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BFPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
