from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AYCPOGuardedBranchTrainingLayerReviewReport:
    summary: dict[str, Any]
    branch_layer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "branch_layer_rows": self.branch_layer_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AYCPOGuardedBranchTrainingLayerReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        branch_admission_payload: dict[str, Any],
        guarded_branch_pilot_payload: dict[str, Any],
    ) -> V112AYCPOGuardedBranchTrainingLayerReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ay_now")):
            raise ValueError("V1.12AY must be open before the review runs.")

        admission_rows = list(branch_admission_payload.get("branch_review_rows", []))
        pilot_summary = dict(guarded_branch_pilot_payload.get("summary", {}))

        branch_layer_rows: list[dict[str, Any]] = []
        for row in admission_rows:
            symbol = str(row.get("symbol"))
            admissible = bool(row.get("guarded_training_context_admissible"))
            layer_posture = "guarded_training_layer_row" if admissible else "review_only_branch_row"
            branch_layer_rows.append(
                {
                    "symbol": symbol,
                    "role_family": str(row.get("role_family")),
                    "active_stage_windows": list(row.get("active_stage_windows", [])),
                    "training_layer_posture": layer_posture,
                    "bounded_training_layer_admissible": admissible,
                    "reading": self._reading(symbol=symbol, admissible=admissible),
                }
            )

        admissible_rows = [row for row in branch_layer_rows if bool(row["bounded_training_layer_admissible"])]
        review_only_rows = [row for row in branch_layer_rows if not bool(row["bounded_training_layer_admissible"])]
        summary = {
            "acceptance_posture": "freeze_v112ay_cpo_guarded_branch_training_layer_review_v1",
            "branch_rows_reviewed": len(branch_layer_rows),
            "guarded_training_layer_admissible_count": len(admissible_rows),
            "branch_rows_retained_review_only_count": len(review_only_rows),
            "core_targets_stable_after_guarded_branch_admission": pilot_summary.get("core_targets_stable_after_guarded_branch_admission"),
            "guarded_targets_stable_after_guarded_branch_admission": pilot_summary.get("guarded_targets_stable_after_guarded_branch_admission"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "consider_extending_bounded_training_layer_with_guarded_branch_rows_only",
        }
        interpretation = [
            "V1.12AY does not open formal training; it only decides whether guarded branch rows may enter the next bounded training-facing layer.",
            "The branch layer remains split: three rows admissible, connector/MPO branch still review-only.",
        ]
        return V112AYCPOGuardedBranchTrainingLayerReviewReport(
            summary=summary,
            branch_layer_rows=branch_layer_rows,
            interpretation=interpretation,
        )

    def _reading(self, *, symbol: str, admissible: bool) -> str:
        if admissible:
            return "This row can enter the next bounded training-facing layer, but only under guarded posture."
        return "This row remains review-only because its branch behavior is still too mixed for training-layer use."


def write_v112ay_cpo_guarded_branch_training_layer_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AYCPOGuardedBranchTrainingLayerReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
