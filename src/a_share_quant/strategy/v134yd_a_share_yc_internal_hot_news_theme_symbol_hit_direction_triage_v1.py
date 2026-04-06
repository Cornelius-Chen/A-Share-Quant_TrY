from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134yc_a_share_internal_hot_news_theme_symbol_hit_replay_audit_v1 import (
    V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer,
)


@dataclass(slots=True)
class V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Report:
        report = V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "sample_row_count": report.summary["sample_row_count"],
            "broad_market_only_count": report.summary["broad_market_only_count"],
            "theme_hit_count": report.summary["theme_hit_count"],
            "theme_hit_with_symbol_watch_count": report.summary["theme_hit_with_symbol_watch_count"],
            "theme_hit_without_symbol_watch_count": report.summary["theme_hit_without_symbol_watch_count"],
            "unique_primary_theme_count": report.summary["unique_primary_theme_count"],
            "unique_watch_symbol_count": report.summary["unique_watch_symbol_count"],
            "authoritative_status": "use themed-hit replay as the practical validation layer before expanding more theme registry breadth",
        }
        triage_rows = [
            {
                "component": "broad_market_only_rows",
                "direction": "treat broad-market-heavy samples as macro/risk traffic rather than a mapping failure",
            },
            {
                "component": "theme_hit_with_symbol_watch_rows",
                "direction": "treat symbol-watch hits as the highest-value validation path for current theme-to-symbol curation",
            },
            {
                "component": "theme_hit_without_symbol_watch_rows",
                "direction": "use uncovered themed rows as the next curation queue before adding more long-tail theme families",
            },
        ]
        interpretation = [
            "This replay is a reality check on the current sample stream rather than an abstract registry-only metric.",
            "It helps distinguish a broad-market news day from a genuine theme-mapping miss.",
        ]
        return V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134yd_a_share_yc_internal_hot_news_theme_symbol_hit_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
