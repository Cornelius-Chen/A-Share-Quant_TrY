from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AZPhaseCheckReport:
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


class V112AZPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        extension_payload: dict[str, Any],
    ) -> V112AZPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        extension_summary = dict(extension_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112az_as_bounded_training_layer_extension",
            "do_open_v112az_now": charter_summary.get("do_open_v112az_now"),
            "row_count_after_extension": extension_summary.get("row_count_after_extension"),
            "guarded_branch_row_count": extension_summary.get("guarded_branch_row_count"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": extension_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112az_training_layer_extension",
                "actual": {
                    "row_count_after_extension": extension_summary.get("row_count_after_extension"),
                    "guarded_branch_row_count": extension_summary.get("guarded_branch_row_count"),
                    "retained_review_only_branch_row_count": extension_summary.get("retained_review_only_branch_row_count"),
                },
                "reading": "The extension is only valid if it remains narrow: three guarded branch rows in, one mixed branch row out.",
            }
        ]
        interpretation = [
            "V1.12AZ is a bounded training-layer assembly step, not formal training.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AZPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112az_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AZPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
