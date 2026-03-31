from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ATPhaseCharterReport:
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


class V112ATPhaseCharterAnalyzer:
    def analyze(self, *, v112as_phase_closure_payload: dict[str, Any]) -> V112ATPhaseCharterReport:
        closure_summary = dict(v112as_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112as_success_criteria_met")):
            raise ValueError("V1.12AT requires the completed V1.12AS closure check.")

        charter = {
            "phase_name": "V1.12AT CPO Post-Patch Rerun",
            "mission": (
                "Rerun the current truth-row pilot with patched board/calendar implementation features "
                "before any row-geometry widen."
            ),
            "in_scope": [
                "reuse the same 7 truth rows",
                "reuse the same core and guarded target stack from V1.12AP",
                "add bounded board/calendar implementation features from V1.12AS",
                "compare current rerun behavior against V1.12AP",
            ],
            "out_of_scope": [
                "row-geometry widen",
                "formal training promotion",
                "formal signal generation",
            ],
            "success_criteria": [
                "the patched rerun remains stable on the current truth rows",
                "implementation-layer effect becomes explicit rather than merely assumed",
                "the next lawful move narrows to either row-geometry widen or another bounded patch",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112at_cpo_post_patch_rerun",
            "do_open_v112at_now": True,
            "recommended_first_action": "freeze_v112at_cpo_post_patch_rerun_v1",
        }
        interpretation = [
            "V1.12AT is a rerun phase, not another readiness review.",
            "The project now tests the effect of implementation backfill on the existing truth geometry.",
        ]
        return V112ATPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112at_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ATPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
