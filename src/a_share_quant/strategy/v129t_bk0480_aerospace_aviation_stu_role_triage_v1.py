from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V129TBK0480AerospaceAviationSTURoleTriageReport:
    summary: dict[str, Any]
    direction_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "direction_rows": self.direction_rows,
            "interpretation": self.interpretation,
        }


class V129TBK0480AerospaceAviationSTURoleTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.role_grammar_path = repo_root / "reports" / "analysis" / "v129s_bk0480_aerospace_aviation_role_grammar_v1.json"
        self.transfer_triage_path = repo_root / "reports" / "analysis" / "v129r_bk0480_aerospace_aviation_transfer_worker_kickoff_triage_v1.json"

    def analyze(self) -> V129TBK0480AerospaceAviationSTURoleTriageReport:
        role_grammar = json.loads(self.role_grammar_path.read_text(encoding="utf-8"))
        transfer_triage = json.loads(self.transfer_triage_path.read_text(encoding="utf-8"))

        direction_rows = [
            {
                "direction": "dual_core_local_role_surface",
                "status": "freeze_as_authoritative_kickoff",
                "reason": "BK0480 currently has only two locally supported names, and both belong to the internal-owner surface.",
            },
            {
                "direction": "borrowed_confirmation_or_mirror_layers",
                "status": "blocked",
                "reason": "Commercial-aerospace confirmation and mirror layers are not allowed to leak into BK0480 at kickoff.",
            },
            {
                "direction": "next_phase",
                "status": role_grammar["summary"]["next_phase"],
                "reason": role_grammar["summary"]["recommended_next_posture"],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v129t_bk0480_aerospace_aviation_stu_role_triage_v1",
            "board_name": role_grammar["summary"]["board_name"],
            "sector_id": role_grammar["summary"]["sector_id"],
            "authoritative_status": "freeze_bk0480_dual_core_role_grammar_and_move_to_control_seed_extraction",
            "worker_status": transfer_triage["summary"]["authoritative_status"],
            "authoritative_rule": "bk0480_must_start_with_its_two_local_owners_only_and_expand_later_only_if_local_evidence_justifies_it",
        }
        interpretation = [
            "V1.29T freezes the BK0480 role grammar as a deliberately narrow dual-core starting point.",
            "The next lawful move is minimal control-seed extraction, not universe expansion or replay.",
        ]
        return V129TBK0480AerospaceAviationSTURoleTriageReport(
            summary=summary,
            direction_rows=direction_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V129TBK0480AerospaceAviationSTURoleTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V129TBK0480AerospaceAviationSTURoleTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129t_bk0480_aerospace_aviation_stu_role_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
