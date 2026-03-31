from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113GPhaseCheckReport:
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


class V113GPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        study_scope_payload: dict[str, Any],
    ) -> V113GPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        scope_summary = dict(study_scope_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "keep_v113g_as_scope_freeze_only",
            "do_open_v113g_now": charter_summary.get("do_open_v113g_now"),
            "selected_archetype": charter_summary.get("selected_archetype"),
            "validated_local_seed_count": scope_summary.get("validated_local_seed_count"),
            "owner_named_candidate_count": scope_summary.get("owner_named_candidate_count"),
            "ready_for_phase_closure_next": True,
            "allow_auto_training_now": False,
            "allow_auto_label_freeze_now": False,
            "recommended_next_posture": "close_v113g_and_decide_whether_to_open_bounded_candidate_validation",
        }
        evidence_rows = [
            {
                "evidence_name": "study_scope",
                "actual": {
                    "validated_local_seed_count": scope_summary.get("validated_local_seed_count"),
                    "owner_named_candidate_count": scope_summary.get("owner_named_candidate_count"),
                    "bounded_study_dimension_count": scope_summary.get("bounded_study_dimension_count"),
                },
                "reading": "The commercial-space deep-study scope is now explicit and bounded rather than implicit owner intuition.",
            }
        ]
        interpretation = [
            "V1.13G succeeds once the high-value commercial-space study scope is frozen cleanly.",
            "This remains above label freeze and training.",
        ]
        return V113GPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v113g_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113GPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
