from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112GPhaseClosureCheckReport:
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


class V112GPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
    ) -> V112GPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112g_as_semantic_v2_rerun_success",
            "v112g_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112g_waiting_state_now": True,
            "allow_auto_scope_widening_now": False,
            "recommended_next_posture": "preserve_v112g_delta_for_owner_review_before_any_label_split_or_dataset_growth",
        }
        evidence_rows = [
            {
                "evidence_name": "v112g_phase_check",
                "actual": {
                    "feature_schema_v2_present": bool(phase_summary.get("feature_schema_v2_present")),
                    "gbdt_v2_present": bool(phase_summary.get("gbdt_v2_present")),
                },
                "reading": "V1.12G closes once semantic v2 has been rerun through both baseline and GBDT on the same frozen dataset.",
            }
        ]
        interpretation = [
            "V1.12G is still a bounded rerun phase, not a deployment or scope-growth phase.",
            "The lawful next posture is waiting state until the owner judges whether the semantic delta justifies label refinement or further implementation.",
            "No automatic widening is allowed from this result.",
        ]
        return V112GPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112g_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112GPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
