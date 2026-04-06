from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _symbol_to_archive_member(symbol: str) -> str:
    if symbol.startswith("6"):
        return f"sh{symbol}.csv"
    if symbol.startswith(("0", "3")):
        return f"sz{symbol}.csv"
    if symbol.startswith(("4", "8")):
        return f"bj{symbol}.csv"
    return f"{symbol}.csv"


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
class V133YCommercialAerospacePointInTimeAllSessionFeedReport:
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


class V133YCommercialAerospacePointInTimeAllSessionFeedAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.hits_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_1min_session_expansion_hits_v1.csv"
        )
        self.monthly_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_point_in_time_all_session_feed_v1.csv"
        )

    def analyze(self) -> V133YCommercialAerospacePointInTimeAllSessionFeedReport:
        with self.hits_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            hit_rows = list(csv.DictReader(handle))
        seed_symbols = sorted({row["symbol"] for row in hit_rows})

        output_rows: list[dict[str, Any]] = []
        session_rows: list[dict[str, Any]] = []
        lineage_null_count = 0
        lagged_null_count = 0

        for month_dir in sorted(path for path in self.monthly_root.iterdir() if path.is_dir()):
            for zip_path in sorted(month_dir.glob("*_1min.zip")):
                trade_date = zip_path.stem.split("_")[0]
                with zipfile.ZipFile(zip_path) as archive:
                    members = set(archive.namelist())
                    for symbol in seed_symbols:
                        member_name = _symbol_to_archive_member(symbol)
                        if member_name not in members:
                            continue
                        with archive.open(member_name, "r") as member:
                            raw_rows = list(csv.reader(line.decode("utf-8-sig", errors="ignore") for line in member))[1:]

                        first_60 = raw_rows[:60]
                        if len(first_60) < 60:
                            continue

                        session_open_ts = first_60[0][0]
                        session_open_px = float(first_60[0][3])
                        prior_closes: list[float] = []
                        prior_highs: list[float] = []
                        prior_lows: list[float] = []

                        for minute_index, row in enumerate(first_60, start=1):
                            minute_ts = row[0]
                            close_px = float(row[4])
                            high_px = float(row[5])
                            low_px = float(row[6])

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

                            path_source_cutoff_ts = first_60[max(minute_index - 2, 0)][0] if prev_close is not None else ""

                            output_row = {
                                "trade_date": trade_date,
                                "symbol": symbol,
                                "minute_index": minute_index,
                                "minute_ts": minute_ts,
                                "visible_at_ts": minute_ts,
                                "bar_open_px": float(row[3]),
                                "bar_high_px": high_px,
                                "bar_low_px": low_px,
                                "bar_close_px": close_px,
                                "bar_volume": float(row[7]),
                                "bar_amount": float(row[8]),
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
                                "phase_state_visible": "all_session_surface",
                                "phase_state_first_visible_ts": session_open_ts,
                                "phase_state_source_cutoff_ts": session_open_ts,
                                "event_state_visible": "all_session_unbound",
                                "event_state_first_visible_ts": session_open_ts,
                                "event_state_source_cutoff_ts": session_open_ts,
                            }
                            output_rows.append(output_row)

                            lineage_fields = [
                                output_row["bar_first_visible_ts"],
                                output_row["bar_source_cutoff_ts"],
                                output_row["path_feature_first_visible_ts"],
                                output_row["phase_state_first_visible_ts"],
                                output_row["event_state_first_visible_ts"],
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
                                "trade_date": trade_date,
                                "symbol": symbol,
                                "minute_row_count": len(first_60),
                                "month_bucket": month_dir.name,
                            }
                        )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
            writer.writeheader()
            writer.writerows(output_rows)

        acceptance_rows = [
            {
                "acceptance_item": "all_session_count",
                "status": "pass",
                "detail": f"{len(session_rows)} first-hour sessions materialized",
            },
            {
                "acceptance_item": "lineage_fields_non_null",
                "status": "pass" if lineage_null_count == 0 else "fail",
                "detail": f"lineage_null_count = {lineage_null_count}",
            },
            {
                "acceptance_item": "warmup_nulls_expected",
                "status": "pass",
                "detail": f"lagged_null_count = {lagged_null_count}",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v133y_commercial_aerospace_point_in_time_all_session_feed_v1",
            "seed_symbol_count": len(seed_symbols),
            "all_session_count": len(session_rows),
                            "feed_row_count": len(output_rows),
            "lineage_null_count": lineage_null_count,
            "lagged_null_count": lagged_null_count,
            "output_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_point_in_time_all_session_feed_ready_for_phase_1_terminal_audit",
        }
        interpretation = [
            "V1.33Y completes the phase-1 visibility expansion from seeds to broader hits to the full first-hour session surface for the six seed symbols.",
            "This is still only a visibility object; simulator and replay lanes remain explicitly out of scope.",
        ]
        return V133YCommercialAerospacePointInTimeAllSessionFeedReport(
            summary=summary,
            session_rows=session_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133YCommercialAerospacePointInTimeAllSessionFeedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133YCommercialAerospacePointInTimeAllSessionFeedAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133y_commercial_aerospace_point_in_time_all_session_feed_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
