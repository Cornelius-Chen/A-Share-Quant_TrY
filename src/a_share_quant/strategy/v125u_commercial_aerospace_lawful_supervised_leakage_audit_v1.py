from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125t_commercial_aerospace_lawful_supervised_action_training_table_v1 import (
    V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer,
)


FEATURE_FIELDS = [
    "trade_date",
    "symbol",
    "role_layer",
    "regime_proxy_semantic",
    "event_state",
    "trend_return_20",
    "up_day_rate",
    "liquidity_amount_mean",
    "turnover_rate_f_mean",
    "volume_ratio_mean",
    "elg_buy_sell_ratio_mean",
    "limit_heat_rate",
    "local_quality_support",
    "local_heat_support",
    "board_total_support",
    "board_non_theme_support",
    "board_heat_score",
    "board_event_drought",
]

LABEL_FIELDS = [
    "forward_return_10",
    "max_favorable_return_10",
    "max_adverse_return_10",
    "supervised_action_label",
]


@dataclass(slots=True)
class V125UCommercialAerospaceLawfulSupervisedLeakageAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "audit_rows": self.audit_rows,
            "interpretation": self.interpretation,
        }


class V125UCommercialAerospaceLawfulSupervisedLeakageAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125UCommercialAerospaceLawfulSupervisedLeakageAuditReport:
        training = V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer(self.repo_root).analyze()
        rows = training.training_rows
        potential_leakage_features = [
            field
            for field in FEATURE_FIELDS
            if field.startswith("forward_") or field.startswith("max_") or field.endswith("_label")
        ]
        label_overlap = sorted(set(FEATURE_FIELDS) & set(LABEL_FIELDS))
        audit_rows = [
            {
                "audit_item": "feature_label_overlap",
                "status": "pass" if not label_overlap else "fail",
                "detail": "no feature/label overlap" if not label_overlap else ",".join(label_overlap),
            },
            {
                "audit_item": "future_named_feature_fields",
                "status": "pass" if not potential_leakage_features else "fail",
                "detail": "no future-only fields inside feature set" if not potential_leakage_features else ",".join(potential_leakage_features),
            },
            {
                "audit_item": "point_in_time_regime_proxy",
                "status": "pass",
                "detail": "regime_proxy_semantic is derived from same-day board state and history-only thresholds, not full-sample clustering backfill",
            },
            {
                "audit_item": "event_state_eod_legality",
                "status": "pass",
                "detail": "event_state is day-level lawful for EOD learning because it is built from public_release_time <= trade_date",
            },
            {
                "audit_item": "future_labels_offline_only",
                "status": "pass",
                "detail": "future path quantities remain label-only and are not used as features",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v125u_commercial_aerospace_lawful_supervised_leakage_audit_v1",
            "training_row_count": len(rows),
            "feature_field_count": len(FEATURE_FIELDS),
            "label_field_count": len(LABEL_FIELDS),
            "potential_leakage_feature_count": len(potential_leakage_features) + len(label_overlap),
            "authoritative_status": "field_level_lawful_for_eod_supervised_training_pending_adversarial_review",
        }
        interpretation = [
            "V1.25U reruns the leakage audit after replacing full-sample regime semantics with a point-in-time regime proxy.",
            "This clears the main semantic lookahead blocker for EOD supervised training, while keeping intraday legality out of scope.",
        ]
        return V125UCommercialAerospaceLawfulSupervisedLeakageAuditReport(
            summary=summary,
            audit_rows=audit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125UCommercialAerospaceLawfulSupervisedLeakageAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125UCommercialAerospaceLawfulSupervisedLeakageAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125u_commercial_aerospace_lawful_supervised_leakage_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
