from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BKPhaseClosureCheckReport:
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


class V112BKPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112BKPhaseClosureCheckReport:
        summary_in = dict(phase_check_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_closure_next")):
            raise ValueError("V1.12BK closure requires the completed phase check.")

        summary = {
            "acceptance_posture": "close_v112bk_as_cpo_tree_ranker_search_success",
            "v112bk_success_criteria_met": True,
            "enter_v112bk_waiting_state_now": True,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bk_phase_check",
                "actual": {
                    "best_variant_name": summary_in.get("best_variant_name"),
                    "best_variant_total_return": summary_in.get("best_variant_total_return"),
                    "best_variant_max_drawdown": summary_in.get("best_variant_max_drawdown"),
                },
                "reading": (
                    "The phase closes once the cheap tree/ranker search has a lawful report-only result and "
                    "the neutral comparison is preserved for owner review."
                ),
            }
        ]
        interpretation = [
            "V1.12BK closes with a bounded tree/ranker search that found a strong random-forest variant but still did not beat neutral on drawdown-guarded criteria.",
        ]
        return V112BKPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bk_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BKPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
