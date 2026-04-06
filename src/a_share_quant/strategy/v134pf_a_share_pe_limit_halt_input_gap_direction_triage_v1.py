from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pe_a_share_limit_halt_derivation_input_gap_audit_v1 import (
    V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PFASharePELimitHaltInputGapDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PFASharePELimitHaltInputGapDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PFASharePELimitHaltInputGapDirectionTriageV1Report:
        report = V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "missing_direct_field_count": report.summary["missing_direct_field_count"],
            "semantic_dependency_field_count": report.summary["semantic_dependency_field_count"],
            "authoritative_status": "limit_halt_derivation_requires_semantic_side_inputs_not_more_price_only_raw",
        }
        triage_rows = [
            {
                "component": "price_math",
                "direction": "treat_price_only_raw_as_sufficient_for_hit_math_but_not_for_complete_limit_halt_semantics",
            },
            {
                "component": "semantic_side_inputs",
                "direction": "add_board_st_and_suspension_side_inputs_before_attempting_limit_halt_materialization",
            },
            {
                "component": "replay_promotion",
                "direction": "keep_replay_promotion_blocked_until_semantic_side_inputs_close_the_limit_halt_gap",
            },
        ]
        interpretation = [
            "The next replay-side move is not another price-data expansion loop.",
            "It is a semantic-side-input closure problem: board classification, ST status, and suspension linkage must be supplied before limit-halt derivation can be promoted.",
        ]
        return V134PFASharePELimitHaltInputGapDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PFASharePELimitHaltInputGapDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PFASharePELimitHaltInputGapDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pf_a_share_pe_limit_halt_input_gap_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
