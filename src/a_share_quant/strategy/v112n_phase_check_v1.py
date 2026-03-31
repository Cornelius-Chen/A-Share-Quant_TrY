from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112NPhaseCheckReport:
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


class V112NPhaseCheckAnalyzer:
    def analyze(self, *, shadow_rerun_payload: dict[str, Any]) -> V112NPhaseCheckReport:
        rerun_summary = dict(shadow_rerun_payload.get("summary", {}))
        baseline_gain = bool(rerun_summary.get("baseline_shadow_incremental_gain_present"))
        gbdt_gain = bool(rerun_summary.get("gbdt_shadow_incremental_gain_present"))
        summary = {
            "acceptance_posture": "keep_v112n_as_shadow_rerun_complete",
            "baseline_shadow_incremental_gain_present": baseline_gain,
            "gbdt_shadow_incremental_gain_present": gbdt_gain,
            "net_incremental_gain_present": baseline_gain or gbdt_gain,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "treat_inner_draft_as_descriptive_until_further_evidence_if_no_gain",
        }
        evidence_rows = [
            {
                "evidence_name": "v112n_shadow_rerun",
                "actual": {
                    "baseline_shadow_test_accuracy": rerun_summary.get("baseline_shadow_test_accuracy"),
                    "baseline_v2_test_accuracy": rerun_summary.get("baseline_v2_test_accuracy"),
                    "gbdt_shadow_test_accuracy": rerun_summary.get("gbdt_shadow_test_accuracy"),
                    "gbdt_v2_test_accuracy": rerun_summary.get("gbdt_v2_test_accuracy"),
                },
                "reading": "V1.12N asks whether the inner-draft shadow features add any incremental predictive value on the frozen pilot.",
            }
        ]
        interpretation = [
            "V1.12N is a same-dataset review-only shadow rerun.",
            "Its main value is diagnostic: gain or no gain both clarify how to treat the inner draft.",
        ]
        return V112NPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112n_phase_check_report(*, reports_dir: Path, report_name: str, result: V112NPhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
