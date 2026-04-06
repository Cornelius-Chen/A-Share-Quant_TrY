from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pi_a_share_limit_halt_side_input_availability_audit_v1 import (
    V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PJASharePILimitHaltSideInputDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PJASharePILimitHaltSideInputDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PJASharePILimitHaltSideInputDirectionTriageV1Report:
        report = V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "retained_family_count": report.summary["retained_family_count"],
            "authoritative_status": "limit_halt_side_input_families_are_now_present_but_require_semantic_materialization",
        }
        triage_rows = [
            {
                "component": "board_and_price_band",
                "direction": "treat_board_identity_and_stk_limit_as_available_foundation_inputs",
            },
            {
                "component": "st_and_suspension",
                "direction": "treat_namechange_and_suspend_d_as_sparse_semantic_inputs_to_be_materialized_not_ignored",
            },
            {
                "component": "next_step",
                "direction": "build_a_replay-facing_limit_halt_semantic_surface_instead_of_searching_for_more_raw_feeds",
            },
        ]
        interpretation = [
            "The replay blocker has narrowed again: it is no longer source-family absence, but semantic unification across retained side-input families.",
            "The next valid move is to materialize a usable limit-halt semantic surface from board, stk_limit, namechange, and suspend_d.",
        ]
        return V134PJASharePILimitHaltSideInputDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PJASharePILimitHaltSideInputDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PJASharePILimitHaltSideInputDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pj_a_share_pi_limit_halt_side_input_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
