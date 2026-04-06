from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pt_a_share_shadow_effective_trade_date_trial_audit_v1 import (
    V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Report:
        report = V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "baseline_missing_count": report.summary["baseline_missing_count"],
            "trial_missing_count": report.summary["trial_missing_count"],
            "trial_improvement_count": report.summary["trial_improvement_count"],
            "authoritative_status": "shadow_effective_trade_date_trial_is_directionally_useful_but_must_remain_shadow_only",
        }
        triage_rows = [
            {
                "component": "trial_result",
                "direction": "retain_the_trial_as_evidence_that_off_calendar_alignment_can_reduce_one_missing_context_row",
            },
            {
                "component": "scope_boundary",
                "direction": "keep_effective_trade_date_logic_in_shadow_only_scope_and_do_not_promote_it_into_pti_timestamp_history",
            },
            {
                "component": "next_move",
                "direction": "if_extended_further_build_a_shadow_only_corrected_binding_view_instead_of_mutating_the_base_binding_registry",
            },
        ]
        interpretation = [
            "The trial is useful because it converts the off-calendar slice into a bound date-level context under a shadow-only auxiliary query date.",
            "That is enough to justify a shadow-only corrected binding experiment, but not enough to rewrite the base PTI or execution-facing layers.",
        ]
        return V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pu_a_share_pt_shadow_effective_trade_date_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
