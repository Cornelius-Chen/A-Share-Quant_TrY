from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import median
from typing import Any, Callable

from a_share_quant.strategy.v115b_cpo_midfreq_intraday_factor_extraction_v1 import (
    _default_fetch_window_rows,
    _window_features,
)


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _score_row(row: dict[str, Any], *, prefix: str) -> float:
    close_location = float(row.get(f"{prefix}close_location", 0.0))
    close_vs_vwap = float(row.get(f"{prefix}close_vs_vwap", 0.0))
    failed_push = float(row.get(f"{prefix}failed_push_proxy", 0.0))
    intraday_return = float(row.get(f"{prefix}intraday_return", 0.0))
    afternoon_return = float(row.get(f"{prefix}afternoon_return", 0.0))
    pullback = float(row.get(f"{prefix}pullback_from_high", 0.0))
    high_time_ratio = float(row.get(f"{prefix}high_time_ratio", 0.0))

    intraday_norm = min(1.0, max(0.0, (intraday_return + 0.05) / 0.20))
    afternoon_norm = min(1.0, max(0.0, (afternoon_return + 0.04) / 0.12))
    vwap_norm = min(1.0, max(0.0, (close_vs_vwap + 0.02) / 0.06))
    pullback_norm = min(1.0, max(0.0, 1.0 + (pullback / 0.10)))
    high_time_norm = min(1.0, max(0.0, high_time_ratio))

    score = (
        0.26 * close_location
        + 0.18 * vwap_norm
        + 0.14 * intraday_norm
        + 0.12 * afternoon_norm
        + 0.16 * pullback_norm
        + 0.08 * high_time_norm
        + 0.06 * (1.0 - failed_push)
    )
    return round(score, 6)


@dataclass(slots=True)
class V115CCpoMidfreqIntradayMissWindowAuditReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    miss_window_rows: list[dict[str, Any]]
    candidate_add_confirmation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "miss_window_rows": self.miss_window_rows,
            "candidate_add_confirmation_rows": self.candidate_add_confirmation_rows,
            "interpretation": self.interpretation,
        }


class V115CCpoMidfreqIntradayMissWindowAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _reconstruct_positions(executed_rows: list[dict[str, Any]]) -> dict[date, set[str]]:
        positions: dict[str, int] = {}
        by_trade_date: dict[date, list[dict[str, Any]]] = {}
        for row in executed_rows:
            dt = parse_trade_date(str(row["execution_trade_date"]))
            by_trade_date.setdefault(dt, []).append(row)

        result: dict[date, set[str]] = {}
        ordered_dates = sorted(by_trade_date)
        for dt in ordered_dates:
            for row in by_trade_date[dt]:
                symbol = str(row["symbol"])
                qty = int(row["quantity"])
                if str(row["action"]) == "buy":
                    positions[symbol] = positions.get(symbol, 0) + qty
                else:
                    positions[symbol] = max(0, positions.get(symbol, 0) - qty)
            result[dt] = {symbol for symbol, qty in positions.items() if qty > 0}
        return result

    @staticmethod
    def _positions_before_or_on(
        *,
        positions_by_execution_date: dict[date, set[str]],
        trade_date: date,
    ) -> set[str]:
        eligible_dates = [dt for dt in positions_by_execution_date if dt <= trade_date]
        if not eligible_dates:
            return set()
        latest = max(eligible_dates)
        return set(positions_by_execution_date[latest])

    def analyze(
        self,
        *,
        v114t_payload: dict[str, Any],
        v114w_payload: dict[str, Any],
        v115b_payload: dict[str, Any],
        fetch_window_rows: Callable[[str, str, str], list[dict[str, Any]]] = _default_fetch_window_rows,
        frequencies: tuple[str, ...] = ("30", "60"),
    ) -> V115CCpoMidfreqIntradayMissWindowAuditReport:
        summary_t = dict(v114t_payload.get("summary", {}))
        summary_w = dict(v114w_payload.get("summary", {}))
        summary_b = dict(v115b_payload.get("summary", {}))
        if str(summary_t.get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V115C expects V114T repaired replay.")
        if str(summary_w.get("acceptance_posture")) != "freeze_v114w_cpo_under_exposure_attribution_repaired_v1":
            raise ValueError("V115C expects V114W repaired under-exposure review.")
        if str(summary_b.get("acceptance_posture")) != "freeze_v115b_cpo_midfreq_intraday_factor_extraction_v1":
            raise ValueError("V115C expects V115B mid-frequency factor extraction.")

        factor_rows = [row for row in list(v115b_payload.get("factor_rows", [])) if row.get("fetch_status") == "success"]
        positive_rows = [
            row for row in factor_rows
            if str(row.get("control_label")) == "eligibility"
            and str(row.get("board_phase")) in {"main_markup", "diffusion"}
        ]
        risk_rows = [
            row for row in factor_rows
            if str(row.get("control_label")) in {"de_risk", "holding_veto"}
            or str(row.get("board_phase")) == "divergence_and_decay"
        ]

        threshold_rows: list[dict[str, Any]] = []
        thresholds: dict[str, float] = {}
        for frequency in frequencies:
            prefix = f"f{frequency}_"
            positive_scores = [_score_row(row, prefix=prefix) for row in positive_rows]
            risk_scores = [_score_row(row, prefix=prefix) for row in risk_rows]
            positive_median = median(positive_scores) if positive_scores else 0.0
            risk_median = median(risk_scores) if risk_scores else 0.0
            midpoint = round((positive_median + risk_median) / 2.0, 6)
            thresholds[prefix] = midpoint
            threshold_rows.append(
                {
                    "frequency": frequency,
                    "positive_reference_count": len(positive_scores),
                    "risk_reference_count": len(risk_scores),
                    "positive_median_score": round(positive_median, 6),
                    "risk_median_score": round(risk_median, 6),
                    "candidate_add_threshold": midpoint,
                }
            )

        positions_by_date = self._reconstruct_positions(list(v114t_payload.get("executed_order_rows", [])))
        miss_rows = list(v114w_payload.get("top_opportunity_miss_rows", []))

        miss_window_rows: list[dict[str, Any]] = []
        for miss in miss_rows:
            trade_date = parse_trade_date(str(miss["trade_date"]))
            held_symbols = sorted(self._positions_before_or_on(positions_by_execution_date=positions_by_date, trade_date=trade_date))
            for symbol in held_symbols:
                merged: dict[str, Any] = {
                    "trade_date": str(trade_date),
                    "symbol": symbol,
                    "board_avg_return": float(miss["board_avg_return"]),
                    "board_breadth": float(miss["board_breadth"]),
                    "gross_exposure_after_close": float(miss["gross_exposure_after_close"]),
                    "miss_reading": str(miss["miss_reading"]),
                }
                try:
                    for frequency in frequencies:
                        rows = fetch_window_rows(symbol, str(trade_date), frequency)
                        merged.update(_window_features(rows, frequency=frequency))
                        prefix = f"f{frequency}_"
                        merged[f"{prefix}confirmation_score"] = _score_row(merged, prefix=prefix)
                        merged[f"{prefix}candidate_add_threshold"] = thresholds[prefix]
                        merged[f"{prefix}candidate_add_confirmation"] = (
                            float(merged[f"{prefix}confirmation_score"]) >= float(thresholds[prefix])
                        )
                    miss_window_rows.append(merged)
                except Exception as exc:  # pragma: no cover - live run path
                    miss_window_rows.append(
                        {
                            **merged,
                            "fetch_status": "error",
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                        }
                    )

        successful_miss_rows = [row for row in miss_window_rows if row.get("fetch_status", "success") == "success"]
        candidate_add_confirmation_rows = [
            row
            for row in successful_miss_rows
            if bool(row.get("f30_candidate_add_confirmation")) or bool(row.get("f60_candidate_add_confirmation"))
        ]
        candidate_add_confirmation_rows.sort(
            key=lambda row: max(float(row.get("f30_confirmation_score", 0.0)), float(row.get("f60_confirmation_score", 0.0))),
            reverse=True,
        )

        summary = {
            "acceptance_posture": "freeze_v115c_cpo_midfreq_intraday_miss_window_audit_v1",
            "miss_day_count": len(miss_rows),
            "miss_window_count": len(miss_window_rows),
            "successful_miss_window_count": len(successful_miss_rows),
            "candidate_add_confirmation_count": len(candidate_add_confirmation_rows),
            "f30_threshold": thresholds.get("f30_", 0.0),
            "f60_threshold": thresholds.get("f60_", 0.0),
            "midfreq_intraday_confirmation_has_action_layer_increment": len(candidate_add_confirmation_rows) > 0,
            "recommended_next_posture": (
                "promote_midfreq_confirmation_as_candidate_add_overlay_for_repaired_miss_days"
                if candidate_add_confirmation_rows
                else "collect_more_intraday_windows_before_law"
            ),
        }

        interpretation = [
            "V115C is the first repaired-surface audit that turns Baostock mid-frequency data into actual miss-day action candidates rather than generic factor tables.",
            "The point is not to legislate directly from intraday bars, but to ask a narrower question: on repaired top-miss days, did already-held core names show add-like confirmation that the daily layer could not see cleanly?",
            "If candidate confirmations appear here, mid-frequency intraday data has action-layer value before long-history 1-minute backfill is even available.",
        ]

        return V115CCpoMidfreqIntradayMissWindowAuditReport(
            summary=summary,
            threshold_rows=threshold_rows,
            miss_window_rows=miss_window_rows,
            candidate_add_confirmation_rows=candidate_add_confirmation_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115CCpoMidfreqIntradayMissWindowAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115CCpoMidfreqIntradayMissWindowAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json"),
        v114w_payload=load_json_report(repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json"),
        v115b_payload=load_json_report(repo_root / "reports" / "analysis" / "v115b_cpo_midfreq_intraday_factor_extraction_v1.json"),
    )
    write_csv_rows(
        path=repo_root / "data" / "raw" / "intraday_requests" / "cpo_midfreq_intraday_miss_window_rows_v1.csv",
        rows=result.miss_window_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115c_cpo_midfreq_intraday_miss_window_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
