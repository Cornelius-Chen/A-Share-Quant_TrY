from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ASPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ASPhaseCharterAnalyzer:
    def analyze(self, *, v112ar_phase_closure_payload: dict[str, Any]) -> V112ASPhaseCharterReport:
        closure_summary = dict(v112ar_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112ar_success_criteria_met")):
            raise ValueError("V1.12AS requires the completed V1.12AR closure check.")

        charter = {
            "phase_name": "V1.12AS CPO Bounded Implementation Backfill",
            "mission": (
                "Apply the frozen board/calendar implementation rules onto the current 7 truth rows "
                "without widening geometry or opening formal training."
            ),
            "in_scope": [
                "backfill bounded board-series columns on current truth rows",
                "backfill bounded calendar columns on current truth rows",
                "audit coverage and explicit placeholder usage",
            ],
            "out_of_scope": [
                "row-geometry widen",
                "formal training promotion",
                "formal signal generation",
                "full market-wide backfill",
            ],
            "success_criteria": [
                "all 6 frozen patch rules are applied to the current truth rows",
                "board and calendar coverage is explicit and auditable",
                "next lawful move is narrowed to a post-patch rerun or widen decision",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112as_cpo_bounded_implementation_backfill",
            "do_open_v112as_now": True,
            "recommended_first_action": "freeze_v112as_cpo_bounded_implementation_backfill_v1",
        }
        interpretation = [
            "V1.12AS does not broaden scope. It operationalizes the already-frozen patch rules on the current truth rows.",
            "This is the smallest lawful move before any post-patch rerun or geometry widen decision.",
        ]
        return V112ASPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112as_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ASPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
