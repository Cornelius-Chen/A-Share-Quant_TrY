from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12TrainingReadinessCheckReport:
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


class V12TrainingReadinessCheckAnalyzer:
    """Judge whether the bounded training pilot is ready to expand or should remain report-only."""

    def analyze(self, *, pilot_payload: dict[str, Any]) -> V12TrainingReadinessCheckReport:
        summary = dict(pilot_payload.get("summary", {}))
        sample_rows = list(pilot_payload.get("sample_rows", []))
        if not summary or not sample_rows:
            raise ValueError("Training pilot payload must contain summary and sample_rows.")

        class_labels = list(summary.get("class_labels", []))
        class_counts = {
            label: sum(1 for row in sample_rows if str(row.get("label")) == label)
            for label in class_labels
        }
        carry_rows = [row for row in sample_rows if str(row.get("label")) == "carry_row_present"]
        carry_signatures = {
            tuple((key, row.get(key)) for key in sorted(row) if key not in {"sample_id", "label"})
            for row in carry_rows
        }
        duplicate_carry_rows = len(carry_rows) - len(carry_signatures)
        sample_count = int(summary.get("sample_count", 0))
        perfect_micro_accuracy = float(summary.get("overall_accuracy", 0.0)) == 1.0
        smallest_class_count = min(class_counts.values()) if class_counts else 0
        class_balance_ratio = round(
            smallest_class_count / max(class_counts.values()), 4
        ) if class_counts else 0.0

        ready_for_next_bounded_model_work = (
            sample_count >= 15
            and smallest_class_count >= 3
            and duplicate_carry_rows == 0
        )
        acceptance_posture = (
            "keep_v12_training_branch_report_only_and_expand_samples_first"
            if not ready_for_next_bounded_model_work
            else "allow_next_bounded_model_work_after_readiness"
        )

        result_summary = {
            "acceptance_posture": acceptance_posture,
            "sample_count": sample_count,
            "class_counts": class_counts,
            "smallest_class_count": smallest_class_count,
            "class_balance_ratio": class_balance_ratio,
            "perfect_micro_accuracy_present": perfect_micro_accuracy,
            "carry_duplicate_row_count": duplicate_carry_rows,
            "carry_row_diversity_still_thin": len(carry_signatures) < 3,
            "ready_for_next_bounded_model_work": ready_for_next_bounded_model_work,
            "allow_strategy_training_now": False,
            "allow_news_branch_training_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "pilot_shape",
                "actual": {
                    "sample_count": sample_count,
                    "class_counts": class_counts,
                    "overall_accuracy": summary.get("overall_accuracy"),
                },
                "reading": "A perfect micro-pilot on a tiny sample can be useful evidence, but it is not enough on its own to justify a stronger model step.",
            },
            {
                "evidence_name": "carry_row_diversity",
                "actual": {
                    "carry_row_count": len(carry_rows),
                    "carry_duplicate_row_count": duplicate_carry_rows,
                    "distinct_carry_signatures": len(carry_signatures),
                },
                "reading": "If carry rows remain duplicated, the training branch still inherits the same row-diversity bottleneck as the carry factor lane.",
            },
            {
                "evidence_name": "branch_boundary",
                "actual": {
                    "ready_for_next_bounded_model_work": ready_for_next_bounded_model_work,
                    "allow_strategy_training_now": False,
                    "allow_news_branch_training_now": False,
                },
                "reading": "The right next step is bounded sample expansion or richer row diversity, not direct strategy ML or catalyst-news training.",
            },
        ]
        interpretation = [
            "The bounded training pilot succeeded as a structure-separation check, but success on 10 frozen samples is still too narrow to justify a larger model step.",
            "The main remaining weakness is the same one already visible in the carry lane: carry rows are still too few and too similar.",
            "So the correct posture is to keep training report-only, preserve strategy/news training as closed, and only revisit model expansion after more row diversity appears.",
        ]
        return V12TrainingReadinessCheckReport(
            summary=result_summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v12_training_readiness_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12TrainingReadinessCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
