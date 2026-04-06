from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135ak_a_share_internal_hot_news_challenger_primary_consumer_promotion_plan_audit_v1 import (
    V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer,
)


@dataclass(slots=True)
class V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Report:
        report = V135AKAShareInternalHotNewsChallengerPrimaryConsumerPromotionPlanAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "rotation_review_state": report.summary["rotation_review_state"],
            "challenger_top_opportunity_theme": report.summary["challenger_top_opportunity_theme"],
            "challenger_top_watch_symbol": report.summary["challenger_top_watch_symbol"],
            "shadow_change_signal_priority": report.summary["shadow_change_signal_priority"],
            "plan_state": report.summary["plan_state"],
            "authoritative_status": "challenger_primary_consumer_promotion_plan_materialized",
        }
        triage_rows = [
            {
                "component": "challenger_rotation_gate",
                "direction": "treat the open challenger review as permission to prepare rollout artifacts, not as permission to silently replace the current primary consumer chain.",
            },
            {
                "component": "challenger_shadow_promotion",
                "direction": "use the challenger shadow packet as the exact handoff state if manual acceptance is granted.",
            },
            {
                "component": "post_promotion_hygiene",
                "direction": "rebaseline symbol-watch and top-level control change signals immediately after any challenger promotion to avoid stale p1 deltas lingering in the stack.",
            },
        ]
        interpretation = [
            "The challenger is now strong enough to justify a full rollout plan.",
            "The next irreversible step is no longer more analysis; it is explicit human acceptance of the challenger promotion plan.",
        ]
        return V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ALAShareAKInternalHotNewsChallengerPrimaryConsumerPromotionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135al_a_share_ak_internal_hot_news_challenger_primary_consumer_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
