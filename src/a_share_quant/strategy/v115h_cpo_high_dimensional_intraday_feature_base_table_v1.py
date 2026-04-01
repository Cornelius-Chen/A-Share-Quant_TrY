from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    low = int(pos)
    high = min(low + 1, len(sorted_values) - 1)
    frac = pos - low
    return sorted_values[low] * (1.0 - frac) + sorted_values[high] * frac


def _robust_zscore(value: float, *, med: float, iqr: float) -> float:
    scale = max(iqr, 1e-9)
    return (value - med) / scale


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


@dataclass(slots=True)
class V115HCpoHighDimensionalIntradayFeatureBaseTableReport:
    summary: dict[str, Any]
    discoverable_feature_rows: list[dict[str, Any]]
    audit_only_field_rows: list[dict[str, Any]]
    dropped_field_rows: list[dict[str, Any]]
    band_orientation_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "discoverable_feature_rows": self.discoverable_feature_rows,
            "audit_only_field_rows": self.audit_only_field_rows,
            "dropped_field_rows": self.dropped_field_rows,
            "band_orientation_rows": self.band_orientation_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


class V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _build_feature_row(row: dict[str, Any]) -> dict[str, Any]:
        built = dict(row)
        built["d5_30_close_vs_vwap"] = round(
            _to_float(row.get("f5_close_vs_vwap")) - _to_float(row.get("f30_close_vs_vwap")),
            6,
        )
        built["d15_60_close_vs_vwap"] = round(
            _to_float(row.get("f15_close_vs_vwap")) - _to_float(row.get("f60_close_vs_vwap")),
            6,
        )
        built["d5_30_last_bar_return"] = round(
            _to_float(row.get("f5_last_bar_return")) - _to_float(row.get("f30_last_bar_return")),
            6,
        )
        built["d15_60_last_bar_return"] = round(
            _to_float(row.get("f15_last_bar_return")) - _to_float(row.get("f60_last_bar_return")),
            6,
        )
        built["d5_30_last_bar_volume_share"] = round(
            _to_float(row.get("f5_last_bar_volume_share")) - _to_float(row.get("f30_last_bar_volume_share")),
            6,
        )
        built["d15_60_last_bar_volume_share"] = round(
            _to_float(row.get("f15_last_bar_volume_share")) - _to_float(row.get("f60_last_bar_volume_share")),
            6,
        )
        built["d15_60_failed_push_proxy"] = round(
            _to_float(row.get("f15_failed_push_proxy")) - _to_float(row.get("f60_failed_push_proxy")),
            6,
        )
        built["d5_30_upper_shadow_ratio"] = round(
            _to_float(row.get("f5_upper_shadow_ratio")) - _to_float(row.get("f30_upper_shadow_ratio")),
            6,
        )
        built["d15_60_upper_shadow_ratio"] = round(
            _to_float(row.get("f15_upper_shadow_ratio")) - _to_float(row.get("f60_upper_shadow_ratio")),
            6,
        )
        built["d5_30_lower_shadow_ratio"] = round(
            _to_float(row.get("f5_lower_shadow_ratio")) - _to_float(row.get("f30_lower_shadow_ratio")),
            6,
        )
        built["d15_60_lower_shadow_ratio"] = round(
            _to_float(row.get("f15_lower_shadow_ratio")) - _to_float(row.get("f60_lower_shadow_ratio")),
            6,
        )
        built["d5_30_last_bar_upper_shadow_ratio"] = round(
            _to_float(row.get("f5_last_bar_upper_shadow_ratio")) - _to_float(row.get("f30_last_bar_upper_shadow_ratio")),
            6,
        )
        built["d15_60_last_bar_upper_shadow_ratio"] = round(
            _to_float(row.get("f15_last_bar_upper_shadow_ratio")) - _to_float(row.get("f60_last_bar_upper_shadow_ratio")),
            6,
        )
        built["d5_30_last_bar_lower_shadow_ratio"] = round(
            _to_float(row.get("f5_last_bar_lower_shadow_ratio")) - _to_float(row.get("f30_last_bar_lower_shadow_ratio")),
            6,
        )
        built["d15_60_last_bar_lower_shadow_ratio"] = round(
            _to_float(row.get("f15_last_bar_lower_shadow_ratio")) - _to_float(row.get("f60_last_bar_lower_shadow_ratio")),
            6,
        )
        return built

    def analyze(self, *, enriched_rows: list[dict[str, Any]]) -> tuple[V115HCpoHighDimensionalIntradayFeatureBaseTableReport, list[dict[str, Any]]]:
        actionable_rows = [
            dict(row)
            for row in enriched_rows
            if str(row.get("action_context")) in {"entry_vs_skip", "add_vs_hold", "reduce_vs_hold", "close_vs_hold"}
        ]
        base_rows = [self._build_feature_row(row) for row in actionable_rows]

        discoverable_features = [
            ("f30_breakout_efficiency", "continuous", "30min main"),
            ("f60_breakout_efficiency", "continuous", "60min main"),
            ("f30_close_vs_vwap", "continuous", "30min main"),
            ("f60_close_vs_vwap", "continuous", "60min main"),
            ("f30_close_location", "continuous", "30min main"),
            ("f60_close_location", "continuous", "60min main"),
            ("f30_pullback_from_high", "continuous", "30min main"),
            ("f60_pullback_from_high", "continuous", "60min main"),
            ("f30_last_bar_return", "continuous", "30min main"),
            ("f60_last_bar_return", "continuous", "60min main"),
            ("f30_last_bar_volume_share", "continuous", "30min main"),
            ("f60_last_bar_volume_share", "continuous", "60min main"),
            ("f30_high_time_ratio", "continuous", "30min main"),
            ("f60_high_time_ratio", "continuous", "60min main"),
            ("f30_afternoon_volume_share", "continuous", "30min main"),
            ("f60_afternoon_volume_share", "continuous", "60min main"),
            ("f30_upper_shadow_ratio", "continuous", "30min main"),
            ("f60_upper_shadow_ratio", "continuous", "60min main"),
            ("f30_lower_shadow_ratio", "continuous", "30min main"),
            ("f60_lower_shadow_ratio", "continuous", "60min main"),
            ("f30_body_ratio", "continuous", "30min main"),
            ("f60_body_ratio", "continuous", "60min main"),
            ("f30_last_bar_upper_shadow_ratio", "continuous", "30min main"),
            ("f60_last_bar_upper_shadow_ratio", "continuous", "60min main"),
            ("f30_last_bar_lower_shadow_ratio", "continuous", "30min main"),
            ("f60_last_bar_lower_shadow_ratio", "continuous", "60min main"),
            ("f30_failed_push_proxy", "binary", "30min main"),
            ("f60_failed_push_proxy", "binary", "60min main"),
            ("d5_30_close_vs_vwap", "continuous", "5minus30 differential"),
            ("d15_60_close_vs_vwap", "continuous", "15minus60 differential"),
            ("d5_30_last_bar_return", "continuous", "5minus30 differential"),
            ("d15_60_last_bar_return", "continuous", "15minus60 differential"),
            ("d5_30_last_bar_volume_share", "continuous", "5minus30 differential"),
            ("d15_60_last_bar_volume_share", "continuous", "15minus60 differential"),
            ("d5_30_upper_shadow_ratio", "continuous", "5minus30 differential"),
            ("d15_60_upper_shadow_ratio", "continuous", "15minus60 differential"),
            ("d5_30_lower_shadow_ratio", "continuous", "5minus30 differential"),
            ("d15_60_lower_shadow_ratio", "continuous", "15minus60 differential"),
            ("d5_30_last_bar_upper_shadow_ratio", "continuous", "5minus30 differential"),
            ("d15_60_last_bar_upper_shadow_ratio", "continuous", "15minus60 differential"),
            ("d5_30_last_bar_lower_shadow_ratio", "continuous", "5minus30 differential"),
            ("d15_60_last_bar_lower_shadow_ratio", "continuous", "15minus60 differential"),
            ("d15_60_failed_push_proxy", "binary", "15minus60 differential"),
        ]

        audit_only_fields = [
            ("symbol", "identity"),
            ("role_family", "identity"),
            ("board_phase", "identity"),
            ("control_label", "identity"),
            ("action_context", "training_label"),
            ("signal_trade_date", "timing"),
            ("execution_trade_date", "timing"),
            ("action_favored_3d", "outcome_label"),
            ("expectancy_proxy_3d", "outcome_label"),
            ("forward_close_return_3d", "outcome_label"),
            ("max_adverse_return_3d", "outcome_label"),
            ("max_favorable_return_3d", "outcome_label"),
            ("P_reduce_avoided_drawdown_proxy_3d", "outcome_label"),
            ("P_close_invalidation_realized_proxy_3d", "outcome_label"),
            ("reduce_payoff_decay_vs_hold_proxy_3d", "outcome_label"),
        ]

        dropped_fields = [
            ("f5_intraday_return", "5min raw duplicate of day path"),
            ("f15_intraday_return", "15min raw duplicate of day path"),
            ("f30_intraday_return", "30min duplicate of breakout/close structure"),
            ("f60_intraday_return", "60min duplicate of breakout/close structure"),
            ("f5_range_pct", "range duplicated across frequencies"),
            ("f15_range_pct", "range duplicated across frequencies"),
            ("f30_range_pct", "range duplicated across frequencies"),
            ("f60_range_pct", "range duplicated across frequencies"),
            ("f5_afternoon_return", "prefer 5/15 as differential, not raw"),
            ("f15_afternoon_return", "prefer 30/60 main and 5/15 differential"),
            ("f30_afternoon_return", "kept indirectly via return/close structure"),
            ("f60_afternoon_return", "kept indirectly via return/close structure"),
            ("f5_amount_per_volume", "price-scale noise"),
            ("f15_amount_per_volume", "price-scale noise"),
            ("f30_amount_per_volume", "price-scale noise"),
            ("f60_amount_per_volume", "price-scale noise"),
            ("board_avg_return", "board state audit only"),
            ("board_breadth", "board state audit only"),
            ("gross_exposure_after_close", "strategy-state audit only"),
        ]

        feature_stats: dict[str, tuple[float, float]] = {}
        for feature_name, feature_kind, _ in discoverable_features:
            if feature_kind == "binary":
                continue
            values = sorted(_to_float(row.get(feature_name)) for row in base_rows)
            med = median(values) if values else 0.0
            q1 = _quantile(values, 0.25)
            q3 = _quantile(values, 0.75)
            feature_stats[feature_name] = (med, q3 - q1)

        final_rows: list[dict[str, Any]] = []
        for row in base_rows:
            final_row = {
                "symbol": row.get("symbol", ""),
                "signal_trade_date": row.get("signal_trade_date", row.get("trade_date", "")),
                "execution_trade_date": row.get("execution_trade_date", ""),
                "action_context": row.get("action_context", ""),
                "board_phase": row.get("board_phase", ""),
                "role_family": row.get("role_family", ""),
                "control_label": row.get("control_label", ""),
                "action_favored_3d": row.get("action_favored_3d", ""),
                "expectancy_proxy_3d": row.get("expectancy_proxy_3d", ""),
                "forward_close_return_3d": row.get("forward_close_return_3d", ""),
                "max_adverse_return_3d": row.get("max_adverse_return_3d", ""),
                "max_favorable_return_3d": row.get("max_favorable_return_3d", ""),
            }
            for feature_name, feature_kind, _ in discoverable_features:
                value = _to_float(row.get(feature_name))
                final_row[feature_name] = round(value, 6)
                if feature_kind == "continuous":
                    med, iqr = feature_stats[feature_name]
                    final_row[f"{feature_name}_rz"] = round(_robust_zscore(value, med=med, iqr=iqr), 6)
            final_rows.append(final_row)

        contexts = sorted({str(row.get("action_context", "")) for row in final_rows})
        band_orientation_rows: list[dict[str, Any]] = []
        for feature_name, feature_kind, _ in discoverable_features:
            row_out: dict[str, Any] = {
                "feature_name": feature_name,
                "feature_kind": feature_kind,
            }
            for context in contexts:
                context_rows = [row for row in final_rows if str(row.get("action_context")) == context]
                values = [_to_float(row.get(feature_name)) for row in context_rows]
                row_out[f"{context}_mean"] = round(_mean(values), 6)
            add_mean = _to_float(row_out.get("add_vs_hold_mean"))
            reduce_mean = _to_float(row_out.get("reduce_vs_hold_mean"))
            close_mean = _to_float(row_out.get("close_vs_hold_mean"))
            row_out["add_minus_reduce_gap"] = round(add_mean - reduce_mean, 6)
            row_out["add_minus_close_gap"] = round(add_mean - close_mean, 6)
            band_orientation_rows.append(row_out)

        discoverable_feature_rows = [
            {
                "feature_name": feature_name,
                "feature_kind": feature_kind,
                "retention_posture": retention_posture,
                "discovery_usage": "allowed_in_unsupervised_base_table",
            }
            for feature_name, feature_kind, retention_posture in discoverable_features
        ]
        audit_only_rows = [
            {
                "field_name": field_name,
                "why_postponed": why_postponed,
                "discovery_usage": "audit_only_not_in_unsupervised_distance_space",
            }
            for field_name, why_postponed in audit_only_fields
        ]
        dropped_field_rows = [
            {
                "field_name": field_name,
                "why_dropped": why_dropped,
            }
            for field_name, why_dropped in dropped_fields
        ]

        summary = {
            "acceptance_posture": "freeze_v115h_cpo_high_dimensional_intraday_feature_base_table_v1",
            "source_row_count": len(enriched_rows),
            "actionable_row_count": len(base_rows),
            "discoverable_feature_count": len(discoverable_features),
            "continuous_feature_count": sum(1 for _, kind, _ in discoverable_features if kind == "continuous"),
            "binary_feature_count": sum(1 for _, kind, _ in discoverable_features if kind == "binary"),
            "audit_only_field_count": len(audit_only_fields),
            "dropped_field_count": len(dropped_fields),
            "table_posture": "high_dimensional_base_table_before_unsupervised_discovery",
            "frequency_design": "30_60_main_plus_5_15_differential_support",
            "identity_fields_removed_from_distance_space": True,
            "recommended_discovery_method": "robust_standardize_then_pca_or_sparse_pca_then_umap_visual_audit_then_continuous_band_review",
            "recommended_next_posture": "run_unsupervised_discovery_on_v115h_base_table_not_on_manually_precompressed_vectors",
        }
        interpretation = [
            "V1.15H deliberately stops before clustering. The purpose is to replace manual semantic compression with a more objective high-dimensional intraday substrate.",
            "The key design choice is to keep 30/60-minute main-state features, add 5/15-minute differentials as supporting microstructure cues, and strip identity or outcome fields out of the discovery distance space.",
            "This table is for unsupervised discovery and audit only. Naming, promotion, and action-law extraction must remain downstream of stability, action-relevance, and incremental-value checks.",
        ]
        report = V115HCpoHighDimensionalIntradayFeatureBaseTableReport(
            summary=summary,
            discoverable_feature_rows=discoverable_feature_rows,
            audit_only_field_rows=audit_only_rows,
            dropped_field_rows=dropped_field_rows,
            band_orientation_rows=band_orientation_rows,
            sample_rows=final_rows[:8],
            interpretation=interpretation,
        )
        return report, final_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115HCpoHighDimensionalIntradayFeatureBaseTableReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv").open("r", encoding="utf-8") as handle:
        enriched_rows = list(csv.DictReader(handle))
    analyzer = V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer(repo_root=repo_root)
    result, final_rows = analyzer.analyze(enriched_rows=enriched_rows)
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        rows=final_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115h_cpo_high_dimensional_intraday_feature_base_table_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
