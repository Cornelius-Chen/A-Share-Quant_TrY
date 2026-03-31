from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112IPhaseCharterReport:
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


class V112IPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V112IPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        if not bool(prior_summary.get("enter_v112g_waiting_state_now")):
            raise ValueError("V1.12I requires V1.12G to be closed into owner-review waiting state.")

        summary = {
            "acceptance_posture": "open_v112i_label_refinement_review_protocol",
            "phase_name": "V1.12I Label Refinement Review Protocol",
            "ready_for_protocol_next": True,
        }
        mission = {
            "goal": (
                "Freeze the review standard for deciding whether high_level_consolidation should remain "
                "a feature-only problem or become a bounded candidate for label splitting."
            ),
            "why_now": (
                "V1.12G isolated a semantic-v2 delta concentrated in high_level_consolidation, so the next mainline "
                "need is a stable review rule rather than immediate relabeling."
            ),
        }
        in_scope = [
            "define review gates for bounded label-split candidacy",
            "define rejection conditions that keep refinement on the feature side only",
            "keep the review tied to the frozen V1.12B/V1.12G pilot basis",
        ]
        out_of_scope = [
            "formal label rewrite",
            "dataset widening",
            "new model family search",
            "strategy integration",
        ]
        success_criteria = [
            "a review-only protocol exists for deciding whether candidate substates justify bounded follow-up",
            "the protocol distinguishes evidence sufficient for drafting from evidence sufficient for formal label changes",
        ]
        stop_criteria = [
            "protocol starts rewriting labels instead of governing review",
            "protocol depends on scope growth or new data before it can be useful",
        ]
        handoff_condition = "use the protocol after a bounded subagent or mainline bucketization output arrives"
        return V112IPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v112i_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V112IPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
