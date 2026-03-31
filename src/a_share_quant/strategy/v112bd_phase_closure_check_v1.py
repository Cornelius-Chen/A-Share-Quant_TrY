from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BDPhaseClosureCheckReport:
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


class V112BDPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BDPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112bd_as_market_regime_overlay_feature_review_success",
            "v112bd_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112bd_waiting_state_now": True,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bd_phase_check",
                "actual": {
                    "overlay_feature_count": phase_summary.get("overlay_feature_count"),
                },
                "reading": "The phase closes once the market-regime overlay family is frozen as a context layer.",
            }
        ]
        interpretation = [
            "V1.12BD closes with an explicit market-regime overlay feature family.",
            "Formal signal rights remain closed.",
        ]
        return V112BDPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bd_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BDPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
