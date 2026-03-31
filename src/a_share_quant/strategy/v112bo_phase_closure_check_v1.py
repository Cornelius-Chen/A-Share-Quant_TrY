from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BOPhaseClosureCheckReport:
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


class V112BOPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BOPhaseClosureCheckReport:
        if not bool(dict(phase_check_payload.get("summary", {})).get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BO closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bo_as_cpo_internal_maturity_overlay_review_success",
            "v112bo_success_criteria_met": True,
            "enter_v112bo_waiting_state_now": True,
            "formal_feature_promotion_now": False,
            "formal_label_promotion_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bo_phase_check",
                "actual": {
                    "overlay_feature_count": dict(phase_check_payload.get("summary", {})).get("overlay_feature_count"),
                },
                "reading": "The phase closes once internal maturity exists as a lawful overlay family distinct from market regime and core truth.",
            }
        ]
        interpretation = [
            "V1.12BO closes with the first explicit internal maturity overlay family for CPO.",
        ]
        return V112BOPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bo_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BOPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
