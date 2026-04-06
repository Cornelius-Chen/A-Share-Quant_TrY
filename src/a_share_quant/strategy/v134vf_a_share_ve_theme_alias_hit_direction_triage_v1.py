from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ve_a_share_theme_alias_hit_drill_audit_v1 import (
    V134VEAShareThemeAliasHitDrillAuditV1Analyzer,
)


@dataclass(slots=True)
class V134VFAShareVEThemeAliasHitDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134VFAShareVEThemeAliasHitDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VFAShareVEThemeAliasHitDirectionTriageV1Report:
        report = V134VEAShareThemeAliasHitDrillAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "case_count": report.summary["case_count"],
            "exact_expected_hit_count": report.summary["exact_expected_hit_count"],
            "expected_covered_count": report.summary["expected_covered_count"],
            "overlap_hit_count": report.summary["overlap_hit_count"],
            "partial_or_miss_count": report.summary["partial_or_miss_count"],
            "authoritative_status": "continue_expanding_registry_only_when_alias_drills_stay_clean_enough_for_repeated_theme_families",
        }
        triage_rows = [
            {
                "component": "alias_readiness",
                "direction": "keep validating theme growth with synthetic hit drills so registry expansion remains reachable by the live classifier",
            },
            {
                "component": "theme_growth",
                "direction": "prefer adding repeated high-frequency families over chasing rare themes that lack durable alias patterns",
            },
        ]
        interpretation = [
            "Registry scale alone is not enough; the classifier must still be able to reach the themes through actual headline language.",
            "This drill makes that constraint explicit before more theme families are added, while tolerating reasonable multi-theme overlap.",
        ]
        return V134VFAShareVEThemeAliasHitDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VFAShareVEThemeAliasHitDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VFAShareVEThemeAliasHitDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134vf_a_share_ve_theme_alias_hit_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
