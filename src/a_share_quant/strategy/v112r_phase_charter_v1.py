from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112RPhaseCharterReport:
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


class V112RPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        v112q_phase_closure_payload: dict[str, Any],
    ) -> V112RPhaseCharterReport:
        closure_summary = dict(v112q_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112q_waiting_state_now")):
            raise ValueError("V1.12R requires V1.12Q to have lawfully closed.")

        charter = {
            "phase_name": "V1.12R Adjacent Cohort Validation",
            "mission": (
                "Clean the adjacent CPO cohort by validating which names can already stand as bounded review assets, "
                "which remain pending role-split or platform clarification, and which should stay deferred."
            ),
            "in_scope": [
                "review direct-related and branch-extension names already present in V1.12P and V1.12Q batch outputs",
                "use official anchors to reduce object-pool ambiguity",
                "separate validated adjacent review assets from pending role-split clusters",
                "keep the result at review-layer only",
            ],
            "out_of_scope": [
                "chronology normalization",
                "spillover truth-check",
                "training authorization",
                "feature promotion",
                "execution or signal logic",
            ],
            "success_criteria": [
                "the adjacent cohort is no longer a flat review-only pile",
                "at least some rows become bounded validated review assets",
                "unclear clusters are named explicitly instead of remaining hidden ambiguity",
            ],
            "stop_criteria": [
                "adjacent validation drifts into chronology design",
                "review-only names are treated as training-ready",
                "no meaningful distinction can be made across the adjacent pool",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112r_adjacent_cohort_validation",
            "do_open_v112r_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112r_adjacent_cohort_validation_v1",
        }
        interpretation = [
            "V1.12R is the first precise cleaning pass after schema hardening.",
            "It exists to reduce object-pool ambiguity before chronology and spillover work proceed.",
            "The output should improve review quality, not open training.",
        ]
        return V112RPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112r_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112RPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
