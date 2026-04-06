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


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _checkpoint_label(raw_checkpoint: str) -> str:
    hhmmss = raw_checkpoint[8:14]
    return f"{hhmmss[0:2]}:{hhmmss[2:4]}"


@dataclass(slots=True)
class V116ZCpoQualitySideCooledRefinementReport:
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


class V116ZCpoQualitySideCooledRefinementAnalyzer:
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
        rebuilt_pca_rows_path: Path,
        training_view_path: Path,
        feature_base_path: Path,
    ) -> V116ZCpoQualitySideCooledRefinementReport:
        expanded_rows = list(v116q_payload.get("expanded_window_rows", []))
        expanded_days = {str(row["trade_date"]) for row in expanded_rows}
        gap_map = {str(row["trade_date"]): _to_float(row.get("under_exposure_gap")) for row in expanded_rows}
        breadth_map = {str(row["trade_date"]): _to_float(row.get("board_breadth")) for row in expanded_rows}
        board_ret_map = {str(row["trade_date"]): _to_float(row.get("board_avg_return")) for row in expanded_rows}
        original_map = {str(row["trade_date"]): bool(row.get("is_original_top_miss")) for row in expanded_rows}

        pca_rows = _load_csv_rows(rebuilt_pca_rows_path)
        candidate_base_rows = [
            row for row in pca_rows
            if str(row.get("action_context")) == "add_vs_hold"
            and str(row.get("signal_trade_date")) in expanded_days
        ]

        threshold_map = {
            round(_to_float(row.get("quantile")), 6): dict(row)
            for row in list(v116d_payload.get("threshold_rows", []))
        }
        selected_quantiles = (0.2, 0.25, 0.33, 0.4)
        selected_thresholds = {
            q: {
                "pc1": _to_float(threshold_map[round(q, 6)]["pc1_low_threshold"]),
                "pc2": _to_float(threshold_map[round(q, 6)]["pc2_low_threshold"]),
            }
            for q in selected_quantiles
        }

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

                visible_scores_by_checkpoint: dict[str, tuple[float, float]] = {}
                earliest_any_visible: str | None = None
                pass_by_quantile: dict[float, dict[str, bool]] = {q: {} for q in selected_quantiles}
                pass_axis_by_quantile: dict[float, dict[str, str]] = {q: {} for q in selected_quantiles}
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
                    checkpoint_label = _checkpoint_label(checkpoint)
                    visible_scores_by_checkpoint[checkpoint_label] = (pc1_score, pc2_score)
                    if earliest_any_visible is None:
                        earliest_any_visible = checkpoint_label
                    axis_marker = "none"
                    for q, thresholds in selected_thresholds.items():
                        pc1_pass = pc1_score <= thresholds["pc1"]
                        pc2_pass = pc2_score <= thresholds["pc2"]
                        passed = pc1_pass or pc2_pass
                        pass_by_quantile[q][checkpoint_label] = passed
                        if pc1_pass and pc2_pass:
                            pass_axis_by_quantile[q][checkpoint_label] = "both"
                        elif pc1_pass:
                            pass_axis_by_quantile[q][checkpoint_label] = "pc1"
                        elif pc2_pass:
                            pass_axis_by_quantile[q][checkpoint_label] = "pc2"
                        else:
                            pass_axis_by_quantile[q][checkpoint_label] = "none"
                        if q == 0.25:
                            axis_marker = pass_axis_by_quantile[q][checkpoint_label]
                    checkpoint_rows.append(
                        {
                            "signal_trade_date": signal_trade_date,
                            "symbol": symbol,
                            "checkpoint": checkpoint_label,
                            "pc1_score": round(pc1_score, 6),
                            "pc2_score": round(pc2_score, 6),
                            "pass_axis_q_0p25": axis_marker,
                        }
                    )

                timing_rows.append(
                    {
                        "signal_trade_date": signal_trade_date,
                        "symbol": symbol,
                        "earliest_any_visible_checkpoint": earliest_any_visible,
                        "visible_scores_by_checkpoint": visible_scores_by_checkpoint,
                        "pass_by_quantile": pass_by_quantile,
                        "pass_axis_by_quantile": pass_axis_by_quantile,
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        def has_pass(row: dict[str, Any], quantile: float, checkpoint: str) -> bool:
            return bool(dict(row["pass_by_quantile"]).get(quantile, {}).get(checkpoint, False))

        def pass_axis(row: dict[str, Any], quantile: float, checkpoint: str) -> str:
            return str(dict(row["pass_axis_by_quantile"]).get(quantile, {}).get(checkpoint, "none"))

        def earliest_visible_quantile(row: dict[str, Any], quantile: float) -> str | None:
            for checkpoint in ("10:30", "11:00", "14:00", "14:30", "15:00"):
                if has_pass(row, quantile, checkpoint):
                    return checkpoint
            return None

        def late_confirmation_checkpoint(row: dict[str, Any], quantile: float) -> str | None:
            for checkpoint in ("14:00", "14:30"):
                if has_pass(row, quantile, checkpoint):
                    return checkpoint
            return None

        variants: list[tuple[str, float, bool]] = [
            ("cooled_q_0p20", 0.2, False),
            ("cooled_q_0p25", 0.25, False),
            ("cooled_q_0p33", 0.33, False),
            ("cooled_q_0p40", 0.4, False),
            ("cooled_q_0p25_pc1_only", 0.25, True),
        ]

        variant_rows: list[dict[str, Any]] = []
        hit_rows: list[dict[str, Any]] = []

        for variant_name, quantile, pc1_only in variants:
            hits: list[dict[str, Any]] = []
            pc2_axis_active = False
            for row in timing_rows:
                # timing structure is fixed; only visible-score quality gate changes
                q_1030 = has_pass(row, quantile, "10:30")
                q_1100 = has_pass(row, quantile, "11:00")
                late_cp = late_confirmation_checkpoint(row, quantile)
                if pc1_only:
                    q_1030 = pass_axis(row, quantile, "10:30") in {"pc1", "both"}
                    q_1100 = pass_axis(row, quantile, "11:00") in {"pc1", "both"}
                    late_cp = next(
                        (
                            checkpoint
                            for checkpoint in ("14:00", "14:30")
                            if pass_axis(row, quantile, checkpoint) in {"pc1", "both"}
                        ),
                        None,
                    )
                if q_1030 and q_1100 and late_cp is not None:
                    hits.append(row)
                    if any(pass_axis(row, quantile, checkpoint) == "pc2" for checkpoint in ("10:30", "11:00", "14:00", "14:30")):
                        pc2_axis_active = True

            hit_day_count = len({str(row["signal_trade_date"]) for row in hits})
            positive_rate = (
                sum(1 for row in hits if _to_float(row.get("expectancy_proxy_3d")) > 0) / len(hits)
                if hits
                else 0.0
            )
            avg_expectancy = (
                sum(_to_float(row.get("expectancy_proxy_3d")) for row in hits) / len(hits)
                if hits
                else 0.0
            )
            avg_adverse = (
                sum(_to_float(row.get("max_adverse_return_3d")) for row in hits) / len(hits)
                if hits
                else 0.0
            )

            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "quantile": quantile,
                    "pc1_only": pc1_only,
                    "hit_row_count": len(hits),
                    "hit_day_count": hit_day_count,
                    "positive_expectancy_hit_rate": round(positive_rate, 6),
                    "avg_expectancy_proxy_3d": round(avg_expectancy, 6),
                    "avg_max_adverse_return_3d": round(avg_adverse, 6),
                    "pc2_axis_active": pc2_axis_active,
                }
            )
            for row in hits:
                day = str(row["signal_trade_date"])
                scores_1030 = dict(row["visible_scores_by_checkpoint"]).get("10:30")
                hit_rows.append(
                    {
                        "variant_name": variant_name,
                        "signal_trade_date": day,
                        "symbol": str(row["symbol"]),
                        "is_original_top_miss": bool(original_map.get(day, False)),
                        "earliest_visible_checkpoint": earliest_visible_quantile(row, quantile),
                        "late_confirmation_checkpoint": late_confirmation_checkpoint(row, quantile),
                        "board_avg_return": board_ret_map.get(day, 0.0),
                        "board_breadth": breadth_map.get(day, 0.0),
                        "under_exposure_gap": gap_map.get(day, 0.0),
                        "visible_pc1_score_1030": None if scores_1030 is None else round(_to_float(scores_1030[0]), 6),
                        "visible_pc2_score_1030": None if scores_1030 is None else round(_to_float(scores_1030[1]), 6),
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )

        variant_map = {row["variant_name"]: row for row in variant_rows}
        recommended_variant_name = "cooled_q_0p20"
        if variant_map["cooled_q_0p20"]["hit_row_count"] == 0:
            recommended_variant_name = "cooled_q_0p25"

        summary = {
            "acceptance_posture": "freeze_v116z_cpo_quality_side_cooled_refinement_v1",
            "expanded_window_day_count": len(expanded_days),
            "candidate_base_row_count": len(candidate_base_rows),
            "authoritative_current_problem": "quality_discrimination_after_coverage_repair",
            "effective_visible_axis": "pc1",
            "pc2_axis_active_any_variant": any(bool(row["pc2_axis_active"]) for row in variant_rows),
            "recommended_quality_variant": recommended_variant_name,
            "recommended_next_posture": "keep_candidate_only_and_use_quality_side_quantile_family_as_next_visible_only_refinement_surface",
        }
        interpretation = [
            "V1.16Z keeps the cooled timing structure fixed and only changes the visible-score quality gate, so this is a quality-side refinement rather than another timing or coverage experiment.",
            "The sweep also audits whether the visible-only family is still genuinely two-dimensional after repair or whether it has collapsed into an effectively PC1-driven line.",
            "Any retained outcome remains candidate-only because the quantile family is still same-sample and same-board; this step is about direction and boundary, not promotion.",
        ]
        return V116ZCpoQualitySideCooledRefinementReport(
            summary=summary,
            variant_rows=variant_rows,
            hit_rows=hit_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116ZCpoQualitySideCooledRefinementReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116ZCpoQualitySideCooledRefinementAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        rebuilt_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116z_cpo_quality_side_cooled_refinement_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
