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
from a_share_quant.strategy.v115j_cpo_high_dimensional_intraday_pca_band_audit_v1 import (
    V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer,
    _quantile,
)
from a_share_quant.strategy.v115o_cpo_intraday_strict_band_signal_timing_audit_v1 import (
    _build_feature_row_from_prefix,
    _filter_prefix_rows,
    _robust_stats,
    _rz,
)
from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    V115PCpoIntradayTimingAwareOverlayReplayAnalyzer,
    _costs,
    _load_daily_bars,
    _max_drawdown,
    parse_trade_date,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _timing_bucket_from_label(label: str) -> str:
    if label <= "14:00":
        return "intraday_same_session"
    if label <= "14:30":
        return "late_session"
    return "post_close_or_next_day"


def _checkpoint_label(raw_checkpoint: str) -> str:
    hhmmss = raw_checkpoint[8:14]
    return f"{hhmmss[0:2]}:{hhmmss[2:4]}"


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V116JCpoVisibleOnlyBroaderShadowReplayReport:
    summary: dict[str, Any]
    timing_rows: list[dict[str, Any]]
    checkpoint_rows: list[dict[str, Any]]
    overlay_order_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "timing_rows": self.timing_rows,
            "checkpoint_rows": self.checkpoint_rows,
            "overlay_order_rows": self.overlay_order_rows,
            "interpretation": self.interpretation,
        }


class V116JCpoVisibleOnlyBroaderShadowReplayAnalyzer:
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

    def _same_day_next_bar_open(
        self,
        *,
        rows_30m: list[dict[str, Any]],
        checkpoint_label: str,
    ) -> float | None:
        checkpoint_hhmm = checkpoint_label.replace(":", "")
        for row in rows_30m:
            row_hhmm = str(row["time"])[8:12]
            if row_hhmm > checkpoint_hhmm:
                return _to_float(row["open"])
        return None

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v114w_payload: dict[str, Any],
        v114x_payload: dict[str, Any],
        v116d_payload: dict[str, Any],
        pca_rows_path: Path,
        training_view_path: Path,
        feature_base_path: Path,
    ) -> V116JCpoVisibleOnlyBroaderShadowReplayReport:
        import baostock as bs

        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_day_map = {parse_trade_date(str(row["trade_date"])): row for row in baseline_day_rows}
        trade_dates = sorted(baseline_day_map.keys())
        baseline_positions_eod = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_positions_eod(
            baseline_executed_orders, trade_dates
        )
        baseline_sell_fraction = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_sell_fraction(
            baseline_executed_orders
        )
        repaired_miss_rows = list(v114w_payload.get("top_opportunity_miss_rows", []))
        wider_days = {str(row["trade_date"]) for row in repaired_miss_rows}
        miss_day_map = {str(row["trade_date"]): row for row in repaired_miss_rows}
        strong_floor = 0.3
        two_line_floor = 0.45
        for row in list(v114x_payload.get("exposure_floor_rows", [])):
            board_state = str(row.get("board_state"))
            if board_state == "strong_board_with_one_high_probability_line":
                strong_floor = _to_float(row.get("minimum_target_gross_exposure"), strong_floor)
            elif board_state == "strong_board_with_two_or_more_credible_lines":
                two_line_floor = _to_float(row.get("minimum_target_gross_exposure"), two_line_floor)

        pca_rows = _load_csv_rows(pca_rows_path)
        candidate_base_rows = [
            row
            for row in pca_rows
            if str(row.get("action_context")) == "add_vs_hold"
            and str(row.get("signal_trade_date")) in wider_days
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

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        try:
            bars_30m_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for row in candidate_base_rows:
                symbol = str(row["symbol"])
                signal_trade_date = str(row["signal_trade_date"])
                raw_by_freq: dict[str, list[dict[str, Any]]] = {}
                for frequency in ("5", "15", "30", "60"):
                    query_rows = self._query_bars_with_relogin(
                        bs_module=bs,
                        symbol=symbol,
                        trade_date=signal_trade_date,
                        frequency=frequency,
                    )
                    raw_by_freq[frequency] = query_rows
                    if frequency == "30":
                        bars_30m_cache[(signal_trade_date, symbol)] = query_rows

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
                        "timing_bucket": "unresolved" if earliest_pass_checkpoint is None else _timing_bucket_from_label(earliest_pass_checkpoint),
                        "earliest_visible_checkpoint": earliest_pass_checkpoint,
                        "visible_pc1_score": None if earliest_pass_scores is None else round(earliest_pass_scores[0], 6),
                        "visible_pc2_score": None if earliest_pass_scores is None else round(earliest_pass_scores[1], 6),
                        "expectancy_proxy_3d": round(_to_float(row.get("expectancy_proxy_3d")), 6),
                        "max_adverse_return_3d": round(_to_float(row.get("max_adverse_return_3d")), 6),
                    }
                )

            overlay_fill_fraction = 0.5
            per_symbol_position_add_cap_ratio = 0.5
            max_extra_notional_per_symbol = 100_000.0

            cash = 1_000_000.0
            positions: dict[str, int] = {}
            baseline_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
            for row in baseline_executed_orders:
                baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)

            overlay_order_rows: list[dict[str, Any]] = []
            equity_curve: list[float] = []
            visible_map = {(str(row["signal_trade_date"]), str(row["symbol"])): row for row in timing_rows}

            for trade_date in trade_dates:
                for row in baseline_orders_by_exec.get(trade_date, []):
                    symbol = str(row["symbol"])
                    quantity = int(row["quantity"])
                    action = str(row["action"])
                    execution_price = _to_float(row["execution_price"])
                    rationale = str(row.get("rationale", ""))
                    if action == "buy":
                        notional = quantity * execution_price
                        cash -= notional + _costs(action="buy", notional=notional)["total_cost"]
                        positions[symbol] = positions.get(symbol, 0) + quantity
                    else:
                        current_qty = positions.get(symbol, 0)
                        if current_qty <= 0:
                            continue
                        if rationale == "close_from_holding_veto":
                            sell_qty = current_qty
                        elif rationale == "reduce_from_board_state_episode":
                            fraction = baseline_sell_fraction.get((trade_date, symbol), 0.0)
                            sell_qty = int((current_qty * fraction) // 100) * 100
                            if sell_qty <= 0:
                                sell_qty = min(current_qty, 100 if current_qty >= 100 else current_qty)
                        else:
                            sell_qty = min(current_qty, quantity)
                        sell_qty = min(current_qty, sell_qty)
                        if sell_qty <= 0:
                            continue
                        notional = sell_qty * execution_price
                        cash += notional - _costs(action="sell", notional=notional)["total_cost"]
                        positions[symbol] = max(0, current_qty - sell_qty)

                signal_trade_date = str(trade_date)
                miss_row = miss_day_map.get(signal_trade_date)
                if miss_row is None:
                    market_value = 0.0
                    for symbol, qty in positions.items():
                        bar = daily_bars.get((symbol, trade_date))
                        if bar is not None:
                            market_value += qty * _to_float(bar["close"])
                    equity_curve.append(cash + market_value)
                    continue

                valid_hits: list[dict[str, Any]] = []
                for row in candidate_base_rows:
                    if str(row["signal_trade_date"]) != signal_trade_date:
                        continue
                    symbol = str(row["symbol"])
                    visible = visible_map.get((signal_trade_date, symbol))
                    if visible is None or str(visible["timing_bucket"]) != "intraday_same_session":
                        continue
                    held_qty = baseline_positions_eod.get((trade_date, symbol), 0)
                    if held_qty <= 0:
                        continue
                    close_row = daily_bars.get((symbol, trade_date))
                    if close_row is None:
                        continue
                    rows_30m = bars_30m_cache.get((signal_trade_date, symbol), [])
                    execution_price = self._same_day_next_bar_open(
                        rows_30m=rows_30m,
                        checkpoint_label=str(visible["earliest_visible_checkpoint"]),
                    )
                    if execution_price is None or execution_price <= 0:
                        continue
                    held_value = held_qty * _to_float(close_row["close"])
                    valid_hits.append(
                        {
                            "symbol": symbol,
                            "held_value": held_value,
                            "execution_price": execution_price,
                            "timing_checkpoint": str(visible["earliest_visible_checkpoint"]),
                            "visible_pc1_score": _to_float(visible.get("visible_pc1_score")),
                            "visible_pc2_score": _to_float(visible.get("visible_pc2_score")),
                        }
                    )

                baseline_day = baseline_day_map[trade_date]
                signal_equity = _to_float(baseline_day.get("equity_after_close"))
                current_exposure = _to_float(miss_row.get("gross_exposure_after_close"))
                board_avg_return = _to_float(miss_row.get("board_avg_return"))
                board_breadth = _to_float(miss_row.get("board_breadth"))
                target_floor = (
                    two_line_floor
                    if board_avg_return >= 0.05 and board_breadth >= 0.8
                    else strong_floor
                )
                gap_to_floor = max(target_floor - current_exposure, 0.0)
                if valid_hits and signal_equity > 0 and gap_to_floor > 0:
                    gross_pool = signal_equity * gap_to_floor * overlay_fill_fraction
                    per_hit_pool = gross_pool / len(valid_hits)
                    for hit in valid_hits:
                        capped_notional = min(
                            per_hit_pool,
                            hit["held_value"] * per_symbol_position_add_cap_ratio,
                            max_extra_notional_per_symbol,
                        )
                        quantity = int((capped_notional / hit["execution_price"]) // 100) * 100
                        affordable_qty = int(cash // (hit["execution_price"] * 1.0018))
                        affordable_qty = (affordable_qty // 100) * 100
                        quantity = min(quantity, max(0, affordable_qty))
                        if quantity <= 0:
                            continue
                        notional = quantity * hit["execution_price"]
                        costs = _costs(action="buy", notional=notional)
                        cash -= notional + costs["total_cost"]
                        positions[hit["symbol"]] = positions.get(hit["symbol"], 0) + quantity
                        overlay_order_rows.append(
                            {
                                "signal_trade_date": signal_trade_date,
                                "execution_trade_date": signal_trade_date,
                                "symbol": hit["symbol"],
                                "action": "buy",
                                "quantity": quantity,
                                "execution_price": round(hit["execution_price"], 4),
                                "notional": round(notional, 4),
                                "commission": costs["commission"],
                                "stamp_tax": costs["stamp_tax"],
                                "slippage": costs["slippage"],
                                "total_cost": costs["total_cost"],
                                "timing_bucket": "intraday_same_session",
                                "timing_checkpoint": hit["timing_checkpoint"],
                                "visible_pc1_score": round(hit["visible_pc1_score"], 6),
                                "visible_pc2_score": round(hit["visible_pc2_score"], 6),
                                "overlay_posture": "visible_only_broader_repaired_window_shadow_replay",
                            }
                        )

                market_value = 0.0
                for symbol, qty in positions.items():
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is not None:
                        market_value += qty * _to_float(bar["close"])
                equity_curve.append(cash + market_value)
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        baseline_equity_curve = [_to_float(row.get("equity_after_close")) for row in baseline_day_rows]
        intraday_rows = [row for row in timing_rows if str(row["timing_bucket"]) == "intraday_same_session"]
        summary = {
            "acceptance_posture": "freeze_v116j_cpo_visible_only_broader_shadow_replay_v1",
            "candidate_posture": "shadow_only_not_promotable",
            "filter_name": "pc1_or_pc2_q_0p25",
            "wider_candidate_row_count": len(candidate_base_rows),
            "intraday_same_session_candidate_count": len(intraday_rows),
            "executed_overlay_order_count": len(overlay_order_rows),
            "baseline_final_equity": round(baseline_equity_curve[-1], 4),
            "shadow_replay_final_equity": round(equity_curve[-1], 4),
            "final_equity_delta_vs_baseline": round(equity_curve[-1] - baseline_equity_curve[-1], 4),
            "baseline_max_drawdown": _max_drawdown(baseline_equity_curve),
            "shadow_replay_max_drawdown": _max_drawdown(equity_curve),
            "overlay_total_transaction_cost": round(sum(_to_float(row["total_cost"]) for row in overlay_order_rows), 4),
            "recommended_next_posture": "use_v116j_as_broader_visible_only_shadow_reference_before_any_new_promotion_discussion",
        }
        interpretation = [
            "V1.16J rebuilds the broader repaired-window shadow replay from point-in-time-visible checkpoint scores rather than relying on prior miss-window hit tables.",
            "The replay remains held-position only, timing-aware, and add-only; it does not open new names or override baseline sell-side controls.",
            "This is a replay-facing shadow candidate for wider repaired under-exposure windows, not a promotable add law.",
        ]
        return V116JCpoVisibleOnlyBroaderShadowReplayReport(
            summary=summary,
            timing_rows=timing_rows,
            checkpoint_rows=checkpoint_rows,
            overlay_order_rows=overlay_order_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116JCpoVisibleOnlyBroaderShadowReplayReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116JCpoVisibleOnlyBroaderShadowReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v114x_payload=json.loads((repo_root / "reports" / "analysis" / "v114x_cpo_probability_expectancy_sizing_framework_repaired_v1.json").read_text(encoding="utf-8")),
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116j_cpo_visible_only_broader_shadow_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
