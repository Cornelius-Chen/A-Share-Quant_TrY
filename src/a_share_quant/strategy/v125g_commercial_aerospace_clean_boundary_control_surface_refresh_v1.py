from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125f_commercial_aerospace_role_grammar_refresh_v3 import (
    V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer,
)


LOOKBACK = 20
FORWARD = 10

CONTROL_FEATURES = [
    "trend_return_20",
    "elg_buy_sell_ratio_mean",
    "liquidity_amount_mean",
    "up_day_rate",
    "limit_heat_rate",
]
RISK_FEATURES = [
    "turnover_rate_f_mean",
    "volume_ratio_mean",
]

VARIANTS = [
    ("clean_core_reference", None, None),
    ("confirmation_gate_zero", 0.0, 0.0),
    ("confirmation_gate_mild", 0.15, -0.15),
    ("confirmation_gate_strict", 0.30, -0.30),
]


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.daily_basic_path = repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        self.moneyflow_path = repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
        self.stk_limit_path = repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"

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

    def _layer_symbols(self) -> tuple[list[str], list[str]]:
        grammar = V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer(self.repo_root).analyze()
        control_symbols = [row["symbol"] for row in grammar.role_rows if row["role_layer"] == "control_core"]
        confirmation_symbols = [row["symbol"] for row in grammar.role_rows if row["role_layer"] == "confirmation"]
        return control_symbols, confirmation_symbols

    def _build_rows(self) -> tuple[list[dict[str, Any]], dict[str, float]]:
        control_symbols, confirmation_symbols = self._layer_symbols()
        focus_symbols = set(control_symbols) | set(confirmation_symbols)

        daily = self._group_by_symbol(_load_csv(self.daily_path))
        daily_basic = self._group_by_symbol(_load_csv(self.daily_basic_path))
        moneyflow = self._group_by_symbol(_load_csv(self.moneyflow_path))
        stk_limit = self._group_by_symbol(_load_csv(self.stk_limit_path))

        row_pool: list[dict[str, Any]] = []
        for symbol in focus_symbols:
            d = daily[symbol]
            b = daily_basic[symbol]
            m = moneyflow[symbol]
            l = stk_limit[symbol]
            dates = sorted(
                set(r["trade_date"] for r in d)
                & set(r["trade_date"] for r in b)
                & set(r["trade_date"] for r in m)
                & set(r["trade_date"] for r in l)
            )
            d_map = {r["trade_date"]: r for r in d}
            b_map = {r["trade_date"]: r for r in b}
            m_map = {r["trade_date"]: r for r in m}
            l_map = {r["trade_date"]: r for r in l}
            for idx in range(LOOKBACK - 1, len(dates) - FORWARD):
                date = dates[idx]
                window_dates = dates[idx - LOOKBACK + 1 : idx + 1]
                close_now = _to_float(d_map[date]["close"])
                close_prev20 = _to_float(d_map[window_dates[0]]["close"])
                close_fwd = _to_float(d_map[dates[idx + FORWARD]]["close"])
                row_pool.append(
                    {
                        "trade_date": date,
                        "symbol": symbol,
                        "layer": "control_core" if symbol in control_symbols else "confirmation",
                        "trend_return_20": 0.0 if close_prev20 == 0 else close_now / close_prev20 - 1.0,
                        "forward_return_10": 0.0 if close_now == 0 else close_fwd / close_now - 1.0,
                        "up_day_rate": sum(
                            1
                            for dt in window_dates
                            if _to_float(d_map[dt]["close"]) > _to_float(d_map[dt]["pre_close"])
                        )
                        / LOOKBACK,
                        "liquidity_amount_mean": sum(_to_float(d_map[dt]["amount"]) for dt in window_dates) / LOOKBACK,
                        "turnover_rate_f_mean": sum(_to_float(b_map[dt]["turnover_rate_f"]) for dt in window_dates) / LOOKBACK,
                        "volume_ratio_mean": sum(_to_float(b_map[dt]["volume_ratio"]) for dt in window_dates) / LOOKBACK,
                        "elg_buy_sell_ratio_mean": sum(
                            (_to_float(m_map[dt].get("buy_elg_amount", "")) + 1.0)
                            / (_to_float(m_map[dt].get("sell_elg_amount", "")) + 1.0)
                            for dt in window_dates
                        )
                        / LOOKBACK,
                        "limit_heat_rate": sum(
                            1
                            for dt in window_dates
                            if _to_float(l_map[dt]["up_limit"]) > 0
                            and _to_float(d_map[dt]["close"]) / _to_float(l_map[dt]["up_limit"]) >= 0.97
                        )
                        / LOOKBACK,
                    }
                )
        return row_pool, {"control_count": float(len(control_symbols)), "confirmation_count": float(len(confirmation_symbols))}

    def analyze(self) -> V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshReport:
        row_pool, layer_counts = self._build_rows()
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in row_pool:
            by_date.setdefault(row["trade_date"], []).append(row)

        variant_rows: list[dict[str, Any]] = []
        for variant, gate_up, gate_down in VARIANTS:
            audited: list[dict[str, Any]] = []
            for trade_date, rows in by_date.items():
                local_control = [r for r in rows if r["layer"] == "control_core"]
                local_confirm = [r for r in rows if r["layer"] == "confirmation"]
                if len(local_control) < 4 or len(local_confirm) < 4:
                    continue
                z_control = {key: self._z({r["symbol"]: r[key] for r in local_control}) for key in CONTROL_FEATURES + RISK_FEATURES}
                z_confirm = {key: self._z({r["symbol"]: r[key] for r in local_confirm}) for key in CONTROL_FEATURES}
                confirmation_breadth_score = (
                    0.30 * (sum(z_confirm["trend_return_20"].values()) / len(z_confirm["trend_return_20"]))
                    + 0.25 * (sum(z_confirm["up_day_rate"].values()) / len(z_confirm["up_day_rate"]))
                    + 0.20 * (sum(z_confirm["limit_heat_rate"].values()) / len(z_confirm["limit_heat_rate"]))
                    + 0.15 * (sum(z_confirm["liquidity_amount_mean"].values()) / len(z_confirm["liquidity_amount_mean"]))
                    + 0.10 * (sum(z_confirm["elg_buy_sell_ratio_mean"].values()) / len(z_confirm["elg_buy_sell_ratio_mean"]))
                )

                scored: list[dict[str, Any]] = []
                for row in local_control:
                    symbol = row["symbol"]
                    control_strength_score = (
                        0.28 * z_control["liquidity_amount_mean"][symbol]
                        + 0.24 * z_control["elg_buy_sell_ratio_mean"][symbol]
                        + 0.20 * z_control["trend_return_20"][symbol]
                        + 0.16 * z_control["up_day_rate"][symbol]
                        + 0.12 * z_control["limit_heat_rate"][symbol]
                    )
                    de_risk_watch_score = (
                        0.30 * (-z_control["trend_return_20"][symbol])
                        + 0.25 * (-z_control["elg_buy_sell_ratio_mean"][symbol])
                        + 0.20 * z_control["turnover_rate_f_mean"][symbol]
                        + 0.15 * z_control["volume_ratio_mean"][symbol]
                        + 0.10 * (-z_control["up_day_rate"][symbol])
                    )
                    scored.append(
                        {
                            **row,
                            "confirmation_breadth_score": confirmation_breadth_score,
                            "control_strength_score": control_strength_score,
                            "de_risk_watch_score": de_risk_watch_score,
                        }
                    )
                strength_sorted = sorted(scored, key=lambda r: r["control_strength_score"], reverse=True)
                risk_sorted = sorted(scored, key=lambda r: r["de_risk_watch_score"], reverse=True)
                eligibility_candidates = {r["symbol"] for r in strength_sorted[:3]}
                risk_candidates = {r["symbol"] for r in risk_sorted[:4]}
                for row in scored:
                    eligibility_flag = row["symbol"] in eligibility_candidates
                    de_risk_watch_flag = row["symbol"] in risk_candidates
                    if gate_up is not None:
                        eligibility_flag = eligibility_flag and row["confirmation_breadth_score"] >= gate_up
                    if gate_down is not None:
                        de_risk_watch_flag = de_risk_watch_flag and row["confirmation_breadth_score"] <= gate_down
                    audited.append(
                        {
                            **row,
                            "eligibility_flag": eligibility_flag,
                            "de_risk_watch_flag": de_risk_watch_flag,
                        }
                    )

            elig = [r["forward_return_10"] for r in audited if r["eligibility_flag"]]
            non_elig = [r["forward_return_10"] for r in audited if not r["eligibility_flag"]]
            risk = [r["forward_return_10"] for r in audited if r["de_risk_watch_flag"]]
            non_risk = [r["forward_return_10"] for r in audited if not r["de_risk_watch_flag"]]

            by_year: dict[str, list[dict[str, Any]]] = {}
            for row in audited:
                by_year.setdefault(row["trade_date"][:4], []).append(row)

            eligibility_year_spreads: list[float] = []
            de_risk_year_spreads: list[float] = []
            for year_rows in by_year.values():
                year_elig = [r["forward_return_10"] for r in year_rows if r["eligibility_flag"]]
                year_non_elig = [r["forward_return_10"] for r in year_rows if not r["eligibility_flag"]]
                if year_elig and year_non_elig:
                    eligibility_year_spreads.append((sum(year_elig) / len(year_elig)) - (sum(year_non_elig) / len(year_non_elig)))
                year_risk = [r["forward_return_10"] for r in year_rows if r["de_risk_watch_flag"]]
                year_non_risk = [r["forward_return_10"] for r in year_rows if not r["de_risk_watch_flag"]]
                if year_risk and year_non_risk:
                    de_risk_year_spreads.append((sum(year_non_risk) / len(year_non_risk)) - (sum(year_risk) / len(year_risk)))

            eligibility_spread = (sum(elig) / len(elig) - sum(non_elig) / len(non_elig)) if elig and non_elig else 0.0
            de_risk_spread = (sum(non_risk) / len(non_risk) - sum(risk) / len(risk)) if risk and non_risk else 0.0
            objective = (
                (sum(eligibility_year_spreads) / len(eligibility_year_spreads) if eligibility_year_spreads else -999.0)
                + (sum(de_risk_year_spreads) / len(de_risk_year_spreads) if de_risk_year_spreads else -999.0)
            )
            variant_rows.append(
                {
                    "variant": variant,
                    "eligibility_forward_spread_10": round(eligibility_spread, 8),
                    "de_risk_avoidance_spread_10": round(de_risk_spread, 8),
                    "eligibility_year_spread_mean": round(
                        sum(eligibility_year_spreads) / len(eligibility_year_spreads), 8
                    )
                    if eligibility_year_spreads
                    else 0.0,
                    "eligibility_year_spread_min": round(min(eligibility_year_spreads), 8)
                    if eligibility_year_spreads
                    else 0.0,
                    "de_risk_year_spread_mean": round(sum(de_risk_year_spreads) / len(de_risk_year_spreads), 8)
                    if de_risk_year_spreads
                    else 0.0,
                    "de_risk_year_spread_min": round(min(de_risk_year_spreads), 8)
                    if de_risk_year_spreads
                    else 0.0,
                    "eligibility_flag_count": len(elig),
                    "de_risk_flag_count": len(risk),
                    "objective_score": round(objective, 8),
                }
            )

        variant_rows.sort(key=lambda r: (r["objective_score"], r["eligibility_year_spread_mean"]), reverse=True)
        best_variant = variant_rows[0]
        summary = {
            "acceptance_posture": "freeze_v125g_commercial_aerospace_clean_boundary_control_surface_refresh_v1",
            "variant_count": len(variant_rows),
            "control_core_count": int(layer_counts["control_count"]),
            "confirmation_count": int(layer_counts["confirmation_count"]),
            "best_variant": best_variant["variant"],
            "best_eligibility_year_spread_mean": best_variant["eligibility_year_spread_mean"],
            "best_de_risk_year_spread_mean": best_variant["de_risk_year_spread_mean"],
        }
        interpretation = [
            "V1.25G rebuilds commercial-aerospace control semantics after boundary cleanup, using only control_core plus clean confirmation breadth.",
            "The purpose is to see whether confirmation breadth can make the control surface lawful again once sentiment-watch names are fully isolated.",
        ]
        return V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125GCommercialAerospaceCleanBoundaryControlSurfaceRefreshAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125g_commercial_aerospace_clean_boundary_control_surface_refresh_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
