from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112RPhaseCheckReport:
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


class V112RPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        validation_payload: dict[str, Any],
    ) -> V112RPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        validation_summary = dict(validation_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112r_as_adjacent_validation_only",
            "do_open_v112r_now": charter_summary.get("do_open_v112r_now"),
            "reviewed_adjacent_row_count": validation_summary.get("reviewed_adjacent_row_count"),
            "validated_review_asset_count": validation_summary.get("validated_review_asset_count"),
            "pending_split_or_role_validation_count": validation_summary.get("pending_split_or_role_validation_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "move_to_chronology_normalization_next",
        }
        evidence_rows = [
            {
                "evidence_name": "adjacent_cohort_validation",
                "actual": {
                    "reviewed_adjacent_row_count": validation_summary.get("reviewed_adjacent_row_count"),
                    "validated_review_asset_count": validation_summary.get("validated_review_asset_count"),
                    "pending_split_or_role_validation_count": validation_summary.get("pending_split_or_role_validation_count"),
                },
                "reading": "The adjacent pool is no longer a flat review-only set; some rows are now cleaner while others are explicitly pending structural cleanup.",
            }
        ]
        interpretation = [
            "V1.12R is a cleaning pass, not a promotion pass.",
            "The next lawful move should be chronology normalization or spillover truth-check, not training.",
        ]
        return V112RPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112r_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112RPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
