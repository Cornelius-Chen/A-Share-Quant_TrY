from __future__ import annotations

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
class V126HCommercialAerospaceTwoLayerEligibilityAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V126HCommercialAerospaceTwoLayerEligibilityAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _split_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        ordered_dates = sorted({row["trade_date"] for row in rows})
        split_idx = max(1, round(len(ordered_dates) * 0.8))
        train_dates = set(ordered_dates[:split_idx])
        return [row for row in rows if row["trade_date"] in train_dates], [row for row in rows if row["trade_date"] not in train_dates]

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

    def _score_rows(self, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]], positive_labels: set[str]) -> list[float]:
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

    def analyze(self) -> V126HCommercialAerospaceTwoLayerEligibilityAuditReport:
        table = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(self.repo_root).analyze()
        rows = table.training_rows
        train_rows, test_rows = self._split_rows(rows)
        train_rows_z, test_rows_z = self._standardize(train_rows, test_rows)
        train_scores = self._score_rows(train_rows_z, train_rows_z, {"probe_eligibility_target", "full_eligibility_target"})
        test_scores = self._score_rows(train_rows_z, test_rows_z, {"probe_eligibility_target", "full_eligibility_target"})

        impulse_train = [
            (row, score)
            for row, score in zip(train_rows_z, train_scores, strict=False)
            if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"
        ]
        impulse_test = [
            (row, score)
            for row, score in zip(test_rows_z, test_scores, strict=False)
            if row["regime_proxy_semantic"] == "impulse_expansion_proxy" and row["event_state"] == "continuation_active"
        ]
        impulse_train_scores = [score for _, score in impulse_train]
        train_probe_count = sum(1 for row, _ in impulse_train if row["supervised_action_label_rc"] == "probe_eligibility_target")
        train_full_count = sum(1 for row, _ in impulse_train if row["supervised_action_label_rc"] == "full_eligibility_target")

        variants = [
            ("probe_q80_full_q60", 0.80, 0.60),
            ("probe_q80_full_q40", 0.80, 0.40),
            ("probe_q70_full_q40", 0.70, 0.40),
        ]
        variant_rows: list[dict[str, Any]] = []
        for variant_name, probe_q, full_q in variants:
            probe_threshold = _quantile(impulse_train_scores, probe_q)
            full_threshold = _quantile(impulse_train_scores, full_q)
            full_hits = [row for row, score in impulse_test if score <= full_threshold]
            probe_only_hits = [row for row, score in impulse_test if full_threshold < score <= probe_threshold]
            full_mean = _mean([float(row["forward_return_10"]) for row in full_hits])
            probe_only_mean = _mean([float(row["forward_return_10"]) for row in probe_only_hits])
            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "probe_threshold_quantile": probe_q,
                    "full_threshold_quantile": full_q,
                    "probe_threshold": round(probe_threshold, 8),
                    "full_threshold": round(full_threshold, 8),
                    "full_hit_count": len(full_hits),
                    "probe_only_hit_count": len(probe_only_hits),
                    "full_forward_mean_10": round(full_mean, 8),
                    "probe_only_forward_mean_10": round(probe_only_mean, 8),
                    "full_minus_probe_only_spread_10": round(full_mean - probe_only_mean, 8),
                }
            )

        best_variant = max(variant_rows, key=lambda row: row["full_minus_probe_only_spread_10"])
        summary = {
            "acceptance_posture": "freeze_v126h_commercial_aerospace_two_layer_eligibility_audit_v1",
            "impulse_train_count": len(impulse_train),
            "impulse_test_count": len(impulse_test),
            "impulse_train_probe_count": train_probe_count,
            "impulse_train_full_count": train_full_count,
            "best_variant_name": best_variant["variant_name"],
            "best_variant_full_minus_probe_only_spread_10": best_variant["full_minus_probe_only_spread_10"],
            "authoritative_rule": "commercial_aerospace_two_layer_probe_full_design_must_be_treated_as_regime_local_score_stratification_not_supervised_full_label_learning_when_impulse_train_full_count_is_zero",
        }
        interpretation = [
            "V1.26H checks whether a probe/full two-layer system can be justified inside impulse-continuation windows.",
            "If impulse-train full-label count is zero, the two-layer replay must be treated as a score-stratified shadow design rather than fully supervised full-eligibility learning.",
        ]
        return V126HCommercialAerospaceTwoLayerEligibilityAuditReport(summary=summary, variant_rows=variant_rows, interpretation=interpretation)


def write_report(*, reports_dir: Path, report_name: str, result: V126HCommercialAerospaceTwoLayerEligibilityAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126HCommercialAerospaceTwoLayerEligibilityAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126h_commercial_aerospace_two_layer_eligibility_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
