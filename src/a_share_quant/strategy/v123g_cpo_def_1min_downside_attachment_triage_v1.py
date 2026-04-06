from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V123GCpoDef1MinDownsideAttachmentTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V123GCpoDef1MinDownsideAttachmentTriageAnalyzer:
    def analyze(self) -> V123GCpoDef1MinDownsideAttachmentTriageReport:
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "keep_attachment_blocked",
                "reason": "no_q75_uplift_and_symbol_min_worsens",
                "recommended_next_step": "retain_both_recent_1min_downside_lines_as_detached_soft_components_only",
            },
            {
                "reviewer": "Tesla",
                "verdict": "keep_attachment_blocked",
                "reason": "same_plane_blend_creates_no_material_transfer_increment",
                "recommended_next_step": "stop_same_plane_blending_and_wait_for_new_orthogonal_branch",
            },
            {
                "reviewer": "James",
                "verdict": "keep_attachment_blocked",
                "reason": "blend_only_shuffles_metrics_without_clean_robustness_gain",
                "recommended_next_step": "retain_gap_exhaustion_stall_as_standalone_soft_component_only",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v123g_cpo_def_1min_downside_attachment_triage_v1",
            "related_runs": ["V123D", "V123E", "V123F"],
            "authoritative_status": "keep_attachment_blocked",
            "majority_vote": {"keep_attachment_blocked": 3},
            "same_plane_attachment_allowed": False,
            "replay_facing_allowed": False,
            "next_posture": "freeze_recent_1min_downside_branches_as_detached_soft_components_and_stop_same_plane_blending",
        }
        interpretation = [
            "V1.23G freezes the same-plane attachment decision for the recent 1-minute downside branches.",
            "The orthogonal branch is worth keeping, but not worth attaching, because the blend failed to produce material non-replay increment over the best standalone reference.",
            "The correct posture is to keep both recent 1-minute downside branches detached and stop same-plane blend tuning.",
        ]
        return V123GCpoDef1MinDownsideAttachmentTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123GCpoDef1MinDownsideAttachmentTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123GCpoDef1MinDownsideAttachmentTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123g_cpo_def_1min_downside_attachment_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

