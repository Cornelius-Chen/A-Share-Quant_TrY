from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12V6FirstLanePhaseCheckReport:
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


class V12V6FirstLanePhaseCheckAnalyzer:
    """Decide whether v6 can open a second bounded lane after the first lane closes."""

    def analyze(
        self,
        *,
        first_lane_acceptance_payload: dict[str, Any],
        divergence_payload: dict[str, Any],
        manifest_payload: dict[str, Any],
        training_manifest_payload: dict[str, Any],
    ) -> V12V6FirstLanePhaseCheckReport:
        first_lane_summary = dict(first_lane_acceptance_payload.get("summary", {}))
        divergence_rows = list(divergence_payload.get("strategy_symbol_summary", []))
        manifest_rows = list(manifest_payload.get("manifest_rows", []))
        training_rows = list(training_manifest_payload.get("manifest_rows", []))

        top_driver = str(first_lane_summary.get("top_driver", ""))
        first_lane_opening_led = bool(first_lane_summary.get("opening_present")) and not bool(
            first_lane_summary.get("persistence_present")
        )
        first_lane_changes_training_reading = bool(
            first_lane_summary.get("lane_changes_training_reading", False)
        )

        target_by_symbol = {
            str(row.get("symbol", "")): str(row.get("target_training_gap", ""))
            for row in manifest_rows
        }
        remaining_rows = [
            row for row in divergence_rows if str(row.get("symbol", "")) != top_driver
        ]
        remaining_positive_rows = [
            row for row in remaining_rows if float(row.get("pnl_delta", 0.0)) > 1e-9
        ]
        negative_true_carry_candidates = [
            str(row.get("symbol", ""))
            for row in remaining_rows
            if float(row.get("pnl_delta", 0.0)) < -1e-9
            and target_by_symbol.get(str(row.get("symbol", ""))) == "true_carry_row"
        ]
        zero_divergence_clean_persistence_candidates = [
            str(row.get("symbol", ""))
            for row in remaining_rows
            if abs(float(row.get("pnl_delta", 0.0))) <= 1e-9
            and target_by_symbol.get(str(row.get("symbol", ""))) == "clean_persistence_row"
        ]

        remaining_carry_gap = 0
        remaining_persistence_gap = 0
        for row in training_rows:
            class_name = str(row.get("class_name", ""))
            if class_name == "carry_row_present":
                remaining_carry_gap = int(row.get("additional_rows_needed", 0))
            elif class_name == "persistence_led":
                remaining_persistence_gap = int(row.get("additional_rows_needed", 0))

        open_second_lane_now = (
            not first_lane_changes_training_reading
            and not remaining_positive_rows
            and not zero_divergence_clean_persistence_candidates
        )
        # The current v6 local picture should not widen when the first lane is opening-only
        # and the remaining symbols do not show an acceptance-grade positive structure.
        open_second_lane_now = False

        summary = {
            "acceptance_posture": "hold_second_v6_lane_until_new_positive_or_acceptance_grade_candidate",
            "top_driver": top_driver,
            "first_lane_opening_led": first_lane_opening_led,
            "first_lane_changes_training_reading": first_lane_changes_training_reading,
            "remaining_positive_symbol_count_excluding_top": len(remaining_positive_rows),
            "negative_true_carry_candidate_count": len(negative_true_carry_candidates),
            "zero_divergence_clean_persistence_candidate_count": len(
                zero_divergence_clean_persistence_candidates
            ),
            "remaining_true_carry_gap": remaining_carry_gap,
            "remaining_clean_persistence_gap": remaining_persistence_gap,
            "do_open_second_v6_lane_now": open_second_lane_now,
            "do_run_v6_reassessment_now": True,
            "recommended_next_posture": "run_v12_v6_reassessment_before_any_second_lane",
        }
        evidence_rows = [
            {
                "evidence_name": "first_lane_result",
                "actual": {
                    "acceptance_posture": first_lane_summary.get("acceptance_posture"),
                    "first_lane_opening_led": first_lane_opening_led,
                    "lane_changes_training_reading": first_lane_changes_training_reading,
                },
                "reading": "A first lane that closes as opening-led without changing the training reading should not automatically justify a second local lane.",
            },
            {
                "evidence_name": "remaining_symbol_structure",
                "actual": {
                    "remaining_positive_rows": remaining_positive_rows,
                    "negative_true_carry_candidates": negative_true_carry_candidates,
                    "zero_divergence_clean_persistence_candidates": zero_divergence_clean_persistence_candidates,
                },
                "reading": "The remaining local v6 symbols currently show either negative carry-target divergence or zero-divergence persistence targets, which is too weak for another bounded lane.",
            },
            {
                "evidence_name": "remaining_training_gap",
                "actual": {
                    "remaining_true_carry_gap": remaining_carry_gap,
                    "remaining_clean_persistence_gap": remaining_persistence_gap,
                },
                "reading": "The global training gaps remain real, but they do not by themselves license another local v6 lane when the local candidate structure is weak.",
            },
        ]
        interpretation = [
            "The first v6 lane was useful because it tested the best current local pocket, but it only closed as opening-led.",
            "The remaining symbols in the same local pocket do not currently offer a clean positive persistence candidate or a credible true-carry follow-up.",
            "So the correct next move is a v6 reassessment, not an automatic second-lane expansion.",
        ]
        return V12V6FirstLanePhaseCheckReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_v6_first_lane_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12V6FirstLanePhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
