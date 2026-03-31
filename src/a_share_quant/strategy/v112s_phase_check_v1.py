from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112SPhaseCheckReport:
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


class V112SPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        chronology_payload: dict[str, Any],
    ) -> V112SPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        chronology_summary = dict(chronology_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112s_as_chronology_normalization_only",
            "do_open_v112s_now": charter_summary.get("do_open_v112s_now"),
            "chronology_segment_count": chronology_summary.get("chronology_segment_count"),
            "timing_gap_count": chronology_summary.get("timing_gap_count"),
            "normalized_calendar_anchor_count": chronology_summary.get("normalized_calendar_anchor_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "move_to_spillover_truth_check_next",
        }
        evidence_rows = [
            {
                "evidence_name": "chronology_normalization",
                "actual": {
                    "chronology_segment_count": chronology_summary.get("chronology_segment_count"),
                    "timing_gap_count": chronology_summary.get("timing_gap_count"),
                    "normalized_calendar_anchor_count": chronology_summary.get("normalized_calendar_anchor_count"),
                },
                "reading": "The CPO line now has explicit timing segments and lag categories instead of only flat event anchors.",
            }
        ]
        interpretation = [
            "V1.12S is a timing-structure pass, not a promotion pass.",
            "The next lawful move should be spillover truth-check, not training.",
        ]
        return V112SPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112s_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112SPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
