from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


INPUT_GLOB = "sina_*_recent_1min_v1.csv"
OUTPUT_RELATIVE_PATH = Path("data") / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_div(numerator: float, denominator: float, *, default: float = 0.0) -> float:
    if abs(denominator) < 1e-12:
        return default
    return numerator / denominator


@dataclass(slots=True)
class V121VCpoRecent1MinMicrostructureFeatureTableReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V121VCpoRecent1MinMicrostructureFeatureTableAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121VCpoRecent1MinMicrostructureFeatureTableReport:
        minute_dir = self.repo_root / "data" / "raw" / "minute_bars"
        output_path = self.repo_root / OUTPUT_RELATIVE_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "symbol",
            "bar_time",
            "trade_date",
            "clock_time",
            "minute_index",
            "is_late_session",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "minute_return",
            "range_pct",
            "body_pct",
            "upper_shadow_pct",
            "lower_shadow_pct",
            "close_location",
            "close_vs_vwap",
            "pullback_from_high",
            "push_efficiency",
            "micro_pullback_depth",
            "volume_ratio_5",
            "value_ratio_5",
            "prev_close_gap",
            "reclaim_after_break_score",
            "burst_then_fade_score",
            "late_session_integrity_score",
        ]

        symbol_rows: list[dict[str, Any]] = []
        total_rows = 0

        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()

            for path in sorted(minute_dir.glob(INPUT_GLOB)):
                symbol = path.name.split("_")[1]
                with path.open("r", encoding="utf-8") as source_handle:
                    rows = list(csv.DictReader(source_handle))
                if not rows:
                    continue

                parsed_rows = []
                for row in rows:
                    bar_time = datetime.strptime(row["day"], "%Y-%m-%d %H:%M:%S")
                    parsed_rows.append(
                        {
                            "bar_time": bar_time,
                            "open": _to_float(row["open"]),
                            "high": _to_float(row["high"]),
                            "low": _to_float(row["low"]),
                            "close": _to_float(row["close"]),
                            "volume": _to_float(row["volume"]),
                            "amount": _to_float(row["amount"]),
                        }
                    )

                cumulative_volume = 0.0
                cumulative_amount = 0.0
                trailing_volumes: list[float] = []
                trailing_amounts: list[float] = []
                previous_close = parsed_rows[0]["open"]

                per_symbol_count = 0
                for index, row in enumerate(parsed_rows):
                    open_price = row["open"]
                    high_price = row["high"]
                    low_price = row["low"]
                    close_price = row["close"]
                    volume = row["volume"]
                    amount = row["amount"]
                    price_range = max(high_price - low_price, 0.0)

                    cumulative_volume += volume
                    cumulative_amount += amount
                    trailing_volumes.append(volume)
                    trailing_amounts.append(amount)
                    if len(trailing_volumes) > 5:
                        trailing_volumes.pop(0)
                    if len(trailing_amounts) > 5:
                        trailing_amounts.pop(0)

                    vwap = _safe_div(cumulative_amount, cumulative_volume, default=close_price)
                    body = close_price - open_price
                    minute_return = _safe_div(close_price - open_price, open_price)
                    range_pct = _safe_div(price_range, open_price)
                    body_pct = _safe_div(body, open_price)
                    upper_shadow_pct = _safe_div(high_price - max(open_price, close_price), open_price)
                    lower_shadow_pct = _safe_div(min(open_price, close_price) - low_price, open_price)
                    close_location = _safe_div(close_price - low_price, price_range, default=0.5)
                    close_vs_vwap = _safe_div(close_price - vwap, vwap)
                    pullback_from_high = _safe_div(close_price - high_price, high_price)
                    push_efficiency = _safe_div(body, price_range, default=0.0)
                    micro_pullback_depth = _safe_div(high_price - close_price, open_price)
                    avg_volume_5 = sum(trailing_volumes) / len(trailing_volumes)
                    avg_amount_5 = sum(trailing_amounts) / len(trailing_amounts)
                    volume_ratio_5 = _safe_div(volume, avg_volume_5, default=1.0)
                    value_ratio_5 = _safe_div(amount, avg_amount_5, default=1.0)
                    prev_close_gap = _safe_div(close_price - previous_close, previous_close)
                    reclaim_after_break_score = _safe_div(close_price - previous_close, previous_close) - max(
                        _safe_div(previous_close - low_price, previous_close),
                        0.0,
                    )
                    burst_then_fade_score = volume_ratio_5 * max(-pullback_from_high, 0.0)
                    late_session_integrity_score = 0.0
                    if row["bar_time"].time() >= datetime.strptime("14:30:00", "%H:%M:%S").time():
                        late_session_integrity_score = close_location + close_vs_vwap + min(push_efficiency, 0.0)

                    feature_row = {
                        "symbol": symbol,
                        "bar_time": row["bar_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "trade_date": row["bar_time"].strftime("%Y-%m-%d"),
                        "clock_time": row["bar_time"].strftime("%H:%M:%S"),
                        "minute_index": index,
                        "is_late_session": int(
                            row["bar_time"].time() >= datetime.strptime("14:30:00", "%H:%M:%S").time()
                        ),
                        "open": round(open_price, 6),
                        "high": round(high_price, 6),
                        "low": round(low_price, 6),
                        "close": round(close_price, 6),
                        "volume": round(volume, 6),
                        "amount": round(amount, 6),
                        "minute_return": round(minute_return, 8),
                        "range_pct": round(range_pct, 8),
                        "body_pct": round(body_pct, 8),
                        "upper_shadow_pct": round(upper_shadow_pct, 8),
                        "lower_shadow_pct": round(lower_shadow_pct, 8),
                        "close_location": round(close_location, 8),
                        "close_vs_vwap": round(close_vs_vwap, 8),
                        "pullback_from_high": round(pullback_from_high, 8),
                        "push_efficiency": round(push_efficiency, 8),
                        "micro_pullback_depth": round(micro_pullback_depth, 8),
                        "volume_ratio_5": round(volume_ratio_5, 8),
                        "value_ratio_5": round(value_ratio_5, 8),
                        "prev_close_gap": round(prev_close_gap, 8),
                        "reclaim_after_break_score": round(reclaim_after_break_score, 8),
                        "burst_then_fade_score": round(burst_then_fade_score, 8),
                        "late_session_integrity_score": round(late_session_integrity_score, 8),
                    }
                    writer.writerow(feature_row)
                    per_symbol_count += 1
                    total_rows += 1
                    previous_close = close_price

                symbol_rows.append(
                    {
                        "symbol": symbol,
                        "row_count": per_symbol_count,
                        "start_time": parsed_rows[0]["bar_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": parsed_rows[-1]["bar_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v121v_cpo_recent_1min_microstructure_feature_table_v1",
            "symbol_count": len(symbol_rows),
            "total_row_count": total_rows,
            "feature_count": len(fieldnames) - 7,
            "output_path": str(OUTPUT_RELATIVE_PATH),
            "recommended_next_posture": "start_1min_microstructure_discovery_on_core_names",
        }
        interpretation = [
            "V1.21V converts the recent rolling 1-minute plane into a concrete microstructure feature table instead of leaving it as raw bars.",
            "The current table is suitable for local feature discovery around reclaim, fade, shadow, VWAP quality, and late-session integrity.",
            "The next useful step is discovery and adversarial auditing on this 1-minute plane, not replay promotion.",
        ]
        return V121VCpoRecent1MinMicrostructureFeatureTableReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121VCpoRecent1MinMicrostructureFeatureTableReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121VCpoRecent1MinMicrostructureFeatureTableAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121v_cpo_recent_1min_microstructure_feature_table_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
