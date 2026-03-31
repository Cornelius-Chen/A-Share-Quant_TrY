from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AICPOLabelDraftIntegrityOwnerReviewReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AICPOLabelDraftIntegrityOwnerReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        label_draft_payload: dict[str, Any],
        preservation_rule_payload: dict[str, Any],
    ) -> V112AICPOLabelDraftIntegrityOwnerReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        rule_summary = dict(preservation_rule_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_owner_review_next")):
            raise ValueError("V1.12AI requires an open owner review charter.")
        if not bool(rule_summary.get("silent_drop_forbidden")):
            raise ValueError("V1.12AI requires silent-drop prohibition.")

        review_rows: list[dict[str, Any]] = []
        draft_ready_count = 0
        guarded_count = 0
        review_only_future_count = 0
        confirmed_only_count = 0
        dropped_count = 0

        for row in label_draft_payload.get("family_support_matrix_rows", []):
            label_name = str(row.get("label_name", ""))
            support_posture = str(row.get("support_posture", ""))
            weak_support = list(row.get("weak_or_missing_support", []))

            if support_posture == "supported_now":
                owner_disposition = "preserve_as_draft_ready_label"
                reading = "This label is sufficiently supported to enter the later dataset draft as a bounded draft-ready label."
                draft_ready_count += 1
            elif support_posture in {
                "supported_with_provisional_guard",
                "supported_with_known_operational_gaps",
                "supported_with_overlay_boundary_guard",
            }:
                owner_disposition = "preserve_as_guarded_draft_label"
                reading = "This label may enter the later dataset draft only with its guard posture explicitly preserved."
                guarded_count += 1
            elif support_posture == "review_only_until_more_support":
                owner_disposition = "preserve_as_review_only_future_target"
                reading = "This label remains useful, but only as a future draft target until unresolved support gaps are reduced."
                review_only_future_count += 1
            elif support_posture == "confirmed_only_review_label":
                owner_disposition = "preserve_as_confirmed_only_review_label"
                reading = "This label remains valuable for review and explanation, but stays outside ex-ante draft truth."
                confirmed_only_count += 1
            else:
                owner_disposition = "preserve_as_unexpected_review_memory"
                reading = "Unexpected posture preserved conservatively under the no-easy-kill rule."

            review_rows.append(
                {
                    "label_name": label_name,
                    "support_posture": support_posture,
                    "owner_disposition": owner_disposition,
                    "weak_or_missing_support": weak_support,
                    "explicit_drop": False,
                    "reading": reading,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112ai_cpo_label_draft_integrity_owner_review_v1",
            "reviewed_label_count": len(review_rows),
            "draft_ready_label_count": draft_ready_count,
            "guarded_draft_label_count": guarded_count,
            "review_only_future_target_count": review_only_future_count,
            "confirmed_only_review_label_count": confirmed_only_count,
            "dropped_label_count": dropped_count,
            "formal_label_freeze_now": False,
            "formal_training_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "bounded_label_draft_dataset_assembly_with_ready_and_guarded_labels_only",
        }
        interpretation = [
            "This owner review does not try to make the draft cleaner than reality.",
            "The main success condition is that no potentially useful label is silently deleted.",
            "Only draft-ready and guarded labels should be allowed into the next bounded dataset assembly step.",
        ]
        return V112AICPOLabelDraftIntegrityOwnerReviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v112ai_cpo_label_draft_integrity_owner_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AICPOLabelDraftIntegrityOwnerReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
