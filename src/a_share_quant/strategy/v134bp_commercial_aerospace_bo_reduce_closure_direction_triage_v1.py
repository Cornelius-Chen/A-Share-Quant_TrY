from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134BPCommercialAerospaceBOReduceClosureDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134BPCommercialAerospaceBOReduceClosureDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.spec_path = (
            repo_root / "reports" / "analysis" / "v134bo_commercial_aerospace_reduce_closure_governance_spec_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_bo_reduce_closure_direction_triage_v1.csv"
        )

    def analyze(self) -> V134BPCommercialAerospaceBOReduceClosureDirectionTriageV1Report:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        triage_rows = [
            {
                "component": "sell_side_phase2_shadow",
                "status": "retained_as_strong_governance",
                "detail": "Intraday sell-side shadow ladder is already the strongest completed reduce component.",
            },
            {
                "component": "board_expectancy_gate",
                "status": "promoted_to_board_level_reduce_context",
                "detail": "Board-level reduce should now be discussed in expectancy / reward-risk terms, not shape-only terms.",
            },
            {
                "component": "board_lockout_unlock_hierarchy",
                "status": "retained_as_upper_governance",
                "detail": "Lockout and unlock remain above local rebound and symbol-level rebuild discussion.",
            },
            {
                "component": "reentry_ladder",
                "status": "retained_but_subordinate",
                "detail": "Reentry remains seed-level supervision and only becomes relevant after board-level vetoes relax.",
            },
            {
                "component": "execution_binding",
                "status": "true_remaining_gap",
                "detail": "The branch is not fully closed because execution-facing binding across sell / lockout / unlock / reentry does not exist yet.",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(triage_rows[0].keys()))
            writer.writeheader()
            writer.writerows(triage_rows)

        summary = {
            "acceptance_posture": "freeze_v134bp_commercial_aerospace_bo_reduce_closure_direction_triage_v1",
            "authoritative_status": "freeze_reduce_closure_governance_and_continue_board_first_reduce_training",
            "closure_stage_count": spec["summary"]["closure_stage_count"],
            "triage_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34BP turns the closure spec into a direction judgment.",
            "The branch has now mostly solved reduce as governance and supervision; what remains unsolved is execution binding, not conceptual structure.",
        ]
        return V134BPCommercialAerospaceBOReduceClosureDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134BPCommercialAerospaceBOReduceClosureDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134BPCommercialAerospaceBOReduceClosureDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bp_commercial_aerospace_bo_reduce_closure_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
