from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.market.limit_halt.materialize_a_share_limit_halt_foundation_v1 import (
    MaterializeAShareLimitHaltFoundationV1,
)


@dataclass(slots=True)
class V134LMAShareLimitHaltFoundationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134LMAShareLimitHaltFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_limit_halt_foundation_status_v1.csv"

    def analyze(self) -> V134LMAShareLimitHaltFoundationAuditV1Report:
        materialized = MaterializeAShareLimitHaltFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "limit_halt_surface",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["surface_path"],
                "coverage_note": f"surface_row_count = {summary['surface_row_count']}",
            },
            {
                "component": "limit_halt_residual_backlog",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"residual_count = {summary['residual_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "acceptance_posture": "build_v134lm_a_share_limit_halt_foundation_audit_v1",
            "surface_row_count": summary["surface_row_count"],
            "limit_up_hit_count": summary["limit_up_hit_count"],
            "limit_down_hit_count": summary["limit_down_hit_count"],
            "halt_or_suspend_count": summary["halt_or_suspend_count"],
            "residual_count": summary["residual_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_limit_halt_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "This closes the first limit-halt backlog with a transparent board-rule bootstrap surface rather than leaving market constraints implicit.",
            "The surface is useful for research and replay guardrails, while still explicitly carrying exchange-precision and intraday-state residual gaps.",
        ]
        return V134LMAShareLimitHaltFoundationAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LMAShareLimitHaltFoundationAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LMAShareLimitHaltFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lm_a_share_limit_halt_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
