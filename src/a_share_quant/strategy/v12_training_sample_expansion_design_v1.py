from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V12TrainingSampleExpansionDesignReport:
    summary: dict[str, Any]
    expansion_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "expansion_rows": self.expansion_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V12TrainingSampleExpansionDesignAnalyzer:
    """Decide where sample expansion should come from after the first bounded training pilot."""

    def analyze(
        self,
        *,
        readiness_payload: dict[str, Any],
        factor_protocol_payload: dict[str, Any],
        registry_payload: dict[str, Any],
    ) -> V12TrainingSampleExpansionDesignReport:
        readiness = dict(readiness_payload.get("summary", {}))
        factor_rows = list(factor_protocol_payload.get("factor_rows", []))
        registry_rows = list(registry_payload.get("registry_rows", []))

        class_counts = dict(readiness.get("class_counts", {}))
        opening_count = int(class_counts.get("opening_led", 0))
        persistence_count = int(class_counts.get("persistence_led", 0))
        carry_count = int(class_counts.get("carry_row_present", 0))

        evaluate_with_penalty = [
            row for row in factor_rows if str(row.get("evaluation_bucket")) == "evaluate_with_penalty"
        ]
        deferred_factors = [
            row for row in factor_rows if str(row.get("evaluation_bucket")) == "hold_for_more_sample"
        ]
        carry_registry_rows = [
            row for row in registry_rows if str(row.get("entry_name")) == "carry_in_basis_advantage"
        ]

        summary = {
            "design_posture": "freeze_v12_training_sample_expansion_design_v1",
            "opening_sample_sufficient_now": opening_count >= 5,
            "persistence_sample_still_thin": persistence_count < 3,
            "carry_sample_still_thin": carry_count < 3,
            "allow_relabelling_penalty_track_into_carry_class": False,
            "allow_relabelling_deferred_basis_track_into_carry_class": False,
            "recommended_expansion_source": "future_refresh_rows_not_relabelled_existing_candidates",
            "recommended_next_action": "expand_true_carry_rows_and_clean_persistence_rows_before_next_model_step",
            "ready_for_training_sample_manifest": True,
        }
        expansion_rows = [
            {
                "class_name": "opening_led",
                "current_count": opening_count,
                "posture": "hold_current_count",
                "reading": "Opening-led samples are no longer the main scarcity; the branch already has enough opening structure to avoid chasing more clones now.",
            },
            {
                "class_name": "persistence_led",
                "current_count": persistence_count,
                "posture": "expand_when_new_clean_persistence_rows_arrive",
                "reading": "Persistence remains thin, but the repo should only add new rows when they are acceptance-grade persistence cases rather than mixed hold examples.",
            },
            {
                "class_name": "carry_row_present",
                "current_count": carry_count,
                "posture": "primary_expansion_target",
                "reading": "Carry remains the primary scarcity and should be expanded using new true carry rows rather than broader opening clones.",
            },
            {
                "candidate_name": str(evaluate_with_penalty[0]["entry_name"]) if evaluate_with_penalty else None,
                "evaluation_bucket": "evaluate_with_penalty",
                "posture": "do_not_relabel_into_carry_training_class",
                "reading": "Penalty-track factors can help later, but opportunity-cost baggage makes them unsafe as direct carry-class substitutes in the current training pilot.",
            },
            {
                "candidate_name": str(deferred_factors[0]["entry_name"]) if deferred_factors else None,
                "evaluation_bucket": "hold_for_more_sample",
                "posture": "keep_deferred_until_repeated",
                "reading": "Thin basis candidates are useful for later row diversity, but should not be relabelled into the carry class until repeated evidence exists.",
            },
            {
                "candidate_name": str(carry_registry_rows[0]["entry_name"]) if carry_registry_rows else None,
                "registry_bucket": "candidate_factor",
                "posture": "expand_via_future_refresh_rows",
                "reading": "The current carry candidate should be strengthened by new rows from later refresh batches, not by collapsing neighboring factor families into the same class.",
            },
        ]
        interpretation = [
            "The next training-step bottleneck is not model choice; it is class expansion discipline.",
            "The repo should avoid cheating by relabelling preemptive or delayed basis examples as carry rows just to enlarge the class.",
            "So the right next move is to define a bounded training-sample manifest that asks for new true carry rows and clean persistence rows from future refresh work.",
        ]
        return V12TrainingSampleExpansionDesignReport(
            summary=summary,
            expansion_rows=expansion_rows,
            interpretation=interpretation,
        )


def write_v12_training_sample_expansion_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V12TrainingSampleExpansionDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
