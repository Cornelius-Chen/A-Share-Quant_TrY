from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v124v_commercial_aerospace_control_core_thinning_retriage_v1 import (
    V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer,
)


LOOKBACK = 20
FORWARD = 10


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V124ZCommercialAerospaceControlSurfaceRollingForwardAuditReport:
    summary: dict[str, Any]
    audit_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "audit_rows": self.audit_rows,
            "interpretation": self.interpretation,
        }


class V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.daily_basic_path = repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        self.moneyflow_path = repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
        self.stk_limit_path = repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"

    def _formal_core_symbols(self) -> list[str]:
        result = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(self.repo_root).analyze()
        return [row["symbol"] for row in result.control_core_rows]

    def _group_by_symbol(self, rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row["symbol"], []).append(row)
        for values in grouped.values():
            values.sort(key=lambda r: r["trade_date"])
        return grouped

    def _z(self, values: dict[str, float]) -> dict[str, float]:
        mean = sum(values.values()) / len(values)
        var = sum((v - mean) ** 2 for v in values.values()) / len(values)
        std = math.sqrt(var) or 1.0
        return {k: (v - mean) / std for k, v in values.items()}

    def analyze(self) -> V124ZCommercialAerospaceControlSurfaceRollingForwardAuditReport:
        symbols = self._formal_core_symbols()
        daily = self._group_by_symbol(_load_csv(self.daily_path))
        daily_basic = self._group_by_symbol(_load_csv(self.daily_basic_path))
        moneyflow = self._group_by_symbol(_load_csv(self.moneyflow_path))
        stk_limit = self._group_by_symbol(_load_csv(self.stk_limit_path))

        row_pool: list[dict[str, Any]] = []
        for symbol in symbols:
            d = daily[symbol]
            b = daily_basic[symbol]
            m = moneyflow[symbol]
            l = stk_limit[symbol]
            dates = sorted(set(r["trade_date"] for r in d) & set(r["trade_date"] for r in b) & set(r["trade_date"] for r in m) & set(r["trade_date"] for r in l))
            d_map = {r["trade_date"]: r for r in d}
            b_map = {r["trade_date"]: r for r in b}
            m_map = {r["trade_date"]: r for r in m}
            l_map = {r["trade_date"]: r for r in l}
            if len(dates) <= LOOKBACK + FORWARD:
                continue
            for idx in range(LOOKBACK - 1, len(dates) - FORWARD):
                date = dates[idx]
                window_dates = dates[idx - LOOKBACK + 1 : idx + 1]
                close_now = _to_float(d_map[date]["close"])
                close_prev20 = _to_float(d_map[window_dates[0]]["close"])
                close_fwd = _to_float(d_map[dates[idx + FORWARD]]["close"])
                trend_return_20 = 0.0 if close_prev20 == 0 else close_now / close_prev20 - 1.0
                forward_return_10 = 0.0 if close_now == 0 else close_fwd / close_now - 1.0
                up_day_rate = sum(1 for dt in window_dates if _to_float(d_map[dt]["close"]) > _to_float(d_map[dt]["pre_close"])) / LOOKBACK
                liquidity_amount_mean = sum(_to_float(d_map[dt]["amount"]) for dt in window_dates) / LOOKBACK
                turnover_rate_f_mean = sum(_to_float(b_map[dt]["turnover_rate_f"]) for dt in window_dates) / LOOKBACK
                volume_ratio_mean = sum(_to_float(b_map[dt]["volume_ratio"]) for dt in window_dates) / LOOKBACK
                elg_buy_sell_ratio_mean = sum(
                    (_to_float(m_map[dt].get("buy_elg_amount", "")) + 1.0) / (_to_float(m_map[dt].get("sell_elg_amount", "")) + 1.0)
                    for dt in window_dates
                ) / LOOKBACK
                limit_heat_rate = sum(
                    1
                    for dt in window_dates
                    if _to_float(l_map[dt]["up_limit"]) > 0 and _to_float(d_map[dt]["close"]) / _to_float(l_map[dt]["up_limit"]) >= 0.97
                ) / LOOKBACK
                row_pool.append(
                    {
                        "trade_date": date,
                        "symbol": symbol,
                        "trend_return_20": trend_return_20,
                        "turnover_rate_f_mean": turnover_rate_f_mean,
                        "volume_ratio_mean": volume_ratio_mean,
                        "elg_buy_sell_ratio_mean": elg_buy_sell_ratio_mean,
                        "limit_heat_rate": limit_heat_rate,
                        "up_day_rate": up_day_rate,
                        "liquidity_amount_mean": liquidity_amount_mean,
                        "forward_return_10": forward_return_10,
                    }
                )

        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in row_pool:
            by_date.setdefault(row["trade_date"], []).append(row)

        scored_rows: list[dict[str, Any]] = []
        for trade_date, rows in by_date.items():
            if len(rows) < 4:
                continue
            z_trend = self._z({r["symbol"]: r["trend_return_20"] for r in rows})
            z_turn = self._z({r["symbol"]: r["turnover_rate_f_mean"] for r in rows})
            z_volr = self._z({r["symbol"]: r["volume_ratio_mean"] for r in rows})
            z_elg = self._z({r["symbol"]: r["elg_buy_sell_ratio_mean"] for r in rows})
            z_limit = self._z({r["symbol"]: r["limit_heat_rate"] for r in rows})
            z_up = self._z({r["symbol"]: r["up_day_rate"] for r in rows})
            z_liq = self._z({r["symbol"]: r["liquidity_amount_mean"] for r in rows})

            local = []
            for row in rows:
                symbol = row["symbol"]
                control_strength_score = (
                    0.28 * z_liq[symbol]
                    + 0.24 * z_elg[symbol]
                    + 0.20 * z_trend[symbol]
                    + 0.16 * z_up[symbol]
                    + 0.12 * z_limit[symbol]
                )
                de_risk_watch_score = (
                    0.30 * (-z_trend[symbol])
                    + 0.25 * (-z_elg[symbol])
                    + 0.20 * z_turn[symbol]
                    + 0.15 * z_volr[symbol]
                    + 0.10 * (-z_up[symbol])
                )
                local.append({**row, "control_strength_score": control_strength_score, "de_risk_watch_score": de_risk_watch_score})

            local.sort(key=lambda r: r["control_strength_score"], reverse=True)
            eligibles = {r["symbol"] for r in local[:3]}
            local.sort(key=lambda r: r["de_risk_watch_score"], reverse=True)
            de_risks = {r["symbol"] for r in local[:4]}
            for row in local:
                scored_rows.append(
                    {
                        **row,
                        "eligibility_flag": row["symbol"] in eligibles,
                        "de_risk_watch_flag": row["symbol"] in de_risks,
                    }
                )

        elig = [r["forward_return_10"] for r in scored_rows if r["eligibility_flag"]]
        non_elig = [r["forward_return_10"] for r in scored_rows if not r["eligibility_flag"]]
        risk = [r["forward_return_10"] for r in scored_rows if r["de_risk_watch_flag"]]
        non_risk = [r["forward_return_10"] for r in scored_rows if not r["de_risk_watch_flag"]]
        summary = {
            "acceptance_posture": "freeze_v124z_commercial_aerospace_control_surface_rolling_forward_audit_v1",
            "row_count": len(scored_rows),
            "date_count": len({r["trade_date"] for r in scored_rows}),
            "symbol_count": len({r["symbol"] for r in scored_rows}),
            "eligibility_mean_forward_return_10": round(sum(elig) / len(elig), 8),
            "non_eligibility_mean_forward_return_10": round(sum(non_elig) / len(non_elig), 8),
            "de_risk_watch_mean_forward_return_10": round(sum(risk) / len(risk), 8),
            "non_de_risk_watch_mean_forward_return_10": round(sum(non_risk) / len(non_risk), 8),
            "eligibility_positive_rate": round(sum(1 for x in elig if x > 0) / len(elig), 6),
            "de_risk_watch_negative_rate": round(sum(1 for x in risk if x < 0) / len(risk), 6),
        }
        interpretation = [
            "V1.24Z converts the first commercial-aerospace control surface into a rolling forward audit rather than a single end-of-sample snapshot.",
            "This is the first legality check before replay: eligibility rows should have better forward outcomes, while de-risk-watch rows should skew weaker.",
        ]
        return V124ZCommercialAerospaceControlSurfaceRollingForwardAuditReport(
            summary=summary,
            audit_rows=scored_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124ZCommercialAerospaceControlSurfaceRollingForwardAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124ZCommercialAerospaceControlSurfaceRollingForwardAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124z_commercial_aerospace_control_surface_rolling_forward_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
