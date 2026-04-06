from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134re_a_share_internal_hot_news_event_cluster_audit_v1 import (
    V134REAShareInternalHotNewsEventClusterAuditV1Analyzer,
)


@dataclass(slots=True)
class V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Report:
        report = V134REAShareInternalHotNewsEventClusterAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "cluster_row_count": report.summary["cluster_row_count"],
            "deduped_row_count": report.summary["deduped_row_count"],
            "duplicate_reduction_count": report.summary["duplicate_reduction_count"],
            "authoritative_status": "continue_feeding_trading_from_deduped_event_stream_not_raw_duplicate_news_rows",
        }
        triage_rows = [
            {
                "component": "event_clustering",
                "direction": "keep_clustering_fast_news_into_event_groups_before_trading_delivery",
            },
            {
                "component": "deduped_delivery",
                "direction": "prefer_the_deduped_event_stream_for_downstream_consumption_when_cluster_rows_exist",
            },
            {
                "component": "duplicate_control",
                "direction": "treat_duplicate_reduction_as_a_quality_gain_not_as_data_loss",
            },
        ]
        interpretation = [
            "The hot-news pipeline can now reduce duplicate message fan-out before the trading layer consumes the stream.",
            "The next refinement should improve clustering quality and important-event promotion rather than reopen source selection.",
        ]
        return V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RFAShareREInternalHotNewsEventClusterDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rf_a_share_re_internal_hot_news_event_cluster_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
