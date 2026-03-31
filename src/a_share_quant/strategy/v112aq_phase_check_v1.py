from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AQPhaseCheckReport:
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


class V112AQPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        patch_review_payload: dict[str, Any],
    ) -> V112AQPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(patch_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112aq_as_bounded_feature_implementation_patch_review",
            "do_open_v112aq_now": charter_summary.get("do_open_v112aq_now"),
            "should_patch_feature_implementation_before_row_widen": review_summary.get(
                "should_patch_feature_implementation_before_row_widen"
            ),
            "minimum_patch_rule_count": review_summary.get("minimum_patch_rule_count"),
            "allow_row_geometry_widen_now": review_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": review_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112aq_patch_review",
                "actual": {
                    "primary_bottleneck_layer": review_summary.get("primary_bottleneck_layer"),
                    "minimum_patch_rule_count": review_summary.get("minimum_patch_rule_count"),
                    "allow_row_geometry_widen_now": review_summary.get("allow_row_geometry_widen_now"),
                },
                "reading": "This phase is successful only if it narrows the next move to a specific patch scope.",
            }
        ]
        interpretation = [
            "V1.12AQ should end with an action-level implementation decision, not another generic request for more review.",
            "Row-geometry widen remains blocked until the bounded patch rule set is frozen.",
        ]
        return V112AQPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112aq_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AQPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
