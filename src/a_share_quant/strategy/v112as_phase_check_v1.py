from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ASPhaseCheckReport:
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


class V112ASPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        backfill_payload: dict[str, Any],
    ) -> V112ASPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        backfill_summary = dict(backfill_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112as_as_bounded_implementation_backfill",
            "do_open_v112as_now": charter_summary.get("do_open_v112as_now"),
            "patch_rule_count_applied": backfill_summary.get("patch_rule_count_applied"),
            "board_backfill_coverage_ratio": backfill_summary.get("board_backfill_coverage_ratio"),
            "calendar_backfill_coverage_ratio": backfill_summary.get("calendar_backfill_coverage_ratio"),
            "allow_row_geometry_widen_now": backfill_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": backfill_summary.get("next_lawful_move"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112as_backfill",
                "actual": {
                    "patch_rule_count_applied": backfill_summary.get("patch_rule_count_applied"),
                    "sample_count": backfill_summary.get("sample_count"),
                    "next_lawful_move": backfill_summary.get("next_lawful_move"),
                },
                "reading": "The backfill phase is successful only if current truth rows now carry the frozen implementation layer explicitly.",
            }
        ]
        interpretation = [
            "V1.12AS should end with current-row implementation now explicit, not with immediate row widening.",
            "Formal training and signal rights remain closed.",
        ]
        return V112ASPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112as_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ASPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
