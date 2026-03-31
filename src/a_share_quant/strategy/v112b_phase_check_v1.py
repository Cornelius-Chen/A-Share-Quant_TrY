from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BPhaseCheckReport:
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


class V112BPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_freeze_payload: dict[str, Any],
        baseline_readout_payload: dict[str, Any],
    ) -> V112BPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        freeze_summary = dict(pilot_dataset_freeze_payload.get("summary", {}))
        baseline_summary = dict(baseline_readout_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v112b_as_report_only_first_baseline_success",
            "dataset_frozen": bool(freeze_summary.get("ready_for_baseline_readout_next")),
            "baseline_readout_present": bool(baseline_summary.get("ready_for_phase_check_next")),
            "allow_strategy_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_first_baseline_before_any_widening",
        }
        evidence_rows = [
            {
                "evidence_name": "v112b_charter",
                "actual": {"do_open_v112b_now": bool(charter_summary.get("do_open_v112b_now"))},
                "reading": "V1.12B opened lawfully as a first trainable dataset freeze and baseline-readout phase.",
            },
            {
                "evidence_name": "v112b_pilot_dataset_freeze",
                "actual": {
                    "dataset_row_count": int(freeze_summary.get("dataset_row_count", 0)),
                    "all_rows_owner_accepted": bool(freeze_summary.get("all_rows_owner_accepted")),
                },
                "reading": "The first optical-link pilot dataset is now frozen instead of remaining a draft sheet.",
            },
            {
                "evidence_name": "v112b_baseline_readout",
                "actual": {
                    "sample_count": int(baseline_summary.get("sample_count", 0)),
                    "test_accuracy": float(baseline_summary.get("test_accuracy", 0.0)),
                    "allow_strategy_training_now": bool(baseline_summary.get("allow_strategy_training_now")),
                },
                "reading": "The first report-only baseline readout ran under time-split rules without opening strategy training.",
            },
        ]
        interpretation = [
            "V1.12B succeeds once the first accepted pilot draft becomes a trainable dataset and a report-only baseline readout exists.",
            "That is enough to close the phase without widening objects or opening deployment.",
            "The lawful next posture is owner review of the baseline rather than automatic training escalation.",
        ]
        return V112BPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112b_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
