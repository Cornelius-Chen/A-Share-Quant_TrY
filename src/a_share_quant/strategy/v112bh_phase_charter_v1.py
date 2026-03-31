from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BHPhaseCharterReport:
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


class V112BHPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bg_phase_closure_payload: dict[str, Any],
        v112bf_phase_closure_payload: dict[str, Any],
        v112bc_phase_closure_payload: dict[str, Any],
    ) -> V112BHPhaseCharterReport:
        if not bool(dict(v112bg_phase_closure_payload.get("summary", {})).get("v112bg_success_criteria_met")):
            raise ValueError("V1.12BH requires the completed V1.12BG closure check.")
        if not bool(dict(v112bf_phase_closure_payload.get("summary", {})).get("v112bf_success_criteria_met")):
            raise ValueError("V1.12BH requires the completed V1.12BF closure check.")
        if not bool(dict(v112bc_phase_closure_payload.get("summary", {})).get("v112bc_success_criteria_met")):
            raise ValueError("V1.12BH requires the completed V1.12BC closure check.")

        charter = {
            "phase_name": "V1.12BH CPO Neutral Selective No-Leak Portfolio Pilot",
            "mission": (
                "Run a no-leak selective portfolio line on the same lawful 10-row CPO layer with explicit cash "
                "admission, stricter probability gates, and drawdown-aware participation discipline."
            ),
            "in_scope": [
                "point-in-time only training cutoff",
                "cash-allowed selective participation",
                "oracle-gap and aggressive-gap comparison",
                "equity, drawdown, and trade trace output",
            ],
            "out_of_scope": [
                "oracle hindsight logic",
                "formal signal generation",
                "deployment",
            ],
            "success_criteria": [
                "the pilot preserves no-leak discipline",
                "the pilot can remain in cash when the gate stack is not met",
                "the pilot reports its comparison to both oracle and aggressive tracks",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bh_cpo_neutral_selective_no_leak_portfolio_pilot",
            "do_open_v112bh_now": True,
            "recommended_first_action": "freeze_v112bh_cpo_neutral_selective_no_leak_portfolio_pilot_v1",
        }
        interpretation = [
            "V1.12BH is not a smaller aggressive track; it is a different objective line that explicitly values cash, drawdown control, and profit-factor quality.",
            "The neutral track remains experimental and non-deployable.",
        ]
        return V112BHPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bh_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BHPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
