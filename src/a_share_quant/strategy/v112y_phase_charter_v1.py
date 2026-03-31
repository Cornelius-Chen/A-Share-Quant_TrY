from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112YPhaseCharterReport:
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


class V112YPhaseCharterAnalyzer:
    def analyze(self, *, v112x_phase_closure_payload: dict[str, Any]) -> V112YPhaseCharterReport:
        closure_summary = dict(v112x_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112x_waiting_state_now")):
            raise ValueError("V1.12Y requires V1.12X to have lawfully closed.")

        charter = {
            "phase_name": "V1.12Y CPO Adjacent Role-Split Sidecar Probe",
            "mission": (
                "Use a bounded black-box sidecar posture to probe whether the unresolved adjacent CPO rows can be split "
                "into cleaner review-only role families without mistaking the probe result for training truth."
            ),
            "in_scope": [
                "probe only the nine unresolved adjacent rows left pending in V1.12R",
                "separate split-ready review assets from still-mixed pending rows",
                "freeze review-only sidecar scores and candidate role families",
            ],
            "out_of_scope": [
                "formal role freeze into training surface",
                "feature promotion",
                "signal generation",
                "new adjacent discovery",
                "cohort widening",
            ],
            "success_criteria": [
                "the unresolved adjacent set is no longer one undifferentiated pending bucket",
                "some rows can be preserved as split-ready review assets with explicit candidate roles",
                "still-mixed rows remain preserved without over-promotion",
            ],
            "stop_criteria": [
                "the phase promotes sidecar suggestions into formal training roles",
                "the phase silently discards the still-mixed adjacent rows",
                "the phase expands beyond the nine unresolved rows from V1.12R",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112y_cpo_adjacent_role_split_sidecar_probe",
            "do_open_v112y_now": True,
            "selected_archetype": "optical_link_price_and_demand_upcycle",
            "recommended_first_action": "freeze_v112y_cpo_adjacent_role_split_sidecar_probe_v1",
        }
        interpretation = [
            "V1.12Y attacks the last large unresolved adjacent-role gap in the CPO foundation line.",
            "Its purpose is bounded sidecar probing, not final role legislation.",
            "The result should split the adjacent pending bucket into cleaner review-only candidates and residual mixed rows.",
        ]
        return V112YPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112y_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112YPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
