from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.ingest_jobs.fetch_a_share_internal_hot_news_cls_telegraph_v1 import (
    FetchAShareInternalHotNewsCLSTelegraphV1,
)
from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_fastlane_v1 import (
    MaterializeAShareInternalHotNewsFastlaneV1,
)
from a_share_quant.info_center.automation.retention_jobs.materialize_a_share_internal_hot_news_retention_v1 import (
    MaterializeAShareInternalHotNewsRetentionV1,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134RAAShareInternalHotNewsFastlaneActivationAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.runtime_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_registry_v1.csv"
        )

    def analyze(self) -> V134RAAShareInternalHotNewsFastlaneActivationAuditV1Report:
        fetch_result = FetchAShareInternalHotNewsCLSTelegraphV1(self.repo_root).materialize()
        pipeline_result = MaterializeAShareInternalHotNewsFastlaneV1(self.repo_root).materialize()
        retention_result = MaterializeAShareInternalHotNewsRetentionV1(self.repo_root).materialize()
        runtime_rows = _read_csv(self.runtime_registry_path)

        rows = [
            {
                "component": "internal_hot_news_runtime",
                "component_state": runtime_rows[0]["runtime_state"],
                "metric": "fetch_row_count",
                "value": str(fetch_result.summary["fetch_row_count"]),
            },
            {
                "component": "fastlane_pipeline",
                "component_state": "pipeline_ready_for_trading_program",
                "metric": "fastlane_row_count",
                "value": str(pipeline_result.summary["fastlane_row_count"]),
            },
            {
                "component": "important_promotion",
                "component_state": "rule_based_bootstrap_active",
                "metric": "important_row_count",
                "value": str(pipeline_result.summary["important_row_count"]),
            },
            {
                "component": "retention",
                "component_state": "hot_5d_ttl_active",
                "metric": "retention_queue_count",
                "value": str(retention_result.summary["retention_queue_count"]),
            },
        ]
        summary = {
            "fetch_row_count": fetch_result.summary["fetch_row_count"],
            "fastlane_row_count": pipeline_result.summary["fastlane_row_count"],
            "important_row_count": pipeline_result.summary["important_row_count"],
            "retention_queue_count": retention_result.summary["retention_queue_count"],
            "runtime_state": runtime_rows[0]["runtime_state"],
            "authoritative_output": "a_share_internal_hot_news_fastlane_internal_only_loop_materialized",
        }
        interpretation = [
            "A parallel internal-only hot-news fast lane is now active without changing live/execution governance gates.",
            "The loop is concrete: CLS telegraph fetch -> fast pipeline surface -> important promotion candidate layer -> 5-day TTL retention queue.",
        ]
        return V134RAAShareInternalHotNewsFastlaneActivationAuditV1Report(
            summary=summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RAAShareInternalHotNewsFastlaneActivationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ra_a_share_internal_hot_news_fastlane_activation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
