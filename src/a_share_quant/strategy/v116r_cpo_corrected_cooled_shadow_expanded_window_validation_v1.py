from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v115b_cpo_midfreq_intraday_factor_extraction_v1 import (
    _to_baostock_symbol,
    _window_features,
)
from a_share_quant.strategy.v115j_cpo_high_dimensional_intraday_pca_band_audit_v1 import (
    V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer,
)
from a_share_quant.strategy.v115o_cpo_intraday_strict_band_signal_timing_audit_v1 import (
    _build_feature_row_from_prefix,
    _filter_prefix_rows,
    _robust_stats,
    _rz,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _checkpoint_label(raw_checkpoint: str) -> str:
    hhmmss = raw_checkpoint[8:14]
    return f"{hhmmss[0:2]}:{hhmmss[2:4]}"


@dataclass(slots=True)
class V116RCpoCorrectedCooledShadowExpandedWindowValidationReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    hit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "hit_rows": self.hit_rows,
            "interpretation": self.interpretation,
        }


class V116RCpoCorrectedCooledShadowExpandedWindowValidationAnalyzer:
    CHECKPOINTS = [
        "20230101103000000",
        "20230101110000000",
        "20230101140000000",
        "20230101143000000",
        "20230101150000000",
    ]

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _query_bars_with_relogin(
        self,
        *,
        bs_module: Any,
        symbol: str,
        trade_date: str,
        frequency: str,
    ) -> list[dict[str, Any]]:
        rs = bs_module.query_history_k_data_plus(
            _to_baostock_symbol(symbol),
            "date,time,code,open,high,low,close,volume,amount,adjustflag",
            start_date=trade_date,
            end_date=trade_date,
            frequency=frequency,
            adjustflag="2",
        )
        if str(rs.error_code) == "10001001":
            try:
                bs_module.logout()
            except Exception:
                pass
            relogin = bs_module.login()
            if str(relogin.error_code) != "0":
                raise RuntimeError(f"baostock_relogin_failed:{relogin.error_code}:{relogin.error_msg}")
            rs = bs_module.query_history_k_data_plus(
                _to_baostock_symbol(symbol),
                "date,time,code,open,high,low,close,volume,amount,adjustflag",
                start_date=trade_date,
                end_date=trade_date,
                frequency=frequency,
                adjustflag="2",
            )
        if str(rs.error_code) != "0":
            raise RuntimeError(f"baostock_query_failed:{rs.error_code}:{rs.error_msg}")
        rows: list[dict[str, Any]] = []
        while rs.next():
            raw = rs.get_row_data()
            rows.append(
                {
                    "date": raw[0],
                    "time": raw[1],
                    "code": raw[2],
                    "open": _to_float(raw[3]),
                    "high": _to_float(raw[4]),
                    "low": _to_float(raw[5]),
                    "close": _to_float(raw[6]),
                    "volume": _to_float(raw[7]),
                    "amount": _to_float(raw[8]),
                    "adjustflag": raw[9],
                }
            )
        return rows

    def analyze(
        self,
        *,
        v116d_payload: dict[str, Any],
        v116q_payload: dict[str, Any],
        pca_rows_path: Path,
        training_view_path: Path,
        feature_base_path: Path,
    ) -> V116RCpoCorrectedCooledShadowExpandedWindowValidationReport:
        expanded_rows = list(v116q_payload.get("expanded_window_rows", []))
        expanded_days = {str(row["trade_date"]) for row in expanded_rows}
        gap_map = {str(row["trade_date"]): _to_float(row.get("under_exposure_gap")) for row in expanded_rows}
        breadth_map = {str(row["trade_date"]): _to_float(row.get("board_breadth")) for row in expanded_rows}
        board_ret_map = {str(row["trade_date"]): _to_float(row.get("board_avg_return")) for row in expanded_rows}
        original_map = {str(row["trade_date"]): bool(row.get("is_original_top_miss")) for row in expanded_rows}

        pca_rows = _load_csv_rows(pca_rows_path)
        candidate_base_rows = [
            row for row in pca_rows
            if str(row.get("action_context")) == "add_vs_hold"
            and str(row.get("signal_trade_date")) in expanded_days
        ]

        threshold_rows = list(v116d_payload.get("threshold_rows", []))
        q25_row = next(row for row in threshold_rows if abs(_to_float(row.get("quantile")) - 0.25) < 1e-9)
        pc1_threshold = _to_float(q25_row.get("pc1_low_threshold"))
        pc2_threshold = _to_float(q25_row.get("pc2_low_threshold"))

        training_view_rows = _load_csv_rows(training_view_path)
        train_rows = [dict(row) for row in training_view_rows if str(row.get("split_group")) == "train"]
        x_train = np.array(
            [[_to_float(row.get(feature)) for feature in V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer.FEATURE_COLUMNS] for row in train_rows],
            dtype=float,
        )
        feature_mean = x_train.mean(axis=0)
        x_centered = x_train - feature_mean
        _, _, vt = np.linalg.svd(x_centered, full_matrices=False)
        components = vt[:3]

        feature_base_rows = _load_csv_rows(feature_base_path)
        raw_feature_names = sorted(
            {
                feature[:-3] if feature.endswith("_rz") else feature
                for feature in V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer.FEATURE_COLUMNS
            }
        )
        feature_stats = _robust_stats(feature_base_rows, raw_feature_names)

        checkpoint_rows: list[dict[str, Any]] = []
        timing_rows: list[dict[str, Any]] = []

        import baostock as bs

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        try:
            for row in candidate_base_rows:
                symbol = str(row["symbol"])
                signal_trade_date = str(row["signal_trade_date"])
                raw_by_freq: dict[str, list[dict[str, Any]]] = {}
                for frequency in ("5", "15", "30", "60"):
                    raw_by_freq[frequency] = self._query_bars_with_relogin(
                        bs_module=bs,
                        symbol=symbol,
                        trade_date=signal_trade_date,
                        frequency=frequency,
                    )

                earliest_pass_checkpoint: str | None = None
                earliest_pass_scores: tuple[float, float] | None = None
                for checkpoint in self.CHECKPOINTS:
                    prefixed_blocks: dict[str, dict[str, float]] = {}
                    checkpoint_ok = True
                    for freq, freq_rows in raw_by_freq.items():
                        rows_upto_checkpoint = _filter_prefix_rows(freq_rows, checkpoint)
                        if not rows_upto_checkpoint:
                            checkpoint_ok = False
                            break
                        prefixed_blocks[freq] = _window_features(rows_upto_checkpoint, frequency=freq)
                    if not checkpoint_ok:
                        continue

                    raw_row = _build_feature_row_from_prefix(prefixed_blocks)
                    feature_vector: list[float] = []
                    for feature in V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer.FEATURE_COLUMNS:
                        if feature.endswith("_rz"):
                            raw_name = feature[:-3]
                            med, iqr = feature_stats[raw_name]
                            feature_vector.append(_rz(_to_float(raw_row.get(raw_name)), med=med, iqr=iqr))
                        else:
                            feature_vector.append(_to_float(raw_row.get(feature)))
                    vector = np.array(feature_vector, dtype=float)
                    scores = components @ (vector - feature_mean)
                    pc1_score = float(scores[0])
                    pc2_score = float(scores[1])
                    visible_pass = pc1_score <= pc1_threshold or pc2_score <= pc2_threshold
                    checkpoint_label = _checkpoint_label(checkpoint)
                    checkpoint_rows.append(
                        {
                            "signal_trade_date": signal_trade_date,
                            "symbol": symbol,
                            "checkpoint": checkpoint_label,
                            "pc1_score": round(pc1_score, 6),
                            "pc2_score": round(pc2_score, 6),
                            "passes_pc1_or_pc2_q_0p25": visible_pass,
                        }
                    )
                    if visible_pass and earliest_pass_checkpoint is None:
                        earliest_pass_checkpoint = checkpoint_label
                        earliest_pass_scores = (pc1_score, pc2_score)

                timing_rows.append(
                    {
                        "signal_trade_date": signal_trade_date,
                        "symbol": symbol,
                        "earliest_visible_checkpoint": earliest_pass_checkpoint,
                        "visible_pc1_score": None if earliest_pass_scores is None else round(earliest_pass_scores[0], 6),
                        "visible_pc2_score": None if earliest_pass_scores is None else round(earliest_pass_scores[1], 6),
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        checkpoint_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in checkpoint_rows:
            checkpoint_map.setdefault((str(row["signal_trade_date"]), str(row["symbol"])), []).append(row)
        for rows in checkpoint_map.values():
            rows.sort(key=lambda row: str(row["checkpoint"]))

        def has_pass(row_key: tuple[str, str], checkpoint: str) -> bool:
            for row in checkpoint_map.get(row_key, []):
                if str(row["checkpoint"]) == checkpoint:
                    return _to_bool(row.get("passes_pc1_or_pc2_q_0p25"))
            return False

        def earliest_late_checkpoint(row_key: tuple[str, str]) -> str | None:
            for checkpoint in ("14:00", "14:30"):
                if has_pass(row_key, checkpoint):
                    return checkpoint
            return None

        def corrected_candidate(row: dict[str, Any]) -> bool:
            row_key = (str(row["signal_trade_date"]), str(row["symbol"]))
            return (
                row.get("earliest_visible_checkpoint") is not None
                and has_pass(row_key, "10:30")
                and has_pass(row_key, "11:00")
                and earliest_late_checkpoint(row_key) is not None
            )

        def hot_upper_bound(row: dict[str, Any]) -> bool:
            return row.get("earliest_visible_checkpoint") is not None

        variants = {
            "corrected_cooled_shadow_candidate": corrected_candidate,
            "hot_upper_bound_reference": hot_upper_bound,
        }

        variant_rows: list[dict[str, Any]] = []
        hit_rows: list[dict[str, Any]] = []
        for variant_name, predicate in variants.items():
            hits = [row for row in timing_rows if predicate(row)]
            hit_count = len(hits)
            hit_day_count = len({str(row["signal_trade_date"]) for row in hits})
            positive_rate = (
                sum(1 for row in hits if _to_float(row.get("expectancy_proxy_3d")) > 0) / hit_count if hit_count > 0 else 0.0
            )
            avg_expectancy = (
                sum(_to_float(row.get("expectancy_proxy_3d")) for row in hits) / hit_count if hit_count > 0 else 0.0
            )
            avg_adverse = (
                sum(_to_float(row.get("max_adverse_return_3d")) for row in hits) / hit_count if hit_count > 0 else 0.0
            )
            original_hit_days = len({str(row["signal_trade_date"]) for row in hits if original_map.get(str(row["signal_trade_date"]), False)})
            new_hit_days = len({str(row["signal_trade_date"]) for row in hits if not original_map.get(str(row["signal_trade_date"]), False)})
            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "expanded_window_day_count": len(expanded_days),
                    "candidate_base_row_count": len(candidate_base_rows),
                    "hit_row_count": hit_count,
                    "hit_day_count": hit_day_count,
                    "original_hit_day_count": original_hit_days,
                    "new_hit_day_count": new_hit_days,
                    "hit_day_rate": round(hit_day_count / len(expanded_days), 6) if expanded_days else 0.0,
                    "positive_expectancy_hit_rate": round(positive_rate, 6),
                    "avg_expectancy_proxy_3d": round(avg_expectancy, 6),
                    "avg_max_adverse_return_3d": round(avg_adverse, 6),
                }
            )
            for row in hits:
                signal_trade_date = str(row["signal_trade_date"])
                row_key = (signal_trade_date, str(row["symbol"]))
                hit_rows.append(
                    {
                        "variant_name": variant_name,
                        "signal_trade_date": signal_trade_date,
                        "symbol": str(row["symbol"]),
                        "earliest_visible_checkpoint": row.get("earliest_visible_checkpoint"),
                        "late_confirmation_checkpoint": earliest_late_checkpoint(row_key),
                        "board_avg_return": board_ret_map.get(signal_trade_date, 0.0),
                        "board_breadth": breadth_map.get(signal_trade_date, 0.0),
                        "under_exposure_gap": gap_map.get(signal_trade_date, 0.0),
                        "is_original_top_miss": original_map.get(signal_trade_date, False),
                        "visible_pc1_score": round(_to_float(row.get("visible_pc1_score")), 6),
                        "visible_pc2_score": round(_to_float(row.get("visible_pc2_score")), 6),
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v116r_cpo_corrected_cooled_shadow_expanded_window_validation_v1",
            "expanded_window_day_count": len(expanded_days),
            "candidate_base_row_count": len(candidate_base_rows),
            "retained_variant_name": "double_confirm_late_quarter",
            "recommended_next_posture": "use_expanded_window_validation_to_judge_whether_the_corrected_candidate_survives_beyond_the_original_top_miss_family",
        }
        interpretation = [
            "V1.16R revalidates the corrected cooled-shadow candidate on the expanded 10-day repaired-window surface rather than the original 6-day top-miss subset.",
            "This remains candidate-only and audit-facing: the goal is to see whether the corrected candidate survives beyond the same old repaired family rather than to create a new replay law.",
            "The result should be read as an expansion of the audit surface, not as replay-facing promotion evidence.",
        ]
        return V116RCpoCorrectedCooledShadowExpandedWindowValidationReport(
            summary=summary,
            variant_rows=variant_rows,
            hit_rows=hit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116RCpoCorrectedCooledShadowExpandedWindowValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116RCpoCorrectedCooledShadowExpandedWindowValidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116r_cpo_corrected_cooled_shadow_expanded_window_validation_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
