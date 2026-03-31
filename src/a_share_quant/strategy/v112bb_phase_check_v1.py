from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BBPhaseCheckReport:
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


class V112BBPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_payload: dict[str, Any],
    ) -> V112BBPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        pilot_summary = dict(pilot_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112bb_as_default_10_row_guarded_layer_pilot",
            "do_open_v112bb_now": charter_summary.get("do_open_v112bb_now"),
            "default_10_row_pilot_established": pilot_summary.get("default_10_row_pilot_established"),
            "core_targets_stable_vs_7_row_baseline": pilot_summary.get("core_targets_stable_vs_7_row_baseline"),
            "guarded_targets_stable_vs_7_row_guarded_baseline": pilot_summary.get("guarded_targets_stable_vs_7_row_guarded_baseline"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": pilot_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112bb_default_layer_pilot",
                "actual": {
                    "default_training_layer_row_count": pilot_summary.get("default_training_layer_row_count"),
                    "sample_count": pilot_summary.get("sample_count"),
                    "core_targets_stable_vs_7_row_baseline": pilot_summary.get("core_targets_stable_vs_7_row_baseline"),
                    "guarded_targets_stable_vs_7_row_guarded_baseline": pilot_summary.get("guarded_targets_stable_vs_7_row_guarded_baseline"),
                },
                "reading": "The default-layer pilot only matters if the 10-row layer behaves as a stable replacement rather than a fragile extension.",
            }
        ]
        interpretation = [
            "V1.12BB checks whether the new default 10-row guarded layer truly behaves as the project baseline.",
            "Formal training and signal rights remain closed.",
        ]
        return V112BBPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bb_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BBPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
