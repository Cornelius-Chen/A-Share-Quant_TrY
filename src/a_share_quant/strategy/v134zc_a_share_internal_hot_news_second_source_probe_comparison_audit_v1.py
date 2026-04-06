from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_second_source_probe_comparison_v1 import (
    MaterializeAShareInternalHotNewsSecondSourceProbeComparisonV1,
)


@dataclass(slots=True)
class V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsSecondSourceProbeComparisonV1(self.repo_root).materialize()
        row = materialized.rows[0]
        rows = [
            {
                "component": "primary_source",
                "component_state": "measured",
                "metric": "primary_theme_hit_count",
                "value": row["primary_theme_hit_count"],
            },
            {
                "component": "probe_source",
                "component_state": "measured",
                "metric": "probe_theme_hit_count",
                "value": row["probe_theme_hit_count"],
            },
            {
                "component": "probe_source",
                "component_state": "measured",
                "metric": "probe_symbol_route_count",
                "value": row["probe_symbol_route_count"],
            },
            {
                "component": "probe_comparison",
                "component_state": row["probe_value_state"],
                "metric": "unique_theme_delta",
                "value": row["unique_theme_delta"],
            },
        ]
        interpretation = [
            "This comparison quantifies whether the second source improves live theme-hit and symbol-route diversity over the current cls-only sample.",
            "It is a controlled merge gate rather than a speculative source-preference argument.",
        ]
        return V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZCAShareInternalHotNewsSecondSourceProbeComparisonAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zc_a_share_internal_hot_news_second_source_probe_comparison_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
