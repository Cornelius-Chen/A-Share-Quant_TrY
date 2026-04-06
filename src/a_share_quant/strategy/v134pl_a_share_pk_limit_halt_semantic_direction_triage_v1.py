from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134pk_a_share_limit_halt_semantic_surface_audit_v1 import (
    V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134PLASharePKLimitHaltSemanticDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134PLASharePKLimitHaltSemanticDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134PLASharePKLimitHaltSemanticDirectionTriageV1Report:
        report = V134PKAShareLimitHaltSemanticSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "surface_row_count": report.summary["surface_row_count"],
            "missing_stk_limit_count": report.summary["missing_stk_limit_count"],
            "authoritative_status": "limit_halt_semantic_surface_materialized_for_replay_recheck",
        }
        triage_rows = [
            {
                "component": "semantic_surface",
                "direction": "use_limit_halt_semantic_surface_as_the_new_replay-facing_pair_layer",
            },
            {
                "component": "promotion_review",
                "direction": "rerun_daily_market_promotion_review_against_the_semantic_surface_before_claiming_replay_open",
            },
            {
                "component": "residual_policy",
                "direction": "keep_st_proxy_and_sparse_suspension_residuals_explicit_while_allowing_recheck",
            },
        ]
        interpretation = [
            "Replay can now be re-evaluated against a semantic limit-halt surface instead of the old bootstrap-only daily surface.",
            "This does not open execution, but it is sufficient to reopen promotion review and see whether the paired-surface blocker materially falls.",
        ]
        return V134PLASharePKLimitHaltSemanticDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PLASharePKLimitHaltSemanticDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PLASharePKLimitHaltSemanticDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pl_a_share_pk_limit_halt_semantic_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
