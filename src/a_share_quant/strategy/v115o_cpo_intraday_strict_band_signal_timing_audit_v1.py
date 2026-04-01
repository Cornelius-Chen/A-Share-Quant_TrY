from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v115b_cpo_midfreq_intraday_factor_extraction_v1 import _window_features
from a_share_quant.strategy.v115j_cpo_high_dimensional_intraday_pca_band_audit_v1 import (
    V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer,
    _quantile,
    _segment_band,
)


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _quantile_raw(sorted_values: list[float], q: float) -> float:
    return _quantile(sorted_values, q)


def _robust_stats(rows: list[dict[str, Any]], feature_names: list[str]) -> dict[str, tuple[float, float]]:
    stats: dict[str, tuple[float, float]] = {}
    for feature_name in feature_names:
        values = sorted(_to_float(row.get(feature_name)) for row in rows)
        med = values[len(values) // 2] if values else 0.0
        q1 = _quantile_raw(values, 0.25)
        q3 = _quantile_raw(values, 0.75)
        stats[feature_name] = (med, q3 - q1)
    return stats


def _rz(value: float, *, med: float, iqr: float) -> float:
    scale = max(iqr, 1e-9)
    return (value - med) / scale


def _build_feature_row_from_prefix(feature_blocks: dict[str, dict[str, float]]) -> dict[str, float]:
    row: dict[str, float] = {}
    for prefix, payload in feature_blocks.items():
        row.update(payload)
    row["d5_30_close_vs_vwap"] = round(_to_float(row.get("f5_close_vs_vwap")) - _to_float(row.get("f30_close_vs_vwap")), 6)
    row["d15_60_close_vs_vwap"] = round(_to_float(row.get("f15_close_vs_vwap")) - _to_float(row.get("f60_close_vs_vwap")), 6)
    row["d5_30_last_bar_return"] = round(_to_float(row.get("f5_last_bar_return")) - _to_float(row.get("f30_last_bar_return")), 6)
    row["d15_60_last_bar_return"] = round(_to_float(row.get("f15_last_bar_return")) - _to_float(row.get("f60_last_bar_return")), 6)
    row["d5_30_last_bar_volume_share"] = round(_to_float(row.get("f5_last_bar_volume_share")) - _to_float(row.get("f30_last_bar_volume_share")), 6)
    row["d15_60_last_bar_volume_share"] = round(_to_float(row.get("f15_last_bar_volume_share")) - _to_float(row.get("f60_last_bar_volume_share")), 6)
    row["d15_60_failed_push_proxy"] = round(_to_float(row.get("f15_failed_push_proxy")) - _to_float(row.get("f60_failed_push_proxy")), 6)
    row["d5_30_upper_shadow_ratio"] = round(_to_float(row.get("f5_upper_shadow_ratio")) - _to_float(row.get("f30_upper_shadow_ratio")), 6)
    row["d15_60_upper_shadow_ratio"] = round(_to_float(row.get("f15_upper_shadow_ratio")) - _to_float(row.get("f60_upper_shadow_ratio")), 6)
    row["d5_30_lower_shadow_ratio"] = round(_to_float(row.get("f5_lower_shadow_ratio")) - _to_float(row.get("f30_lower_shadow_ratio")), 6)
    row["d15_60_lower_shadow_ratio"] = round(_to_float(row.get("f15_lower_shadow_ratio")) - _to_float(row.get("f60_lower_shadow_ratio")), 6)
    row["d5_30_last_bar_upper_shadow_ratio"] = round(_to_float(row.get("f5_last_bar_upper_shadow_ratio")) - _to_float(row.get("f30_last_bar_upper_shadow_ratio")), 6)
    row["d15_60_last_bar_upper_shadow_ratio"] = round(_to_float(row.get("f15_last_bar_upper_shadow_ratio")) - _to_float(row.get("f60_last_bar_upper_shadow_ratio")), 6)
    row["d5_30_last_bar_lower_shadow_ratio"] = round(_to_float(row.get("f5_last_bar_lower_shadow_ratio")) - _to_float(row.get("f30_last_bar_lower_shadow_ratio")), 6)
    row["d15_60_last_bar_lower_shadow_ratio"] = round(_to_float(row.get("f15_last_bar_lower_shadow_ratio")) - _to_float(row.get("f60_last_bar_lower_shadow_ratio")), 6)
    return row


def _filter_prefix_rows(rows: list[dict[str, Any]], checkpoint: str) -> list[dict[str, Any]]:
    checkpoint_hhmmss = checkpoint[8:14]
    filtered: list[dict[str, Any]] = []
    for row in rows:
        row_hhmmss = str(row["time"])[8:14]
        if row_hhmmss <= checkpoint_hhmmss:
            filtered.append(row)
    return filtered


def _timing_bucket(checkpoint: str) -> str:
    if checkpoint <= "20230101140000000":
        return "intraday_same_session"
    if checkpoint <= "20230101143000000":
        return "late_session"
    return "post_close_or_next_day"


def _checkpoint_label(checkpoint: str) -> str:
    hhmmss = checkpoint[8:14]
    return f"{hhmmss[0:2]}:{hhmmss[2:4]}"


def _to_baostock_symbol(symbol: str) -> str:
    symbol = str(symbol).strip()
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return f"sh.{symbol}"
    return f"sz.{symbol}"


@dataclass(slots=True)
class V115OCpoIntradayStrictBandSignalTimingAuditReport:
    summary: dict[str, Any]
    timing_rows: list[dict[str, Any]]
    checkpoint_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "timing_rows": self.timing_rows,
            "checkpoint_rows": self.checkpoint_rows,
            "interpretation": self.interpretation,
        }


class V115OCpoIntradayStrictBandSignalTimingAuditAnalyzer:
    CHECKPOINTS = [
        "20230101103000000",
        "20230101110000000",
        "20230101140000000",
        "20230101143000000",
        "20230101150000000",
    ]

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        strict_overlay_rows: list[dict[str, Any]],
        training_view_rows: list[dict[str, Any]],
        feature_base_rows: list[dict[str, Any]],
    ) -> V115OCpoIntradayStrictBandSignalTimingAuditReport:
        import baostock as bs

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

        checkpoint_rows: list[dict[str, Any]] = []
        timing_rows: list[dict[str, Any]] = []
        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        try:
            for strict_row in strict_overlay_rows:
                symbol = str(strict_row["symbol"])
                signal_trade_date = str(strict_row["signal_trade_date"])
                raw_by_freq: dict[str, list[dict[str, Any]]] = {}
                for frequency in ("5", "15", "30", "60"):
                    rs = bs.query_history_k_data_plus(
                        _to_baostock_symbol(symbol),
                        "date,time,code,open,high,low,close,volume,amount,adjustflag",
                        start_date=signal_trade_date,
                        end_date=signal_trade_date,
                        frequency=frequency,
                        adjustflag="2",
                    )
                    if str(rs.error_code) == "10001001":
                        try:
                            bs.logout()
                        except Exception:
                            pass
                        relogin_result = bs.login()
                        if str(relogin_result.error_code) != "0":
                            raise RuntimeError(
                                f"baostock_relogin_failed:{relogin_result.error_code}:{relogin_result.error_msg}"
                            )
                        rs = bs.query_history_k_data_plus(
                            _to_baostock_symbol(symbol),
                            "date,time,code,open,high,low,close,volume,amount,adjustflag",
                            start_date=signal_trade_date,
                            end_date=signal_trade_date,
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
                    raw_by_freq[frequency] = rows

                first_strict_checkpoint: str | None = None
                first_state_band: str | None = None
                for checkpoint in self.CHECKPOINTS:
                    prefixed_blocks: dict[str, dict[str, float]] = {}
                    checkpoint_ok = True
                    for freq, rows in raw_by_freq.items():
                        checkpoint_rows_for_freq = _filter_prefix_rows(rows, checkpoint)
                        if not checkpoint_rows_for_freq:
                            checkpoint_ok = False
                            break
                        prefixed_blocks[freq] = _window_features(checkpoint_rows_for_freq, frequency=freq)
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
                    state_band = f"pc1_{_segment_band(pc1_score, low=pc1_low, high=pc1_high)}__pc2_{_segment_band(pc2_score, low=pc2_low, high=pc2_high)}"
                    is_strict = state_band in {"pc1_low__pc2_low", "pc1_high__pc2_low"}
                    checkpoint_rows.append(
                        {
                            "signal_trade_date": signal_trade_date,
                            "symbol": symbol,
                            "checkpoint": _checkpoint_label(checkpoint),
                            "pc1_score": round(pc1_score, 6),
                            "pc2_score": round(pc2_score, 6),
                            "state_band": state_band,
                            "is_strict_band": is_strict,
                        }
                    )
                    if is_strict and first_strict_checkpoint is None:
                        first_strict_checkpoint = checkpoint
                        first_state_band = state_band

                timing_rows.append(
                    {
                        "signal_trade_date": signal_trade_date,
                        "symbol": symbol,
                        "strict_band_from_v115m": str(strict_row["state_band"]),
                        "earliest_strict_checkpoint": None if first_strict_checkpoint is None else _checkpoint_label(first_strict_checkpoint),
                        "earliest_state_band": first_state_band,
                        "timing_bucket": "unresolved" if first_strict_checkpoint is None else _timing_bucket(first_strict_checkpoint),
                    }
                )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        bucket_counts: dict[str, int] = {}
        for row in timing_rows:
            bucket = str(row["timing_bucket"])
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        summary = {
            "acceptance_posture": "freeze_v115o_cpo_intraday_strict_band_signal_timing_audit_v1",
            "strict_signal_count": len(timing_rows),
            "intraday_same_session_count": bucket_counts.get("intraday_same_session", 0),
            "late_session_count": bucket_counts.get("late_session", 0),
            "post_close_or_next_day_count": bucket_counts.get("post_close_or_next_day", 0),
            "unresolved_count": bucket_counts.get("unresolved", 0),
            "recommended_next_posture": "bind_intraday_same_session_and_late_session_signals_to_timing_aware_execution_before_relying_on_t_plus_1_open",
        }
        interpretation = [
            "V1.15O audits the earliest legal checkpoint at which strict intraday add-band signals appear, instead of assuming all such signals belong to the same execution bucket.",
            "This separates intraday, late-session, and post-close signal timing and prevents the project from overusing T+1-open execution for signals that are already visible during the session.",
            "The output should feed a timing-aware replay layer rather than be read as another standalone factor study.",
        ]
        return V115OCpoIntradayStrictBandSignalTimingAuditReport(
            summary=summary,
            timing_rows=timing_rows,
            checkpoint_rows=checkpoint_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V115OCpoIntradayStrictBandSignalTimingAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    v115m_payload = json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8"))
    strict_overlay_rows = list(v115m_payload.get("strict_overlay_hit_rows", []))
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv").open("r", encoding="utf-8") as handle:
        training_view_rows = list(csv.DictReader(handle))
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv").open("r", encoding="utf-8") as handle:
        feature_base_rows = list(csv.DictReader(handle))

    analyzer = V115OCpoIntradayStrictBandSignalTimingAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        strict_overlay_rows=strict_overlay_rows,
        training_view_rows=training_view_rows,
        feature_base_rows=feature_base_rows,
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_intraday_strict_band_signal_timing_rows_v1.csv",
        rows=result.timing_rows,
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_intraday_strict_band_checkpoint_rows_v1.csv",
        rows=result.checkpoint_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115o_cpo_intraday_strict_band_signal_timing_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
