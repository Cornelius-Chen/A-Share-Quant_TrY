from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_theme_symbol_routing_drill_v1 import (
    MaterializeAShareThemeSymbolRoutingDrillV1,
)


@dataclass(slots=True)
class V134YEAShareThemeSymbolRoutingDrillAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134YEAShareThemeSymbolRoutingDrillAuditV1Report:
        materialized = MaterializeAShareThemeSymbolRoutingDrillV1(self.repo_root).materialize()
        rows = [
            {
                "component": "theme_symbol_routing_drill",
                "component_state": "materialized",
                "metric": "case_count",
                "value": str(materialized.summary["case_count"]),
            },
            {
                "component": "theme_symbol_routing_drill",
                "component_state": "measured",
                "metric": "routed_count",
                "value": str(materialized.summary["routed_count"]),
            },
            {
                "component": "theme_symbol_routing_drill",
                "component_state": "measured",
                "metric": "direct_route_count",
                "value": str(materialized.summary["direct_route_count"]),
            },
            {
                "component": "theme_symbol_routing_drill",
                "component_state": "measured",
                "metric": "unresolved_primary_count",
                "value": str(materialized.summary["unresolved_primary_count"]),
            },
        ]
        interpretation = [
            "This drill validates the full route from detected theme strings to governed primary theme and top symbol route.",
            "It is stricter than alias reachability because it asks whether the current registry can produce a usable top symbol.",
        ]
        return V134YEAShareThemeSymbolRoutingDrillAuditV1Report(
            summary=materialized.summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YEAShareThemeSymbolRoutingDrillAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ye_a_share_theme_symbol_routing_drill_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
