from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134zg_a_share_internal_hot_news_controlled_merge_candidate_surface_audit_v1 import (
    V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer,
)


@dataclass(slots=True)
class V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Report:
        report = V134ZGAShareInternalHotNewsControlledMergeCandidateSurfaceAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            **report.summary,
            "authoritative_status": "keep_cls_primary_fastlane_and_stage_sina_additive_theme_symbol_rows_through_controlled_candidate_surface",
        }
        triage_rows = [
            {
                "component": "cls_primary_lane",
                "direction": "retain cls primary rows as the anchor stream while second-source merge stays controlled",
            },
            {
                "component": "sina_additive_lane",
                "direction": "treat additive sina themed rows as the highest-priority second-source candidate set",
            },
            {
                "component": "promotion_gate",
                "direction": "promote from the candidate surface only after duplicate review and downstream consumer checks remain stable",
            },
        ]
        interpretation = [
            "The merge question has moved from source value to controlled promotion sequencing.",
            "This lane adds thematic diversity without replacing the current cls anchor stream.",
        ]
        return V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ZHAShareZGInternalHotNewsControlledMergeCandidateDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134zh_a_share_zg_internal_hot_news_controlled_merge_candidate_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
