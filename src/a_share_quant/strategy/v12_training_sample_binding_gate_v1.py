from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12TrainingSampleBindingGateReport:
    summary: dict[str, Any]
    binding_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "binding_rows": self.binding_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12TrainingSampleBindingGateAnalyzer:
    """Decide whether currently surfaced lanes may bind into the bounded training manifest."""

    def analyze(
        self,
        *,
        manifest_payload: dict[str, Any],
        v3_first_lane_payload: dict[str, Any],
        v4_first_lane_payload: dict[str, Any],
    ) -> V12TrainingSampleBindingGateReport:
        manifest_summary = dict(manifest_payload.get("summary", {}))

        def _row_needed(class_name: str) -> int:
            for row in manifest_payload.get("manifest_rows", []):
                if str(row.get("class_name")) == class_name:
                    return int(row.get("additional_rows_needed", 0))
            return 0

        opening_needed = _row_needed("opening_led")
        persistence_needed = _row_needed("persistence_led")
        carry_needed = _row_needed("carry_row_present")

        candidate_rows: list[dict[str, Any]] = []
        for payload in (v3_first_lane_payload, v4_first_lane_payload):
            summary = dict(payload.get("summary", {}))
            candidate_rows.append(
                {
                    "dataset": str(summary.get("dataset_name")),
                    "slice_name": str(summary.get("slice_name")),
                    "symbol": str(summary.get("top_driver")),
                    "opening_present": bool(summary.get("opening_present", False)),
                    "persistence_present": bool(summary.get("persistence_present", False)),
                    "carry_breakthrough_present": bool(summary.get("lane_changes_carry_reading", False)),
                }
            )

        bindable_rows: list[dict[str, Any]] = []
        non_bindable_rows: list[dict[str, Any]] = []
        for row in candidate_rows:
            if row["opening_present"] and not row["persistence_present"] and not row["carry_breakthrough_present"]:
                non_bindable_rows.append(
                    {
                        **row,
                        "binding_posture": "do_not_bind_now",
                        "reason": "opening_class_frozen",
                    }
                )
            else:
                bindable_rows.append(row)

        binding_rows = non_bindable_rows
        summary = {
            "binding_gate_posture": "freeze_v12_training_sample_binding_gate_v1",
            "opening_class_frozen": bool(manifest_summary.get("opening_count_frozen", False)),
            "additional_persistence_rows_needed": persistence_needed,
            "additional_carry_rows_needed": carry_needed,
            "current_bindable_row_count": len(bindable_rows),
            "current_non_bindable_row_count": len(non_bindable_rows),
            "allow_binding_current_opening_led_rows": False,
            "allow_binding_future_clean_persistence_rows": persistence_needed > 0,
            "allow_binding_future_true_carry_rows": carry_needed > 0,
            "ready_for_future_row_binding": True,
            "recommended_next_binding_source": "future_refresh_acceptance_grade_persistence_or_true_carry_rows",
        }
        interpretation = [
            "The bounded training branch should not absorb currently surfaced opening-led first lanes because the opening class is already frozen.",
            "The next bindable rows must come from future acceptance-grade persistence lanes or true carry rows.",
            "This gate turns the training manifest into an operational binding rule instead of a static note.",
        ]
        return V12TrainingSampleBindingGateReport(
            summary=summary,
            binding_rows=binding_rows,
            interpretation=interpretation,
        )


def write_v12_training_sample_binding_gate_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12TrainingSampleBindingGateReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
