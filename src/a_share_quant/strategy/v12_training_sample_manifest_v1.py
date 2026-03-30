from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12TrainingSampleManifestReport:
    summary: dict[str, Any]
    manifest_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "manifest_rows": self.manifest_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12TrainingSampleManifestAnalyzer:
    """Freeze the next bounded-sample request before any further training work."""

    def analyze(
        self,
        *,
        expansion_design_payload: dict[str, Any],
        readiness_payload: dict[str, Any],
    ) -> V12TrainingSampleManifestReport:
        design_summary = dict(expansion_design_payload.get("summary", {}))
        readiness_summary = dict(readiness_payload.get("summary", {}))
        class_counts = dict(readiness_summary.get("class_counts", {}))

        opening_count = int(class_counts.get("opening_led", 0))
        persistence_count = int(class_counts.get("persistence_led", 0))
        carry_count = int(class_counts.get("carry_row_present", 0))

        target_opening_count = opening_count
        target_persistence_count = max(4, persistence_count)
        target_carry_count = max(4, carry_count)

        manifest_rows = [
            {
                "class_name": "opening_led",
                "current_count": opening_count,
                "target_count": target_opening_count,
                "additional_rows_needed": max(0, target_opening_count - opening_count),
                "expansion_posture": "freeze_current_opening_count",
                "allowed_source": "none_required_now",
                "forbidden_source": "opening_clone_chasing",
            },
            {
                "class_name": "persistence_led",
                "current_count": persistence_count,
                "target_count": target_persistence_count,
                "additional_rows_needed": max(0, target_persistence_count - persistence_count),
                "expansion_posture": "add_only_clean_persistence_rows",
                "allowed_source": "future_refresh_acceptance_grade_persistence_rows",
                "forbidden_source": "mixed_hold_examples",
            },
            {
                "class_name": "carry_row_present",
                "current_count": carry_count,
                "target_count": target_carry_count,
                "additional_rows_needed": max(0, target_carry_count - carry_count),
                "expansion_posture": "primary_expansion_target",
                "allowed_source": "future_refresh_true_carry_rows",
                "forbidden_source": "relabelled_penalty_or_deferred_basis_rows",
            },
        ]

        summary = {
            "manifest_posture": "freeze_v12_training_sample_manifest_v1",
            "opening_count_frozen": True,
            "additional_opening_rows_needed": 0,
            "additional_persistence_rows_needed": max(0, target_persistence_count - persistence_count),
            "additional_carry_rows_needed": max(0, target_carry_count - carry_count),
            "allow_penalty_relabelling_into_carry": False,
            "allow_deferred_basis_relabelling_into_carry": False,
            "recommended_manifest_source": str(
                design_summary.get("recommended_expansion_source", "future_refresh_rows_not_relabelled_existing_candidates")
            ),
            "ready_for_future_refresh_binding": True,
        }
        interpretation = [
            "The next bounded training step should request only true carry rows and clean persistence rows.",
            "Opening-led rows are already sufficient for the current micro branch and should not be expanded further now.",
            "This manifest keeps the branch honest by preventing penalty-track or deferred basis rows from being relabelled into the carry class.",
        ]
        return V12TrainingSampleManifestReport(
            summary=summary,
            manifest_rows=manifest_rows,
            interpretation=interpretation,
        )


def write_v12_training_sample_manifest_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12TrainingSampleManifestReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
