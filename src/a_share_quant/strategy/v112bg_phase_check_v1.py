from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BGPhaseCheckReport:
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


class V112BGPhaseCheckAnalyzer:
    def analyze(self, *, gap_review_payload: dict[str, Any]) -> V112BGPhaseCheckReport:
        summary_in = dict(gap_review_payload.get("summary", {}))
        if not bool(summary_in.get("open_neutral_selective_track_next")):
            raise ValueError("V1.12BG phase check requires an explicit neutral-track recommendation.")

        summary = {
            "acceptance_posture": "keep_v112bg_as_cpo_oracle_vs_no_leak_gap_review",
            "do_open_v112bg_now": True,
            "primary_gap_axis": str(summary_in.get("primary_gap_axis")),
            "recommended_probability_margin_floor": float(summary_in.get("recommended_probability_margin_floor", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bg_gap_review",
                "actual": {
                    "return_capture_ratio": summary_in.get("return_capture_ratio"),
                    "drawdown_penalty_vs_oracle": summary_in.get("drawdown_penalty_vs_oracle"),
                    "primary_gap_axis": summary_in.get("primary_gap_axis"),
                },
                "reading": "The review is only useful if it produces a concrete bottleneck attribution and a next-track gate stack.",
            }
        ]
        interpretation = [
            "V1.12BG is valid because it converts the oracle gap into a selective gate design problem rather than another round of generic feature wish-listing.",
        ]
        return V112BGPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bg_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BGPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
