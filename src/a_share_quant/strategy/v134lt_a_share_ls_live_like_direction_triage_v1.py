from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ls_a_share_live_like_gate_readiness_audit_v1 import (
    V134LSAShareLiveLikeGateReadinessAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LTAShareLSLiveLikeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LTAShareLSLiveLikeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LTAShareLSLiveLikeDirectionTriageV1Report:
        audit = V134LSAShareLiveLikeGateReadinessAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "live_like_gate",
                "direction": "keep_closed",
            },
            {
                "component": "next_named_gaps",
                "direction": "close_source_manual_closure_boundary_residuals_and_replay_execution_stub_before_reopen",
            },
        ]
        summary = {
            "live_like_ready_now": audit.summary["live_like_ready_now"],
            "closed_gate_count": audit.summary["closed_gate_count"],
            "authoritative_status": "live_like_opening_still_blocked_by_named_prerequisites",
        }
        interpretation = [
            "The center is now mature enough to explain precisely why live-like is still closed.",
            "The remaining blockers are named infrastructure gaps, not confusion about research semantics.",
        ]
        return V134LTAShareLSLiveLikeDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LTAShareLSLiveLikeDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LTAShareLSLiveLikeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lt_a_share_ls_live_like_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
