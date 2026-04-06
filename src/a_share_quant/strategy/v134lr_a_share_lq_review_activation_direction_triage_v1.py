from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lq_a_share_review_activation_audit_v1 import (
    V134LQAShareReviewActivationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LRAShareLQReviewActivationDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LRAShareLQReviewActivationDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LRAShareLQReviewActivationDirectionTriageV1Report:
        audit = V134LQAShareReviewActivationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "review_queues",
                "direction": "freeze_as_current_human_in_the_loop_surface",
            },
            {
                "component": "next_frontier",
                "direction": "shift_into_live_like_gate_readiness_audit_using_source_activation_review_and_governance_as_inputs",
            },
        ]
        summary = {
            "review_registry_count": audit.summary["review_registry_count"],
            "low_confidence_queue_count": audit.summary["low_confidence_queue_count"],
            "contradiction_queue_count": audit.summary["contradiction_queue_count"],
            "attention_soft_queue_count": audit.summary["attention_soft_queue_count"],
            "authoritative_status": "review_activation_complete_enough_to_freeze_and_shift_into_live_like_gate_readiness",
        }
        interpretation = [
            "The center now has an actual review layer rather than just the promise of one.",
            "The next honest question is no longer whether review exists, but whether the whole stack is ready to open any live-like gate at all.",
        ]
        return V134LRAShareLQReviewActivationDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LRAShareLQReviewActivationDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LRAShareLQReviewActivationDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lr_a_share_lq_review_activation_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
