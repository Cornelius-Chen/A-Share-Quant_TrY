from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112XPhaseClosureCheckReport:
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


class V112XPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112XPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112x_as_spillover_sidecar_probe_success",
            "v112x_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112x_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112x_phase_check",
                "actual": {
                    "bounded_spillover_factor_candidate_count": phase_summary.get("bounded_spillover_factor_candidate_count"),
                    "weak_memory_only_row_count": phase_summary.get("weak_memory_only_row_count"),
                },
                "reading": "The spillover layer is now split between bounded factor candidates and weaker preserved memory.",
            }
        ]
        interpretation = [
            "V1.12X closes once the spillover-factor gap has an explicit bounded sidecar-backed candidacy judgment.",
            "The next step remains owner-level prioritization; no automatic training or feature action is opened.",
        ]
        return V112XPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112x_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112XPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
