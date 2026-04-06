from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BOCommercialAerospaceReduceClosureGovernanceSpecV1Report:
    summary: dict[str, Any]
    closure_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "closure_rows": self.closure_rows,
            "interpretation": self.interpretation,
        }


class V134BOCommercialAerospaceReduceClosureGovernanceSpecV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.expectancy_path = (
            repo_root / "reports" / "analysis" / "v134bm_commercial_aerospace_board_expectancy_supervision_audit_v1.json"
        )
        self.hierarchy_path = (
            repo_root / "reports" / "analysis" / "v134bi_commercial_aerospace_hierarchy_governance_spec_v1.json"
        )
        self.reentry_path = (
            repo_root / "reports" / "analysis" / "v134bc_commercial_aerospace_post_exit_reentry_ladder_audit_v1.json"
        )
        self.phase2_stack_path = (
            repo_root / "reports" / "analysis" / "v134aq_commercial_aerospace_phase2_current_shadow_stack_v4.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reduce_closure_governance_spec_v1.csv"
        )

    def analyze(self) -> V134BOCommercialAerospaceReduceClosureGovernanceSpecV1Report:
        expectancy = json.loads(self.expectancy_path.read_text(encoding="utf-8"))
        hierarchy = json.loads(self.hierarchy_path.read_text(encoding="utf-8"))
        reentry = json.loads(self.reentry_path.read_text(encoding="utf-8"))
        phase2_stack = json.loads(self.phase2_stack_path.read_text(encoding="utf-8"))

        closure_rows = [
            {
                "stage_order": 1,
                "stage_name": "intraday_sell_ladder",
                "state_driver": "mild / reversal / severe shadow supervision",
                "current_status": "phase2_shadow_reference_ready",
                "current_reference": phase2_stack["summary"]["current_phase2_wider_reference"],
                "governance_role": "detect and execute defensive sell-side shadow actions on same-day path",
                "blocking_reason": "not replay-facing",
            },
            {
                "stage_order": 2,
                "stage_name": "board_expectancy_gate",
                "state_driver": "lockout_worthy / false_bounce_only / unlock_worthy",
                "current_status": "supervision_ready",
                "current_reference": "v134bm_board_expectancy_supervision",
                "governance_role": "decide whether the board is worth touching at all on forward expectancy and reward-risk",
                "blocking_reason": "governance-only, no execution binding",
            },
            {
                "stage_order": 3,
                "stage_name": "board_lockout_unlock_hierarchy",
                "state_driver": "board_cooling_lockout > local_only_rebound_guard > board_revival_unlock",
                "current_status": "hierarchy_ready",
                "current_reference": "v134bi_hierarchy_governance_spec",
                "governance_role": "keep board-first precedence so local strength cannot override board weakness",
                "blocking_reason": "board unlock still governance-only",
            },
            {
                "stage_order": 4,
                "stage_name": "seed_reentry_ladder",
                "state_driver": "block -> observe -> rebuild watch -> later confirmation",
                "current_status": "seed_supervision_ready",
                "current_reference": f"{reentry['summary']['seed_count']} seed cases",
                "governance_role": "govern post-exit rebuild timing only after board-level vetoes no longer dominate",
                "blocking_reason": "no reentry simulator or replay lane",
            },
            {
                "stage_order": 5,
                "stage_name": "execution_binding",
                "state_driver": "unified reduce closure binding",
                "current_status": "still_blocked",
                "current_reference": "not available",
                "governance_role": "would bind sell-side, board gate, and reentry into one replay-facing lane",
                "blocking_reason": "intraday replay lane and reentry execution lane do not exist",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(closure_rows[0].keys()))
            writer.writeheader()
            writer.writerows(closure_rows)

        summary = {
            "acceptance_posture": "freeze_v134bo_commercial_aerospace_reduce_closure_governance_spec_v1",
            "closure_stage_count": len(closure_rows),
            "phase2_shadow_reference": phase2_stack["summary"]["current_phase2_wider_reference"],
            "expectancy_seed_count": expectancy["summary"]["seed_count"],
            "hierarchy_level_count": hierarchy["summary"]["hierarchy_level_count"],
            "reentry_seed_count": reentry["summary"]["seed_count"],
            "closure_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_reduce_closure_governance_spec_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34BO compresses the current branch into a single reduce closure stack: sell ladder first, board expectancy second, board hierarchy third, reentry ladder fourth, execution binding last.",
            "The point is not to pretend the branch is closed. The point is to show exactly where closure exists as governance and exactly where it still fails as execution.",
        ]
        return V134BOCommercialAerospaceReduceClosureGovernanceSpecV1Report(
            summary=summary,
            closure_rows=closure_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BOCommercialAerospaceReduceClosureGovernanceSpecV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BOCommercialAerospaceReduceClosureGovernanceSpecV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bo_commercial_aerospace_reduce_closure_governance_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
