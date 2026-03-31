from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112SPhaseCharterReport:
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


class V112SPhaseCharterAnalyzer:
    def analyze(self, *, v112r_phase_closure_payload: dict[str, Any]) -> V112SPhaseCharterReport:
        closure_summary = dict(v112r_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112r_waiting_state_now")):
            raise ValueError("V1.12S requires V1.12R to have lawfully closed.")

        charter = {
            "phase_name": "V1.12S CPO Chronology Normalization",
            "mission": (
                "Normalize the CPO full-cycle time axis so public catalyst anchors, earnings windows, "
                "capex references, design-win latency, and route-event timing can be attached to a consistent chronology "
                "instead of remaining as flat anchor lists."
            ),
            "in_scope": [
                "freeze bounded chronology segments for the CPO cycle",
                "normalize event windows and post-event follow-through windows",
                "normalize lag structures such as capex-to-order and launch-to-ramp",
                "keep the result at review-layer only",
            ],
            "out_of_scope": [
                "spillover truth-check",
                "training authorization",
                "feature promotion",
                "execution or signal logic",
            ],
            "success_criteria": [
                "the CPO line has a normalized chronology grammar instead of only event anchors",
                "major timing blind spots are turned into explicit review objects",
                "the next lawful move becomes spillover truth-check rather than more chronology brainstorming",
            ],
            "stop_criteria": [
                "chronology work drifts into object-pool validation",
                "timing anchors are treated as predictive signals directly",
                "the phase expands into execution timing logic",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112s_cpo_chronology_normalization",
            "do_open_v112s_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112s_cpo_chronology_normalization_v1",
        }
        interpretation = [
            "V1.12S is the second precise cleaning pass after adjacent cohort validation.",
            "The point is not to add more dates; the point is to make timing relationships explicit and reviewable.",
            "This still does not authorize training or signal work.",
        ]
        return V112SPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112s_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112SPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
