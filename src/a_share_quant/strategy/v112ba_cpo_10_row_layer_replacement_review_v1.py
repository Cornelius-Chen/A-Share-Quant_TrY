from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BACPO10RowLayerReplacementReviewReport:
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


class V112BACPO10RowLayerReplacementReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        training_readiness_payload: dict[str, Any],
        guarded_branch_pilot_payload: dict[str, Any],
        training_layer_extension_payload: dict[str, Any],
    ) -> V112BACPO10RowLayerReplacementReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ba_now")):
            raise ValueError("V1.12BA must be open before the replacement review runs.")

        readiness_summary = dict(training_readiness_payload.get("summary", {}))
        guarded_pilot_summary = dict(guarded_branch_pilot_payload.get("summary", {}))
        extension_summary = dict(training_layer_extension_payload.get("summary", {}))

        comparison_rows = [
            {
                "comparison_name": "row_count",
                "old_7_row_baseline": readiness_summary.get("truth_candidate_row_count"),
                "new_10_row_layer": extension_summary.get("row_count_after_extension"),
                "reading": "The replacement only matters if the wider layer stays bounded rather than drifting into generic widen.",
            },
            {
                "comparison_name": "core_target_stability",
                "old_7_row_baseline": "stable_in_v112am_and_followups",
                "new_10_row_layer": guarded_pilot_summary.get("core_targets_stable_after_guarded_branch_admission"),
                "reading": "Core stability must survive the guarded branch addition.",
            },
            {
                "comparison_name": "guarded_target_stability",
                "old_7_row_baseline": "stable_after_guarded_target_widen",
                "new_10_row_layer": guarded_pilot_summary.get("guarded_targets_stable_after_guarded_branch_admission"),
                "reading": "Guarded targets must also survive, otherwise the wider layer should not replace the old one.",
            },
            {
                "comparison_name": "boundary_posture",
                "old_7_row_baseline": "no_branch_rows",
                "new_10_row_layer": "3_guarded_branch_rows_plus_1_retained_review_only_row_outside",
                "reading": "The new layer is only lawful because the mixed connector/MPO branch stays outside.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112ba_cpo_10_row_layer_replacement_review_v1",
            "old_baseline_row_count": readiness_summary.get("truth_candidate_row_count"),
            "new_layer_row_count": extension_summary.get("row_count_after_extension"),
            "replace_7_row_baseline_now": bool(guarded_pilot_summary.get("core_targets_stable_after_guarded_branch_admission"))
            and bool(guarded_pilot_summary.get("guarded_targets_stable_after_guarded_branch_admission")),
            "replacement_posture": "10_row_guarded_layer_becomes_default_next_pilot_layer",
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "open_next_bounded_pilot_on_10_row_guarded_layer",
        }
        interpretation = [
            "The 10-row layer can replace the 7-row baseline for the next bounded pilot because the guarded branch addition remained stable.",
            "This replacement does not erase the guarded boundary on the three added branch rows.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BACPO10RowLayerReplacementReviewReport(
            summary=summary,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )


def write_v112ba_cpo_10_row_layer_replacement_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BACPO10RowLayerReplacementReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
