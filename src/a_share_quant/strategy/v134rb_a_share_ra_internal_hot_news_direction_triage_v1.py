from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ra_a_share_internal_hot_news_fastlane_activation_audit_v1 import (
    V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer,
)


@dataclass(slots=True)
class V134RBAShareRAInternalHotNewsDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134RBAShareRAInternalHotNewsDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134RBAShareRAInternalHotNewsDirectionTriageV1Report:
        report = V134RAAShareInternalHotNewsFastlaneActivationAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "fetch_row_count": report.summary["fetch_row_count"],
            "fastlane_row_count": report.summary["fastlane_row_count"],
            "important_row_count": report.summary["important_row_count"],
            "authoritative_status": "continue_news_ingest_from_internal_only_fastlane_then_refine_message_grading_in_pipeline",
        }
        triage_rows = [
            {
                "component": "source_choice",
                "direction": "use_cls_telegraph_as_the_single_internal_fastlane_source_to_minimize_duplicate_news_fan-out",
            },
            {
                "component": "pipeline",
                "direction": "send_news_to_the_trading_program_from_the_fastlane_surface_first_then_iterate_message_grading",
            },
            {
                "component": "retention",
                "direction": "keep_hot_copy_for_5_days_and_retain_only_promoted_important_rows_beyond_ttl",
            },
        ]
        interpretation = [
            "The fastest safe next step is no longer source expansion; it is refining message grading on top of an already-running single-source fast lane.",
            "This lane is intentionally internal-only so it can feed research/shadow workflows without silently opening execution authority.",
        ]
        return V134RBAShareRAInternalHotNewsDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134RBAShareRAInternalHotNewsDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134RBAShareRAInternalHotNewsDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134rb_a_share_ra_internal_hot_news_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
