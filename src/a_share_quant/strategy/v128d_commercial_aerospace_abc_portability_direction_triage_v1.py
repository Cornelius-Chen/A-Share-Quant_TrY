from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128DCommercialAerospaceABCPortabilityDirectionTriageReport:
    summary: dict[str, Any]
    subagent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "subagent_rows": self.subagent_rows,
            "interpretation": self.interpretation,
        }


class V128DCommercialAerospaceABCPortabilityDirectionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.portability_path = repo_root / "reports" / "analysis" / "v128c_commercial_aerospace_current_primary_portability_audit_v1.json"

    def analyze(self) -> V128DCommercialAerospaceABCPortabilityDirectionTriageReport:
        portability = json.loads(self.portability_path.read_text(encoding="utf-8"))
        summary = {
            "acceptance_posture": "freeze_v128d_commercial_aerospace_abc_portability_direction_triage_v1",
            "current_primary_variant": portability["summary"]["current_primary_variant"],
            "main_window_delta_new_minus_old": portability["summary"]["main_window_delta_new_minus_old"],
            "post_window_delta_new_minus_old": portability["summary"]["post_window_delta_new_minus_old"],
            "portability_status": portability["summary"]["portability_status"],
            "authoritative_next_step": "main_window_deeper_downside_grammar",
            "secondary_followup": "post_window_tail_repair_if_main_window_branch_hits_stopline",
            "stop_doing": [
                "do_not_start_cross_board_migration_yet",
                "do_not_reopen_entry_side_aggression",
                "do_not_treat_post_window_tail_as_primary_problem_before_main_window_is_exhausted",
            ],
        }
        subagent_rows = [
            {
                "subagent": "Pauli",
                "vote": "B_post_window_tail_repair",
                "reason": "The main improvement is already concentrated in the main window, while the visible remaining weakness is the post-window giveback.",
            },
            {
                "subagent": "Tesla",
                "vote": "A_main_window_deeper_downside_grammar",
                "reason": "The main window still contains almost all of the economic edge, so the biggest remaining value is to improve downside execution there.",
            },
            {
                "subagent": "James",
                "vote": "C_cross_board_migration",
                "reason": "The board-level grammar may already be good enough to migrate, but this is a minority view against the current local optimization evidence.",
            },
        ]
        interpretation = [
            "V1.28D resolves the first post-portability direction split after the current commercial-aerospace primary was frozen and its edge decomposition was made explicit.",
            "The minority migration vote is acknowledged but not accepted because the current portability audit still shows the main economic edge living inside the main downside window.",
            "The authoritative next step stays inside commercial aerospace and targets deeper downside grammar in the main window, with tail repair reserved as the second line if that branch reaches stopline quickly.",
        ]
        return V128DCommercialAerospaceABCPortabilityDirectionTriageReport(
            summary=summary,
            subagent_rows=subagent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128DCommercialAerospaceABCPortabilityDirectionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128DCommercialAerospaceABCPortabilityDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128d_commercial_aerospace_abc_portability_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
