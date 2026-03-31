from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112XPhaseCheckReport:
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


class V112XPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        factor_review_payload: dict[str, Any],
    ) -> V112XPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(factor_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112x_as_spillover_sidecar_probe_only",
            "do_open_v112x_now": charter_summary.get("do_open_v112x_now"),
            "bounded_spillover_factor_candidate_count": review_summary.get("bounded_spillover_factor_candidate_count"),
            "weak_memory_only_row_count": review_summary.get("weak_memory_only_row_count"),
            "formal_feature_candidate_count": review_summary.get("formal_feature_candidate_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_of_cpo_foundation_residual_gaps",
        }
        evidence_rows = [
            {
                "evidence_name": "spillover_factor_candidacy_review",
                "actual": {
                    "bounded_spillover_factor_candidate_count": review_summary.get("bounded_spillover_factor_candidate_count"),
                    "weak_memory_only_row_count": review_summary.get("weak_memory_only_row_count"),
                },
                "reading": "The spillover layer now distinguishes bounded factor candidates from weaker memory-only rows.",
            }
        ]
        interpretation = [
            "V1.12X remains a review-only sidecar probe pass.",
            "It reduces ambiguity in the spillover layer without authorizing model use.",
        ]
        return V112XPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112x_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112XPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
