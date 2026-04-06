from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125x_commercial_aerospace_eod_binary_action_pilot_v1 import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    _mean,
    _std,
)
from a_share_quant.strategy.v126a_commercial_aerospace_regime_conditioned_label_table_v1 import (
    V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer,
)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V126FCommercialAerospaceZeroTriggerAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "audit_rows": self.audit_rows, "interpretation": self.interpretation}


class V126FCommercialAerospaceZeroTriggerAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _split_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        train_dates = set(ordered_dates[:split_idx])
        test_dates = set(ordered_dates[split_idx:])
        return [row for row in rows if row["trade_date"] in train_dates], [row for row in rows if row["trade_date"] in test_dates]

    def _standardize(self, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        stats: dict[str, tuple[float, float]] = {}
        for feature in NUMERIC_FEATURES:
            values = [float(row[feature]) for row in train_rows]
            mean = _mean(values)
            std = _std(values, mean)
            stats[feature] = (mean, std)

        def transform(rows_in: list[dict[str, Any]]) -> list[dict[str, Any]]:
            out: list[dict[str, Any]] = []
            for row in rows_in:
                enriched = dict(row)
                for feature in NUMERIC_FEATURES:
                    mean, std = stats[feature]
                    enriched[f"{feature}_z"] = (float(row[feature]) - mean) / std
                out.append(enriched)
            return out

        return transform(train_rows), transform(eval_rows)

    def _score_rows(self, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> list[float]:
        positive_labels = {"probe_eligibility_target", "full_eligibility_target"}
        positives = [row for row in train_rows if row["supervised_action_label_rc"] in positive_labels]
        negatives = [row for row in train_rows if row["supervised_action_label_rc"] not in positive_labels]
        pos_numeric = {feature: _mean([float(row[f"{feature}_z"]) for row in positives]) for feature in NUMERIC_FEATURES}
        neg_numeric = {feature: _mean([float(row[f"{feature}_z"]) for row in negatives]) for feature in NUMERIC_FEATURES}
        pos_cat = {
            feature: max(
                {value for value in (row[feature] for row in positives)},
                key=lambda candidate: sum(1 for row in positives if row[feature] == candidate),
            )
            for feature in CATEGORICAL_FEATURES
        }
        neg_cat = {
            feature: max(
                {value for value in (row[feature] for row in negatives)},
                key=lambda candidate: sum(1 for row in negatives if row[feature] == candidate),
            )
            for feature in CATEGORICAL_FEATURES
        }
        scores: list[float] = []
        for row in eval_rows:
            numeric_score = sum(
                abs(float(row[f"{feature}_z"]) - neg_numeric[feature]) - abs(float(row[f"{feature}_z"]) - pos_numeric[feature])
                for feature in NUMERIC_FEATURES
            )
            cat_score = sum(
                (0.5 if row[feature] == pos_cat[feature] else 0.0) - (0.5 if row[feature] == neg_cat[feature] else 0.0)
                for feature in CATEGORICAL_FEATURES
            )
            scores.append(numeric_score + cat_score)
        return scores

    def analyze(self) -> V126FCommercialAerospaceZeroTriggerAuditReport:
        table = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(self.repo_root).analyze()
        train_rows, test_rows = self._split_rows(table.training_rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)
        train_scores = self._score_rows(train_rows_z, train_rows_z)
        test_scores = self._score_rows(train_rows_z, test_rows_z)
        global_threshold = _quantile(train_scores, 0.8)

        train_impulse = [score for row, score in zip(train_rows_z, train_scores, strict=False) if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"]
        regime_local_threshold = _quantile(train_impulse, 0.8)

        impulse_test_rows = [row for row in test_rows_z if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"]
        impulse_test_scores = [score for row, score in zip(test_rows_z, test_scores, strict=False) if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"]

        global_hits = sum(1 for score in impulse_test_scores if score <= global_threshold)
        regime_local_hits = sum(1 for score in impulse_test_scores if score <= regime_local_threshold)

        audit_rows = [
            {
                "audit_item": "impulse_continuation_rows_in_test",
                "value": len(impulse_test_rows),
            },
            {
                "audit_item": "global_low_pass_q80_threshold",
                "value": round(global_threshold, 8),
            },
            {
                "audit_item": "impulse_local_low_pass_q80_threshold",
                "value": round(regime_local_threshold, 8),
            },
            {
                "audit_item": "global_threshold_impulse_hits",
                "value": global_hits,
            },
            {
                "audit_item": "regime_local_threshold_impulse_hits",
                "value": regime_local_hits,
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v126f_commercial_aerospace_zero_trigger_audit_v1",
            "impulse_continuation_test_count": len(impulse_test_rows),
            "global_threshold_impulse_hits": global_hits,
            "regime_local_threshold_impulse_hits": regime_local_hits,
            "authoritative_rule": "commercial_aerospace_zero_trade_shadow_replay_should_be_treated_as_global_threshold_mismatch_not_absence_of_impulse_regime",
        }
        interpretation = [
            "V1.26F separates a true no-opportunity period from a threshold mismatch.",
            "If regime-local eligibility hits exist while global-threshold hits are zero, the blocker is calibration geometry rather than missing structure.",
        ]
        return V126FCommercialAerospaceZeroTriggerAuditReport(
            summary=summary,
            audit_rows=audit_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126FCommercialAerospaceZeroTriggerAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126FCommercialAerospaceZeroTriggerAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126f_commercial_aerospace_zero_trigger_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
