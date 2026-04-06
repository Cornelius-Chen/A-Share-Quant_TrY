from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.market.limit_halt.materialize_a_share_limit_halt_semantic_surface_v1 import (
    MaterializeAShareLimitHaltSemanticSurfaceV1,
)


@dataclass(slots=True)
class V134PKAShareLimitHaltSemanticSurfaceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_limit_halt_semantic_surface_status_v1.csv"

    def analyze(self) -> V134PKAShareLimitHaltSemanticSurfaceAuditV1Report:
        materialized = MaterializeAShareLimitHaltSemanticSurfaceV1(self.repo_root).materialize()
        summary = materialized.summary
        rows = [
            {
                "component": "limit_halt_semantic_surface",
                "component_state": "materialized_semantic_replay_surface",
                "artifact_path": summary["surface_path"],
                "coverage_note": f"surface_row_count = {summary['surface_row_count']}",
            },
            {
                "component": "semantic_residuals",
                "component_state": "materialized_named_residuals",
                "artifact_path": summary["residual_path"],
                "coverage_note": f"missing_stk_limit_count = {summary['missing_stk_limit_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        report_summary = {
            "surface_row_count": summary["surface_row_count"],
            "symbol_count": summary["symbol_count"],
            "coverage_start": summary["coverage_start"],
            "coverage_end": summary["coverage_end"],
            "st_proxy_row_count": summary["st_proxy_row_count"],
            "suspended_row_count": summary["suspended_row_count"],
            "missing_stk_limit_count": summary["missing_stk_limit_count"],
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_limit_halt_semantic_surface_ready_for_replay_recheck",
        }
        interpretation = [
            "The replay-facing limit-halt layer is no longer purely heuristic or source-missing; it is now a semantic surface built from retained side-input families.",
            "Residual uncertainty remains explicit, but replay can now be rechecked against a materially richer limit-halt context than the original 2024-only bootstrap surface.",
        ]
        return V134PKAShareLimitHaltSemanticSurfaceAuditV1Report(
            summary=report_summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PKAShareLimitHaltSemanticSurfaceAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pk_a_share_limit_halt_semantic_surface_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
