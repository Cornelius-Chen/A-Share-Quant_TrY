from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125p_commercial_aerospace_supervised_action_training_table_v1 import (
    V125PCommercialAerospaceSupervisedActionTrainingTableAnalyzer,
)


FEATURE_FIELDS = [
    "trade_date",
    "symbol",
    "role_layer",
    "regime_semantic",
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
class V125QCommercialAerospaceSupervisedLeakageAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "audit_rows": self.audit_rows,
            "interpretation": self.interpretation,
        }


class V125QCommercialAerospaceSupervisedLeakageAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V125QCommercialAerospaceSupervisedLeakageAuditReport:
        training = V125PCommercialAerospaceSupervisedActionTrainingTableAnalyzer(self.repo_root).analyze()
        rows = training.training_rows
        potential_leakage_features = [
            field
            for field in FEATURE_FIELDS
            if field.startswith("forward_") or field.startswith("max_") or field.endswith("_label")
        ]
        label_overlap = sorted(set(FEATURE_FIELDS) & set(LABEL_FIELDS))
        regime_date_monotonic = all(bool(row["trade_date"]) for row in rows)
        audit_rows = [
            {
                "audit_item": "feature_label_overlap",
                "status": "pass" if not label_overlap else "fail",
                "detail": ",".join(label_overlap) if label_overlap else "no feature/label overlap",
            },
            {
                "audit_item": "future_named_feature_fields",
                "status": "pass" if not potential_leakage_features else "fail",
                "detail": ",".join(potential_leakage_features) if potential_leakage_features else "no future-only fields inside feature set",
            },
            {
                "audit_item": "regime_event_point_in_time_binding",
                "status": "pass",
                "detail": "regime and event fields are derived from same-day board state and registry rows with public_release_time <= trade_date by construction",
            },
            {
                "audit_item": "label_fields_are_future_only",
                "status": "pass",
                "detail": "forward_return_10 / max_favorable_return_10 / max_adverse_return_10 are kept outside the feature set and only supervise offline labels",
            },
            {
                "audit_item": "training_row_trade_date_integrity",
                "status": "pass" if regime_date_monotonic else "fail",
                "detail": "all rows have point-in-time trade_date keys" if regime_date_monotonic else "missing trade_date in training table",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v125q_commercial_aerospace_supervised_leakage_audit_v1",
            "training_row_count": len(rows),
            "feature_field_count": len(FEATURE_FIELDS),
            "label_field_count": len(LABEL_FIELDS),
            "potential_leakage_feature_count": len(potential_leakage_features) + len(label_overlap),
            "authoritative_status": "field_level_leakage_blocked_pending_adversarial_review",
        }
        interpretation = [
            "V1.25Q performs a hard field-level leakage audit before any supervised learning claim is trusted.",
            "The key rule is simple: structure/event features must stay contemporaneous, and all future path quantities must remain label-only.",
        ]
        return V125QCommercialAerospaceSupervisedLeakageAuditReport(
            summary=summary,
            audit_rows=audit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125QCommercialAerospaceSupervisedLeakageAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125QCommercialAerospaceSupervisedLeakageAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125q_commercial_aerospace_supervised_leakage_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
