from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AZCPOBoundedTrainingLayerExtensionReport:
    summary: dict[str, Any]
    training_layer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "training_layer_rows": self.training_layer_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AZCPOBoundedTrainingLayerExtensionAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
        branch_training_layer_review_payload: dict[str, Any],
    ) -> V112AZCPOBoundedTrainingLayerExtensionReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112az_now")):
            raise ValueError("V1.12AZ must be open before the extension runs.")

        dataset_rows = {str(row.get("symbol")): row for row in list(dataset_assembly_payload.get("dataset_draft_rows", []))}
        branch_review_rows = list(branch_training_layer_review_payload.get("branch_layer_rows", []))
        admissible_symbols = {
            str(row.get("symbol"))
            for row in branch_review_rows
            if bool(row.get("bounded_training_layer_admissible"))
        }
        if len(admissible_symbols) != 3:
            raise ValueError("V1.12AZ expects exactly three branch rows to be bounded-training-layer admissible.")

        training_layer_rows: list[dict[str, Any]] = []
        for symbol, row in dataset_rows.items():
            include_base = bool(row.get("include_in_truth_candidate_rows"))
            include_branch = symbol in admissible_symbols
            include_now = include_base or include_branch
            if not include_now:
                continue

            training_layer_rows.append(
                {
                    "symbol": symbol,
                    "cohort_layer": str(row.get("cohort_layer")),
                    "role_family": str(row.get("role_family")),
                    "training_layer_posture": self._training_layer_posture(symbol=symbol, base_include=include_base),
                    "allowed_ready_labels": list(row.get("allowed_ready_labels", [])),
                    "allowed_guarded_labels": self._allowed_guarded_labels(symbol=symbol, source_row=row),
                    "active_stage_windows": list(row.get("active_stage_windows", [])),
                    "reading": self._reading(symbol=symbol, base_include=include_base),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112az_cpo_bounded_training_layer_extension_v1",
            "row_count_before_extension": 7,
            "row_count_after_extension": len(training_layer_rows),
            "guarded_branch_row_count": len(admissible_symbols),
            "retained_review_only_branch_row_count": 1,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "review_if_10_row_bounded_training_layer_can_replace_the_7_row_baseline_for_next_pilot",
        }
        interpretation = [
            "V1.12AZ assembles the first 10-row bounded training-facing layer without broadening beyond the three guarded-admissible branch rows.",
            "The added branch rows remain guarded and do not inherit unrestricted truth posture.",
        ]
        return V112AZCPOBoundedTrainingLayerExtensionReport(
            summary=summary,
            training_layer_rows=training_layer_rows,
            interpretation=interpretation,
        )

    def _training_layer_posture(self, *, symbol: str, base_include: bool) -> str:
        if base_include:
            return "core_or_secondary_truth_row"
        return "guarded_branch_training_layer_row"

    def _allowed_guarded_labels(self, *, symbol: str, source_row: dict[str, Any]) -> list[str]:
        if bool(source_row.get("include_in_truth_candidate_rows")):
            return list(source_row.get("allowed_guarded_labels", []))
        return [
            "board_condition_label",
            "role_transition_label",
        ]

    def _reading(self, *, symbol: str, base_include: bool) -> str:
        if base_include:
            return "This row stays in the bounded training-facing layer as part of the original 7-row skeleton."
        return "This branch row enters the bounded training-facing layer under guarded posture only."


def write_v112az_cpo_bounded_training_layer_extension_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AZCPOBoundedTrainingLayerExtensionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
