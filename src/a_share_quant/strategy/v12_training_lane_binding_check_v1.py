from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class V12TrainingLaneBindingCheckReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12TrainingLaneBindingCheckAnalyzer:
    """Classify closed lane artifacts against the frozen bounded-training manifest."""

    def analyze(
        self,
        *,
        manifest_payload: dict[str, Any],
        candidate_payloads: list[tuple[str, dict[str, Any]]],
    ) -> V12TrainingLaneBindingCheckReport:
        manifest_rows = list(manifest_payload.get("manifest_rows", []))

        def _additional_needed(class_name: str) -> int:
            for row in manifest_rows:
                if str(row.get("class_name")) == class_name:
                    return int(row.get("additional_rows_needed", 0))
            return 0

        opening_frozen = bool(dict(manifest_payload.get("summary", {})).get("opening_count_frozen", False))
        candidate_rows: list[dict[str, Any]] = []
        bindable_counts = {
            "persistence_led": 0,
            "carry_row_present": 0,
        }
        rejected_count = 0

        for report_path, payload in candidate_payloads:
            summary = dict(payload.get("summary", {}))
            opening_present = bool(summary.get("opening_present", False))
            persistence_present = bool(summary.get("persistence_present", False))
            carry_breakthrough = bool(summary.get("lane_changes_carry_reading", False))

            if carry_breakthrough:
                binding_outcome = "bind_as_carry_row_present"
                bindable_counts["carry_row_present"] += 1
            elif persistence_present and not opening_present:
                binding_outcome = "bind_as_persistence_led"
                bindable_counts["persistence_led"] += 1
            elif persistence_present and opening_present:
                binding_outcome = "hold_as_mixed_lane"
                rejected_count += 1
            elif opening_present and opening_frozen:
                binding_outcome = "reject_opening_class_frozen"
                rejected_count += 1
            else:
                binding_outcome = "reject_no_bindable_structure"
                rejected_count += 1

            candidate_rows.append(
                {
                    "report_path": report_path,
                    "dataset_name": str(summary.get("dataset_name", "")),
                    "slice_name": str(summary.get("slice_name", "")),
                    "top_driver": str(summary.get("top_driver", "")),
                    "opening_present": opening_present,
                    "persistence_present": persistence_present,
                    "lane_changes_carry_reading": carry_breakthrough,
                    "binding_outcome": binding_outcome,
                }
            )

        summary = {
            "binding_check_posture": "freeze_v12_training_lane_binding_check_v1",
            "candidate_report_count": len(candidate_rows),
            "opening_class_frozen": opening_frozen,
            "bindable_persistence_count": bindable_counts["persistence_led"],
            "bindable_carry_count": bindable_counts["carry_row_present"],
            "rejected_candidate_count": rejected_count,
            "additional_persistence_rows_needed": _additional_needed("persistence_led"),
            "additional_carry_rows_needed": _additional_needed("carry_row_present"),
            "ready_to_expand_training_sample_now": any(value > 0 for value in bindable_counts.values()),
        }
        interpretation = [
            "This check is the per-lane operational entry for the bounded training branch.",
            "A closed lane may bind only if it contributes a clean persistence row or a true carry row.",
            "Opening-led lanes remain structurally useful but should continue to stay outside the training sample while the opening class is frozen.",
        ]
        return V12TrainingLaneBindingCheckReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_v12_training_lane_binding_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12TrainingLaneBindingCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def load_candidate_binding_check_config(
    path: Path,
) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]], Path, str]:
    payload = load_yaml_config(path)
    manifest_payload = load_json_report(Path(payload["paths"]["manifest_report"]))
    candidate_payloads: list[tuple[str, dict[str, Any]]] = []
    for report_path in payload["candidate_reports"]:
        path_str = str(report_path)
        candidate_payloads.append((path_str, load_json_report(Path(path_str))))
    reports_dir = Path(payload["paths"]["reports_dir"])
    report_name = str(payload["report"]["name"])
    return manifest_payload, candidate_payloads, reports_dir, report_name
