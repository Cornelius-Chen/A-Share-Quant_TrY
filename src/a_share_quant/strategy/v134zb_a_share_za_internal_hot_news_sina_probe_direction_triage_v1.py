from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134za_a_share_internal_hot_news_sina_theme_probe_audit_v1 import (
    V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Report:
        report = V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "fetch_row_count": report.summary["fetch_row_count"],
            "theme_hit_count": report.summary["theme_hit_count"],
            "theme_hit_with_symbol_route_count": report.summary["theme_hit_with_symbol_route_count"],
            "unique_primary_theme_count": report.summary["unique_primary_theme_count"],
            "authoritative_status": "use_sina_probe_to_measure_live_theme-hit_lift_before_merging_second_source_into_primary_fastlane",
        }
        triage_rows = [
            {
                "component": "second_source_probe",
                "direction": "keep sina_7x24 as a parallel probe until its live theme-hit yield justifies merging into the primary fastlane",
            },
            {
                "component": "theme_hit_measurement",
                "direction": "compare real theme-hit density and symbol-route yield against the current cls-only sample rather than judging source value abstractly",
            },
            {
                "component": "merge_gate",
                "direction": "promote probe to primary-source merge only after it improves live theme/symbol diversity without unacceptable duplicate fan-out",
            },
        ]
        interpretation = [
            "This direction card keeps source expansion empirical instead of speculative.",
            "The probe should prove lift in real theme hits before it is allowed to affect the main consumer packet.",
        ]
        return V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zb_a_share_za_internal_hot_news_sina_probe_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
