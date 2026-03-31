from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112TPhaseCheckReport:
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


class V112TPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        spillover_payload: dict[str, Any],
    ) -> V112TPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        spillover_summary = dict(spillover_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112t_as_spillover_truth_check_only",
            "do_open_v112t_now": charter_summary.get("do_open_v112t_now"),
            "reviewed_spillover_row_count": spillover_summary.get("reviewed_spillover_row_count"),
            "candidate_a_share_spillover_factor_count": spillover_summary.get("candidate_a_share_spillover_factor_count"),
            "pure_name_bonus_or_board_follow_count": spillover_summary.get("pure_name_bonus_or_board_follow_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_of_overall_cpo_information_foundation",
        }
        evidence_rows = [
            {
                "evidence_name": "spillover_truth_check",
                "actual": {
                    "reviewed_spillover_row_count": spillover_summary.get("reviewed_spillover_row_count"),
                    "candidate_a_share_spillover_factor_count": spillover_summary.get("candidate_a_share_spillover_factor_count"),
                    "pure_name_bonus_or_board_follow_count": spillover_summary.get("pure_name_bonus_or_board_follow_count"),
                },
                "reading": "The spillover bucket is no longer an undifferentiated noise pile; it now has explicit review categories.",
            }
        ]
        interpretation = [
            "V1.12T is the final cleaning pass in this CPO information-foundation sequence.",
            "It preserves A-share-specific spillover information without granting any training rights.",
        ]
        return V112TPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112t_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112TPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
