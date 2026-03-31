from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BKPhaseCharterReport:
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


class V112BKPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bi_phase_closure_payload: dict[str, Any],
        v112bj_phase_closure_payload: dict[str, Any],
        v112bd_phase_closure_payload: dict[str, Any] | None = None,
        v112bh_phase_closure_payload: dict[str, Any] | None = None,
    ) -> V112BKPhaseCharterReport:
        if not bool(dict(v112bi_phase_closure_payload.get("summary", {})).get("v112bi_success_criteria_met")):
            raise ValueError("V1.12BK requires the completed V1.12BI closure check.")
        if not bool(dict(v112bj_phase_closure_payload.get("summary", {})).get("v112bj_success_criteria_met")):
            raise ValueError("V1.12BK requires the completed V1.12BJ closure check.")
        if v112bd_phase_closure_payload is not None and not bool(
            dict(v112bd_phase_closure_payload.get("summary", {})).get("v112bd_success_criteria_met")
        ):
            raise ValueError("V1.12BK requires the completed V1.12BD overlay review when provided.")
        if v112bh_phase_closure_payload is not None and not bool(
            dict(v112bh_phase_closure_payload.get("summary", {})).get("v112bh_success_criteria_met")
        ):
            raise ValueError("V1.12BK requires the completed V1.12BH closure check when provided.")

        charter = {
            "phase_name": "V1.12BK CPO Regime-Aware Gate Model Search",
            "mission": (
                "Test whether a bounded regime-aware gate can learn the neutral selective discipline better than the "
                "current teacher imitation line, while staying no-leak on the same lawful 10-row CPO layer."
            ),
            "in_scope": [
                "market-regime overlay features from broad index, board style, liquidity, and ETF proxies",
                "bounded model search over cheap gate models",
                "teacher decision reconstruction from the neutral selective track",
                "comparison against neutral, aggressive, ranker, and oracle lines",
            ],
            "out_of_scope": [
                "formal signal generation",
                "formal training opening",
                "heavy deep learning",
                "reinforcement learning",
            ],
            "success_criteria": [
                "the branch remains no-leak",
                "it emits an explicit portfolio trace",
                "it tests whether regime context helps learn neutral-style participation discipline",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bk_cpo_regime_aware_gate_model_search",
            "do_open_v112bk_now": True,
            "recommended_first_action": "freeze_v112bk_cpo_regime_aware_gate_model_search_v1",
        }
        interpretation = [
            "V1.12BK is a bounded model-zoo branch that adds explicit market-regime context to the teacher-gate problem.",
            "It is a no-leak comparison line, not a production signal.",
        ]
        return V112BKPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bk_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BKPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
