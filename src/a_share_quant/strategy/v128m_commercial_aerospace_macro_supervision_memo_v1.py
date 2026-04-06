from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128MCommercialAerospaceMacroSupervisionMemoReport:
    summary: dict[str, Any]
    priority_rows: list[dict[str, Any]]
    stop_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "priority_rows": self.priority_rows,
            "stop_rows": self.stop_rows,
            "interpretation": self.interpretation,
        }


class V128MCommercialAerospaceMacroSupervisionMemoAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V128MCommercialAerospaceMacroSupervisionMemoReport:
        summary = {
            "acceptance_posture": "freeze_v128m_commercial_aerospace_macro_supervision_memo_v1",
            "current_primary_variant": "tail_weakdrift_full",
            "current_primary_final_equity": 1309426.5555,
            "current_primary_max_drawdown": 0.09309927,
            "macro_supervision_rule": "macro_supervision_may_flag_structural_governance_improvements_but_must_not_directly_leak_future_information_into_lawful_training_or_replay",
        }
        priority_rows = [
            {
                "priority_rank": 1,
                "theme": "time_chain_audit",
                "problem": "chart and trade interpretation can confuse signal date with execution date, especially around decisive news or regulation days",
                "why_it_matters": "a formally lawful trade can still look suspicious unless signal date, execution date, and pre-open event visibility are separated",
                "lawful_translation_candidate": "add signal_date / execution_date / pre_open_event_state triplet to all replay audit surfaces",
            },
            {
                "priority_rank": 2,
                "theme": "pre_open_decisive_event_veto",
                "problem": "current replay may carry prior-day EOD eligibility into next-open execution even when a decisive continuation break or regulation signal is visible before the open",
                "why_it_matters": "this is a top-down governance gap, not a local alpha gap",
                "lawful_translation_candidate": "introduce pre-open decisive-event veto layer using only already-public events before open",
            },
            {
                "priority_rank": 3,
                "theme": "phase_granularity_upgrade",
                "problem": "probe/full is still too coarse for A-share thematic preheat sequences",
                "why_it_matters": "the system currently proves preheat matters, but lacks a lawful middle intensity layer",
                "lawful_translation_candidate": "rebuild participation ladder as probe / full-pre / full instead of binary probe/full only",
            },
            {
                "priority_rank": 4,
                "theme": "board_heat_dual_surface",
                "problem": "control-core board overlay alone misses sentiment-leadership distortion and concept spillover",
                "why_it_matters": "theme runs often fail when sentiment breadth diverges from control-core breadth",
                "lawful_translation_candidate": "maintain secondary heat surfaces for confirmation layer and sentiment-leadership layer as governance overlays, not action authority",
            },
            {
                "priority_rank": 5,
                "theme": "portfolio_concentration_governance",
                "problem": "current primary is not single-name fragile, but economic improvement remains moderately concentrated",
                "why_it_matters": "board-level success can still hide cluster overexposure",
                "lawful_translation_candidate": "add cluster or theme-concentration budget audits before more local alpha tuning",
            },
            {
                "priority_rank": 6,
                "theme": "failure_library",
                "problem": "formally lawful but economically suspicious trades are not yet turned into a structured error library",
                "why_it_matters": "these failures are high-signal supervision objects even when they cannot be immediately translated into training labels",
                "lawful_translation_candidate": "maintain a macro-supervision failure library and only promote items that survive point-in-time legality review",
            },
        ]
        stop_rows = [
            {
                "stop_theme": "more_local_entry_alpha",
                "reason": "commercial-aerospace board-local micro-tuning has already reached stopline after multiple promotions",
            },
            {
                "stop_theme": "intraday_execution_reopen_now",
                "reason": "intraday legality, point-in-time event visibility, and historical minute support are still incomplete; reopening now would destabilize the frozen EOD stack",
            },
            {
                "stop_theme": "cross_board_rule_copying",
                "reason": "portable methodology is ready, but local chronology and theme archetype must not be copied as if they were generic rules",
            },
        ]
        interpretation = [
            "V1.28M is a macro-supervision memo, not a new lawful alpha family.",
            "Its role is to flag structural governance improvements that may later be translated back into point-in-time legal replay controls after separate leakage review.",
        ]
        return V128MCommercialAerospaceMacroSupervisionMemoReport(
            summary=summary,
            priority_rows=priority_rows,
            stop_rows=stop_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128MCommercialAerospaceMacroSupervisionMemoReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128MCommercialAerospaceMacroSupervisionMemoAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128m_commercial_aerospace_macro_supervision_memo_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
