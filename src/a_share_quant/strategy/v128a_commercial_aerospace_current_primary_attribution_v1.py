from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v127g_commercial_aerospace_primary_reference_attribution_v1 import (
    V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer,
    _load_csv,
)
from a_share_quant.strategy.v127y_commercial_aerospace_primary_reference_robustness_audit_v1 import (
    V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer,
)


@dataclass(slots=True)
class V128ACommercialAerospaceCurrentPrimaryAttributionReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    symbol_attribution_rows: list[dict[str, Any]]
    drawdown_rows: list[dict[str, Any]]
    reason_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "symbol_attribution_rows": self.symbol_attribution_rows,
            "drawdown_rows": self.drawdown_rows,
            "reason_rows": self.reason_rows,
            "interpretation": self.interpretation,
        }


class V128ACommercialAerospaceCurrentPrimaryAttributionAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.helper = V127GCommercialAerospacePrimaryReferenceAttributionAnalyzer(repo_root)
        self.robustness = V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer(repo_root)
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"

    @staticmethod
    def _reason_rows(variant_name: str, order_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        counter: Counter[tuple[str, str]] = Counter(
            (row["action"], row["reason"])
            for row in order_rows
        )
        return [
            {
                "variant": variant_name,
                "action": action,
                "reason": reason,
                "count": count,
            }
            for (action, reason), count in sorted(counter.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
        ]

    def analyze(self) -> V128ACommercialAerospaceCurrentPrimaryAttributionReport:
        rows, ordered_dates = self.robustness._prepare_rows()
        split_idx = max(1, round(len(ordered_dates) * 0.80))
        test_dates = ordered_dates[split_idx:]
        old_primary = self.robustness._simulate_variant(
            rows=rows,
            ordered_dates=ordered_dates,
            test_dates=test_dates,
            config=self.robustness.old_variant,
        )
        new_primary = self.robustness._simulate_variant(
            rows=rows,
            ordered_dates=ordered_dates,
            test_dates=test_dates,
            config=self.robustness.new_variant,
        )

        daily_map = {(row["symbol"], row["trade_date"]): row for row in _load_csv(self.daily_path)}
        variant_rows = [
            {
                "variant": old_primary["variant"],
                "final_equity": old_primary["final_equity"],
                "max_drawdown": old_primary["max_drawdown"],
                "executed_order_count": old_primary["executed_order_count"],
            },
            {
                "variant": new_primary["variant"],
                "final_equity": new_primary["final_equity"],
                "max_drawdown": new_primary["max_drawdown"],
                "executed_order_count": new_primary["executed_order_count"],
            },
        ]

        symbol_attribution_rows = self.helper._symbol_attribution_rows(
            variant_name=old_primary["variant"],
            daily_rows=old_primary["daily_rows"],
            order_rows=old_primary["order_rows"],
            daily_map=daily_map,
        ) + self.helper._symbol_attribution_rows(
            variant_name=new_primary["variant"],
            daily_rows=new_primary["daily_rows"],
            order_rows=new_primary["order_rows"],
            daily_map=daily_map,
        )

        new_episodes = self.helper._drawdown_episodes(new_primary["daily_rows"])[:3]
        drawdown_rows: list[dict[str, Any]] = []
        for episode in new_episodes:
            peak = episode["peak_trade_date"]
            trough = episode["trough_trade_date"]
            old_reduce_count, old_reduce_notional = self.helper._reduce_orders_in_window(old_primary["order_rows"], peak, trough)
            new_reduce_count, new_reduce_notional = self.helper._reduce_orders_in_window(new_primary["order_rows"], peak, trough)
            drawdown_rows.append(
                {
                    "peak_trade_date": peak,
                    "trough_trade_date": trough,
                    "old_drawdown": self.helper._window_drawdown(old_primary["daily_rows"], peak, trough),
                    "new_drawdown": self.helper._window_drawdown(new_primary["daily_rows"], peak, trough),
                    "old_reduce_count": old_reduce_count,
                    "old_reduce_notional": old_reduce_notional,
                    "new_reduce_count": new_reduce_count,
                    "new_reduce_notional": new_reduce_notional,
                }
            )

        reason_rows = self._reason_rows(old_primary["variant"], old_primary["order_rows"]) + self._reason_rows(
            new_primary["variant"],
            new_primary["order_rows"],
        )

        old_symbol_pnl = {row["symbol"]: row["total_pnl"] for row in symbol_attribution_rows if row["variant"] == old_primary["variant"]}
        new_symbol_pnl = {row["symbol"]: row["total_pnl"] for row in symbol_attribution_rows if row["variant"] == new_primary["variant"]}
        all_symbols = sorted(set(old_symbol_pnl) | set(new_symbol_pnl))
        symbol_deltas = sorted(
            (
                {
                    "symbol": symbol,
                    "total_pnl_delta_new_minus_old": round(new_symbol_pnl.get(symbol, 0.0) - old_symbol_pnl.get(symbol, 0.0), 4),
                }
                for symbol in all_symbols
            ),
            key=lambda item: (-item["total_pnl_delta_new_minus_old"], item["symbol"]),
        )

        summary = {
            "acceptance_posture": "freeze_v128a_commercial_aerospace_current_primary_attribution_v1",
            "old_primary_variant": old_primary["variant"],
            "old_primary_final_equity": old_primary["final_equity"],
            "old_primary_max_drawdown": old_primary["max_drawdown"],
            "new_primary_variant": new_primary["variant"],
            "new_primary_final_equity": new_primary["final_equity"],
            "new_primary_max_drawdown": new_primary["max_drawdown"],
            "equity_delta_new_minus_old": round(new_primary["final_equity"] - old_primary["final_equity"], 4),
            "drawdown_delta_new_minus_old": round(new_primary["max_drawdown"] - old_primary["max_drawdown"], 8),
            "top_symbol_improver": symbol_deltas[0]["symbol"] if symbol_deltas else "",
            "top_symbol_improver_delta": symbol_deltas[0]["total_pnl_delta_new_minus_old"] if symbol_deltas else 0.0,
            "largest_new_drawdown_window": (
                f"{drawdown_rows[0]['peak_trade_date']}->{drawdown_rows[0]['trough_trade_date']}"
                if drawdown_rows
                else ""
            ),
        }
        interpretation = [
            "V1.28A explains why the current commercial-aerospace primary reference beats the prior primary after the robustness freeze.",
            "The attribution compares symbol PnL, top drawdown windows, and execution reasons under the same lawful EOD replay geometry.",
        ]
        return V128ACommercialAerospaceCurrentPrimaryAttributionReport(
            summary=summary,
            variant_rows=variant_rows,
            symbol_attribution_rows=symbol_attribution_rows,
            drawdown_rows=drawdown_rows,
            reason_rows=reason_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128ACommercialAerospaceCurrentPrimaryAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128ACommercialAerospaceCurrentPrimaryAttributionAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128a_commercial_aerospace_current_primary_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
