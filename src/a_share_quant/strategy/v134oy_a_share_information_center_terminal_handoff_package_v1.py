from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134qs_a_share_runtime_scheduler_governance_opening_review_audit_v1 import (
    V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class V134OYAShareInformationCenterTerminalHandoffPackageV1Report:
    summary: dict[str, Any]
    handoff_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "handoff_rows": self.handoff_rows,
            "interpretation": self.interpretation,
        }


class V134OYAShareInformationCenterTerminalHandoffPackageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.build_status_path = (
            repo_root / "reports" / "analysis" / "v134os_a_share_information_center_build_completion_status_card_v1.json"
        )
        self.source_checklist_path = (
            repo_root / "reports" / "analysis" / "v134qm_a_share_runtime_scheduler_activation_checklist_audit_v1.json"
        )
        self.replay_checklist_path = (
            repo_root / "reports" / "analysis" / "v134ny_a_share_replay_promotion_latest_status_card_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_information_center_terminal_handoff_package_v1.csv"
        )

    def analyze(self) -> V134OYAShareInformationCenterTerminalHandoffPackageV1Report:
        build_status = _read_json(self.build_status_path)["summary"]
        source_checklist = _read_json(self.source_checklist_path)["summary"]
        opening_review = V134QSAShareRuntimeSchedulerGovernanceOpeningReviewAuditV1Analyzer(self.repo_root).analyze()
        replay_status = _read_json(self.replay_checklist_path)
        replay_promotable_now_count = 0
        replay_shadow_eligible_subset_count = 15
        for row in replay_status["rows"]:
            if row["replay_component"] == "daily_market_promotion":
                replay_promotable_now_count = int(row["decisive_metric"].split("=")[1].strip())

        handoff_rows = [
            {
                "handoff_component": "information_center_core",
                "handoff_state": "build_complete_enough",
                "next_real_world_mode": "freeze_internal_build_and_keep_core_as_system_of_truth",
                "decisive_metric": f"foundation_complete_count = {build_status['foundation_complete_count']}",
            },
            {
                "handoff_component": "source_internal_manual",
                "handoff_state": "single_runtime_scheduler_governance_opening_followthrough_lane",
                "next_real_world_mode": "retain_completed prework and continue only through scheduler activation then governance re-audit for html-article fetch",
                "decisive_metric": (
                    f"pending_step_count = {source_checklist['pending_step_count']}; "
                    f"governance_closed_count = {opening_review.summary['governance_closed_count']}"
                ),
            },
            {
                "handoff_component": "replay_promotion_lane",
                "handoff_state": "shadow_execution_eligible_subset_controlled_recheck_lane",
                "next_real_world_mode": "continue_from_the_15_row_shadow_execution_eligible_subset_and_retain_the_2_boundary_exclusions",
                "decisive_metric": f"eligible_subset_count = {replay_shadow_eligible_subset_count}",
            },
            {
                "handoff_component": "live_like_execution",
                "handoff_state": "retain_blocked",
                "next_real_world_mode": "do_not_open_before_source_manual_and_replay_internal_build_preconditions_move",
                "decisive_metric": f"global_blocker_count = {build_status['global_blocker_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(handoff_rows[0].keys()))
            writer.writeheader()
            writer.writerows(handoff_rows)

        summary = {
            "handoff_component_count": len(handoff_rows),
            "foundation_complete_count": build_status["foundation_complete_count"],
            "source_pending_step_count": source_checklist["pending_step_count"],
            "replay_promotable_now_count": replay_promotable_now_count,
            "replay_shadow_eligible_subset_count": replay_shadow_eligible_subset_count,
            "artifact_path": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_status": "information_center_internal_build_terminal_handoff_materialized",
        }
        interpretation = [
            "The information center should now be handled as a completed internal build with two remaining real-world lanes: source-side scheduler followthrough for the html-article lane and replay-side controlled recheck from a 15-row shadow-execution eligible subset.",
            "Further internal registry expansion would now be drift unless new external source movement or completed manual review changes the state surface.",
        ]
        return V134OYAShareInformationCenterTerminalHandoffPackageV1Report(
            summary=summary,
            handoff_rows=handoff_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OYAShareInformationCenterTerminalHandoffPackageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OYAShareInformationCenterTerminalHandoffPackageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oy_a_share_information_center_terminal_handoff_package_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
