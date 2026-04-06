from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122VCpoStu1MinDownsideBridgeTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    authoritative_conclusion: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "authoritative_conclusion": self.authoritative_conclusion,
            "interpretation": self.interpretation,
        }


class V122VCpoStu1MinDownsideBridgeTriageAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122VCpoStu1MinDownsideBridgeTriageReport:
        v122s = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122s_cpo_1min_historical_bridge_overlap_audit_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v122t = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122t_cpo_1min_downside_same_plane_stack_audit_v1.json").read_text(
                encoding="utf-8"
            )
        )
        v122u = json.loads(
            (self.repo_root / "reports" / "analysis" / "v122u_cpo_1min_downside_attachment_stopline_v1.json").read_text(
                encoding="utf-8"
            )
        )

        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "classification": "keep_standalone_soft_component_only",
                "hard_reasons": [
                    "historical_bridge_invalid_because_overlap_zero",
                    "same_plane_stack_not_materially_better_than_base",
                    "attachment_would_be_decoration_not_increment",
                ],
            },
            {
                "reviewer": "Tesla",
                "classification": "keep_standalone_soft_component_only",
                "hard_reasons": [
                    "direct_bridge_closed_by_date_gap",
                    "same_plane_stack_degrades_q75_and_time_split",
                    "retain_only_the_standalone_1min_downside_component",
                ],
            },
            {
                "reviewer": "James",
                "classification": "keep_standalone_soft_component_only",
                "hard_reasons": [
                    "standalone_soft_component_survives_but_attachment_does_not",
                    "stack_has_no_clear_transfer_improvement",
                    "defer_until_historical_1min_exists",
                ],
            },
        ]

        authoritative_conclusion = {
            "branch_name": "recent_1min_downside_soft_component_bridge",
            "authoritative_status": "keep_standalone_soft_component_only",
            "direct_historical_bridge_allowed": False,
            "same_plane_attachment_allowed": False,
            "replay_facing_allowed": False,
            "shadow_replay_allowed": False,
            "majority_vote": {
                "keep_standalone_soft_component_only": 3,
            },
            "why_attachment_is_blocked": [
                "historical overlap count is zero",
                "same-plane stack improves discovery gap but worsens q75 BA and time-split mean",
                "stack does not provide clear transfer increment over base downside failure score",
            ],
            "next_posture": "retain_v122r_as_standalone_1min_downside_soft_component_and_wait_for_historical_1min_or_new_recent_increment",
        }

        summary = {
            "acceptance_posture": "freeze_v122v_cpo_stu_1min_downside_bridge_triage_v1",
            "related_runs": ["V122S", "V122T", "V122U"],
            "historical_overlap_day_count": v122s["summary"]["overlap_day_count"],
            "base_discovery_gap": v122t["summary"]["base_discovery_gap"],
            "stack_discovery_gap": v122t["summary"]["stack_discovery_gap"],
            "base_time_split_mean": v122t["summary"]["base_time_split_mean"],
            "stack_time_split_mean": v122t["summary"]["stack_time_split_mean"],
            "authoritative_status": "keep_standalone_soft_component_only",
            "replay_facing_allowed": False,
        }
        interpretation = [
            "V1.22V freezes the bridge decision for the recent 1-minute downside branch after overlap and same-plane stack audits.",
            "The branch itself stays alive only as the standalone soft component already accepted in V122R.",
            "What is blocked is not the component, but the temptation to attach it to the broader downside stack before the data actually supports that move.",
        ]
        return V122VCpoStu1MinDownsideBridgeTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            authoritative_conclusion=authoritative_conclusion,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122VCpoStu1MinDownsideBridgeTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122VCpoStu1MinDownsideBridgeTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122v_cpo_stu_1min_downside_bridge_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
