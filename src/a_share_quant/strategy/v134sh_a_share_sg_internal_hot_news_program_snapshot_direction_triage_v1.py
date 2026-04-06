from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134sg_a_share_internal_hot_news_program_snapshot_audit_v1 import (
    V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer,
)


@dataclass(slots=True)
class V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Report:
        report = V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "snapshot_row_count": report.summary["snapshot_row_count"],
            "risk_feed_row_count": report.summary["risk_feed_row_count"],
            "opportunity_feed_row_count": report.summary["opportunity_feed_row_count"],
            "session_handling_mode": report.summary["session_handling_mode"],
            "risk_consumer_gate": report.summary["risk_consumer_gate"],
            "opportunity_consumer_gate": report.summary["opportunity_consumer_gate"],
            "snapshot_consumer_gate_mode": report.summary["snapshot_consumer_gate_mode"],
            "top_risk_score": report.summary["top_risk_score"],
            "top_opportunity_score": report.summary["top_opportunity_score"],
            "top_opportunity_primary_theme_slug": report.summary["top_opportunity_primary_theme_slug"],
            "top_opportunity_theme_governance_state": report.summary["top_opportunity_theme_governance_state"],
            "top_opportunity_mapping_confidence": report.summary["top_opportunity_mapping_confidence"],
            "top_opportunity_linkage_class": report.summary["top_opportunity_linkage_class"],
            "top_opportunity_beneficiary_symbols_top5": report.summary["top_opportunity_beneficiary_symbols_top5"],
            "top_watch_symbol": report.summary["top_watch_symbol"],
            "top_watch_primary_theme_slug": report.summary["top_watch_primary_theme_slug"],
            "top_watch_mapping_confidence": report.summary["top_watch_mapping_confidence"],
            "top_watch_linkage_class": report.summary["top_watch_linkage_class"],
            "top_watch_symbols_top5": report.summary["top_watch_symbols_top5"],
            "authoritative_status": "continue_serving_downstream_with_single_program_snapshot_row",
        }
        triage_rows = [
            {
                "component": "polling_consumer",
                "direction": "prefer_the_program_snapshot_when_the_consumer_only_needs_current_top-risk_and_top-opportunity_state_plus_current_feed_gates",
            },
            {
                "component": "deeper_consumer",
                "direction": "fall_back_to_split_feeds_when_the_consumer_needs_more_than_the_top_snapshot_row_or_needs_row-level_risk_opportunity_details",
            },
            {
                "component": "debug_consumer",
                "direction": "fall_back_to_minimal_view_or_full_ingress_for_diagnostics_and_feature_validation",
            },
        ]
        interpretation = [
            "The snapshot is a convenience layer above the split feeds, not a replacement for deeper internal surfaces.",
            "This is the most compact consumer interface built so far on the hot-news pipeline, and it now carries the current feed-level consumer gates.",
            "The snapshot now also carries the top-opportunity beneficiary mapping payload so top-level consumers can act without rejoining the opportunity feed.",
            "It also carries the top governed watch symbol and top-five watch bundle so a symbol-first consumer can stay on the snapshot layer for the first watch decision.",
            "It additionally exposes the governed primary theme so overlap handling can stay below the top-level consumer boundary.",
        ]
        return V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SHAShareSGInternalHotNewsProgramSnapshotDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sh_a_share_sg_internal_hot_news_program_snapshot_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
