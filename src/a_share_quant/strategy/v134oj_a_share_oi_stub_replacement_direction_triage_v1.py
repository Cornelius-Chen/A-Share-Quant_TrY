from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134oi_a_share_shadow_execution_stub_replacement_precondition_audit_v1 import (
    V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134OJAShareOIStubReplacementDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134OJAShareOIStubReplacementDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134OJAShareOIStubReplacementDirectionTriageV1Report:
        report = V134OIAShareShadowExecutionStubReplacementPreconditionAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "precondition_count": report.summary["precondition_count"],
            "unsatisfied_count": report.summary["unsatisfied_count"],
            "promotable_now_count": report.summary["promotable_now_count"],
            "authoritative_status": "shadow_execution_stub_should_remain_until_market_context_closes_despite_replay_foundation_progress",
        }
        triage_rows = [
            {
                "component": "market_context",
                "direction": "treat_market_context_closure_as_first_real_requirement_for_stub_replacement",
            },
            {
                "component": "paired_surface_promotion",
                "direction": "treat_daily_market_promotion_and_pairing_as_foundation_ready_but_not_sufficient_without_market_context_closure",
            },
            {
                "component": "cost_model_foundation",
                "direction": "retain_cost_model_foundation_as_ready_but_nonpromotive_support_only",
            },
        ]
        interpretation = [
            "The correct next replay-internal move is not to redesign the execution journal stub.",
            "The stub should remain because market-context coverage is still open, even though replay promotion and pairing have materially advanced.",
        ]
        return V134OJAShareOIStubReplacementDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134OJAShareOIStubReplacementDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134OJAShareOIStubReplacementDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134oj_a_share_oi_stub_replacement_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
