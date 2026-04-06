from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BICommercialAerospaceHierarchyGovernanceSpecV1Report:
    summary: dict[str, Any]
    hierarchy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "hierarchy_rows": self.hierarchy_rows,
            "interpretation": self.interpretation,
        }


class V134BICommercialAerospaceHierarchyGovernanceSpecV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.lockout_path = (
            repo_root / "reports" / "analysis" / "v134be_commercial_aerospace_board_cooling_lockout_audit_v1.json"
        )
        self.unlock_path = (
            repo_root / "reports" / "analysis" / "v134bg_commercial_aerospace_board_revival_unlock_audit_v1.json"
        )
        self.reentry_ladder_path = (
            repo_root / "reports" / "analysis" / "v134bc_commercial_aerospace_post_exit_reentry_ladder_audit_v1.json"
        )
        self.local_rebound_path = (
            repo_root / "reports" / "analysis" / "v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_hierarchy_governance_spec_v1.csv"
        )

    def analyze(self) -> V134BICommercialAerospaceHierarchyGovernanceSpecV1Report:
        lockout = json.loads(self.lockout_path.read_text(encoding="utf-8"))
        unlock = json.loads(self.unlock_path.read_text(encoding="utf-8"))
        reentry = json.loads(self.reentry_ladder_path.read_text(encoding="utf-8"))
        local_rebound = json.loads(self.local_rebound_path.read_text(encoding="utf-8"))

        hierarchy_rows = [
            {
                "precedence": 1,
                "state_name": "board_cooling_lockout",
                "state_role": "top_level_veto",
                "activation_condition": "board drawdown plus persistent weak-drift/risk-off cluster after full window",
                "release_condition": "only board_revival_unlock_seed may discuss release",
                "subordinate_effect": "seed-level reentry ladder remains subordinate while lockout is active",
            },
            {
                "precedence": 2,
                "state_name": "local_only_rebound_guard",
                "state_role": "anti_false_bounce_guard",
                "activation_condition": (
                    "few-stock rebound under lockout with concentrated top-symbol forward strength but insufficient board breadth"
                ),
                "release_condition": "none; it is negative evidence that supports keeping lockout active",
                "subordinate_effect": "blocks treating isolated strong names as board revival",
            },
            {
                "precedence": 3,
                "state_name": "board_revival_unlock",
                "state_role": "lockout_release_guard",
                "activation_condition": "probe_plus_full_count >= 6, full_count >= 2, de_risk_count = 0",
                "release_condition": "governance-only release discussion; still no execution binding",
                "subordinate_effect": "only after this guard turns favorable does seed-level rebuild discussion recover meaning",
            },
            {
                "precedence": 4,
                "state_name": "seed_reentry_ladder",
                "state_role": "symbol_level_rebuild_supervision",
                "activation_condition": "board unlock supervision no longer vetoes rebuild discussion",
                "release_condition": "n/a",
                "subordinate_effect": "governs block -> observe -> rebuild watch -> later confirmation at seed level",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(hierarchy_rows[0].keys()))
            writer.writeheader()
            writer.writerows(hierarchy_rows)

        summary = {
            "acceptance_posture": "freeze_v134bi_commercial_aerospace_hierarchy_governance_spec_v1",
            "hierarchy_level_count": len(hierarchy_rows),
            "lockout_seed_count": len(lockout["seed_rows"]),
            "local_only_rebound_seed_count": len(local_rebound["seed_rows"]),
            "unlock_positive_seed_count": len(unlock["positive_seed_rows"]),
            "reentry_seed_count": len(reentry["seed_rows"]),
            "hierarchy_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_hierarchy_governance_spec_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BI formalizes the stack the branch has been converging toward: board lockout first, anti-false-bounce local rebound guard second, board unlock third, seed reentry ladder last.",
            "This makes the user's intuition explicit: a few strong names can exist inside a weak board, but they cannot release a board-level cooling lockout on their own.",
        ]
        return V134BICommercialAerospaceHierarchyGovernanceSpecV1Report(
            summary=summary,
            hierarchy_rows=hierarchy_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BICommercialAerospaceHierarchyGovernanceSpecV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BICommercialAerospaceHierarchyGovernanceSpecV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bi_commercial_aerospace_hierarchy_governance_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
