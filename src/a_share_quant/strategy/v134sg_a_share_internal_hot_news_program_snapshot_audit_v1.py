from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_program_snapshot_v1 import (
    MaterializeAShareInternalHotNewsProgramSnapshotV1,
)


@dataclass(slots=True)
class V134SGAShareInternalHotNewsProgramSnapshotAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134SGAShareInternalHotNewsProgramSnapshotAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsProgramSnapshotV1(self.repo_root).materialize()
        rows = [
            {
                "component": "program_snapshot",
                "component_state": "read_ready_internal_only",
                "metric": "snapshot_row_count",
                "value": str(materialized.summary["snapshot_row_count"]),
            },
            {
                "component": "risk_snapshot",
                "component_state": "materialized",
                "metric": "risk_feed_row_count",
                "value": str(materialized.summary["risk_feed_row_count"]),
            },
            {
                "component": "opportunity_snapshot",
                "component_state": "materialized",
                "metric": "opportunity_feed_row_count",
                "value": str(materialized.summary["opportunity_feed_row_count"]),
            },
            {
                "component": "timing_snapshot",
                "component_state": "materialized",
                "metric": "session_handling_mode",
                "value": materialized.summary["session_handling_mode"],
            },
            {
                "component": "risk_consumer_gate",
                "component_state": "materialized",
                "metric": "risk_consumer_gate",
                "value": materialized.summary["risk_consumer_gate"],
            },
            {
                "component": "opportunity_consumer_gate",
                "component_state": "materialized",
                "metric": "opportunity_consumer_gate",
                "value": materialized.summary["opportunity_consumer_gate"],
            },
            {
                "component": "top_opportunity_mapping",
                "component_state": "materialized",
                "metric": "top_opportunity_mapping_confidence",
                "value": materialized.summary["top_opportunity_mapping_confidence"],
            },
            {
                "component": "top_opportunity_mapping",
                "component_state": "materialized",
                "metric": "top_opportunity_linkage_class",
                "value": materialized.summary["top_opportunity_linkage_class"],
            },
            {
                "component": "top_opportunity_beneficiary_symbols",
                "component_state": "materialized",
                "metric": "top_opportunity_beneficiary_symbols_top5",
                "value": materialized.summary["top_opportunity_beneficiary_symbols_top5"],
            },
            {
                "component": "top_watch_symbol",
                "component_state": "materialized",
                "metric": "top_watch_symbol",
                "value": materialized.summary["top_watch_symbol"],
            },
            {
                "component": "top_watch_theme",
                "component_state": "materialized",
                "metric": "top_watch_primary_theme_slug",
                "value": materialized.summary["top_watch_primary_theme_slug"],
            },
            {
                "component": "top_watch_bundle",
                "component_state": "materialized",
                "metric": "top_watch_symbols_top5",
                "value": materialized.summary["top_watch_symbols_top5"],
            },
            {
                "component": "top_watch_bundle",
                "component_state": "materialized",
                "metric": "top_watch_linkage_class",
                "value": materialized.summary["top_watch_linkage_class"],
            },
            {
                "component": "top_opportunity_theme_governance",
                "component_state": "materialized",
                "metric": "top_opportunity_primary_theme_slug",
                "value": materialized.summary["top_opportunity_primary_theme_slug"],
            },
            {
                "component": "top_opportunity_theme_governance",
                "component_state": "materialized",
                "metric": "top_opportunity_theme_governance_state",
                "value": materialized.summary["top_opportunity_theme_governance_state"],
            },
        ]
        interpretation = [
            "The trading program can now poll one compact snapshot row instead of scanning full feeds every time.",
            "The snapshot exposes top-risk and top-opportunity state plus current session handling and direct feed consumer gates while preserving the full split feeds for deeper processing.",
            "Top-opportunity mapping state is now carried into the snapshot so the program can see beneficiary-symbol readiness without reopening the opportunity feed.",
            "Both the top opportunity and top watch symbol now carry linkage class, so direct beneficiaries can be separated from weaker proxies at snapshot level.",
            "The snapshot now also carries the top governed watch symbol and the top-five watch bundle, so symbol-first consumers can stay on the snapshot path for the first routing decision.",
            "When overlap governance applies, the snapshot now carries the governed primary theme rather than leaving multi-theme ambiguity to the outer consumer.",
        ]
        return V134SGAShareInternalHotNewsProgramSnapshotAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134SGAShareInternalHotNewsProgramSnapshotAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134SGAShareInternalHotNewsProgramSnapshotAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134sg_a_share_internal_hot_news_program_snapshot_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
