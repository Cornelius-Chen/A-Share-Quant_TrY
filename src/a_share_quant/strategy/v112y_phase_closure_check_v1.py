from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112YPhaseClosureCheckReport:
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


class V112YPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112YPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112y_as_adjacent_role_split_sidecar_probe_success",
            "v112y_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112y_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112y_phase_check",
                "actual": {
                    "split_ready_review_asset_count": phase_summary.get("split_ready_review_asset_count"),
                    "still_pending_row_count": phase_summary.get("still_pending_row_count"),
                },
                "reading": "The adjacent-role gap is now split between cleaner review assets and a smaller residual pending set.",
            }
        ]
        interpretation = [
            "V1.12Y closes once the unresolved adjacent rows have explicit sidecar-backed split suggestions.",
            "The next step remains owner-level prioritization; no automatic training or feature action is opened.",
        ]
        return V112YPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112y_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112YPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
