from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ye_a_share_theme_symbol_routing_drill_audit_v1 import (
    V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer,
)


@dataclass(slots=True)
class V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Report:
        report = V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "case_count": report.summary["case_count"],
            "routed_count": report.summary["routed_count"],
            "direct_route_count": report.summary["direct_route_count"],
            "unresolved_primary_count": report.summary["unresolved_primary_count"],
            "authoritative_status": "use theme-symbol routing drill as the end-to-end curation validation layer before adding more long-tail theme families",
        }
        triage_rows = [
            {
                "component": "direct_routes",
                "direction": "treat direct-routed cases as the highest-confidence evidence that the theme registry can support symbol-first consumers",
            },
            {
                "component": "resolved_but_proxy_routes",
                "direction": "use proxy-routed cases as a curation-improvement queue rather than a routing failure",
            },
            {
                "component": "unresolved_primary_cases",
                "direction": "treat unresolved-primary cases as governance or registry coverage debt before further theme expansion",
            },
        ]
        interpretation = [
            "This drill tells you whether simulated theme headlines can actually reach a governed top symbol route.",
            "It is the closest synthetic validation layer before live multi-source samples become broader.",
        ]
        return V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134yf_a_share_ye_theme_symbol_routing_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
