from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lm_a_share_limit_halt_foundation_audit_v1 import (
    V134LMAShareLimitHaltFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LNAShareLMLimitHaltDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LNAShareLMLimitHaltDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LNAShareLMLimitHaltDirectionTriageV1Report:
        audit = V134LMAShareLimitHaltFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "limit_halt_surface",
                "direction": "freeze_as_current_market_constraint_surface",
            },
            {
                "component": "residual_backlog",
                "direction": "retain_for_future_exchange_precision_and_intraday_limit_state_enrichment",
            },
        ]
        summary = {
            "surface_row_count": audit.summary["surface_row_count"],
            "residual_count": audit.summary["residual_count"],
            "authoritative_status": "limit_halt_surface_complete_enough_to_freeze_as_bootstrap",
        }
        interpretation = [
            "Limit and halt information is now explicit in the information center instead of being a missing market side table.",
            "Future enrichment should improve precision and intraday state, not rebuild the surface from zero.",
        ]
        return V134LNAShareLMLimitHaltDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LNAShareLMLimitHaltDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LNAShareLMLimitHaltDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ln_a_share_lm_limit_halt_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
