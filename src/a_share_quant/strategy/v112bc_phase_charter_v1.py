from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BCPhaseCharterReport:
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


class V112BCPhaseCharterAnalyzer:
    def analyze(self, *, v112bb_phase_closure_payload: dict[str, Any]) -> V112BCPhaseCharterReport:
        closure_summary = dict(v112bb_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112bb_success_criteria_met")):
            raise ValueError("V1.12BC requires the completed V1.12BB closure check.")

        charter = {
            "phase_name": "V1.12BC CPO Portfolio Objective Protocol",
            "mission": (
                "Freeze the objective tracks, no-leak boundaries, model-zoo search scope, "
                "marginal-value stopping rule, and output format for downstream CPO portfolio experiments."
            ),
            "in_scope": [
                "portfolio objective tracks",
                "oracle-vs-no-leak separation",
                "model-zoo search bounds",
                "stopping rules based on marginal improvement",
                "required portfolio charts and process output",
            ],
            "out_of_scope": [
                "actual portfolio backtest execution",
                "formal strategy deployment",
                "live trading signal generation",
            ],
            "success_criteria": [
                "the project has explicit objective tracks instead of vague performance goals",
                "oracle upper bound and no-leak tracks are separated cleanly",
                "model-zoo exploration has a hard stopping rule",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bc_cpo_portfolio_objective_protocol",
            "do_open_v112bc_now": True,
            "recommended_first_action": "freeze_v112bc_cpo_portfolio_objective_protocol_v1",
        }
        interpretation = [
            "V1.12BC exists to prevent black-box expansion from turning into uncontrolled search.",
            "The phase freezes objective tracks before any broader portfolio experiment opens.",
        ]
        return V112BCPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bc_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BCPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
