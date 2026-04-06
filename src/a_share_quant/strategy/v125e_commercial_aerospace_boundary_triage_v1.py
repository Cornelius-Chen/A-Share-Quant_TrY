from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125d_commercial_aerospace_sentiment_control_boundary_audit_v1 import (
    V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer,
)


@dataclass(slots=True)
class V125ECommercialAerospaceBoundaryTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V125ECommercialAerospaceBoundaryTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125ECommercialAerospaceBoundaryTriageReport:
        upstream = V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer(self.repo_root).analyze()
        summary = upstream.summary
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "status": "boundary_audit_says_sentiment_layer_must_be_quarantined_not_promoted",
                "key_point": "zero_clean_sentiment_promotions_means_current_sentiment_bucket_is_still_mixed_with_control_like_names",
            },
            {
                "reviewer": "Tesla",
                "status": "000547_is_important_but_not_clean_sentiment_only",
                "key_point": "航天发展 should stay visible as a sentiment watch name, not as control and not as generic mirror",
            },
            {
                "reviewer": "James",
                "status": "refresh_role_grammar_before_information_layer",
                "key_point": "resolve sentiment-control contamination first so event inputs do not bind onto the wrong authority layer",
            },
        ]
        authoritative_status = "boundary_audited_role_grammar_refresh_required"
        next_step = "refresh_role_grammar_with_sentiment_watch_quarantine"
        report_summary = {
            "acceptance_posture": "freeze_v125e_commercial_aerospace_boundary_triage_v1",
            "authoritative_status": authoritative_status,
            "recommended_sentiment_count": summary["recommended_sentiment_count"],
            "boundary_risk_count": summary["boundary_risk_count"],
            "000547_boundary_semantic": summary["000547_boundary_semantic"],
            "000547_boundary_recommendation": summary["000547_boundary_recommendation"],
            "allow_replay_now": False,
            "authoritative_next_step": next_step,
        }
        interpretation = [
            "V1.25E freezes the result of the first commercial-aerospace sentiment-control boundary audit.",
            "The key conclusion is negative: no non-formal name is clean enough to be promoted into a standalone sentiment-leadership authority layer.",
            "The lawful next move is to refresh the role grammar so that boundary-risk names stay visible as sentiment watch names while remaining quarantined from control.",
        ]
        return V125ECommercialAerospaceBoundaryTriageReport(
            summary=report_summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125ECommercialAerospaceBoundaryTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125ECommercialAerospaceBoundaryTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125e_commercial_aerospace_boundary_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
