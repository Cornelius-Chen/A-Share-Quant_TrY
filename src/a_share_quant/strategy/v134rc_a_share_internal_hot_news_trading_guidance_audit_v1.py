from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_trading_guidance_v1 import (
    MaterializeAShareInternalHotNewsTradingGuidanceV1,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134RCAShareInternalHotNewsTradingGuidanceAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.serving_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "serving_registry"
            / "a_share_internal_hot_news_trading_guidance_view_v1.csv"
        )

    def analyze(self) -> V134RCAShareInternalHotNewsTradingGuidanceAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsTradingGuidanceV1(self.repo_root).materialize()
        serving_rows = _read_csv(self.serving_path)

        rows = [
            {
                "component": "trading_guidance_surface",
                "component_state": "read_ready_internal_only",
                "metric": "guidance_row_count",
                "value": str(materialized.summary["guidance_row_count"]),
            },
            {
                "component": "board_guidance_summary",
                "component_state": "materialized",
                "metric": "board_summary_count",
                "value": str(materialized.summary["board_summary_count"]),
            },
            {
                "component": "market_guidance_surface",
                "component_state": "read_ready_internal_only",
                "metric": "market_guidance_row_count",
                "value": str(materialized.summary["market_guidance_row_count"]),
            },
            {
                "component": "board_signal_surface",
                "component_state": "read_ready_internal_only",
                "metric": "board_signal_row_count",
                "value": str(materialized.summary["board_signal_row_count"]),
            },
            {
                "component": "risk_queue_surface",
                "component_state": "read_ready_internal_only",
                "metric": "risk_queue_row_count",
                "value": str(materialized.summary["risk_queue_row_count"]),
            },
            {
                "component": "decision_signal_surface",
                "component_state": "read_ready_internal_only",
                "metric": "decision_signal_row_count",
                "value": str(materialized.summary["decision_signal_row_count"]),
            },
            {
                "component": "serving_view",
                "component_state": "multi_view_materialized",
                "metric": "serving_view_count",
                "value": str(len(serving_rows)),
            },
        ]
        summary = {
            "guidance_row_count": materialized.summary["guidance_row_count"],
            "guidance_event_count": materialized.summary["guidance_event_count"],
            "risk_event_count": materialized.summary["risk_event_count"],
            "trigger_event_count": materialized.summary["trigger_event_count"],
            "market_guidance_row_count": materialized.summary["market_guidance_row_count"],
            "board_signal_row_count": materialized.summary["board_signal_row_count"],
            "risk_queue_row_count": materialized.summary["risk_queue_row_count"],
            "decision_signal_row_count": materialized.summary["decision_signal_row_count"],
            "authoritative_output": "a_share_internal_hot_news_trading_guidance_surface_materialized",
        }
        interpretation = [
            "The internal hot-news fast lane now emits structured trading guidance instead of only raw news snippets.",
            "Messages are normalized into source role, event domain, target scope, guidance class, direction, strength, routing bucket, and candidate beneficiary symbols.",
            "The pipeline now also emits separate market guidance, board signal, risk queue, and decision signal views for downstream trading consumption.",
        ]
        return V134RCAShareInternalHotNewsTradingGuidanceAuditV1Report(
            summary=summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RCAShareInternalHotNewsTradingGuidanceAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RCAShareInternalHotNewsTradingGuidanceAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rc_a_share_internal_hot_news_trading_guidance_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
