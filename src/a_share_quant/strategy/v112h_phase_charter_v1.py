from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112HPhaseCharterReport:
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


class V112HPhaseCharterAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112HPhaseCharterReport:
        phase_check_summary = dict(phase_check_payload.get("summary", {}))
        if not bool(phase_check_summary.get("ready_for_phase_closure_next")):
            raise ValueError("V1.12H requires V1.12G to have reached phase closure readiness.")

        charter = {
            "phase_name": "V1.12H High-Level Consolidation Candidate Substate Draft",
            "mission": (
                "Generate a review-only candidate substate draft for high_level_consolidation "
                "using the frozen V1.12B pilot dataset and V1.12G semantic-v2 features."
            ),
            "in_scope": [
                "high_level_consolidation rows only",
                "candidate substate drafting only",
                "cluster statistics and representative rows only",
                "review-only output",
            ],
            "out_of_scope": [
                "formal label rewrite",
                "dataset widening",
                "new model families",
                "phase judgment",
                "strategy integration",
            ],
            "success_criteria": [
                "produce 2-4 candidate substates",
                "summarize semantic-v2 differences per cluster",
                "show test-fold misread-rate differences per cluster",
                "remain review-only",
            ],
            "stop_criteria": [
                "the draft needs new labels to stay coherent",
                "the evidence collapses into a single undifferentiated bucket",
                "the draft requires scope widening or heavy search",
            ],
            "handoff_condition": "owner review before any label split or dataset growth",
        }
        summary = {
            "acceptance_posture": "open_v112h_for_high_level_consolidation_candidate_substate_draft",
            "ready_for_candidate_substate_draft_next": True,
        }
        interpretation = [
            "V1.12H is a review-only drafting phase, not a formal label split.",
            "Its purpose is to expose candidate substates that can later be judged by the owner.",
            "No automatic label change is authorized by this charter.",
        ]
        return V112HPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112h_phase_charter_report(*, reports_dir: Path, report_name: str, result: V112HPhaseCharterReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
