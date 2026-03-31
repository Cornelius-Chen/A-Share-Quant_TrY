from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112TPhaseCharterReport:
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


class V112TPhaseCharterAnalyzer:
    def analyze(self, *, v112s_phase_closure_payload: dict[str, Any]) -> V112TPhaseCharterReport:
        closure_summary = dict(v112s_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112s_waiting_state_now")):
            raise ValueError("V1.12T requires V1.12S to have lawfully closed.")

        charter = {
            "phase_name": "V1.12T CPO Spillover Truth-Check",
            "mission": (
                "Classify weak-relevance, name-bonus, and board-follow CPO spillover rows into bounded review categories "
                "so the project preserves A-share-specific spillover information without letting noise silently pollute the cohort."
            ),
            "in_scope": [
                "review only the mixed-relevance spillover rows already frozen in V1.12P",
                "separate likely board-follow noise from possible A-share-specific spillover factor candidates",
                "keep all outputs in review-layer memory",
            ],
            "out_of_scope": [
                "adjacent cohort revalidation",
                "chronology redesign",
                "training authorization",
                "formal feature promotion",
                "execution or signal logic",
            ],
            "success_criteria": [
                "the spillover rows are no longer an undifferentiated noise bucket",
                "potential A-share-specific spillover candidates are preserved explicitly",
                "purely weak rows are identified without being silently discarded",
            ],
            "stop_criteria": [
                "the phase claims business truth it cannot support",
                "spillover rows are promoted into training candidates",
                "the phase turns into general object discovery rather than truth-check",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112t_cpo_spillover_truth_check",
            "do_open_v112t_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112t_cpo_spillover_truth_check_v1",
        }
        interpretation = [
            "V1.12T is the third precise cleaning pass after adjacent cleanup and chronology normalization.",
            "Its goal is preservation with separation, not deletion.",
            "This still does not authorize training, feature promotion, or signal work.",
        ]
        return V112TPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112t_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112TPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
