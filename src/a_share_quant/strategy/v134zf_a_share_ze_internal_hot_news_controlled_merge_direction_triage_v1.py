from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134ze_a_share_internal_hot_news_controlled_merge_review_audit_v1 import (
    V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZFAShareZEInternalHotNewsControlledMergeDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZFAShareZEInternalHotNewsControlledMergeDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZFAShareZEInternalHotNewsControlledMergeDirectionTriageV1Report:
        report = V134ZEAShareInternalHotNewsControlledMergeReviewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "open_controlled_cls_sina_merge_candidate_only_after_duplicate_candidates_are_explicitly_reviewed",
        }
        triage_rows = [
            {
                "component": "cross_source_duplicates",
                "direction": "review cross-source duplicate candidates before allowing both sources into the same primary fastlane stream",
            },
            {
                "component": "additive_sina_candidates",
                "direction": "treat additive sina themed rows as the highest-value merge candidates because they improve theme and symbol diversity",
            },
            {
                "component": "merge_gate",
                "direction": "merge through a controlled candidate surface first instead of replacing the current cls-only fastlane in one step",
            },
        ]
        interpretation = [
            "The second source has already proven value; the remaining question is controlled duplicate handling.",
            "This keeps merge progression empirical and reversible.",
        ]
        return V134ZFAShareZEInternalHotNewsControlledMergeDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZFAShareZEInternalHotNewsControlledMergeDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZFAShareZEInternalHotNewsControlledMergeDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zf_a_share_ze_internal_hot_news_controlled_merge_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
