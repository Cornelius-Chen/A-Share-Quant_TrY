from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BRPhaseCharterReport:
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


class V112BRPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112bq_phase_closure_payload: dict[str, Any],
        v112bp_phase_closure_payload: dict[str, Any],
        v112bo_phase_closure_payload: dict[str, Any],
    ) -> V112BRPhaseCharterReport:
        required = [
            ("V1.12BQ", v112bq_phase_closure_payload, "v112bq_success_criteria_met"),
            ("V1.12BP", v112bp_phase_closure_payload, "v112bp_success_criteria_met"),
            ("V1.12BO", v112bo_phase_closure_payload, "v112bo_success_criteria_met"),
        ]
        for phase_name, payload, flag_name in required:
            if not bool(dict(payload.get("summary", {})).get(flag_name)):
                raise ValueError(f"{phase_name} must be closed before V1.12BR can open.")

        charter = {
            "phase_name": "V1.12BR State Representation And Resonance Discovery",
            "mission": (
                "Build a richer state representation for lawful CPO observations, discover latent state structure "
                "without hard-coding low-dimensional thresholds, then map those structures back to return, "
                "drawdown, and eligibility/veto interpretations."
            ),
            "in_scope": [
                "state vector construction from selector, chronology, role, regime, and internal maturity layers",
                "unsupervised state structure discovery",
                "target mapping to return, drawdown, and veto/eligibility pockets",
                "candidate resonance bundle extraction",
            ],
            "out_of_scope": [
                "formal training opening",
                "formal signal generation",
                "cluster promotion into truth labels",
                "new selector family expansion",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112br_state_representation_and_resonance_discovery",
            "do_open_v112br_now": True,
            "recommended_first_action": "freeze_v112br_state_representation_and_resonance_discovery_v1",
        }
        interpretation = [
            "V1.12BR opens because low-dimensional gate sweeps have now shown diminishing returns.",
            "The lawful next move is to let state geometry surface candidate eligibility and veto regions before turning them back into explicit rules.",
        ]
        return V112BRPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112br_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BRPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
