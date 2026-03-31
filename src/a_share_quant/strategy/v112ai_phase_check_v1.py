from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AIPhaseCheckReport:
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


class V112AIPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        owner_review_payload: dict[str, Any],
    ) -> V112AIPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(owner_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ai_as_owner_review_of_label_draft_integrity",
            "do_open_v112ai_now": charter_summary.get("do_open_v112ai_now"),
            "reviewed_label_count": review_summary.get("reviewed_label_count"),
            "draft_ready_label_count": review_summary.get("draft_ready_label_count"),
            "guarded_draft_label_count": review_summary.get("guarded_draft_label_count"),
            "review_only_future_target_count": review_summary.get("review_only_future_target_count"),
            "confirmed_only_review_label_count": review_summary.get("confirmed_only_review_label_count"),
            "dropped_label_count": review_summary.get("dropped_label_count"),
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": review_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ai_owner_review",
                "actual": {
                    "draft_ready_label_count": review_summary.get("draft_ready_label_count"),
                    "guarded_draft_label_count": review_summary.get("guarded_draft_label_count"),
                    "review_only_future_target_count": review_summary.get("review_only_future_target_count"),
                    "confirmed_only_review_label_count": review_summary.get("confirmed_only_review_label_count"),
                    "dropped_label_count": review_summary.get("dropped_label_count"),
                },
                "reading": "The owner review now distinguishes what can enter bounded dataset assembly from what must remain guarded or review-only.",
            }
        ]
        interpretation = [
            "V1.12AI succeeds if the draft becomes tiered without silent deletion.",
            "Formal freeze and training remain closed.",
        ]
        return V112AIPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ai_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AIPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
