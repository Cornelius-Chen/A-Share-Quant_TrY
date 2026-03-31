from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112QPhaseCheckReport:
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


class V112QPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        schema_payload: dict[str, Any],
    ) -> V112QPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        schema_summary = dict(schema_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112q_as_schema_freeze_only",
            "do_open_v112q_now": charter_summary.get("do_open_v112q_now"),
            "cycle_stage_count": schema_summary.get("cycle_stage_count"),
            "information_layer_count": schema_summary.get("information_layer_count"),
            "bucket_count": schema_summary.get("bucket_count"),
            "feature_slot_count": schema_summary.get("feature_slot_count"),
            "subagent_collection_task_count": schema_summary.get("subagent_collection_task_count"),
            "ready_for_phase_closure_next": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": "launch_bounded_parallel_collection_drafts_against_frozen_schema",
        }
        evidence_rows = [
            {
                "evidence_name": "schema_freeze",
                "actual": {
                    "cycle_stage_count": schema_summary.get("cycle_stage_count"),
                    "information_layer_count": schema_summary.get("information_layer_count"),
                    "bucket_count": schema_summary.get("bucket_count"),
                    "feature_slot_count": schema_summary.get("feature_slot_count"),
                },
                "reading": "The CPO line now has a layered schema with explicit pre-rise coverage and bucket separation.",
            },
            {
                "evidence_name": "subagent_safe_routes",
                "actual": {
                    "subagent_collection_task_count": schema_summary.get("subagent_collection_task_count"),
                    "recommended_parallel_collection_now": schema_summary.get("recommended_parallel_collection_now"),
                },
                "reading": "Repetitive collection work can now be parallelized without turning subagents into schema lawmakers.",
            },
        ]
        interpretation = [
            "V1.12Q succeeds once the registry is hardened into a schema strong enough to guide future collection.",
            "This remains a foundation phase and does not authorize training, feature promotion, or execution logic.",
        ]
        return V112QPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112q_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112QPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
