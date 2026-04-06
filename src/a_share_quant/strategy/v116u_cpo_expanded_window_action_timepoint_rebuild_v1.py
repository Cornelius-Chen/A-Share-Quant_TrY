from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v115b_cpo_midfreq_intraday_factor_extraction_v1 import (
    _to_baostock_symbol,
    _window_features,
)
from a_share_quant.strategy.v115d_cpo_midfreq_action_outcome_training_table_v1 import (
    V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer,
)
from a_share_quant.strategy.v115h_cpo_high_dimensional_intraday_feature_base_table_v1 import (
    V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer,
)
from a_share_quant.strategy.v115i_cpo_high_dimensional_intraday_action_training_pilot_v1 import (
    V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v115j_cpo_high_dimensional_intraday_pca_band_audit_v1 import (
    V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer,
    _quantile,
    _segment_band,
)
from a_share_quant.strategy.v115o_cpo_intraday_strict_band_signal_timing_audit_v1 import (
    _robust_stats,
    _rz,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
class V116UCpoExpandedWindowActionTimepointRebuildReport:
    summary: dict[str, Any]
    rebuilt_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "rebuilt_rows": self.rebuilt_rows,
            "interpretation": self.interpretation,
        }


class V116UCpoExpandedWindowActionTimepointRebuildAnalyzer:
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
        v116s_payload: dict[str, Any],
        original_pca_rows_path: Path,
        training_view_path: Path,
        feature_base_path: Path,
        daily_bar_path: Path,
    ) -> tuple[V116UCpoExpandedWindowActionTimepointRebuildReport, list[dict[str, Any]], list[dict[str, Any]]]:
        coverage_rows = list(v116s_payload.get("coverage_rows", []))
        gap_rows = [row for row in coverage_rows if bool(row.get("coverage_gap"))]

        original_pca_rows = _load_csv_rows(original_pca_rows_path)
        training_view_rows = _load_csv_rows(training_view_path)
        feature_base_rows = _load_csv_rows(feature_base_path)

        train_rows = [dict(row) for row in training_view_rows if str(row.get("split_group")) == "train"]
        x_train = np.array(
            [[_to_float(row.get(feature)) for feature in V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer.FEATURE_COLUMNS] for row in train_rows],
            dtype=float,
        )
        feature_mean = x_train.mean(axis=0)
        x_centered = x_train - feature_mean
        _, _, vt = np.linalg.svd(x_centered, full_matrices=False)
        components = vt[:3]
        train_scores = components @ x_centered.T
        pc1_values = sorted(float(value) for value in train_scores[0])
        pc2_values = sorted(float(value) for value in train_scores[1])
        pc1_low = _quantile(pc1_values, 0.33)
        pc1_high = _quantile(pc1_values, 0.67)
        pc2_low = _quantile(pc2_values, 0.33)
        pc2_high = _quantile(pc2_values, 0.67)

        raw_feature_names = sorted(
            {
                feature[:-3] if feature.endswith("_rz") else feature
                for feature in V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer.FEATURE_COLUMNS
            }
        )
        feature_stats = _robust_stats(feature_base_rows, raw_feature_names)

        daily_loader = V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer(repo_root=self.repo_root)
        daily_bars = daily_loader._load_daily_bars(daily_bar_path)
        next_trade_date_map = V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer._next_trade_date_map(daily_bars)
        ordered_dates = sorted({dt for _, dt in daily_bars.keys()})

        rebuilt_rows: list[dict[str, Any]] = []

        import baostock as bs

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        try:
            for gap_row in gap_rows:
                signal_trade_date = str(gap_row["trade_date"])
                under_exposure_gap = _to_float(gap_row.get("under_exposure_gap"))
                for symbol in list(gap_row.get("held_mature_symbols", [])):
                    feature_blocks: dict[str, dict[str, float]] = {}
                    for frequency in ("5", "15", "30", "60"):
                        feature_blocks[frequency] = _window_features(
                            self._query_bars_with_relogin(
                                bs_module=bs,
                                symbol=symbol,
                                trade_date=signal_trade_date,
                                frequency=frequency,
                            ),
                            frequency=frequency,
                        )

                    assembled = {
                        "symbol": symbol,
                        "trade_date": signal_trade_date,
                        "signal_trade_date": signal_trade_date,
                        "board_phase": "main_markup",
                        "role_family": "expanded_window_rebuild",
                        "control_label": "eligibility",
                        "action_context": "add_vs_hold",
                        "held_before_signal": True,
                        "is_repaired_miss_window": False,
                        "is_expanded_window_rebuild": True,
                        "rebuild_reason": "coverage_gap_repair",
                        "under_exposure_gap": round(under_exposure_gap, 6),
                        **feature_blocks["5"],
                        **feature_blocks["15"],
                        **feature_blocks["30"],
                        **feature_blocks["60"],
                    }

                    signal_date = parse_trade_date(signal_trade_date)
                    execution_date = next_trade_date_map.get(signal_date)
                    if execution_date is None:
                        continue
                    execution_bar = daily_bars.get((symbol, execution_date))
                    if execution_bar is None:
                        continue
                    assembled["execution_trade_date"] = str(execution_date)
                    assembled["execution_open_price"] = round(float(execution_bar["open"]), 6)

                    for horizon in (1, 3, 5):
                        future_rows = V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer._future_path(
                            symbol=symbol,
                            execution_date=execution_date,
                            daily_bars=daily_bars,
                            ordered_dates=ordered_dates,
                            horizon=horizon,
                        )
                        labels = V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer._compute_horizon_labels(
                            execution_open=float(execution_bar["open"]),
                            future_rows=future_rows,
                        )
                        assembled[f"forward_close_return_{horizon}d"] = labels["forward_close_return"]
                        assembled[f"max_favorable_return_{horizon}d"] = labels["max_favorable_return"]
                        assembled[f"max_adverse_return_{horizon}d"] = labels["max_adverse_return"]
                        assembled[f"expectancy_proxy_{horizon}d"] = labels["expectancy_proxy"]

                    fwd3 = _to_float(assembled["forward_close_return_3d"])
                    mae3 = _to_float(assembled["max_adverse_return_3d"])
                    assembled["action_favored_3d"] = bool(fwd3 > 0.03 and mae3 > -0.04)
                    assembled["coarse_label"] = V115ICpoHighDimensionalIntradayActionTrainingPilotAnalyzer._coarse_label(assembled)

                    feature_row = V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer._build_feature_row(assembled)
                    final_row = {
                        "symbol": symbol,
                        "signal_trade_date": signal_trade_date,
                        "execution_trade_date": str(execution_date),
                        "action_context": "add_vs_hold",
                        "board_phase": "main_markup",
                        "role_family": "expanded_window_rebuild",
                        "control_label": "eligibility",
                        "action_favored_3d": assembled["action_favored_3d"],
                        "expectancy_proxy_3d": assembled["expectancy_proxy_3d"],
                        "forward_close_return_3d": assembled["forward_close_return_3d"],
                        "max_adverse_return_3d": assembled["max_adverse_return_3d"],
                        "max_favorable_return_3d": assembled["max_favorable_return_3d"],
                        "under_exposure_gap": round(under_exposure_gap, 6),
                        "is_expanded_window_rebuild": True,
                        "coarse_label": assembled["coarse_label"],
                    }
                    feature_vector: list[float] = []
                    for feature in V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer.FEATURE_COLUMNS:
                        if feature.endswith("_rz"):
                            raw_name = feature[:-3]
                            raw_value = _to_float(feature_row.get(raw_name))
                            med, iqr = feature_stats[raw_name]
                            rz_value = _rz(raw_value, med=med, iqr=iqr)
                            final_row[feature] = round(rz_value, 6)
                            feature_vector.append(rz_value)
                        else:
                            raw_value = _to_float(feature_row.get(feature))
                            final_row[feature] = round(raw_value, 6)
                            feature_vector.append(raw_value)

                    vector = np.array(feature_vector, dtype=float)
                    scores = components @ (vector - feature_mean)
                    final_row["pc1_score"] = round(float(scores[0]), 6)
                    final_row["pc2_score"] = round(float(scores[1]), 6)
                    final_row["pc3_score"] = round(float(scores[2]), 6)
                    final_row["pc1_band"] = _segment_band(float(scores[0]), low=pc1_low, high=pc1_high)
                    final_row["pc2_band"] = _segment_band(float(scores[1]), low=pc2_low, high=pc2_high)
                    final_row["state_band"] = f"pc1_{final_row['pc1_band']}__pc2_{final_row['pc2_band']}"
                    rebuilt_rows.append(final_row)
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        existing_keys = {
            (str(row.get("signal_trade_date")), str(row.get("symbol")), str(row.get("action_context")))
            for row in original_pca_rows
        }
        merged_rows = list(original_pca_rows)
        for row in rebuilt_rows:
            key = (str(row.get("signal_trade_date")), str(row.get("symbol")), str(row.get("action_context")))
            if key not in existing_keys:
                merged_rows.append(row)
                existing_keys.add(key)

        rebuilt_days = sorted({str(row["signal_trade_date"]) for row in rebuilt_rows})
        summary = {
            "acceptance_posture": "freeze_v116u_cpo_expanded_window_action_timepoint_rebuild_v1",
            "requested_gap_day_count": len(gap_rows),
            "rebuilt_day_count": len(rebuilt_days),
            "rebuilt_row_count": len(rebuilt_rows),
            "merged_pca_row_count": len(merged_rows),
            "recommended_next_posture": "rerun_expanded_window_candidate_coverage_audit_on_merged_pca_rows_before_more_visible_only_validation",
        }
        interpretation = [
            "V1.16U rebuilds the intraday add-vs-hold action-timepoint rows for the true expanded-window coverage-gap days rather than retuning visible-only thresholds again.",
            "The rebuild keeps the original PCA geometry fixed and only appends newly constructed rows for held mature names on 2023-11-07, 2024-01-18, and 2024-01-23.",
            "This is a coverage repair step, not a new law-discovery step.",
        ]
        report = V116UCpoExpandedWindowActionTimepointRebuildReport(
            summary=summary,
            rebuilt_rows=rebuilt_rows,
            interpretation=interpretation,
        )
        return report, rebuilt_rows, merged_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V116UCpoExpandedWindowActionTimepointRebuildReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116UCpoExpandedWindowActionTimepointRebuildAnalyzer(repo_root=repo_root)
    result, rebuilt_rows, merged_rows = analyzer.analyze(
        v116s_payload=json.loads((repo_root / "reports" / "analysis" / "v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1.json").read_text(encoding="utf-8")),
        original_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        daily_bar_path=repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv",
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_expanded_window_rebuilt_rows_v1.csv",
        rows=rebuilt_rows,
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
        rows=merged_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116u_cpo_expanded_window_action_timepoint_rebuild_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
