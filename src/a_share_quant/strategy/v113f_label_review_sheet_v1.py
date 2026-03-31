from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113FLabelReviewSheetReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113FLabelReviewSheetAnalyzer:
    """Produce the first owner-correctable review sheet for the theme-diffusion pilot."""

    def analyze(
        self,
        *,
        pilot_object_pool_payload: dict[str, Any],
        pilot_protocol_payload: dict[str, Any],
    ) -> V113FLabelReviewSheetReport:
        pool_summary = dict(pilot_object_pool_payload.get("summary", {}))
        protocol = dict(pilot_protocol_payload.get("labeling_protocol", {}))
        if not bool(pool_summary.get("ready_for_label_review_sheet_next")):
            raise ValueError("V1.13F object pool must be frozen before label review sheet assembly.")

        label_blocks = dict(protocol.get("label_blocks", {}))
        review_rows = []
        for object_row in pilot_object_pool_payload.get("object_rows", []):
            review_rows.append(
                {
                    "symbol": object_row["symbol"],
                    "name": object_row["name"],
                    "pool_role_guess": object_row["pool_role_guess"],
                    "role_guess_reason": object_row["role_guess_reason"],
                    "cycle_window_start_guess": object_row["first_seen_in_local_mapping"],
                    "cycle_window_end_guess": object_row["last_seen_in_local_mapping"],
                    "include_in_first_pilot_guess": True,
                    "object_missing_or_extra_review": "owner_review_needed",
                    "role_correction_status": "owner_review_needed",
                    "cycle_window_correction_status": "owner_review_needed",
                    "state_label_review_status": "owner_review_needed",
                    "strength_label_review_status": "owner_review_needed",
                    "driver_presence_review_status": "owner_review_needed",
                    "label_blocks_to_review": list(label_blocks.keys()),
                    "owner_notes": "",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113f_label_review_sheet_v1",
            "review_row_count": len(review_rows),
            "owner_review_required_count": len(review_rows),
            "label_block_focus_count": len(label_blocks),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The first theme-diffusion pilot sheet is intentionally draft-heavy because object roles and windows remain archetype-review questions, not fixed truth.",
            "Every row is exposed to owner correction before any label freeze or training starts.",
            "The sheet is a bounded collaboration surface, not a finished training file.",
        ]
        return V113FLabelReviewSheetReport(summary=summary, review_rows=review_rows, interpretation=interpretation)


def write_v113f_label_review_sheet_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113FLabelReviewSheetReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
