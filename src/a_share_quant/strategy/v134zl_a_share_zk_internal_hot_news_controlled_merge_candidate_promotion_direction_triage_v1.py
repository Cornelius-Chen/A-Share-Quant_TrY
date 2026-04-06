from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zk_a_share_internal_hot_news_controlled_merge_candidate_promotion_gate_audit_v1 import (
    V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Report:
        report = V134ZKAShareInternalHotNewsControlledMergeCandidatePromotionGateAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "hold_second_source_promotion_until_consumer_rotation_is_explicitly_accepted",
        }
        triage_rows = [
            {
                "component": "top_opportunity_rotation_gate",
                "direction": "keep promotion held when the candidate lane would rotate the top opportunity theme",
            },
            {
                "component": "top_watch_rotation_gate",
                "direction": "keep promotion held when the candidate lane would rotate the top symbol watch focus",
            },
            {
                "component": "promotion_decision",
                "direction": "promote only after explicit acceptance of the induced focus rotation rather than as a silent source merge",
            },
        ]
        interpretation = [
            "The merge decision has now been reduced to an explicit consumer-rotation gate.",
            "This keeps second-source expansion controlled and reversible.",
        ]
        return V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZLAShareZKInternalHotNewsControlledMergeCandidatePromotionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zl_a_share_zk_internal_hot_news_controlled_merge_candidate_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
