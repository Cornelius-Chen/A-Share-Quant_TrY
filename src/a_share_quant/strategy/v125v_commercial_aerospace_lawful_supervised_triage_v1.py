from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125u_commercial_aerospace_lawful_supervised_leakage_audit_v1 import (
    V125UCommercialAerospaceLawfulSupervisedLeakageAuditAnalyzer,
)


@dataclass(slots=True)
class V125VCommercialAerospaceLawfulSupervisedTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V125VCommercialAerospaceLawfulSupervisedTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125VCommercialAerospaceLawfulSupervisedTriageReport:
        leakage = V125UCommercialAerospaceLawfulSupervisedLeakageAuditAnalyzer(self.repo_root).analyze()
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "EOD_lawful_for_supervised_training_pending_adversarial_review",
                "hard_lookahead": False,
                "intraday_lawful": False,
            },
            {
                "reviewer": "Tesla",
                "verdict": "eod_lawful_for_supervised_training_non_intraday_pending_adversarial_review",
                "hard_lookahead": False,
                "intraday_lawful": False,
            },
            {
                "reviewer": "James",
                "verdict": "eod_lawful_for_supervised_training_non_intraday_pending_adversarial_review",
                "hard_lookahead": False,
                "intraday_lawful": False,
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v125v_commercial_aerospace_lawful_supervised_triage_v1",
            "training_row_count": leakage.summary["training_row_count"],
            "hard_lookahead_detected": False,
            "eod_lawful": True,
            "intraday_lawful": False,
            "authoritative_status": "commercial_aerospace_lawful_supervised_table_unblocked_for_eod_training_but_blocked_for_intraday_or_direct_execution",
            "authoritative_rule": "use_v125t_for_eod_supervised_learning_only_do_not_promote_to_intraday_or_replay_directly",
        }
        interpretation = [
            "The commercial-aerospace supervised table is now lawful for EOD supervised training because the main semantic hindsight blocker has been removed.",
            "This does not unlock intraday legality or direct execution; the table remains an offline EOD learning substrate only.",
        ]
        return V125VCommercialAerospaceLawfulSupervisedTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125VCommercialAerospaceLawfulSupervisedTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125VCommercialAerospaceLawfulSupervisedTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125v_commercial_aerospace_lawful_supervised_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
