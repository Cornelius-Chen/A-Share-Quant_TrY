from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CGPackagingRefinedActionMappingPilotReport:
    summary: dict[str, Any]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CGPackagingRefinedActionMappingPilotAnalyzer:
    def analyze(
        self,
        *,
        cd_payload: dict[str, Any],
        cf_payload: dict[str, Any],
    ) -> V112CGPackagingRefinedActionMappingPilotReport:
        cd_summary = dict(cd_payload.get("summary", {}))
        cf_summary = dict(cf_payload.get("summary", {}))
        comparison_rows = [
            {
                "comparison_name": "realized_path_invariance",
                "reading": "The refined packaging boundary improves broader action mapping accuracy, but does not alter the currently realized baseline path because the two realized packaging states remain veto and eligibility after refinement.",
            },
            {
                "comparison_name": "validation_accuracy_gain",
                "old_value": cf_summary.get("previous_action_mapping_accuracy"),
                "new_value": cf_summary.get("refined_action_mapping_accuracy"),
                "delta": cf_summary.get("accuracy_delta"),
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v112cg_packaging_refined_action_mapping_pilot_v1",
            "realized_path_changed": False,
            "cd_total_return": cd_summary.get("total_return"),
            "cd_max_drawdown": cd_summary.get("max_drawdown"),
            "cf_validation_accuracy": cf_summary.get("refined_action_mapping_accuracy"),
            "recommended_next_posture": "freeze_refined_packaging_template_and_apply_only_when_future_packaging_like_states_reappear",
        }
        interpretation = [
            "V1.12CG confirms that the refined packaging veto/de-risk boundary is a template-stabilizing change, not a realized-path-distorting change.",
            "The path-level outcome remains the same as V1.12CD, while the broader packaging family validation improves materially under V1.12CF.",
        ]
        return V112CGPackagingRefinedActionMappingPilotReport(
            summary=summary,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )


def write_v112cg_packaging_refined_action_mapping_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CGPackagingRefinedActionMappingPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
