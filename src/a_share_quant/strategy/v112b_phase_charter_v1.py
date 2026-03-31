from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BPhaseCharterReport:
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


class V112BPhaseCharterAnalyzer:
    """Open the first trainable pilot-dataset freeze and baseline-readout phase."""

    def analyze(
        self,
        *,
        v112a_pilot_dataset_draft_payload: dict[str, Any],
    ) -> V112BPhaseCharterReport:
        draft_summary = dict(v112a_pilot_dataset_draft_payload.get("summary", {}))
        if int(draft_summary.get("dataset_row_count", 0)) != 3:
            raise ValueError("V1.12B requires a three-row unified pilot draft before opening.")

        charter = {
            "phase_name": "V1.12B First Trainable Pilot Dataset Freeze And Baseline Readout",
            "mission": (
                "Freeze the first owner-accepted three-object optical-link pilot dataset and run one "
                "report-only baseline readout under the existing V1.12 training protocol."
            ),
            "in_scope": [
                "freeze the owner-accepted pilot rows into a first trainable dataset",
                "assemble daily sample rows inside the accepted cycle windows",
                "run one bounded time-split baseline readout",
                "keep the result report-only and owner-reviewable",
            ],
            "out_of_scope": [
                "strategy integration",
                "intraday execution features",
                "retained-feature promotion",
                "black-box deployment",
                "automatic multi-object widening beyond the first three optical-link names",
            ],
            "success_criteria": [
                "the first trainable pilot dataset is frozen from the accepted three-symbol draft",
                "one bounded baseline readout runs successfully under time-split rules",
                "the output remains report-only and does not auto-open strategy training",
            ],
            "stop_criteria": [
                "cycle windows cannot be converted into a clean sample table",
                "the bounded baseline readout cannot run without breaking protocol rules",
                "the result would require strategy integration or widened object growth to stay alive",
            ],
            "handoff_condition": (
                "after the first baseline readout, return to owner review instead of auto-opening a wider "
                "training branch"
            ),
        }
        summary = {
            "acceptance_posture": "open_v112b_now_for_first_trainable_dataset_freeze_and_baseline",
            "owner_accepted_unified_cycle_draft": True,
            "pilot_object_count": 3,
            "do_open_v112b_now": True,
            "ready_for_dataset_freeze_next": True,
        }
        interpretation = [
            "V1.12B is not a strategy-training phase; it is the first lawful step from accepted draft data into a trainable pilot table.",
            "The phase remains bounded to the three optical-link pilot names and the existing V1.12 grammar.",
            "The correct close-out posture is owner review of the report-only readout, not automatic widening.",
        ]
        return V112BPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112b_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
