from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ALabelReviewSheetReport:
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


class V112ALabelReviewSheetAnalyzer:
    """Produce the first owner-correctable label review sheet."""

    def analyze(
        self,
        *,
        pilot_object_pool_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
    ) -> V112ALabelReviewSheetReport:
        pool_summary = dict(pilot_object_pool_payload.get("summary", {}))
        protocol = dict(training_protocol_payload.get("protocol", {}))
        if not bool(pool_summary.get("ready_for_label_review_sheet_next")):
            raise ValueError("V1.12A object pool must be frozen before label review sheet assembly.")

        feature_blocks = list(dict(protocol.get("feature_blocks", {})).keys())
        review_rows = []
        for object_row in pilot_object_pool_payload.get("object_rows", []):
            review_rows.append(
                {
                    "symbol": object_row["symbol"],
                    "name": object_row["name"],
                    "pool_role_guess": object_row["pool_role_guess"],
                    "cycle_window_start_guess": "",
                    "cycle_window_end_guess": "",
                    "include_in_first_pilot_guess": True,
                    "object_missing_or_extra_review": "owner_review_needed",
                    "role_correction_status": "owner_review_needed",
                    "cycle_window_correction_status": "owner_review_needed",
                    "feature_block_focus": feature_blocks,
                    "label_fields_to_review": [
                        "forward_return_bucket",
                        "max_drawdown_bucket",
                        "carry_outcome_class",
                    ],
                    "owner_notes": "",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112a_label_review_sheet_v1",
            "review_row_count": len(review_rows),
            "owner_review_required_count": len(review_rows),
            "feature_block_focus_count": len(feature_blocks),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The first pilot sheet is intentionally incomplete in the places where owner correction adds the most value: object inclusion, role, and cycle window.",
            "This lets the owner correct omissions and misreads before any training data is finalized.",
            "The sheet is a bounded collaboration surface, not a finished label file.",
        ]
        return V112ALabelReviewSheetReport(summary=summary, review_rows=review_rows, interpretation=interpretation)


def write_v112a_label_review_sheet_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ALabelReviewSheetReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
