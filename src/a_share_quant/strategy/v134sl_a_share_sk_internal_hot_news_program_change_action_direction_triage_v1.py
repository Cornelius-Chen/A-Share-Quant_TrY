from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sk_a_share_internal_hot_news_program_change_action_audit_v1 import (
    V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Report:
        report = V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "action_row_count": report.summary["action_row_count"],
            "top_risk_action": report.summary["top_risk_action"],
            "top_opportunity_action": report.summary["top_opportunity_action"],
            "global_program_action_mode": report.summary["global_program_action_mode"],
            "authoritative_status": "continue_serving_program_change_actions_above_snapshot_change_signal",
        }
        triage_rows = [
            {
                "component": "risk_branch",
                "direction": "treat_top_risk_action_as_the_default_guardrail_instruction_when_risk_and_opportunity_branches_conflict",
            },
            {
                "component": "opportunity_branch",
                "direction": "treat_top_opportunity_action_as_a_watchlist_or_rerank_instruction_not_as_a_direct_trade_opening",
            },
            {
                "component": "global_mode",
                "direction": "use_global_program_action_mode_as_the_first_switch_for_risk_first_opportunity_first_or_balanced_behavior",
            },
        ]
        interpretation = [
            "This is the first layer that explicitly tells the downstream consumer what kind of reaction is appropriate.",
            "It remains advisory and research-shadow only; it does not open execution authority.",
        ]
        return V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SLAShareSKInternalHotNewsProgramChangeActionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sl_a_share_sk_internal_hot_news_program_change_action_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
