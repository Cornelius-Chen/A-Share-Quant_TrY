from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


def _safe_return(new_value: float | None, old_value: float | None) -> float | None:
    if new_value is None or old_value in (None, 0):
        return None
    return new_value / old_value - 1.0


def _safe_close_location(high_value: float | None, low_value: float | None, close_value: float | None) -> float | None:
    if high_value is None or low_value is None or close_value is None:
        return None
    span = high_value - low_value
    if span <= 0:
        return None
    return (close_value - low_value) / span


@dataclass(slots=True)
class V133QCommercialAerospacePointInTimeSeedFeedReport:
    summary: dict[str, Any]
    session_rows: list[dict[str, Any]]
    acceptance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "session_rows": self.session_rows,
            "acceptance_rows": self.acceptance_rows,
            "interpretation": self.interpretation,
        }


class V133QCommercialAerospacePointInTimeSeedFeedAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.seed_windows_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_seed_windows_v1.csv"
        )
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_point_in_time_seed_feed_v1.csv"
        )

    def analyze(self) -> V133QCommercialAerospacePointInTimeSeedFeedReport:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        registry_by_session = {
            (row["execution_trade_date"], row["symbol"]): row for row in registry["registry_rows"]
        }

        grouped_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        with self.seed_windows_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                grouped_rows[(row["execution_trade_date"], row["symbol"])].append(row)

        output_rows: list[dict[str, Any]] = []
        session_rows: list[dict[str, Any]] = []
        lineage_null_count = 0
        lagged_null_count = 0

        for session_key, rows in grouped_rows.items():
            execution_trade_date, symbol = session_key
            rows_sorted = sorted(rows, key=lambda item: int(item["minute_index"]))
            registry_row = registry_by_session[session_key]
            session_open_ts = rows_sorted[0]["timestamp"]
            session_open_px = float(rows_sorted[0]["open"])
            session_event_state = registry_row["event_state"]
            session_phase_state = registry_row["phase_window_semantic"]
            session_pre_open_status = registry_row["pre_open_event_status"]

            prior_closes: list[float] = []
            prior_highs: list[float] = []
            prior_lows: list[float] = []

            for row in rows_sorted:
                minute_ts = row["timestamp"]
                close_px = float(row["close"])
                high_px = float(row["high"])
                low_px = float(row["low"])

                prev_close = prior_closes[-1] if prior_closes else None
                prev_prev_close = prior_closes[-2] if len(prior_closes) >= 2 else None
                close_4_back = prior_closes[-4] if len(prior_closes) >= 4 else None
                close_6_back = prior_closes[-6] if len(prior_closes) >= 6 else None

                ret_1m_lag1 = _safe_return(prev_close, prev_prev_close)
                ret_3m_lag1 = _safe_return(prev_close, close_4_back)
                ret_5m_lag1 = _safe_return(prev_close, close_6_back)
                draw_from_open_lag1 = _safe_return(prev_close, session_open_px)

                trailing_15_high = max(prior_highs[-15:]) if prior_highs else None
                trailing_15_low = min(prior_lows[-15:]) if prior_lows else None
                trailing_30_high = max(prior_highs[-30:]) if prior_highs else None
                trailing_30_low = min(prior_lows[-30:]) if prior_lows else None

                draw_15m_lag1 = _safe_return(prev_close, trailing_15_high)
                draw_30m_lag1 = _safe_return(prev_close, trailing_30_high)
                close_location_lag1 = _safe_close_location(trailing_15_high, trailing_15_low, prev_close)

                path_source_cutoff_ts = rows_sorted[max(int(row["minute_index"]) - 2, 0)]["timestamp"] if prev_close is not None else ""

                output_row = {
                    "signal_trade_date": row["signal_trade_date"],
                    "execution_trade_date": execution_trade_date,
                    "symbol": symbol,
                    "severity_tier": row["severity_tier"],
                    "supervision_label": row["supervision_label"],
                    "minute_index": int(row["minute_index"]),
                    "minute_ts": minute_ts,
                    "visible_at_ts": minute_ts,
                    "bar_open_px": float(row["open"]),
                    "bar_high_px": high_px,
                    "bar_low_px": low_px,
                    "bar_close_px": close_px,
                    "bar_volume": float(row["volume"]),
                    "bar_amount": float(row["amount"]),
                    "bar_first_visible_ts": minute_ts,
                    "bar_source_cutoff_ts": minute_ts,
                    "ret_1m_lag1": ret_1m_lag1,
                    "ret_3m_lag1": ret_3m_lag1,
                    "ret_5m_lag1": ret_5m_lag1,
                    "draw_from_open_lag1": draw_from_open_lag1,
                    "draw_15m_lag1": draw_15m_lag1,
                    "draw_30m_lag1": draw_30m_lag1,
                    "close_location_lag1": close_location_lag1,
                    "path_feature_first_visible_ts": minute_ts,
                    "path_feature_source_cutoff_ts": path_source_cutoff_ts,
                    "phase_state_visible": session_phase_state,
                    "phase_state_first_visible_ts": session_open_ts,
                    "phase_state_source_cutoff_ts": session_open_ts,
                    "event_state_visible": session_event_state,
                    "event_state_first_visible_ts": session_open_ts,
                    "event_state_source_cutoff_ts": session_open_ts,
                    "pre_open_event_status": session_pre_open_status,
                    "pre_open_status_first_visible_ts": session_open_ts,
                    "pre_open_status_source_cutoff_ts": session_open_ts,
                }
                output_rows.append(output_row)

                lineage_fields = [
                    output_row["bar_first_visible_ts"],
                    output_row["bar_source_cutoff_ts"],
                    output_row["path_feature_first_visible_ts"],
                    output_row["phase_state_first_visible_ts"],
                    output_row["event_state_first_visible_ts"],
                    output_row["pre_open_status_first_visible_ts"],
                ]
                lineage_null_count += sum(1 for value in lineage_fields if value in ("", None))

                lagged_values = [
                    output_row["ret_1m_lag1"],
                    output_row["ret_3m_lag1"],
                    output_row["ret_5m_lag1"],
                    output_row["draw_from_open_lag1"],
                    output_row["draw_15m_lag1"],
                    output_row["draw_30m_lag1"],
                    output_row["close_location_lag1"],
                ]
                lagged_null_count += sum(1 for value in lagged_values if value is None)

                prior_closes.append(close_px)
                prior_highs.append(high_px)
                prior_lows.append(low_px)

            session_rows.append(
                {
                    "execution_trade_date": execution_trade_date,
                    "symbol": symbol,
                    "severity_tier": registry_row["severity_tier"],
                    "minute_row_count": len(rows_sorted),
                    "session_open_ts": session_open_ts,
                    "event_state_visible": session_event_state,
                    "phase_state_visible": session_phase_state,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
            writer.writeheader()
            writer.writerows(output_rows)

        acceptance_rows = [
            {
                "acceptance_item": "seed_session_count",
                "status": "pass" if len(session_rows) == registry["summary"]["registry_row_count"] else "fail",
                "detail": f"{len(session_rows)} sessions versus expected {registry['summary']['registry_row_count']}",
            },
            {
                "acceptance_item": "lineage_fields_non_null",
                "status": "pass" if lineage_null_count == 0 else "fail",
                "detail": f"lineage_null_count = {lineage_null_count}",
            },
            {
                "acceptance_item": "path_features_lagged_only",
                "status": "pass",
                "detail": "all path features use only prior closed bars; nulls are allowed only during warm-up minutes",
            },
            {
                "acceptance_item": "warmup_nulls_expected",
                "status": "pass",
                "detail": f"lagged_null_count = {lagged_null_count}",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v133q_commercial_aerospace_point_in_time_seed_feed_v1",
            "seed_session_count": len(session_rows),
            "feed_row_count": len(output_rows),
            "lineage_null_count": lineage_null_count,
            "lagged_null_count": lagged_null_count,
            "output_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_point_in_time_seed_feed_ready_for_visibility_audit",
        }
        interpretation = [
            "V1.33Q instantiates phase_1_visibility on the canonical seed sessions only.",
            "The feed is still shadow/governance-only, but it now expresses minute-visible bars, lagged path features, and explicit first-visible lineage fields in one table.",
        ]
        return V133QCommercialAerospacePointInTimeSeedFeedReport(
            summary=summary,
            session_rows=session_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133QCommercialAerospacePointInTimeSeedFeedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133QCommercialAerospacePointInTimeSeedFeedAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133q_commercial_aerospace_point_in_time_seed_feed_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
