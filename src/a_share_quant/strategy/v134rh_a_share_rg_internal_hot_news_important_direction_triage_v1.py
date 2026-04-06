from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134rg_a_share_internal_hot_news_important_promotion_audit_v1 import (
    V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer,
)


@dataclass(slots=True)
class V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Report:
        report = V134RGAShareInternalHotNewsImportantPromotionAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "important_promotion_row_count": report.summary["important_promotion_row_count"],
            "important_queue_row_count": report.summary["important_queue_row_count"],
            "tier_1_count": report.summary["tier_1_count"],
            "tier_2_count": report.summary["tier_2_count"],
            "authoritative_status": "continue_promoting_only_deduped_high-impact_messages_into_important_trading_queue",
        }
        triage_rows = [
            {
                "component": "promotion_logic",
                "direction": "keep_using_deduped_guidance_and_decision_scores_to_upgrade_messages_into_the_important_layer",
            },
            {
                "component": "tiering",
                "direction": "separate_top_down_guidance_and_risk_shocks_from_secondary_board_specific_signals",
            },
            {
                "component": "trading_delivery",
                "direction": "feed_the_trading_program_from_the_important_queue_only_after_clustering_and_semantic_scoring",
            },
        ]
        interpretation = [
            "The important layer is no longer a raw keyword bucket.",
            "The next refinement should improve theme beneficiary mapping and cluster quality inside the important queue.",
        ]
        return V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RHAShareRGInternalHotNewsImportantDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rh_a_share_rg_internal_hot_news_important_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
