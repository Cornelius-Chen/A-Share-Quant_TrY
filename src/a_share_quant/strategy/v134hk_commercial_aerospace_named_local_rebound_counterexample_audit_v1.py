from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOCKOUT_START = "20260115"
LOCKOUT_END = "20260320"
ANALYSIS_END = "20260403"

TARGET_SYMBOLS: dict[str, str] = {
    "300342": "天银机电",
    "603601": "再升科技",
    "002361": "神剑股份",
    "000547": "航天发展",
    "600343": "航天动力",
    "301306": "西测测试",
}


@dataclass(slots=True)
class V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Report:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "family_rows": self.family_rows,
            "interpretation": self.interpretation,
        }


class V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_bars_path = (
            repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        )
        self.local_rebound_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_only_rebound_audit_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_named_local_rebound_counterexamples_v1.csv"
        )

    def analyze(self) -> V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Report:
        with self.daily_bars_path.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))
        with self.local_rebound_path.open("r", encoding="utf-8-sig", newline="") as handle:
            local_rebound_rows = list(csv.DictReader(handle))

        top_symbol_counts: dict[str, int] = {}
        for row in local_rebound_rows:
            symbol = row["top_symbol"]
            top_symbol_counts[symbol] = top_symbol_counts.get(symbol, 0) + 1

        symbol_rows: list[dict[str, Any]] = []
        family_counts: dict[str, int] = {}

        for symbol, display_name in TARGET_SYMBOLS.items():
            rows = [row for row in daily_rows if row["symbol"] == symbol]
            rows.sort(key=lambda row: row["trade_date"])
            pre_lockout_rows = [row for row in rows if row["trade_date"] < LOCKOUT_START]
            post_rows = [row for row in rows if LOCKOUT_START <= row["trade_date"] <= ANALYSIS_END]

            if not post_rows:
                family = "coverage_gap_or_inactive"
                row = {
                    "symbol": symbol,
                    "display_name": display_name,
                    "analysis_start_trade_date": LOCKOUT_START,
                    "analysis_end_trade_date": ANALYSIS_END,
                    "post_lockout_row_count": 0,
                    "local_only_top_seed_day_count": top_symbol_counts.get(symbol, 0),
                    "pre_lockout_peak_close": "",
                    "pre_lockout_peak_trade_date": "",
                    "post_lockout_start_close": "",
                    "post_lockout_max_close": "",
                    "post_lockout_max_trade_date": "",
                    "post_lockout_end_close": "",
                    "post_lockout_max_return_from_start": "",
                    "post_lockout_max_vs_pre_lockout_peak": "",
                    "post_lockout_drawdown_from_max_to_end": "",
                    "max_date_zone": "no_post_lockout_coverage",
                    "crossed_pre_lockout_peak": False,
                    "counterexample_family": family,
                    "learning_reading": "no_local_path_to_learn_until_post_lockout_symbol_coverage_exists",
                }
                symbol_rows.append(row)
                family_counts[family] = family_counts.get(family, 0) + 1
                continue

            pre_peak_row = max(pre_lockout_rows, key=lambda row: float(row["close"])) if pre_lockout_rows else None
            pre_peak_close = float(pre_peak_row["close"]) if pre_peak_row else None
            pre_peak_trade_date = pre_peak_row["trade_date"] if pre_peak_row else ""

            post_start_close = float(post_rows[0]["close"])
            post_max_row = max(post_rows, key=lambda row: float(row["close"]))
            post_max_close = float(post_max_row["close"])
            post_max_trade_date = post_max_row["trade_date"]
            post_end_close = float(post_rows[-1]["close"])

            max_return_from_start = round(post_max_close / post_start_close - 1.0, 8) if post_start_close else ""
            max_vs_pre_peak = (
                round(post_max_close / pre_peak_close - 1.0, 8) if pre_peak_close not in (None, 0.0) else ""
            )
            drawdown_from_max_to_end = (
                round(post_end_close / post_max_close - 1.0, 8) if post_max_close else ""
            )
            max_date_zone = "lockout_window" if post_max_trade_date <= LOCKOUT_END else "post_lockout_raw_only_window"
            crossed_pre_peak = bool(pre_peak_close and post_max_close > pre_peak_close)

            if max_date_zone == "lockout_window" and crossed_pre_peak:
                family = "lockout_outlier_breakout_then_fade"
                learning_reading = (
                    "symbol_can_break_prior_peak_inside_board_lockout_but_still_not_reopen_board_regime"
                )
            elif max_date_zone == "post_lockout_raw_only_window" and crossed_pre_peak:
                family = "raw_only_post_lockout_breakout_without_board_context"
                learning_reading = (
                    "symbol_can_resume_breakout_after_lockout_end_in_raw_prices_but_still_lacks_derived_board_unlock_context"
                )
            elif max_date_zone == "post_lockout_raw_only_window" and max_vs_pre_peak != "" and float(max_vs_pre_peak) > -0.03:
                family = "raw_only_near_high_rebound_without_breakout"
                learning_reading = (
                    "symbol_can recover near prior peak after lockout end but still not supply a legal board-level unlock handoff"
                )
            else:
                family = "locked_board_weak_repair_only"
                learning_reading = (
                    "symbol_rebounds_locally_but_never repairs enough to clear prior peak or reopen board participation"
                )

            row = {
                "symbol": symbol,
                "display_name": display_name,
                "analysis_start_trade_date": LOCKOUT_START,
                "analysis_end_trade_date": ANALYSIS_END,
                "post_lockout_row_count": len(post_rows),
                "local_only_top_seed_day_count": top_symbol_counts.get(symbol, 0),
                "pre_lockout_peak_close": round(pre_peak_close, 4) if pre_peak_close is not None else "",
                "pre_lockout_peak_trade_date": pre_peak_trade_date,
                "post_lockout_start_close": round(post_start_close, 4),
                "post_lockout_max_close": round(post_max_close, 4),
                "post_lockout_max_trade_date": post_max_trade_date,
                "post_lockout_end_close": round(post_end_close, 4),
                "post_lockout_max_return_from_start": max_return_from_start,
                "post_lockout_max_vs_pre_lockout_peak": max_vs_pre_peak,
                "post_lockout_drawdown_from_max_to_end": drawdown_from_max_to_end,
                "max_date_zone": max_date_zone,
                "crossed_pre_lockout_peak": crossed_pre_peak,
                "counterexample_family": family,
                "learning_reading": learning_reading,
            }
            symbol_rows.append(row)
            family_counts[family] = family_counts.get(family, 0) + 1

        symbol_rows.sort(key=lambda row: (row["counterexample_family"], row["symbol"]))
        family_rows = [
            {"counterexample_family": family, "symbol_count": count}
            for family, count in sorted(family_counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        summary = {
            "acceptance_posture": "freeze_v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1",
            "analysis_symbol_count": len(symbol_rows),
            "lockout_window_end_trade_date": LOCKOUT_END,
            "analysis_end_trade_date": ANALYSIS_END,
            "crossed_pre_lockout_peak_count": sum(1 for row in symbol_rows if row["crossed_pre_lockout_peak"]),
            "local_only_top_seed_symbol_count": sum(1 for row in symbol_rows if int(row["local_only_top_seed_day_count"]) > 0),
            "family_count": len(family_rows),
            "counterexample_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_named_local_rebound_counterexample_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34HK checks whether named strong rebound symbols after the January 15, 2026 lockout should be learned as counterexamples rather than as restart evidence.",
            "The key question is not whether they bounced, but whether they bounced inside lockout, after lockout only in raw prices, or without ever rebuilding enough to clear their own prior peak.",
        ]
        return V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Report(
            summary=summary,
            symbol_rows=symbol_rows,
            family_rows=family_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HKCommercialAerospaceNamedLocalReboundCounterexampleAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
