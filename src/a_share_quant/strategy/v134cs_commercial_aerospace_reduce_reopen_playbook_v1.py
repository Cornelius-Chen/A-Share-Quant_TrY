from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CSCommercialAerospaceReduceReopenPlaybookV1Report:
    summary: dict[str, Any]
    playbook_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "playbook_rows": self.playbook_rows,
            "interpretation": self.interpretation,
        }


class V134CSCommercialAerospaceReduceReopenPlaybookV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        analysis_dir = repo_root / "reports" / "analysis"
        self.residue_path = analysis_dir / "v134ck_commercial_aerospace_cj_local_rebound_direction_triage_v1.json"
        self.blocker_path = analysis_dir / "v134bq_commercial_aerospace_reduce_execution_binding_blocker_audit_v1.json"
        self.output_csv = repo_root / "data" / "training" / "commercial_aerospace_reduce_reopen_playbook_v1.csv"

    def analyze(self) -> V134CSCommercialAerospaceReduceReopenPlaybookV1Report:
        residue = json.loads(self.residue_path.read_text(encoding="utf-8"))
        blockers = json.loads(self.blocker_path.read_text(encoding="utf-8"))

        playbook_rows = [
            {
                "reopen_scope": "local_residue_supervision",
                "trigger": "one_of_the_four_residue_cases_requires_local_refresh",
                "allowed_action": "rerun_local_case_supervision_only",
            },
            {
                "reopen_scope": "sell_side_execution_binding",
                "trigger": "one_or_more_execution_blockers_change_state",
                "allowed_action": "reassess_binding_surfaces_without_reopening_broad_reduce_semantics",
            },
            {
                "reopen_scope": "broad_reduce_semantics",
                "trigger": "not_allowed_without_new_board_local_context",
                "allowed_action": "keep_frozen",
            },
            {
                "reopen_scope": "next_frontier_handoff",
                "trigger": "explicit_program_shift_to_intraday_add",
                "allowed_action": "start_intraday_add_as_new_frontier_while_preserving_reduce_freeze",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(playbook_rows[0].keys()))
            writer.writeheader()
            writer.writerows(playbook_rows)

        summary = {
            "acceptance_posture": "freeze_v134cs_commercial_aerospace_reduce_reopen_playbook_v1",
            "residue_seed_count": residue["summary"]["residue_seed_count"],
            "execution_blocker_count": blockers["summary"]["full_reduce_binding_blocker_count"],
            "authoritative_output": "commercial_aerospace_reduce_reopen_playbook_ready_for_gate_driven_restart",
            "playbook_csv": str(self.output_csv.relative_to(self.repo_root)),
        }
        interpretation = [
            "V1.34CS converts the frozen reduce branch into a practical reopen playbook.",
            "The branch may reopen locally for residue maintenance or for changed execution infrastructure, but not for broad semantic wandering.",
        ]
        return V134CSCommercialAerospaceReduceReopenPlaybookV1Report(
            summary=summary,
            playbook_rows=playbook_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CSCommercialAerospaceReduceReopenPlaybookV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CSCommercialAerospaceReduceReopenPlaybookV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cs_commercial_aerospace_reduce_reopen_playbook_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
