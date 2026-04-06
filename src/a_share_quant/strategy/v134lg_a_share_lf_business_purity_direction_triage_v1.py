from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134lf_a_share_business_purity_foundation_audit_v1 import (
    V134LFAShareBusinessPurityFoundationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134LGAShareLFBusinessPurityDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "triage_rows": self.triage_rows,
            "interpretation": self.interpretation,
        }


class V134LGAShareLFBusinessPurityDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134LGAShareLFBusinessPurityDirectionTriageV1Report:
        audit = V134LFAShareBusinessPurityFoundationAuditV1Analyzer(self.repo_root).analyze()
        triage_rows = [
            {
                "component": "business_reference",
                "direction": "freeze_as_current_business_anchor_surface",
            },
            {
                "component": "concept_purity",
                "direction": "freeze_as_current_cross_theme_and_purity_guardrail_surface",
            },
            {
                "component": "residual_backlog",
                "direction": "retain_for_future_fundamental_text_and_cross_theme_enrichment",
            },
        ]
        summary = {
            "business_reference_count": audit.summary["business_reference_count"],
            "concept_purity_count": audit.summary["concept_purity_count"],
            "residual_count": audit.summary["residual_count"],
            "authoritative_status": "business_reference_and_concept_purity_complete_enough_to_freeze_as_bootstrap",
        }
        interpretation = [
            "The information center now has first-pass business anchors and concept-purity guardrails, which closes one of the biggest remaining taxonomy backlogs.",
            "Future external fundamentals can enrich this layer, but they no longer need to create it from zero.",
        ]
        return V134LGAShareLFBusinessPurityDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134LGAShareLFBusinessPurityDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134LGAShareLFBusinessPurityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134lg_a_share_lf_business_purity_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
