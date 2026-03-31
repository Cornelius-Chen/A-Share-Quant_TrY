from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BUPhaseCharterReport:
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


class V112BUPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bt_phase_closure_payload: dict[str, Any],
        v112bp_phase_closure_payload: dict[str, Any],
    ) -> V112BUPhaseCharterReport:
        if not bool(dict(v112bt_phase_closure_payload.get("summary", {})).get("v112bt_success_criteria_met")):
            raise ValueError("V1.12BT must be closed before V1.12BU can open.")
        if not bool(dict(v112bp_phase_closure_payload.get("summary", {})).get("v112bp_success_criteria_met")):
            raise ValueError("V1.12BP must be closed before V1.12BU can open.")

        charter = {
            "phase_name": "V1.12BU Phase-Conditioned Control Pilot",
            "mission": (
                "Test whether the extracted phase-conditioned controls from V1.12BT can improve the selector-maturity "
                "fusion baseline by vetoing dangerous entries, shortening dangerous holdings, and activating risk-off "
                "overrides without destroying the alpha backbone."
            ),
            "in_scope": [
                "entry veto application on the frozen fusion baseline",
                "holding veto application via shorter holding half-life",
                "risk-off override application on mapped risk dates",
                "report-only performance comparison versus V1.12BP and neutral baseline",
            ],
            "out_of_scope": [
                "formal training opening",
                "formal signal generation",
                "new selector training",
                "new clustering or mapping layers",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bu_phase_conditioned_control_pilot",
            "do_open_v112bu_now": True,
            "recommended_first_action": "freeze_v112bu_phase_conditioned_control_pilot_v1",
        }
        interpretation = [
            "V1.12BU opens because V1.12BT has already translated risk regions into explicit control-layer objects.",
            "The lawful next step is to test those control objects on top of the existing fusion baseline instead of inventing a new selector.",
        ]
        return V112BUPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bu_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BUPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
