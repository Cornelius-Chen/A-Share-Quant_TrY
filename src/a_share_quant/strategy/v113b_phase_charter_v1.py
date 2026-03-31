from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113BPhaseCharterReport:
    summary: dict[str, Any]
    mission: dict[str, Any]
    in_scope: list[str]
    out_of_scope: list[str]
    success_criteria: list[str]
    stop_criteria: list[str]
    handoff_condition: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mission": self.mission,
            "in_scope": self.in_scope,
            "out_of_scope": self.out_of_scope,
            "success_criteria": self.success_criteria,
            "stop_criteria": self.stop_criteria,
            "handoff_condition": self.handoff_condition,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113BPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V113BPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        if str(prior_summary.get("recommended_next_posture")) != "review_candidate_mainline_drivers_before_any_model_or_execution_line":
            raise ValueError("V1.13B requires V1.13A to recommend candidate mainline driver review next.")

        summary = {
            "acceptance_posture": "open_v113b_candidate_mainline_driver_review_v1",
            "phase_name": "V1.13B Candidate Mainline Driver Review",
            "ready_for_driver_review_next": True,
        }
        mission = {
            "goal": (
                "Review the frozen review-only candidate drivers and compress them into priority tiers that can guide "
                "later bounded state-usage review without prematurely legislating them as formal schema variables."
            ),
            "why_now": (
                "V1.13A froze the theme-diffusion grammar and preserved ten review-only candidate drivers. The next lawful "
                "move is to rank them for bounded follow-up, not to open models or execution."
            ),
        }
        in_scope = [
            "review the ten review-only candidate drivers preserved by V1.13A",
            "compress candidates into high / medium / deferred priority tiers",
            "mark which candidates are suitable for bounded state-usage review next",
        ]
        out_of_scope = [
            "formal driver promotion into schema law",
            "model training",
            "execution-timing design",
            "strategy integration",
            "new candidate-driver discovery",
        ]
        success_criteria = [
            "the current candidate-driver list is compressed into bounded priority tiers",
            "the next lawful review target is narrowed without promoting any candidate into formal driver law",
        ]
        stop_criteria = [
            "the phase tries to legislate candidate drivers as final variables",
            "the phase expands into new discovery instead of reviewing the frozen candidate set",
        ]
        handoff_condition = "mainline can decide whether to open a bounded state-usage review using only the highest-priority candidate drivers"
        return V113BPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v113b_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V113BPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
