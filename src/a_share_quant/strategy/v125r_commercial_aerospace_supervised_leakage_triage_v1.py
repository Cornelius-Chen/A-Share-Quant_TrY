from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125q_commercial_aerospace_supervised_leakage_audit_v1 import (
    V125QCommercialAerospaceSupervisedLeakageAuditAnalyzer,
)


@dataclass(slots=True)
class V125RCommercialAerospaceSupervisedLeakageTriageReport:
    summary: dict[str, Any]
    reviewer_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "reviewer_rows": self.reviewer_rows,
            "interpretation": self.interpretation,
        }


class V125RCommercialAerospaceSupervisedLeakageTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125RCommercialAerospaceSupervisedLeakageTriageReport:
        leakage = V125QCommercialAerospaceSupervisedLeakageAuditAnalyzer(self.repo_root).analyze()
        reviewer_rows = [
            {
                "reviewer": "Pauli",
                "verdict": "provisionally_no_leak_compatible_but_regime_provenance_not_yet_cleared",
                "hard_lookahead": False,
                "main_risk": "regime_semantic_full_sample_backfill",
                "secondary_risk": "same_day_event_cutoff_is_eod_only_not_intraday",
            },
            {
                "reviewer": "Tesla",
                "verdict": "no_obvious_direct_lookahead_but_semantic_pti_audit_required",
                "hard_lookahead": False,
                "main_risk": "regime_semantic_full_sample_backfill",
                "secondary_risk": "same_day_event_cutoff_is_eod_only_not_intraday",
            },
            {
                "reviewer": "James",
                "verdict": "no_obvious_hard_lookahead_but_requires_point_in_time_lineage_audit",
                "hard_lookahead": False,
                "main_risk": "regime_semantic_full_sample_backfill",
                "secondary_risk": "same_day_event_cutoff_is_eod_only_not_intraday",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v125r_commercial_aerospace_supervised_leakage_triage_v1",
            "training_row_count": leakage.summary["training_row_count"],
            "feature_field_count": leakage.summary["feature_field_count"],
            "label_field_count": leakage.summary["label_field_count"],
            "hard_lookahead_detected": False,
            "semantic_point_in_time_risk_detected": True,
            "main_blocker": "regime_semantic_is_currently_generated_from_full_sample_structural_clustering_and_backfilled_to_trade_dates",
            "secondary_blocker": "event_state_is_day_level_legal_for_eod_learning_but_not_yet_intraday_strict",
            "authoritative_status": "supervised_table_blocked_for_lawful_training_until_regime_semantic_is_replaced_by_point_in_time_or_lagged_regime_proxy",
            "authoritative_rule": "keep_future_labels_offline_but_do_not_train_on_full_sample_regime_semantic",
        }
        interpretation = [
            "The supervised table has no obvious hard lookahead because feature fields and future labels stay separated.",
            "The blocker is semantic point-in-time lineage: regime_semantic is currently learned on the full sample and then written back to each trade date.",
            "This table is acceptable for exploratory offline analysis, but not yet lawful for time-series supervised training until regime_semantic is converted to a point-in-time or lagged proxy.",
        ]
        return V125RCommercialAerospaceSupervisedLeakageTriageReport(
            summary=summary,
            reviewer_rows=reviewer_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125RCommercialAerospaceSupervisedLeakageTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125RCommercialAerospaceSupervisedLeakageTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125r_commercial_aerospace_supervised_leakage_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
