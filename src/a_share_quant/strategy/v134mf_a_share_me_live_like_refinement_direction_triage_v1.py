from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134me_a_share_live_like_gate_refinement_audit_v1 import (
    V134MEAShareLiveLikeGateRefinementAuditV1Analyzer,
)


@dataclass(slots=True)
class V134MFAShareMELiveLikeRefinementDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134MFAShareMELiveLikeRefinementDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134MFAShareMELiveLikeRefinementDirectionTriageV1Report:
        report = V134MEAShareLiveLikeGateRefinementAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "policy_bound_adapter_count": report.summary["policy_bound_adapter_count"],
            "materialized_live_like_view_count": report.summary["materialized_live_like_view_count"],
            "authoritative_status": "live_like_gate_refined_and_kept_blocked_until_selective_activation_and_execution_shift",
        }
        triage_rows = [
            {
                "component": "source_activation",
                "direction": "freeze_policy_bound_network_fetch_without_runtime_activation",
            },
            {
                "component": "next_frontier",
                "direction": "selective_network_activation_or_execution_binding_backlog_closure_before_live_like_promotion",
            },
        ]
        interpretation = [
            "The source-side live-like blocker is no longer a missing adapter gap; it is a controlled activation gate.",
            "That is a healthier stopline for future promotion decisions because the remaining blockers are explicit and narrower.",
        ]
        return V134MFAShareMELiveLikeRefinementDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MFAShareMELiveLikeRefinementDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MFAShareMELiveLikeRefinementDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mf_a_share_me_live_like_refinement_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
