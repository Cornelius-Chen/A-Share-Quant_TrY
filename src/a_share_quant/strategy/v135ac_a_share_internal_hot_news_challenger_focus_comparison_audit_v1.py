from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_challenger_focus_comparison_v1 import (
    MaterializeAShareInternalHotNewsChallengerFocusComparisonV1,
)


@dataclass(slots=True)
class V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Report:
        materialized = MaterializeAShareInternalHotNewsChallengerFocusComparisonV1(self.repo_root).materialize()
        rows = [
            {
                "component": "challenger_focus_comparison",
                "component_state": "materialized",
                "metric": "challenger_row_count",
                "value": str(materialized.summary["challenger_row_count"]),
            },
            {
                "component": "challenger_focus_comparison",
                "component_state": "materialized",
                "metric": "top_challenger_theme_slug",
                "value": materialized.summary["top_challenger_theme_slug"],
            },
            {
                "component": "challenger_focus_comparison",
                "component_state": "materialized",
                "metric": "top_challenger_symbol",
                "value": materialized.summary["top_challenger_symbol"],
            },
            {
                "component": "challenger_focus_comparison",
                "component_state": "materialized",
                "metric": "top_challenger_support_row_count",
                "value": str(materialized.summary["top_challenger_support_row_count"]),
            },
            {
                "component": "challenger_focus_comparison",
                "component_state": "materialized",
                "metric": "top_challenger_source_family_count",
                "value": str(materialized.summary["top_challenger_source_family_count"]),
            },
        ]
        interpretation = [
            "This comparison isolates the strongest non-current theme/symbol candidates that could challenge the accepted primary focus later.",
            "It gives the next rotation decision a simpler challenger board instead of requiring a full reread of the entire controlled merge candidate lane.",
        ]
        return V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135ACAShareInternalHotNewsChallengerFocusComparisonAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ac_a_share_internal_hot_news_challenger_focus_comparison_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
