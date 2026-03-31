from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112OPhaseCharterReport:
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


class V112OPhaseCharterAnalyzer:
    """Reenter the optical-link line at the archetype-scope layer."""

    def analyze(
        self,
        *,
        v112n_phase_closure_payload: dict[str, Any],
        owner_reprioritizes_to_cpo: bool,
    ) -> V112OPhaseCharterReport:
        closure_summary = dict(v112n_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112n_waiting_state_now")):
            raise ValueError("V1.12O requires V1.12N to have closed into waiting state.")

        do_open_now = owner_reprioritizes_to_cpo
        charter = {
            "phase_name": "V1.12O Optical-Link Deep Archetype Scope",
            "mission": (
                "Lift the optical-link price-and-demand upcycle from a three-symbol pilot into a bounded deep-archetype "
                "study scope so the project can widen CPO understanding without reopening the already-closed "
                "high-level-consolidation local refinement pocket."
            ),
            "in_scope": [
                "freeze optical-link as the current reprioritized deep-study archetype",
                "preserve the three validated local seeds from the frozen pilot dataset",
                "record adjacent cohort candidates as review-only study rows",
                "freeze bounded study dimensions for leader-beta-component divergence and adjacent CPO drift",
            ],
            "out_of_scope": [
                "reopening V1.12M/V1.12N inner-refinement work",
                "automatic label split",
                "automatic training rerun",
                "strategy signal generation",
                "execution timing logic",
            ],
            "success_criteria": [
                "optical-link becomes a bounded archetype scope rather than only a frozen three-symbol pilot",
                "adjacent cohort expansion is moved into explicit candidate tiers instead of implicit future ideas",
                "the next lawful move becomes bounded candidate validation or bounded cohort-widening review",
            ],
            "stop_criteria": [
                "if the phase reopens the closed high-level-consolidation predictive pocket",
                "if the phase treats review-only adjacent names as validated training objects",
                "if the phase widens into execution or signal logic",
            ],
            "handoff_condition": (
                "After scope freeze, the next legal move is bounded candidate validation for adjacent optical-link cohort "
                "names, not automatic dataset widening or training."
            ),
            "owner_heavy_context_phase": False,
        }
        summary = {
            "acceptance_posture": (
                "open_v112o_optical_link_deep_archetype_scope"
                if do_open_now
                else "hold_v112o_until_owner_reprioritizes_to_cpo"
            ),
            "do_open_v112o_now": do_open_now,
            "reprioritized_family": "earnings_transmission_carry",
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112o_optical_link_study_scope_v1",
        }
        interpretation = [
            "V1.12O does not undo the lawful V1.12N closure; it changes altitude from local pocket refinement to broader CPO archetype understanding.",
            "The three frozen pilot names remain validated local seeds rather than being discarded or retrained immediately.",
            "The next asset is explicit cohort and scope memory, not another pass over the already-exhausted stall pocket.",
        ]
        return V112OPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112o_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112OPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
