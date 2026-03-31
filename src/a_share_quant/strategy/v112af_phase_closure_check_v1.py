from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AFPhaseClosureCheckReport:
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


class V112AFPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AFPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112af_as_bounded_feature_family_design_success",
            "v112af_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112af_waiting_state_now": True,
            "allow_auto_feature_promotion_now": False,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112af_phase_check",
                "actual": {
                    "feature_family_count": phase_summary.get("feature_family_count"),
                    "design_ready_feature_count": phase_summary.get("design_ready_feature_count"),
                    "speculative_feature_count": phase_summary.get("speculative_feature_count"),
                    "overlay_only_feature_count": phase_summary.get("overlay_only_feature_count"),
                },
                "reading": "The CPO feature shortlist is now a bounded family-design layer and can be consumed by later label-draft work without opening promotion rights.",
            }
        ]
        interpretation = [
            "V1.12AF closes once the brainstorm batch and dynamic-role layer are compressed into governed families with guards.",
            "The next lawful move is bounded label-draft assembly.",
        ]
        return V112AFPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112af_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AFPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
