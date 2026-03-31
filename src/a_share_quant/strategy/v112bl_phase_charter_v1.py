from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BLPhaseCharterReport:
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


class V112BLPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bd_phase_closure_payload: dict[str, Any],
        v112bh_phase_closure_payload: dict[str, Any],
        v112bi_phase_closure_payload: dict[str, Any],
        v112bj_phase_closure_payload: dict[str, Any],
    ) -> V112BLPhaseCharterReport:
        if not bool(dict(v112bd_phase_closure_payload.get("summary", {})).get("v112bd_success_criteria_met")):
            raise ValueError("V1.12BL requires the completed V1.12BD overlay closure.")
        if not bool(dict(v112bh_phase_closure_payload.get("summary", {})).get("v112bh_success_criteria_met")):
            raise ValueError("V1.12BL requires the completed V1.12BH closure.")
        if not bool(dict(v112bi_phase_closure_payload.get("summary", {})).get("v112bi_success_criteria_met")):
            raise ValueError("V1.12BL requires the completed V1.12BI closure.")
        if not bool(dict(v112bj_phase_closure_payload.get("summary", {})).get("v112bj_success_criteria_met")):
            raise ValueError("V1.12BL requires the completed V1.12BJ closure.")

        charter = {
            "phase_name": "V1.12BL CPO Regime-Aware Gate Pilot",
            "mission": (
                "Test whether a bounded no-leak gate model can learn neutral-style participation discipline when "
                "market_regime_overlay_family is added explicitly on top of the current CPO skeleton."
            ),
            "in_scope": [
                "teacher decision reconstruction from the neutral selective track",
                "point-in-time gate-model training",
                "regime-aware overlay features from the frozen market_regime_overlay_family",
                "cash-versus-entry learning on the same lawful 10-row CPO layer",
                "bounded comparison against aggressive, neutral, and ranker tracks",
            ],
            "out_of_scope": [
                "formal signal generation",
                "formal training opening",
                "row-geometry widen",
                "deep RL",
                "heavy transformer search",
            ],
            "success_criteria": [
                "the regime-aware gate line remains no-leak",
                "it emits an explicit portfolio trace",
                "it improves over the naive teacher-gate attempt or exposes a clear regime mechanism",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bl_cpo_regime_aware_gate_pilot",
            "do_open_v112bl_now": True,
            "recommended_first_action": "freeze_v112bl_cpo_regime_aware_gate_pilot_v1",
        }
        interpretation = [
            "V1.12BL is not a new ideology; it is a regime-aware attempt to learn the strongest no-leak line's participation discipline.",
            "It uses the frozen market-regime overlay family explicitly rather than pretending neutral is only a stock-level gate.",
        ]
        return V112BLPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bl_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BLPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
