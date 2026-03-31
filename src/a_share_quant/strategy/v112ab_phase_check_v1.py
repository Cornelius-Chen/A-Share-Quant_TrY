from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ABPhaseCheckReport:
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


class V112ABPhaseCheckAnalyzer:
    def analyze(self, *, phase_charter_payload: dict[str, Any], labeling_review_payload: dict[str, Any]) -> V112ABPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(labeling_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ab_as_bounded_labeling_review_only",
            "do_open_v112ab_now": charter_summary.get("do_open_v112ab_now"),
            "primary_labeling_surface_count": review_summary.get("primary_labeling_surface_count"),
            "secondary_labeling_surface_count": review_summary.get("secondary_labeling_surface_count"),
            "excluded_pending_surface_count": review_summary.get("excluded_pending_surface_count"),
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_then_bounded_label_draft_assembly",
        }
        evidence_rows = [
            {
                "evidence_name": "v112ab_labeling_review",
                "actual": {
                    "primary_labeling_surface_count": review_summary.get("primary_labeling_surface_count"),
                    "secondary_labeling_surface_count": review_summary.get("secondary_labeling_surface_count"),
                    "excluded_pending_surface_count": review_summary.get("excluded_pending_surface_count"),
                },
                "reading": "The CPO line now has explicit later label surfaces and exclusions.",
            }
        ]
        interpretation = [
            "V1.12AB keeps label freezing closed while making later drafting surfaces explicit.",
            "Training remains closed.",
        ]
        return V112ABPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ab_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ABPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
