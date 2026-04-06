from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zu_a_share_internal_hot_news_accepted_rotation_primary_consumer_promotion_plan_audit_v1 import (
    V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Report:
        report = V134ZUAShareInternalHotNewsAcceptedRotationPrimaryConsumerPromotionPlanAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "primary_consumer_promotion_requires_explicit_manual_acceptance_before_any_focus_rotation_is_applied",
        }
        triage_rows = [
            {
                "component": "acceptance_gate",
                "direction": "do not promote while promotion_gate_state remains hold and the p1 rotation has not been explicitly accepted",
            },
            {
                "component": "promotion_sequence",
                "direction": "promote snapshot first, then control packet, then rebaseline change signals in order",
            },
            {
                "component": "discipline_boundary",
                "direction": "keep all accepted-state artifacts in shadow form until the manual acceptance step is complete",
            },
        ]
        interpretation = [
            "The merge problem is now reduced to a human acceptance decision followed by a bounded rollout sequence.",
            "No silent primary-consumer mutation is needed or allowed before that decision.",
        ]
        return V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZVAShareZUInternalHotNewsAcceptedRotationPrimaryConsumerPromotionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zv_a_share_zu_internal_hot_news_accepted_rotation_primary_consumer_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
