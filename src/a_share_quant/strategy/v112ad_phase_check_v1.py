from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ADPhaseCheckReport:
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


class V112ADPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        feature_review_payload: dict[str, Any],
    ) -> V112ADPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(feature_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112ad_as_review_only_dynamic_role_transition_layer",
            "do_open_v112ad_now": charter_summary.get("do_open_v112ad_now"),
            "transition_event_count": review_summary.get("transition_event_count"),
            "dynamic_feature_count": review_summary.get("dynamic_feature_count"),
            "role_change_is_time_conditioned": review_summary.get("role_change_is_time_conditioned"),
            "allow_auto_feature_promotion_now": False,
            "allow_auto_label_freeze_now": False,
            "allow_auto_training_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_then_bounded_label_draft_assembly_or_feature-family-design",
        }
        evidence_rows = [
            {
                "evidence_name": "v112ad_dynamic_role_transition_feature_review",
                "actual": {
                    "transition_event_count": review_summary.get("transition_event_count"),
                    "dynamic_feature_count": review_summary.get("dynamic_feature_count"),
                    "role_change_is_time_conditioned": review_summary.get("role_change_is_time_conditioned"),
                },
                "reading": "Role migration is now explicit and bounded, but still review-only.",
            }
        ]
        interpretation = [
            "V1.12AD succeeds if dynamic role change becomes explicit without being legislated as formal truth.",
            "Feature promotion, label freeze, and training remain closed.",
        ]
        return V112ADPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112ad_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ADPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
