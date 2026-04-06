from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128NCommercialAerospaceMacroSupervisionTriageReport:
    summary: dict[str, Any]
    retained_rows: list[dict[str, Any]]
    blocked_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_rows": self.retained_rows,
            "blocked_rows": self.blocked_rows,
            "interpretation": self.interpretation,
        }


class V128NCommercialAerospaceMacroSupervisionTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128NCommercialAerospaceMacroSupervisionTriageReport:
        summary = {
            "acceptance_posture": "freeze_v128n_commercial_aerospace_macro_supervision_triage_v1",
            "current_primary_variant": "tail_weakdrift_full",
            "authoritative_rule": "macro_supervision_may_only_promote_items_that_can_be_rewritten_as_point_in_time_eod_governance_or_replay_controls",
            "next_direction": "time_chain_and_pre_open_event_governance_before_any_new_local_alpha_tuning",
        }
        retained_rows = [
            {
                "priority_rank": 1,
                "theme": "time_chain_audit",
                "status": "retain_for_translation",
                "why": "all sides agree signal date, execution date, and pre-open visibility should be separated more explicitly",
                "lawful_target": "signal_date_execution_date_preopen_event_triplet",
            },
            {
                "priority_rank": 2,
                "theme": "pre_open_decisive_event_veto",
                "status": "retain_for_translation",
                "why": "highest-value top-down governance gap that can still be point-in-time lawful",
                "lawful_target": "next_open veto if decisive continuation break or regulation risk is already public before open",
            },
            {
                "priority_rank": 3,
                "theme": "phase_state_machine",
                "status": "retain_for_translation",
                "why": "consensus says the next frontier is clearer phase/window-conditioned budgeting, not more local alpha discovery",
                "lawful_target": "preheat/probe/full-pre/full plus main-window and tail-window downside transitions",
            },
            {
                "priority_rank": 4,
                "theme": "portfolio_concentration_governance",
                "status": "retain_as_governance_overlay",
                "why": "board result is not single-name only, but still moderately concentrated",
                "lawful_target": "theme or cluster exposure budget audit",
            },
            {
                "priority_rank": 5,
                "theme": "failure_library",
                "status": "retain_as_supervision_layer",
                "why": "formally lawful but suspicious trades should be captured first as governance objects, then translated only after legality review",
                "lawful_target": "macro failure memo feeding later point-in-time audits",
            },
            {
                "priority_rank": 6,
                "theme": "portability_packaging",
                "status": "retain_as_next_stage",
                "why": "subagents consistently prefer packaging transferable grammar over more commercial-aerospace-local patching",
                "lawful_target": "cross-board shadow portability of methodology, not local semantics",
            },
        ]
        blocked_rows = [
            {
                "theme": "symbol_micro_tuning",
                "status": "blocked",
                "why": "this is now predominantly hindsight noise and was already at stopline in board-local audits",
            },
            {
                "theme": "more_aggressive_entry_variants",
                "status": "blocked",
                "why": "current macro supervision agrees the missing value is governance and downside handling, not hotter entry",
            },
            {
                "theme": "hindsight_event_storytelling",
                "status": "blocked",
                "why": "only strictly timestamped pre-open visible events may return to lawful execution; narrative expansion stays explanatory only",
            },
        ]
        interpretation = [
            "V1.28N freezes the macro-supervision consensus after combining the local supervision memo with three subagent critiques.",
            "The result is a governance queue: improve time-chain transparency and pre-open decisive-event veto first, and stop board-local micro-tuning.",
        ]
        return V128NCommercialAerospaceMacroSupervisionTriageReport(
            summary=summary,
            retained_rows=retained_rows,
            blocked_rows=blocked_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128NCommercialAerospaceMacroSupervisionTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128NCommercialAerospaceMacroSupervisionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128n_commercial_aerospace_macro_supervision_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
