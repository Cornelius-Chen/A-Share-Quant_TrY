from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112UPhaseCharterReport:
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


class V112UPhaseCharterAnalyzer:
    def analyze(self, *, v112t_phase_closure_payload: dict[str, Any]) -> V112UPhaseCharterReport:
        closure_summary = dict(v112t_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112t_waiting_state_now")):
            raise ValueError("V1.12U requires V1.12T to have lawfully closed.")

        charter = {
            "phase_name": "V1.12U CPO Foundation Completeness And Research-Readiness Review",
            "mission": (
                "Review whether the current CPO information foundation is structured, sufficiently complete, and clean enough "
                "for bounded deep research without confusing that threshold with formal training readiness."
            ),
            "in_scope": [
                "review the combined outputs of V1.12Q, V1.12R, V1.12S, and V1.12T",
                "separate research readiness from formal training readiness",
                "freeze explicit remaining material gaps instead of hand-waving completeness",
            ],
            "out_of_scope": [
                "opening training",
                "opening feature promotion",
                "signal generation",
                "execution logic",
                "automatic next-phase expansion",
            ],
            "success_criteria": [
                "the project has an explicit yes-or-no answer on bounded research readiness",
                "remaining material gaps are listed explicitly rather than left implicit",
                "training readiness is not inferred automatically from registry completeness",
            ],
            "stop_criteria": [
                "the phase silently opens training",
                "the phase collapses research readiness and training readiness into one judgment",
                "the phase invents new cohort rows or chronology windows instead of reviewing readiness",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112u_cpo_foundation_readiness_review",
            "do_open_v112u_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112u_cpo_foundation_readiness_review_v1",
        }
        interpretation = [
            "V1.12U is an owner-level readiness review after the three-step CPO cleaning sequence.",
            "Its purpose is to decide whether the CPO foundation is ready for bounded research, not to authorize training.",
            "The result should make future omissions and remaining gaps explicit and auditable.",
        ]
        return V112UPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112u_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112UPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
