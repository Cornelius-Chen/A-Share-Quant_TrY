from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112NPhaseCharterReport:
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


class V112NPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V112NPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        recommended_next_posture = str(prior_summary.get("recommended_next_posture", ""))
        if recommended_next_posture != "preserve_inner_draft_pieces_and_pause_before_any_label_or_schema decision":
            raise ValueError("V1.12N requires the V1.12M closure posture to preserve inner-draft pieces without schema change.")

        summary = {
            "acceptance_posture": "open_v112n_review_only_shadow_rerun",
            "phase_name": "V1.12N Review-Only Shadow Rerun",
            "ready_for_shadow_rerun_next": True,
        }
        mission = {
            "goal": (
                "Run one review-only rerun with inner-draft shadow flags added as features, to check whether the V1.12M "
                "inner structures create measurable incremental value before any label or schema action."
            ),
            "why_now": (
                "V1.12M produced two preserved review-only inner candidates and one unresolved residue, so the next "
                "lawful question is whether these inner structures help the frozen pilot at all."
            ),
        }
        in_scope = [
            "same frozen pilot dataset",
            "same labels and same time split",
            "three review-only shadow flags derived from V1.12M inner-draft logic",
            "baseline and GBDT comparison against V1.12G",
        ]
        out_of_scope = [
            "formal label split",
            "schema promotion",
            "dataset widening",
            "model-family expansion",
            "strategy deployment",
        ]
        success_criteria = [
            "the shadow rerun completes on the frozen pilot",
            "the report clearly states whether the inner-draft shadow features add incremental value or not",
            "the result remains review-only regardless of outcome",
        ]
        stop_criteria = [
            "the rerun requires label changes to show any value",
            "the rerun drifts into wider model search or dataset widening",
        ]
        handoff_condition = "mainline can decide whether the inner-draft pieces are only descriptive or also useful as future feature-side assets"
        return V112NPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v112n_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V112NPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
