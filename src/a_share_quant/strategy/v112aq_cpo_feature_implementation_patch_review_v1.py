from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AQCPOFeatureImplementationPatchReviewReport:
    summary: dict[str, Any]
    layer_decision_rows: list[dict[str, Any]]
    patch_scope_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "layer_decision_rows": self.layer_decision_rows,
            "patch_scope_rows": self.patch_scope_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AQCPOFeatureImplementationPatchReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        readiness_payload: dict[str, Any],
        widen_pilot_payload: dict[str, Any],
        daily_board_payload: dict[str, Any],
        future_calendar_payload: dict[str, Any],
    ) -> V112AQCPOFeatureImplementationPatchReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112aq_now")):
            raise ValueError("V1.12AQ must be open before the patch review runs.")

        readiness_summary = dict(readiness_payload.get("summary", {}))
        widen_summary = dict(widen_pilot_payload.get("summary", {}))
        daily_gaps = list(daily_board_payload.get("unresolved_gap_rows", []))
        calendar_gaps = list(future_calendar_payload.get("unresolved_gap_rows", []))

        layer_decision_rows = [
            {
                "layer_name": "feature_implementation",
                "current_posture": readiness_summary.get("feature_implementation_readiness_posture"),
                "widen_implication": "patch_before_row_geometry_widen",
                "why": (
                    "V1.12AL identified implementation as the primary bottleneck, and V1.12AP showed that "
                    "one lawful widen step already survives on the current row set."
                ),
            },
            {
                "layer_name": "row_geometry",
                "current_posture": readiness_summary.get("row_geometry_readiness_posture"),
                "widen_implication": "defer_until_patch_rules_are_frozen",
                "why": (
                    "Widening rows before freezing board/calendar rules would confound geometry risk with "
                    "unfinished implementation risk."
                ),
            },
            {
                "layer_name": "label_binding",
                "current_posture": readiness_summary.get("label_binding_readiness_posture"),
                "widen_implication": "not_the_next_primary_blocker",
                "why": (
                    "Binding remains constrained, but it is no longer the narrowest aperture."
                ),
            },
        ]

        patch_scope_rows: list[dict[str, Any]] = []
        for row in daily_gaps:
            patch_scope_rows.append(
                {
                    "patch_domain": "daily_board_series",
                    "gap_name": row.get("gap_name"),
                    "patch_priority": 1,
                    "patch_reason": row.get("why_it_still_matters"),
                    "recommended_action": "freeze_as_bounded_implementation_rule",
                }
            )
        for row in calendar_gaps:
            patch_scope_rows.append(
                {
                    "patch_domain": "future_catalyst_calendar",
                    "gap_name": row.get("gap_name"),
                    "patch_priority": 2,
                    "patch_reason": row.get("why_it_still_matters"),
                    "recommended_action": "freeze_as_bounded_implementation_rule",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112aq_cpo_feature_implementation_patch_review_v1",
            "primary_bottleneck_layer": readiness_summary.get("primary_bottleneck_layer"),
            "secondary_bottleneck_layer": readiness_summary.get("secondary_bottleneck_layer"),
            "core_targets_stable_after_widen": widen_summary.get("core_targets_stable_after_widen"),
            "guarded_targets_learnable_count": widen_summary.get("guarded_targets_learnable_count"),
            "should_patch_feature_implementation_before_row_widen": True,
            "board_gap_count": len(daily_gaps),
            "calendar_gap_count": len(calendar_gaps),
            "minimum_patch_rule_count": len(daily_gaps) + len(calendar_gaps),
            "allow_row_geometry_widen_now": False,
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "freeze_bounded_board_and_calendar_patch_rules_before_any_row_geometry_widen",
        }
        interpretation = [
            "V1.12AQ does not reopen generic review. It narrows the next legal move to implementation patching.",
            "The widened pilot was strong enough to show that row geometry is no longer the first question to ask.",
            "The next lawful step is to freeze bounded board/calendar implementation rules, not to widen rows immediately.",
        ]
        return V112AQCPOFeatureImplementationPatchReviewReport(
            summary=summary,
            layer_decision_rows=layer_decision_rows,
            patch_scope_rows=patch_scope_rows,
            interpretation=interpretation,
        )


def write_v112aq_cpo_feature_implementation_patch_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AQCPOFeatureImplementationPatchReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
