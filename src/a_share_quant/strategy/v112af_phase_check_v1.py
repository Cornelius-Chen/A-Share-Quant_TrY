from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AFPhaseCheckReport:
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


class V112AFPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_family_review_payload: dict[str, Any],
    ) -> V112AFPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_family_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112af_as_bounded_feature_family_design_layer",
            "do_open_v112af_now": charter_summary.get("do_open_v112af_now"),
            "feature_family_count": review_summary.get("feature_family_count"),
            "design_ready_feature_count": review_summary.get("design_ready_feature_count"),
            "speculative_feature_count": review_summary.get("speculative_feature_count"),
            "overlay_only_feature_count": review_summary.get("overlay_only_feature_count"),
            "allow_auto_feature_promotion_now": False,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "bounded_label_draft_assembly_with_feature_family_inputs",
        }
        evidence_rows = [
            {
                "evidence_name": "v112af_feature_family_design_review",
                "actual": {
                    "feature_family_count": review_summary.get("feature_family_count"),
                    "design_ready_feature_count": review_summary.get("design_ready_feature_count"),
                    "overlay_only_feature_count": review_summary.get("overlay_only_feature_count"),
                    "blind_spot_count": review_summary.get("blind_spot_count"),
                },
                "reading": "The brainstorm shortlist is now compressed into bounded families with explicit guards and preserved blind spots.",
            }
        ]
        interpretation = [
            "V1.12AF succeeds if candidate features become governed families rather than staying as a noun list.",
            "Promotion, label freeze, and training remain closed.",
        ]
        return V112AFPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112af_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AFPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
