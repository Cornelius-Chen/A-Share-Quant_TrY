from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112MPhaseCheckReport:
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


class V112MPhaseCheckAnalyzer:
    def analyze(self, *, inner_draft_payload: dict[str, Any]) -> V112MPhaseCheckReport:
        draft_summary = dict(inner_draft_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112m_as_inner_draft_success",
            "preservable_review_only_inner_candidate_count": int(
                draft_summary.get("preservable_review_only_inner_candidate_count", 0)
            ),
            "unresolved_inner_residue_count": int(draft_summary.get("unresolved_inner_residue_count", 0)),
            "formal_label_split_now": bool(draft_summary.get("formal_label_split_now")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "preserve_inner_draft_for_owner_review_before_any_schema_change",
        }
        evidence_rows = [
            {
                "evidence_name": "v112m_mixed_stall_inner_draft",
                "actual": {
                    "preservable_review_only_inner_candidate_count": summary["preservable_review_only_inner_candidate_count"],
                    "unresolved_inner_residue_count": summary["unresolved_inner_residue_count"],
                    "formal_label_split_now": summary["formal_label_split_now"],
                },
                "reading": "V1.12M succeeds once the mixed stall cluster is reduced into bounded inner-draft pieces without formal relabeling.",
            }
        ]
        interpretation = [
            "V1.12M narrows one mixed cluster into smaller review-only pieces.",
            "The result is still drafting, not legislation.",
        ]
        return V112MPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112m_phase_check_report(*, reports_dir: Path, report_name: str, result: V112MPhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
