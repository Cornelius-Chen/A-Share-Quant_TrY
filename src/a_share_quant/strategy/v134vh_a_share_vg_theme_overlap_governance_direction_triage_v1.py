from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134vg_a_share_theme_overlap_governance_audit_v1 import (
    V134VGAShareThemeOverlapGovernanceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Report:
        report = V134VGAShareThemeOverlapGovernanceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "governance_rule_count": report.summary["governance_rule_count"],
            "resolved_overlap_count": report.summary["resolved_overlap_count"],
            "unresolved_overlap_count": report.summary["unresolved_overlap_count"],
            "authoritative_status": "continue_resolving_repeated_overlap_pairs_before_expanding_more_theme_layers",
        }
        triage_rows = [
            {
                "component": "resolved_overlap_pairs",
                "direction": "prefer the primary theme for routing while preserving secondary themes for context and audit.",
            },
            {
                "component": "unresolved_overlap_pairs",
                "direction": "leave unresolved overlaps visible and only add new rules when the same pair repeats often enough to justify governance.",
            },
        ]
        interpretation = [
            "Overlap governance should stay narrow and repeated-pair driven, not become a giant taxonomy bureaucracy.",
            "The current rules are enough to stop the most common high-frequency overlaps from flattening downstream routing.",
        ]
        return V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134VHAShareVGThemeOverlapGovernanceDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134vh_a_share_vg_theme_overlap_governance_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
