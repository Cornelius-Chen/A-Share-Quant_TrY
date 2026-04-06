from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1 import (
    TARGET_SYMBOLS as NAMED_SYMBOLS,
)


FORMAL_SYMBOL_NAMES = {
    "002085": "万丰奥威",
    "000738": "航发控制",
    "600118": "中国卫星",
}


@dataclass(slots=True)
class V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Report:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.universe_triage_path = (
            repo_root / "data" / "training" / "commercial_aerospace_universe_triage_v1.csv"
        )
        self.daily_bars_path = (
            repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        )
        self.daily_basic_path = (
            repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        )
        self.local_rebound_path = (
            repo_root / "data" / "training" / "commercial_aerospace_local_only_rebound_audit_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_expanded_symbol_universe_carrier_search_v1.csv"
        )

    def analyze(self) -> V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Report:
        with self.universe_triage_path.open("r", encoding="utf-8-sig", newline="") as handle:
            universe_rows = list(csv.DictReader(handle))
        with self.daily_bars_path.open("r", encoding="utf-8-sig", newline="") as handle:
            daily_rows = list(csv.DictReader(handle))
        with self.daily_basic_path.open("r", encoding="utf-8-sig", newline="") as handle:
            basic_rows = list(csv.DictReader(handle))
        with self.local_rebound_path.open("r", encoding="utf-8-sig", newline="") as handle:
            local_rows = list(csv.DictReader(handle))

        formal_symbols = [row["symbol"] for row in universe_rows]
        local_top_counts: dict[str, int] = {}
        for row in local_rows:
            symbol = row["top_symbol"]
            local_top_counts[symbol] = local_top_counts.get(symbol, 0) + 1

        daily_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for row in daily_rows:
            symbol = row["symbol"]
            if symbol in formal_symbols:
                daily_by_symbol.setdefault(symbol, []).append(row)
        for rows in daily_by_symbol.values():
            rows.sort(key=lambda row: row["trade_date"])

        basic_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for row in basic_rows:
            symbol = row["symbol"]
            if symbol in formal_symbols and "20260115" <= row["trade_date"] <= "20260403":
                basic_by_symbol.setdefault(symbol, []).append(row)

        symbol_rows: list[dict[str, Any]] = []
        for symbol in formal_symbols:
            rows = daily_by_symbol.get(symbol, [])
            pre_rows = [row for row in rows if row["trade_date"] < "20260115"]
            post_rows = [row for row in rows if "20260115" <= row["trade_date"] <= "20260403"]
            if not pre_rows or not post_rows:
                continue

            pre_peak = max(float(row["close"]) for row in pre_rows)
            post_start = float(post_rows[0]["close"])
            post_end = float(post_rows[-1]["close"])
            post_max_row = max(post_rows, key=lambda row: float(row["close"]))
            post_max = float(post_max_row["close"])
            avg_turn = ""
            max_turn = ""
            turnover_values = [
                float(row["turnover_rate_f"])
                for row in basic_by_symbol.get(symbol, [])
                if row.get("turnover_rate_f") not in {"", None}
            ]
            if turnover_values:
                avg_turn = round(sum(turnover_values) / len(turnover_values), 8)
                max_turn = round(max(turnover_values), 8)

            peak_gap = round(post_max / pre_peak - 1.0, 8)
            max_return = round(post_max / post_start - 1.0, 8)
            drawdown = round(post_end / post_max - 1.0, 8)
            local_top_day_count = local_top_counts.get(symbol, 0)

            if local_top_day_count > 0 and peak_gap > 0.10 and max_return > 0.25:
                candidate_label = "priority_second_carrier_search_candidate"
                reading = (
                    "formal/core symbol shows repeated local rebound leadership plus post-lockout breakout strength, so it deserves explicit search as the best outside-named second-carrier candidate"
                )
            elif peak_gap > -0.12 and max_return > 0.0:
                candidate_label = "formal_strength_watch_not_yet_carrier"
                reading = (
                    "formal/core symbol has some post-lockout repair but does not yet carry enough local leadership evidence to enter second-carrier promotion"
                )
            else:
                candidate_label = "formal_noncandidate"
                reading = (
                    "formal/core symbol lacks the combination of local leadership and post-lockout strength needed for second-carrier search"
                )

            symbol_rows.append(
                {
                    "symbol": symbol,
                    "display_name": FORMAL_SYMBOL_NAMES.get(symbol, symbol),
                    "inside_named_set": symbol in NAMED_SYMBOLS,
                    "local_top_day_count": local_top_day_count,
                    "post_lockout_max_vs_pre_lockout_peak": peak_gap,
                    "post_lockout_max_return_from_start": max_return,
                    "post_lockout_drawdown_from_max_to_end": drawdown,
                    "post_lockout_max_trade_date": post_max_row["trade_date"],
                    "avg_turnover_rate_f": avg_turn,
                    "max_turnover_rate_f": max_turn,
                    "carrier_search_label": candidate_label,
                    "learning_reading": reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(symbol_rows[0].keys()))
            writer.writeheader()
            writer.writerows(symbol_rows)

        summary = {
            "acceptance_posture": "freeze_v134iq_commercial_aerospace_expanded_symbol_universe_carrier_search_audit_v1",
            "expanded_formal_symbol_count": len(symbol_rows),
            "outside_named_formal_symbol_count": sum(1 for row in symbol_rows if not row["inside_named_set"]),
            "priority_second_carrier_candidate_count": sum(
                1 for row in symbol_rows if row["carrier_search_label"] == "priority_second_carrier_search_candidate"
            ),
            "formal_strength_watch_count": sum(
                1 for row in symbol_rows if row["carrier_search_label"] == "formal_strength_watch_not_yet_carrier"
            ),
            "carrier_search_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the first disciplined expanded-universe pass points to one priority outside-named second-carrier search candidate inside the formal/core symbol set, while the other formal names remain watches or noncandidates",
        }
        interpretation = [
            "V1.34IQ opens the expanded-symbol-universe route conservatively by searching only the formal/core commercial aerospace names first.",
            "The point is not to promote a new carrier immediately, but to prove whether the next evidence source really exists outside the original named set.",
        ]
        return V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Report(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IQCommercialAerospaceExpandedSymbolUniverseCarrierSearchAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iq_commercial_aerospace_expanded_symbol_universe_carrier_search_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
