from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _to_baostock_symbol(symbol: str) -> str:
    symbol = str(symbol).strip()
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return f"sh.{symbol}"
    return f"sz.{symbol}"


def _safe_float(value: Any) -> float:
    return float(str(value))


def _default_fetch_window_rows(symbol: str, trade_date: str, frequency: str) -> list[dict[str, Any]]:
    import baostock as bs

    login_result = bs.login()
    if str(login_result.error_code) != "0":
        raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
    try:
        rs = bs.query_history_k_data_plus(
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
                    "open": _safe_float(raw[3]),
                    "high": _safe_float(raw[4]),
                    "low": _safe_float(raw[5]),
                    "close": _safe_float(raw[6]),
                    "volume": _safe_float(raw[7]),
                    "amount": _safe_float(raw[8]),
                    "adjustflag": raw[9],
                }
            )
        return rows
    finally:
        try:
            bs.logout()
        except Exception:
            pass


def _window_features(rows: list[dict[str, Any]], *, frequency: str) -> dict[str, float]:
    if not rows:
        raise ValueError("mid-frequency rows are required to compute features")

    first = rows[0]
    last = rows[-1]
    highs = [row["high"] for row in rows]
    lows = [row["low"] for row in rows]
    closes = [row["close"] for row in rows]
    volumes = [row["volume"] for row in rows]
    amounts = [row["amount"] for row in rows]
    opens = [row["open"] for row in rows]

    upper_shadow_ratios: list[float] = []
    lower_shadow_ratios: list[float] = []
    body_ratios: list[float] = []
    for row in rows:
        bar_range = max(row["high"] - row["low"], 1e-9)
        upper_shadow = max(row["high"] - max(row["open"], row["close"]), 0.0)
        lower_shadow = max(min(row["open"], row["close"]) - row["low"], 0.0)
        body = abs(row["close"] - row["open"])
        upper_shadow_ratios.append(upper_shadow / bar_range)
        lower_shadow_ratios.append(lower_shadow / bar_range)
        body_ratios.append(body / bar_range)

    day_high = max(highs)
    day_low = min(lows)
    day_range = max(day_high - day_low, 1e-9)
    midpoint = max(len(rows) // 2, 1)
    mid_close = rows[midpoint - 1]["close"]
    second_half = rows[midpoint:]
    second_half_volume = sum(row["volume"] for row in second_half)
    total_volume = max(sum(volumes), 1e-9)
    last_bar = rows[-1]
    prev_close = rows[-2]["close"] if len(rows) > 1 else first["open"]
    high_index = highs.index(day_high)

    intraday_return = last["close"] / first["open"] - 1.0
    afternoon_return = last["close"] / mid_close - 1.0
    close_location = (last["close"] - day_low) / day_range
    pullback_from_high = last["close"] / day_high - 1.0
    range_pct = day_high / day_low - 1.0 if day_low > 0 else 0.0
    breakout_efficiency = intraday_return / range_pct if range_pct > 0 else 0.0
    afternoon_volume_share = second_half_volume / total_volume
    last_bar_return = last_bar["close"] / prev_close - 1.0 if prev_close > 0 else 0.0
    high_time_ratio = (high_index + 1) / len(rows)
    vwap = sum(row["close"] * row["volume"] for row in rows) / total_volume if total_volume > 0 else last["close"]
    close_vs_vwap = last["close"] / vwap - 1.0 if vwap > 0 else 0.0
    last_bar_volume_share = last_bar["volume"] / total_volume
    amount_per_volume = sum(amounts) / total_volume if total_volume > 0 else 0.0
    failed_push_proxy = 1.0 if high_time_ratio < 0.7 and close_location < 0.45 and afternoon_return < 0 else 0.0
    upper_shadow_ratio = _mean(upper_shadow_ratios)
    lower_shadow_ratio = _mean(lower_shadow_ratios)
    body_ratio = _mean(body_ratios)
    last_bar_range = max(last_bar["high"] - last_bar["low"], 1e-9)
    last_bar_upper_shadow_ratio = max(last_bar["high"] - max(last_bar["open"], last_bar["close"]), 0.0) / last_bar_range
    last_bar_lower_shadow_ratio = max(min(last_bar["open"], last_bar["close"]) - last_bar["low"], 0.0) / last_bar_range

    prefix = f"f{frequency}_"
    return {
        f"{prefix}intraday_return": round(intraday_return, 6),
        f"{prefix}afternoon_return": round(afternoon_return, 6),
        f"{prefix}close_location": round(close_location, 6),
        f"{prefix}pullback_from_high": round(pullback_from_high, 6),
        f"{prefix}range_pct": round(range_pct, 6),
        f"{prefix}breakout_efficiency": round(breakout_efficiency, 6),
        f"{prefix}afternoon_volume_share": round(afternoon_volume_share, 6),
        f"{prefix}last_bar_return": round(last_bar_return, 6),
        f"{prefix}high_time_ratio": round(high_time_ratio, 6),
        f"{prefix}close_vs_vwap": round(close_vs_vwap, 6),
        f"{prefix}last_bar_volume_share": round(last_bar_volume_share, 6),
        f"{prefix}amount_per_volume": round(amount_per_volume, 6),
        f"{prefix}failed_push_proxy": round(failed_push_proxy, 6),
        f"{prefix}upper_shadow_ratio": round(upper_shadow_ratio, 6),
        f"{prefix}lower_shadow_ratio": round(lower_shadow_ratio, 6),
        f"{prefix}body_ratio": round(body_ratio, 6),
        f"{prefix}last_bar_upper_shadow_ratio": round(last_bar_upper_shadow_ratio, 6),
        f"{prefix}last_bar_lower_shadow_ratio": round(last_bar_lower_shadow_ratio, 6),
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


@dataclass(slots=True)
class V115BCpoMidfreqIntradayFactorExtractionReport:
    summary: dict[str, Any]
    factor_rows: list[dict[str, Any]]
    separation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "factor_rows": self.factor_rows,
            "separation_rows": self.separation_rows,
            "interpretation": self.interpretation,
        }


class V115BCpoMidfreqIntradayFactorExtractionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(
        self,
        *,
        v114z_payload: dict[str, Any],
        fetch_window_rows: Callable[[str, str, str], list[dict[str, Any]]] = _default_fetch_window_rows,
        frequencies: tuple[str, ...] = ("5", "15", "30", "60"),
    ) -> V115BCpoMidfreqIntradayFactorExtractionReport:
        manifest_rows = list(v114z_payload.get("manifest_rows", []))
        if not manifest_rows:
            raise ValueError("V115B requires V114Z manifest rows.")

        factor_rows: list[dict[str, Any]] = []
        for manifest in manifest_rows:
            symbol = str(manifest["symbol"])
            trade_date = str(manifest["trade_date"])
            merged: dict[str, Any] = dict(manifest)
            merged["fetch_status"] = "success"
            try:
                for frequency in frequencies:
                    rows = fetch_window_rows(symbol, trade_date, frequency)
                    merged.update(_window_features(rows, frequency=frequency))
                factor_rows.append(merged)
            except Exception as exc:  # pragma: no cover - real run path
                factor_rows.append(
                    {
                        **merged,
                        "fetch_status": "error",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                )

        success_rows = [row for row in factor_rows if row["fetch_status"] == "success"]
        eligibility_rows = [row for row in success_rows if row.get("control_label") == "eligibility"]
        risk_rows = [row for row in success_rows if row.get("control_label") in {"de_risk", "holding_veto"}]

        candidate_fields = [
            "f5_close_location",
            "f5_pullback_from_high",
            "f5_close_vs_vwap",
            "f15_afternoon_return",
            "f15_failed_push_proxy",
            "f30_breakout_efficiency",
            "f60_high_time_ratio",
            "f30_upper_shadow_ratio",
            "f60_upper_shadow_ratio",
            "f30_lower_shadow_ratio",
            "f60_lower_shadow_ratio",
        ]

        separation_rows: list[dict[str, Any]] = []
        for field in candidate_fields:
            elig_values = [float(row[field]) for row in eligibility_rows if field in row]
            risk_values = [float(row[field]) for row in risk_rows if field in row]
            separation_rows.append(
                {
                    "factor_name": field,
                    "eligibility_mean": round(_mean(elig_values), 6),
                    "risk_mean": round(_mean(risk_values), 6),
                    "mean_gap": round(_mean(elig_values) - _mean(risk_values), 6),
                    "separation_direction": "eligibility_higher" if _mean(elig_values) >= _mean(risk_values) else "risk_higher",
                }
            )

        separation_rows.sort(key=lambda row: abs(float(row["mean_gap"])), reverse=True)

        summary = {
            "acceptance_posture": "freeze_v115b_cpo_midfreq_intraday_factor_extraction_v1",
            "board_name": "CPO",
            "window_count": len(manifest_rows),
            "successful_window_count": len(success_rows),
            "failed_window_count": len(factor_rows) - len(success_rows),
            "eligibility_window_count": len(eligibility_rows),
            "risk_window_count": len(risk_rows),
            "top_separating_factor": separation_rows[0]["factor_name"] if separation_rows else None,
            "midfreq_factor_layer_ready_for_candidate_use": len(success_rows) >= max(len(manifest_rows) - 3, 1),
            "recommended_next_posture": "use_midfreq_factors_as_candidate_confirmation_features_not_direct_law_and_test_them_against_add_reduce_expectancy_labels",
        }

        interpretation = [
            "V1.15B is the first real mid-frequency intraday factor table for CPO, built on historical key windows rather than generic current snapshots.",
            "The objective here is not to legislate from intraday bars immediately, but to see whether mid-frequency confirmation features can materially separate eligibility windows from de-risk/holding-veto windows.",
            "This sits exactly between the exhausted daily layer and the not-yet-available long-history 1-minute layer.",
        ]

        return V115BCpoMidfreqIntradayFactorExtractionReport(
            summary=summary,
            factor_rows=factor_rows,
            separation_rows=separation_rows,
            interpretation=interpretation,
        )


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_report(*, reports_dir: Path, report_name: str, result: V115BCpoMidfreqIntradayFactorExtractionReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115BCpoMidfreqIntradayFactorExtractionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114z_payload=load_json_report(repo_root / "reports/analysis/v114z_cpo_intraday_key_window_availability_audit_v1.json"),
    )
    write_csv_rows(
        path=repo_root / "data/raw/intraday_requests/cpo_midfreq_intraday_factor_rows_v1.csv",
        rows=result.factor_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115b_cpo_midfreq_intraday_factor_extraction_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
