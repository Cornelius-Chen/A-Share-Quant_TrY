from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AGPhaseCheckReport:
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


class V112AGPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        label_draft_payload: dict[str, Any],
    ) -> V112AGPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        draft_summary = dict(label_draft_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ag_as_bounded_label_draft_integrity_layer",
            "do_open_v112ag_now": charter_summary.get("do_open_v112ag_now"),
            "label_skeleton_count": draft_summary.get("label_skeleton_count"),
            "family_support_mapping_count": draft_summary.get("family_support_mapping_count"),
            "anti_leakage_review_count": draft_summary.get("anti_leakage_review_count"),
            "ambiguity_preservation_count": draft_summary.get("ambiguity_preservation_count"),
            "labels_supported_now_count": draft_summary.get("labels_supported_now_count"),
            "labels_supported_with_guard_count": draft_summary.get("labels_supported_with_guard_count"),
            "labels_review_only_or_confirmed_only_count": draft_summary.get("labels_review_only_or_confirmed_only_count"),
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_of_bounded_label_draft_integrity",
        }
        evidence_rows = [
            {
                "evidence_name": "v112ag_bounded_label_draft_assembly",
                "actual": {
                    "label_skeleton_count": draft_summary.get("label_skeleton_count"),
                    "family_support_mapping_count": draft_summary.get("family_support_mapping_count"),
                    "anti_leakage_review_count": draft_summary.get("anti_leakage_review_count"),
                    "ambiguity_preservation_count": draft_summary.get("ambiguity_preservation_count"),
                },
                "reading": "The label draft is now assembled as a consistency check across labels, families, cohort layers, and ambiguity rules rather than as a hidden training launch.",
            }
        ]
        interpretation = [
            "V1.12AG is successful if the draft becomes structurally auditable, not if it becomes cosmetically complete.",
            "Training and formal label freeze remain closed after this pass.",
        ]
        return V112AGPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ag_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AGPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
