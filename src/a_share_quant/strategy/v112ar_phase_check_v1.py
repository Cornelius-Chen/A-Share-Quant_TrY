from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ARPhaseCheckReport:
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


class V112ARPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        patch_spec_payload: dict[str, Any],
    ) -> V112ARPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        spec_summary = dict(patch_spec_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ar_as_bounded_feature_implementation_patch_spec_freeze",
            "do_open_v112ar_now": charter_summary.get("do_open_v112ar_now"),
            "total_patch_rule_count": spec_summary.get("total_patch_rule_count"),
            "next_lawful_move": spec_summary.get("next_lawful_move"),
            "allow_row_geometry_widen_now": spec_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112ar_patch_spec",
                "actual": {
                    "board_patch_rule_count": spec_summary.get("board_patch_rule_count"),
                    "calendar_patch_rule_count": spec_summary.get("calendar_patch_rule_count"),
                    "next_lawful_move": spec_summary.get("next_lawful_move"),
                },
                "reading": "The phase is successful only if the patch scope is frozen tightly enough to drive a bounded backfill next.",
            }
        ]
        interpretation = [
            "V1.12AR is not broad implementation. It is a bounded rule freeze.",
            "Row-geometry widen remains blocked after this phase.",
        ]
        return V112ARPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ar_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ARPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
