from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AIPhaseCharterReport:
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


class V112AIPhaseCharterAnalyzer:
    def analyze(
        self,
        *,
        label_draft_closure_payload: dict[str, Any],
        preservation_rule_payload: dict[str, Any],
    ) -> V112AIPhaseCharterReport:
        closure_summary = dict(label_draft_closure_payload.get("summary", {}))
        rule_summary = dict(preservation_rule_payload.get("summary", {}))
        if not bool(closure_summary.get("enter_v112ag_waiting_state_now")):
            raise ValueError("V1.12AI requires V1.12AG to be closed into waiting state.")
        if not bool(rule_summary.get("owner_review_must_apply_rule")):
            raise ValueError("V1.12AI requires the factor preservation rule to be active.")

        charter = {
            "phase_name": "V1.12AI CPO Label-Draft Integrity Owner Review",
            "mission": (
                "Review the bounded CPO label draft and classify each label into draft-ready, guarded-draft, "
                "review-only future target, or confirmed-only review language without silently dropping "
                "potentially useful structures."
            ),
            "in_scope": [
                "apply preservation-first review to all draft labels",
                "freeze owner dispositions for each draft label",
                "preserve provisional and confirmed splits where needed",
                "confirm that no label is silently deleted",
            ],
            "out_of_scope": [
                "formal label freeze",
                "formal training",
                "formal signal generation",
                "rewriting the label skeleton itself",
            ],
            "success_criteria": [
                "all draft labels are classified into bounded review tiers",
                "no label is dropped without explicit leakage or exact-duplicate justification",
                "guarded and confirmed-only labels remain fenced away from automatic training rights",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112ai_cpo_label_draft_integrity_owner_review",
            "ready_for_owner_review_next": True,
            "do_open_v112ai_now": True,
            "recommended_first_action": "freeze_v112ai_cpo_label_draft_integrity_owner_review_v1",
        }
        interpretation = [
            "V1.12AI is the owner review gate that converts the draft-integrity layer into a bounded disposition map.",
            "Preservation-first discipline applies: downgrade and archive are allowed; silent deletion is not.",
            "Training remains closed throughout this owner review.",
        ]
        return V112AIPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112ai_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AIPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
