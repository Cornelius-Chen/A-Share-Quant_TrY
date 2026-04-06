from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v127y_commercial_aerospace_primary_reference_robustness_audit_v1 import (
    V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer,
)


def _equity_on_or_after(daily_rows: list[dict[str, Any]], trade_date: str) -> float:
    for row in daily_rows:
        if row["trade_date"] >= trade_date:
            return float(row["equity"])
    return float(daily_rows[-1]["equity"]) if daily_rows else 1_000_000.0


def _equity_on_or_before(daily_rows: list[dict[str, Any]], trade_date: str) -> float:
    eligible = [row for row in daily_rows if row["trade_date"] <= trade_date]
    return float(eligible[-1]["equity"]) if eligible else (float(daily_rows[0]["equity"]) if daily_rows else 1_000_000.0)


@dataclass(slots=True)
class V128CCommercialAerospaceCurrentPrimaryPortabilityAuditReport:
    summary: dict[str, Any]
    symbol_delta_rows: list[dict[str, Any]]
    period_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_delta_rows": self.symbol_delta_rows,
            "period_rows": self.period_rows,
            "interpretation": self.interpretation,
        }


class V128CCommercialAerospaceCurrentPrimaryPortabilityAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.attr_path = repo_root / "reports" / "analysis" / "v128a_commercial_aerospace_current_primary_attribution_v1.json"
        self.robustness = V127YCommercialAerospacePrimaryReferenceRobustnessAuditAnalyzer(repo_root)

    def analyze(self) -> V128CCommercialAerospaceCurrentPrimaryPortabilityAuditReport:
        attribution = json.loads(self.attr_path.read_text(encoding="utf-8"))
        rows, ordered_dates = self.robustness._prepare_rows()
        split_idx = max(1, round(len(ordered_dates) * 0.80))
        test_dates = ordered_dates[split_idx:]
        old_payload = self.robustness._simulate_variant(
            rows=rows,
            ordered_dates=ordered_dates,
            test_dates=test_dates,
            config=self.robustness.old_variant,
        )
        new_payload = self.robustness._simulate_variant(
            rows=rows,
            ordered_dates=ordered_dates,
            test_dates=test_dates,
            config=self.robustness.new_variant,
        )

        old_variant = attribution["summary"]["old_primary_variant"]
        new_variant = attribution["summary"]["new_primary_variant"]
        symbol_rows = attribution["symbol_attribution_rows"]
        old_symbol = {row["symbol"]: row["total_pnl"] for row in symbol_rows if row["variant"] == old_variant}
        new_symbol = {row["symbol"]: row["total_pnl"] for row in symbol_rows if row["variant"] == new_variant}
        total_delta = float(attribution["summary"]["equity_delta_new_minus_old"])
        symbol_delta_rows = sorted(
            [
                {
                    "symbol": symbol,
                    "old_total_pnl": round(old_symbol.get(symbol, 0.0), 4),
                    "new_total_pnl": round(new_symbol.get(symbol, 0.0), 4),
                    "delta_new_minus_old": round(new_symbol.get(symbol, 0.0) - old_symbol.get(symbol, 0.0), 4),
                    "share_of_total_delta": round(
                        0.0 if total_delta == 0 else (new_symbol.get(symbol, 0.0) - old_symbol.get(symbol, 0.0)) / total_delta,
                        6,
                    ),
                }
                for symbol in sorted(set(old_symbol) | set(new_symbol))
            ],
            key=lambda row: (-row["delta_new_minus_old"], row["symbol"]),
        )

        largest_window = attribution["summary"]["largest_new_drawdown_window"]
        window_start, window_end = largest_window.split("->")
        test_start = test_dates[0]
        test_end = test_dates[-1]

        period_specs = [
            ("pre_window", test_start, "20260111"),
            ("main_window", window_start, window_end),
            ("post_window", "20260213", test_end),
        ]
        period_rows: list[dict[str, Any]] = []
        for label, start, end in period_specs:
            old_start_equity = _equity_on_or_before(old_payload["daily_rows"], start)
            old_end_equity = _equity_on_or_before(old_payload["daily_rows"], end)
            new_start_equity = _equity_on_or_before(new_payload["daily_rows"], start)
            new_end_equity = _equity_on_or_before(new_payload["daily_rows"], end)
            old_change = old_end_equity - old_start_equity
            new_change = new_end_equity - new_start_equity
            period_rows.append(
                {
                    "period_label": label,
                    "start_trade_date": start,
                    "end_trade_date": end,
                    "old_change": round(old_change, 4),
                    "new_change": round(new_change, 4),
                    "delta_new_minus_old": round(new_change - old_change, 4),
                }
            )

        top1 = symbol_delta_rows[0] if symbol_delta_rows else {"share_of_total_delta": 0.0}
        top3_concentration = round(sum(max(0.0, row["share_of_total_delta"]) for row in symbol_delta_rows[:3]), 6)
        main_period = next((row for row in period_rows if row["period_label"] == "main_window"), {"delta_new_minus_old": 0.0})
        pre_period = next((row for row in period_rows if row["period_label"] == "pre_window"), {"delta_new_minus_old": 0.0})
        post_period = next((row for row in period_rows if row["period_label"] == "post_window"), {"delta_new_minus_old": 0.0})

        summary = {
            "acceptance_posture": "freeze_v128c_commercial_aerospace_current_primary_portability_audit_v1",
            "current_primary_variant": new_variant,
            "prior_primary_variant": old_variant,
            "equity_delta_new_minus_old": round(total_delta, 4),
            "top1_symbol_share_of_total_delta": top1["share_of_total_delta"],
            "top3_positive_symbol_share_of_total_delta": top3_concentration,
            "pre_window_delta_new_minus_old": pre_period["delta_new_minus_old"],
            "main_window_delta_new_minus_old": main_period["delta_new_minus_old"],
            "post_window_delta_new_minus_old": post_period["delta_new_minus_old"],
            "portability_status": (
                "moderately_concentrated_but_not_single_symbol_only"
                if top1["share_of_total_delta"] < 0.75 and main_period["delta_new_minus_old"] > 0
                else "concentration_risk_high"
            ),
        }
        interpretation = [
            "V1.28C audits whether the current primary's edge looks portable or is merely concentrated in one symbol or one time segment.",
            "The key test is not universality; it is whether the improvement remains distributed enough that the execution grammar can be treated as a board-level object rather than a single-name accident.",
        ]
        return V128CCommercialAerospaceCurrentPrimaryPortabilityAuditReport(
            summary=summary,
            symbol_delta_rows=symbol_delta_rows,
            period_rows=period_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128CCommercialAerospaceCurrentPrimaryPortabilityAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128CCommercialAerospaceCurrentPrimaryPortabilityAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128c_commercial_aerospace_current_primary_portability_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
