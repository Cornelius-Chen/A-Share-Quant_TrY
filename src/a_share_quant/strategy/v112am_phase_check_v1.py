from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AMPhaseCheckReport:
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


class V112AMPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        training_pilot_payload: dict[str, Any],
    ) -> V112AMPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pilot_summary = dict(training_pilot_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112am_as_extremely_small_core_skeleton_training_pilot",
            "do_open_v112am_now": charter_summary.get("do_open_v112am_now"),
            "sample_count": pilot_summary.get("sample_count"),
            "target_count": pilot_summary.get("target_count"),
            "model_count": pilot_summary.get("model_count"),
            "best_target_by_gbdt_gain": pilot_summary.get("best_target_by_gbdt_gain"),
            "best_target_gain": pilot_summary.get("best_target_gain"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": pilot_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112am_core_skeleton_training_pilot",
                "actual": {
                    "sample_count": pilot_summary.get("sample_count"),
                    "target_count": pilot_summary.get("target_count"),
                    "best_target_by_gbdt_gain": pilot_summary.get("best_target_by_gbdt_gain"),
                    "best_target_gain": pilot_summary.get("best_target_gain"),
                },
                "reading": "The project now has a real bounded failure-exposure experiment instead of another purely pre-pilot audit.",
            }
        ]
        interpretation = [
            "V1.12AM succeeds if it exposes learnability and limits without pretending to be a broad training launch.",
            "Formal training and signal generation remain closed.",
        ]
        return V112AMPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112am_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AMPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
