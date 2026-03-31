from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112QPhaseClosureCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112QPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112QPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112q_as_cpo_registry_schema_success",
            "v112q_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112q_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": "execute_bounded_parallel_collection_drafts_then_owner_review",
        }
        evidence_rows = [
            {
                "evidence_name": "v112q_phase_check",
                "actual": {
                    "cycle_stage_count": phase_summary.get("cycle_stage_count"),
                    "information_layer_count": phase_summary.get("information_layer_count"),
                    "bucket_count": phase_summary.get("bucket_count"),
                    "feature_slot_count": phase_summary.get("feature_slot_count"),
                    "subagent_collection_task_count": phase_summary.get("subagent_collection_task_count"),
                },
                "reading": "The CPO line now has enough schema hardness to support bounded parallel collection without automatic drift into training.",
            }
        ]
        interpretation = [
            "V1.12Q closes once the schema is explicit enough that collection can proceed in bounded drafts rather than ad hoc note-taking.",
            "The next lawful move is parallel draft collection and owner review, not model or signal work.",
        ]
        return V112QPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112q_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112QPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
