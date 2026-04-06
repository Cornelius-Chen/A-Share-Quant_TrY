from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134nu_a_share_allowlist_promotion_precondition_surface_audit_v1 import (
    V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134NVAShareNUAllowlistPreconditionDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134NVAShareNUAllowlistPreconditionDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134NVAShareNUAllowlistPreconditionDirectionTriageV1Report:
        report = V134NUAShareAllowlistPromotionPreconditionSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "precondition_count": report.summary["precondition_count"],
            "unsatisfied_count": report.summary["unsatisfied_count"],
            "authoritative_status": "allowlist_promotion_must_wait_for_manual_record_and_runtime_closure",
        }
        triage_rows = [
            {
                "component": "manual_review_records",
                "direction": "fill_standardized_manual_review_records_before_reopening_any_promotion_discussion",
            },
            {
                "component": "manual_outcomes",
                "direction": "convert_license_and_runtime_outcomes_from_pending_to_explicit_decisions",
            },
            {
                "component": "runtime_candidate",
                "direction": "recheck_html_article_runtime_only_after_batch_one_manual_closure",
            },
            {
                "component": "promotion_gate",
                "direction": "keep_allowlist_promotion_fully_closed_until_all_preconditions_turn_satisfied",
            },
        ]
        interpretation = [
            "The next valid move is closure of explicit preconditions, not additional restructuring.",
            "This keeps source-side governance strict while still making later promotion reproducible.",
        ]
        return V134NVAShareNUAllowlistPreconditionDirectionTriageV1Report(
            summary=summary, triage_rows=triage_rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134NVAShareNUAllowlistPreconditionDirectionTriageV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134NVAShareNUAllowlistPreconditionDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134nv_a_share_nu_allowlist_precondition_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
