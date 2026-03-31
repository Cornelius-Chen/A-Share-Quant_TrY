from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112GFeatureSchemaV2Report:
    summary: dict[str, Any]
    feature_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_rows": self.feature_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112GFeatureSchemaV2Analyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        refinement_design_payload: dict[str, Any],
    ) -> V112GFeatureSchemaV2Report:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        design_rows = list(refinement_design_payload.get("catalyst_state_refinement_rows", []))
        if not bool(charter_summary.get("ready_for_feature_schema_v2_next")):
            raise ValueError("V1.12G feature schema requires an open V1.12G charter.")

        feature_rows = [
            {
                "feature_name": "catalyst_freshness_state",
                "source_semantic": design_rows[0]["semantic_question"] if len(design_rows) > 0 else "",
                "implementation_basis": "demand_acceleration_proxy + breakout_or_hold_structure + catalyst_presence",
                "target_stage": "major_markup,high_level_consolidation",
            },
            {
                "feature_name": "cross_day_catalyst_persistence",
                "source_semantic": design_rows[1]["semantic_question"] if len(design_rows) > 1 else "",
                "implementation_basis": "product_price_change_proxy + relative_strength_persistence + catalyst_presence",
                "target_stage": "high_level_consolidation",
            },
            {
                "feature_name": "theme_breadth_confirmation_proxy",
                "source_semantic": design_rows[2]["semantic_question"] if len(design_rows) > 2 else "",
                "implementation_basis": "cross-symbol same-day breadth from positive ret_5 and above-ma20 cohort share",
                "target_stage": "major_markup,high_level_consolidation",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v112g_feature_schema_v2",
            "new_feature_count": len(feature_rows),
            "total_feature_count_v2": 15,
            "ready_for_baseline_v2_next": True,
        }
        interpretation = [
            "The v2 schema adds bounded semantics rather than a generic catalyst feature explosion.",
            "All three additions are stage-targeted and remain derivable from the same frozen dataset plus cross-symbol cohort context.",
            "The next lawful move is to rerun the same pilot baseline and sidecar with these added semantics.",
        ]
        return V112GFeatureSchemaV2Report(summary=summary, feature_rows=feature_rows, interpretation=interpretation)


def write_v112g_feature_schema_v2_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112GFeatureSchemaV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
