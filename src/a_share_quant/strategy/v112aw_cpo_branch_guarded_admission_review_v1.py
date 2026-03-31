from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AWCPOBranchGuardedAdmissionReviewReport:
    summary: dict[str, Any]
    branch_review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "branch_review_rows": self.branch_review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AWCPOBranchGuardedAdmissionReviewAnalyzer:
    GUARDED_ADMIT_SYMBOLS = {"688498", "688313", "300757"}
    RETAIN_REVIEW_ONLY_SYMBOLS = {"300570"}

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        widen_payload: dict[str, Any],
        branch_patch_payload: dict[str, Any],
        dataset_assembly_payload: dict[str, Any],
    ) -> V112AWCPOBranchGuardedAdmissionReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112aw_now")):
            raise ValueError("V1.12AW must be open before the admission review runs.")

        widen_summary = dict(widen_payload.get("summary", {}))
        patch_summary = dict(branch_patch_payload.get("summary", {}))
        if not bool(patch_summary.get("core_targets_stable_after_branch_patch")):
            raise ValueError("Branch admission review requires stable core targets after the branch patch.")

        dataset_rows = {
            str(row.get("symbol")): row for row in list(dataset_assembly_payload.get("dataset_draft_rows", []))
        }
        widened_rows = list(widen_payload.get("widened_row_rows", []))

        branch_review_rows: list[dict[str, Any]] = []
        for row in widened_rows:
            symbol = str(row.get("symbol"))
            dataset_row = dict(dataset_rows[symbol])
            recommended_posture = self._recommended_posture(symbol=symbol)
            branch_review_rows.append(
                {
                    "symbol": symbol,
                    "role_family": str(row.get("role_family")),
                    "active_stage_windows": list(row.get("active_stage_windows", [])),
                    "dataset_posture_before_review": str(dataset_row.get("dataset_posture")),
                    "recommended_posture_after_review": recommended_posture,
                    "guarded_training_context_admissible": recommended_posture == "guarded_training_context_row",
                    "reading": self._reading(symbol=symbol),
                }
            )

        guarded_rows = [row for row in branch_review_rows if bool(row["guarded_training_context_admissible"])]
        retained_review_rows = [row for row in branch_review_rows if not bool(row["guarded_training_context_admissible"])]
        summary = {
            "acceptance_posture": "freeze_v112aw_cpo_branch_guarded_admission_review_v1",
            "branch_rows_under_review": len(branch_review_rows),
            "guarded_training_context_admissible_count": len(guarded_rows),
            "retained_review_only_count": len(retained_review_rows),
            "core_targets_stable_after_branch_patch": patch_summary.get("core_targets_stable_after_branch_patch"),
            "guarded_targets_stable_after_branch_patch": patch_summary.get("guarded_targets_stable_after_branch_patch"),
            "role_state_patch_gain": patch_summary.get("role_state_patch_gain"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "run_guarded_branch_admitted_pilot_before_any_broader_row_widen",
        }
        interpretation = [
            "V1.12AW does not promote all branch rows at once; it uses the patch evidence to make a narrower guarded-admission split.",
            "Rows admitted here move only into a guarded training-facing context, not into formal training rights.",
            "The connector/MPO branch remains review-only because its late-cycle and diffusion overlap is still structurally mixed.",
        ]
        return V112AWCPOBranchGuardedAdmissionReviewReport(
            summary=summary,
            branch_review_rows=branch_review_rows,
            interpretation=interpretation,
        )

    def _recommended_posture(self, *, symbol: str) -> str:
        if symbol in self.GUARDED_ADMIT_SYMBOLS:
            return "guarded_training_context_row"
        if symbol in self.RETAIN_REVIEW_ONLY_SYMBOLS:
            return "review_support_context_row"
        raise ValueError(f"Unexpected branch symbol: {symbol}")

    def _reading(self, *, symbol: str) -> str:
        if symbol == "300570":
            return (
                "Retain as review-only because connector/MPO branch behavior still overlaps diffusion and "
                "late-cycle catch-up, which makes guarded truth usage too mixed for now."
            )
        if symbol in {"688498", "688313"}:
            return (
                "Promote into guarded training context because the branch patch restored role geometry and these "
                "rows stay concentrated in re-ignition/major-markup windows."
            )
        if symbol == "300757":
            return (
                "Promote into guarded training context because packaging/process enabler now binds cleanly enough "
                "to the strengthened branch role geometry."
            )
        raise ValueError(symbol)


def write_v112aw_cpo_branch_guarded_admission_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AWCPOBranchGuardedAdmissionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
