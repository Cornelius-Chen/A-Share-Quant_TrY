from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v135ae_a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_audit_v1 import (
    V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer,
)


@dataclass(slots=True)
class V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Report:
    summary: dict[str, Any]
    triage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "triage_rows": self.triage_rows, "interpretation": self.interpretation}


class V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Report:
        report = V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer(self.repo_root).analyze()
        summary = {
            "incumbent_theme_slug": report.summary["incumbent_theme_slug"],
            "incumbent_watch_symbol": report.summary["incumbent_watch_symbol"],
            "challenger_theme_slug": report.summary["challenger_theme_slug"],
            "challenger_watch_symbol": report.summary["challenger_watch_symbol"],
            "support_delta_vs_incumbent": report.summary["support_delta_vs_incumbent"],
            "review_state": report.summary["review_state"],
            "authoritative_status": "incumbent_vs_challenger_rotation_review_materialized",
        }
        triage_rows = [
            {
                "component": "incumbent_hold",
                "direction": "keep the current primary focus as the live anchor while the challenger advantage remains below the open-review threshold.",
            },
            {
                "component": "challenger_monitoring",
                "direction": "continue watching whether challenger support keeps compounding across new second-source rows instead of reacting to a single current spike.",
            },
            {
                "component": "next_rotation_rule",
                "direction": "only open the next accepted-rotation review once challenger support exceeds incumbent support by the configured margin.",
            },
        ]
        interpretation = [
            "The current review is a stopline between continuous challenger monitoring and a new full rotation plan.",
            "It converts the next rotation question from intuition into a simple gated comparison between incumbent support and challenger support.",
        ]
        return V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Report(
            summary=summary,
            triage_rows=triage_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135af_a_share_ae_internal_hot_news_incumbent_vs_challenger_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
