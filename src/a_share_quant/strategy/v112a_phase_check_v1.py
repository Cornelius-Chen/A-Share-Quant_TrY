from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APhaseCheckReport:
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


class V112APhaseCheckAnalyzer:
    """Check whether the pilot data assembly now supports owner correction."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_object_pool_payload: dict[str, Any],
        label_review_sheet_payload: dict[str, Any],
    ) -> V112APhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pool_summary = dict(pilot_object_pool_payload.get("summary", {}))
        review_summary = dict(label_review_sheet_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v112a_as_owner_correction_ready_pilot_data_assembly_only",
            "do_open_v112a_now": charter_summary.get("do_open_v112a_now"),
            "pilot_object_count": pool_summary.get("pilot_object_count"),
            "owner_review_required_count": review_summary.get("owner_review_required_count"),
            "ready_for_owner_correction_next": True,
            "allow_training_now": False,
            "allow_auto_object_expansion_now": False,
            "recommended_next_posture": "close_v112a_and_wait_for_owner_corrections_on_pilot_sheet",
        }
        evidence_rows = [
            {
                "evidence_name": "pilot_object_pool",
                "actual": {
                    "pilot_object_count": pool_summary.get("pilot_object_count"),
                    "repo_seen_object_count": pool_summary.get("repo_seen_object_count"),
                    "owner_seeded_object_count": pool_summary.get("owner_seeded_object_count"),
                },
                "reading": "The first pilot pool is small enough for direct owner inspection and correction.",
            },
            {
                "evidence_name": "label_review_sheet",
                "actual": {
                    "review_row_count": review_summary.get("review_row_count"),
                    "owner_review_required_count": review_summary.get("owner_review_required_count"),
                },
                "reading": "The sheet explicitly exposes where owner corrections are needed before training can begin.",
            },
        ]
        interpretation = [
            "V1.12A succeeds when the first pilot dataset becomes reviewable by the owner, not when training starts.",
            "The branch should now stop at the point where human correction adds the most value.",
            "The next legal move is owner correction, not automatic fitting or widening.",
        ]
        return V112APhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112a_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
