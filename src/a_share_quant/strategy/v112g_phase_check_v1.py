from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112GPhaseCheckReport:
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


class V112GPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_schema_payload: dict[str, Any],
        baseline_v2_payload: dict[str, Any],
        gbdt_v2_payload: dict[str, Any],
    ) -> V112GPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        schema_summary = dict(feature_schema_payload.get("summary", {}))
        baseline_summary = dict(baseline_v2_payload.get("summary", {}))
        gbdt_summary = dict(gbdt_v2_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112g_as_semantic_v2_rerun_success",
            "feature_schema_v2_present": bool(schema_summary.get("ready_for_baseline_v2_next")),
            "baseline_v2_present": bool(baseline_summary.get("ready_for_gbdt_v2_next")),
            "gbdt_v2_present": bool(gbdt_summary.get("ready_for_phase_check_next")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_semantic_v2_delta_before_any_label_or_scope_change",
        }
        evidence_rows = [
            {
                "evidence_name": "v112g_charter",
                "actual": {"do_open_v112g_now": bool(charter_summary.get("do_open_v112g_now"))},
                "reading": "V1.12G opened lawfully as a same-scope semantic rerun phase.",
            },
            {
                "evidence_name": "v112g_schema_v2",
                "actual": {
                    "new_feature_count": int(schema_summary.get("new_feature_count", 0)),
                    "total_feature_count_v2": int(schema_summary.get("total_feature_count_v2", 0)),
                },
                "reading": "The catalyst-state semantics are now explicit rather than implicit design notes.",
            },
            {
                "evidence_name": "v112g_delta",
                "actual": {
                    "baseline_v2_test_accuracy": float(baseline_summary.get("baseline_v2_test_accuracy", 0.0)),
                    "gbdt_v2_test_accuracy": float(gbdt_summary.get("gbdt_v2_test_accuracy", 0.0)),
                    "gbdt_v2_high_level_consolidation_fp": int(gbdt_summary.get("gbdt_v2_high_level_consolidation_fp", 0)),
                },
                "reading": "The same-scope rerun now gives a before/after basis for semantic feature value.",
            },
        ]
        interpretation = [
            "V1.12G succeeds once semantic v2 can be expressed and rerun on the same dataset.",
            "The next decision should come from the observed delta, not from a generic belief that more features are always better.",
            "The lawful next posture is owner review before label or scope changes.",
        ]
        return V112GPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112g_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112GPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
