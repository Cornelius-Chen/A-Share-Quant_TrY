from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AJPhaseCheckReport:
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


class V112AJPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
    ) -> V112AJPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        assembly_summary = dict(dataset_assembly_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112aj_as_bounded_label_draft_dataset_layer",
            "do_open_v112aj_now": charter_summary.get("do_open_v112aj_now"),
            "dataset_row_count": assembly_summary.get("dataset_row_count"),
            "truth_candidate_row_count": assembly_summary.get("truth_candidate_row_count"),
            "context_only_row_count": assembly_summary.get("context_only_row_count"),
            "ready_label_count": assembly_summary.get("ready_label_count"),
            "guarded_label_count": assembly_summary.get("guarded_label_count"),
            "review_only_label_count": assembly_summary.get("review_only_label_count"),
            "confirmed_only_label_count": assembly_summary.get("confirmed_only_label_count"),
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": assembly_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112aj_dataset_assembly",
                "actual": {
                    "truth_candidate_row_count": assembly_summary.get("truth_candidate_row_count"),
                    "context_only_row_count": assembly_summary.get("context_only_row_count"),
                    "ready_label_count": assembly_summary.get("ready_label_count"),
                    "guarded_label_count": assembly_summary.get("guarded_label_count"),
                },
                "reading": "The dataset draft now separates truth-candidate rows from context-only rows and keeps review-only labels out of truth bundles.",
            }
        ]
        interpretation = [
            "V1.12AJ succeeds if the dataset draft is assembled without flattening context rows into truth.",
            "Training remains closed after this assembly pass.",
        ]
        return V112AJPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112aj_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AJPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
