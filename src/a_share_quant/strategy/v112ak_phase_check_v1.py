from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AKPhaseCheckReport:
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


class V112AKPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_binding_payload: dict[str, Any],
    ) -> V112AKPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        binding_summary = dict(feature_binding_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ak_as_bounded_feature_binding_review",
            "do_open_v112ak_now": charter_summary.get("do_open_v112ak_now"),
            "truth_candidate_row_count": binding_summary.get("truth_candidate_row_count"),
            "evaluated_binding_count": binding_summary.get("evaluated_binding_count"),
            "direct_bindable_count": binding_summary.get("direct_bindable_count"),
            "guarded_bindable_count": binding_summary.get("guarded_bindable_count"),
            "row_specific_blocked_count": binding_summary.get("row_specific_blocked_count"),
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": binding_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112ak_feature_binding_review",
                "actual": {
                    "evaluated_binding_count": binding_summary.get("evaluated_binding_count"),
                    "direct_bindable_count": binding_summary.get("direct_bindable_count"),
                    "guarded_bindable_count": binding_summary.get("guarded_bindable_count"),
                    "row_specific_blocked_count": binding_summary.get("row_specific_blocked_count"),
                },
                "reading": "The current row-label set now has an explicit binding map instead of assuming all admitted labels are equally usable.",
            }
        ]
        interpretation = [
            "V1.12AK succeeds if row-level binding weakness is made explicit before any training-readiness claim.",
            "Training remains closed.",
        ]
        return V112AKPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ak_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AKPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
