from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ATPhaseCheckReport:
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


class V112ATPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        rerun_payload: dict[str, Any],
    ) -> V112ATPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        rerun_summary = dict(rerun_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112at_as_post_patch_rerun",
            "do_open_v112at_now": charter_summary.get("do_open_v112at_now"),
            "core_targets_stable_after_post_patch_rerun": rerun_summary.get("core_targets_stable_after_post_patch_rerun"),
            "guarded_targets_stable_after_post_patch_rerun": rerun_summary.get("guarded_targets_stable_after_post_patch_rerun"),
            "implementation_family_role_accuracy_drop": rerun_summary.get("implementation_family_role_accuracy_drop"),
            "allow_row_geometry_widen_now": rerun_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": rerun_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112at_rerun",
                "actual": {
                    "sample_count": rerun_summary.get("sample_count"),
                    "implementation_feature_count": rerun_summary.get("implementation_feature_count"),
                    "core_targets_stable_after_post_patch_rerun": rerun_summary.get("core_targets_stable_after_post_patch_rerun"),
                    "guarded_targets_stable_after_post_patch_rerun": rerun_summary.get("guarded_targets_stable_after_post_patch_rerun"),
                },
                "reading": "The post-patch rerun matters only if the patched implementation layer remains stable on the current truth rows.",
            }
        ]
        interpretation = [
            "V1.12AT should end by deciding whether current-row stability survives explicit board/calendar implementation backfill.",
            "Formal training and signal rights remain closed even if row-geometry widen becomes discussable.",
        ]
        return V112ATPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112at_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ATPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
