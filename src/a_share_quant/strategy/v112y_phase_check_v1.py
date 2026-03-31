from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112YPhaseCheckReport:
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


class V112YPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        probe_payload: dict[str, Any],
    ) -> V112YPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        probe_summary = dict(probe_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112y_as_adjacent_role_split_sidecar_probe_only",
            "do_open_v112y_now": charter_summary.get("do_open_v112y_now"),
            "split_ready_review_asset_count": probe_summary.get("split_ready_review_asset_count"),
            "still_pending_row_count": probe_summary.get("still_pending_row_count"),
            "formal_training_candidate_count": probe_summary.get("formal_training_candidate_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_of_cpo_foundation_residual_gaps",
        }
        evidence_rows = [
            {
                "evidence_name": "adjacent_role_split_sidecar_probe",
                "actual": {
                    "split_ready_review_asset_count": probe_summary.get("split_ready_review_asset_count"),
                    "still_pending_row_count": probe_summary.get("still_pending_row_count"),
                },
                "reading": "The unresolved adjacent set is no longer a flat pending bucket; most rows now have cleaner review-only split suggestions.",
            }
        ]
        interpretation = [
            "V1.12Y remains a review-only sidecar probe pass.",
            "It reduces adjacent-role ambiguity without authorizing model use.",
        ]
        return V112YPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112y_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112YPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
