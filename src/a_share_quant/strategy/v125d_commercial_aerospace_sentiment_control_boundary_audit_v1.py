from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
SENTIMENT_FEATURES = [
    "trend_return_20",
    "turnover_rate_f_mean",
    "volume_ratio_mean",
    "limit_heat_rate",
    "up_day_rate",
    "liquidity_amount_mean",
]


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V125DCommercialAerospaceSentimentControlBoundaryAuditReport:
    summary: dict[str, Any]
    boundary_rows: list[dict[str, Any]]
    recommended_sentiment_rows: list[dict[str, Any]]
    boundary_risk_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "boundary_rows": self.boundary_rows,
            "recommended_sentiment_rows": self.recommended_sentiment_rows,
            "boundary_risk_rows": self.boundary_risk_rows,
            "interpretation": self.interpretation,
        }


class V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.universe_path = repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"
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

    def _build_row_pool(self) -> list[dict[str, Any]]:
        universe_rows = _load_csv(self.universe_path)
        daily = self._group_by_symbol(_load_csv(self.daily_path))
        daily_basic = self._group_by_symbol(_load_csv(self.daily_basic_path))
        moneyflow = self._group_by_symbol(_load_csv(self.moneyflow_path))
        stk_limit = self._group_by_symbol(_load_csv(self.stk_limit_path))

        row_pool: list[dict[str, Any]] = []
        for meta in universe_rows:
            symbol = meta["symbol"]
            d = daily.get(symbol, [])
            b = daily_basic.get(symbol, [])
            m = moneyflow.get(symbol, [])
            l = stk_limit.get(symbol, [])
            if not d or not b or not m or not l:
                continue
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
                up_day_rate = sum(
                    1 for dt in window_dates if _to_float(d_map[dt]["close"]) > _to_float(d_map[dt]["pre_close"])
                ) / LOOKBACK
                liquidity_amount_mean = sum(_to_float(d_map[dt]["amount"]) for dt in window_dates) / LOOKBACK
                turnover_rate_f_mean = sum(_to_float(b_map[dt]["turnover_rate_f"]) for dt in window_dates) / LOOKBACK
                volume_ratio_mean = sum(_to_float(b_map[dt]["volume_ratio"]) for dt in window_dates) / LOOKBACK
                elg_buy_sell_ratio_mean = sum(
                    (_to_float(m_map[dt].get("buy_elg_amount", "")) + 1.0)
                    / (_to_float(m_map[dt].get("sell_elg_amount", "")) + 1.0)
                    for dt in window_dates
                ) / LOOKBACK
                limit_heat_rate = sum(
                    1
                    for dt in window_dates
                    if _to_float(l_map[dt]["up_limit"]) > 0
                    and _to_float(d_map[dt]["close"]) / _to_float(l_map[dt]["up_limit"]) >= 0.97
                ) / LOOKBACK
                row_pool.append(
                    {
                        "trade_date": date,
                        "symbol": symbol,
                        "name": meta["name"],
                        "group": meta["group"],
                        "subgroup": meta["subgroup"],
                        "confidence": meta["confidence"],
                        "source_layer": meta["source_layer"],
                        "reason": meta["reason"],
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
        return row_pool

    def analyze(self) -> V125DCommercialAerospaceSentimentControlBoundaryAuditReport:
        row_pool = self._build_row_pool()
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in row_pool:
            by_date.setdefault(row["trade_date"], []).append(row)

        scored_rows: list[dict[str, Any]] = []
        for trade_date, rows in by_date.items():
            if len(rows) < 8:
                continue
            z_control = {key: self._z({r["symbol"]: r[key] for r in rows}) for key in CONTROL_FEATURES + RISK_FEATURES}
            z_sentiment = {key: self._z({r["symbol"]: r[key] for r in rows}) for key in SENTIMENT_FEATURES}

            local: list[dict[str, Any]] = []
            for row in rows:
                symbol = row["symbol"]
                control_like_score = (
                    0.28 * z_control["liquidity_amount_mean"][symbol]
                    + 0.24 * z_control["elg_buy_sell_ratio_mean"][symbol]
                    + 0.20 * z_control["trend_return_20"][symbol]
                    + 0.16 * z_control["up_day_rate"][symbol]
                    + 0.12 * z_control["limit_heat_rate"][symbol]
                )
                de_risk_like_score = (
                    0.30 * (-z_control["trend_return_20"][symbol])
                    + 0.25 * (-z_control["elg_buy_sell_ratio_mean"][symbol])
                    + 0.20 * z_control["turnover_rate_f_mean"][symbol]
                    + 0.15 * z_control["volume_ratio_mean"][symbol]
                    + 0.10 * (-z_control["up_day_rate"][symbol])
                )
                sentiment_like_score = (
                    0.26 * z_sentiment["limit_heat_rate"][symbol]
                    + 0.22 * z_sentiment["turnover_rate_f_mean"][symbol]
                    + 0.18 * z_sentiment["volume_ratio_mean"][symbol]
                    + 0.14 * z_sentiment["up_day_rate"][symbol]
                    + 0.12 * z_sentiment["liquidity_amount_mean"][symbol]
                    + 0.08 * z_sentiment["trend_return_20"][symbol]
                )
                local.append(
                    {
                        **row,
                        "control_like_score": control_like_score,
                        "de_risk_like_score": de_risk_like_score,
                        "sentiment_like_score": sentiment_like_score,
                    }
                )

            local_control_sorted = sorted(local, key=lambda r: r["control_like_score"], reverse=True)
            local_sentiment_sorted = sorted(local, key=lambda r: r["sentiment_like_score"], reverse=True)
            control_top = {r["symbol"] for r in local_control_sorted[: max(3, round(len(local) * 0.25))]}
            sentiment_top = {r["symbol"] for r in local_sentiment_sorted[: max(5, round(len(local) * 0.20))]}

            for row in local:
                scored_rows.append(
                    {
                        **row,
                        "control_top_flag": row["symbol"] in control_top,
                        "sentiment_top_flag": row["symbol"] in sentiment_top,
                    }
                )

        per_symbol: dict[str, list[dict[str, Any]]] = {}
        for row in scored_rows:
            per_symbol.setdefault(row["symbol"], []).append(row)

        boundary_rows: list[dict[str, Any]] = []
        recommended_sentiment_rows: list[dict[str, Any]] = []
        boundary_risk_rows: list[dict[str, Any]] = []
        for symbol, rows in per_symbol.items():
            base = rows[0]
            n = len(rows)
            control_top_rate = sum(1 for r in rows if r["control_top_flag"]) / n
            sentiment_top_rate = sum(1 for r in rows if r["sentiment_top_flag"]) / n
            control_forward_mean = sum(r["forward_return_10"] for r in rows if r["control_top_flag"]) / max(
                1, sum(1 for r in rows if r["control_top_flag"])
            )
            sentiment_forward_mean = sum(r["forward_return_10"] for r in rows if r["sentiment_top_flag"]) / max(
                1, sum(1 for r in rows if r["sentiment_top_flag"])
            )
            control_score_mean = sum(r["control_like_score"] for r in rows) / n
            sentiment_score_mean = sum(r["sentiment_like_score"] for r in rows) / n
            semantic = "mirror_only"
            recommendation = "keep_outside_control"
            if base["group"] == "正式组":
                semantic = "formal_control_reference"
                recommendation = "keep_in_control_core"
            elif sentiment_top_rate >= 0.20 and control_top_rate < 0.12:
                semantic = "sentiment_leadership_candidate"
                recommendation = "promote_to_sentiment_layer"
            elif sentiment_top_rate >= 0.15 and control_top_rate >= 0.12:
                semantic = "boundary_risk"
                recommendation = "quarantine_from_control_and_watch"
            elif sentiment_top_rate >= 0.10:
                semantic = "sympathy_or_secondary"
                recommendation = "keep_as_sentiment_or_mirror"

            enriched = {
                "symbol": symbol,
                "name": base["name"],
                "group": base["group"],
                "subgroup": base["subgroup"],
                "confidence": base["confidence"],
                "source_layer": base["source_layer"],
                "boundary_semantic": semantic,
                "boundary_recommendation": recommendation,
                "sample_count": n,
                "control_top_rate": round(control_top_rate, 6),
                "sentiment_top_rate": round(sentiment_top_rate, 6),
                "control_score_mean": round(control_score_mean, 6),
                "sentiment_score_mean": round(sentiment_score_mean, 6),
                "control_forward_mean_10": round(control_forward_mean, 8),
                "sentiment_forward_mean_10": round(sentiment_forward_mean, 8),
                "boundary_gap_sentiment_minus_control": round(sentiment_top_rate - control_top_rate, 6),
            }
            boundary_rows.append(enriched)
            if recommendation == "promote_to_sentiment_layer":
                recommended_sentiment_rows.append(enriched)
            if semantic == "boundary_risk":
                boundary_risk_rows.append(enriched)

        boundary_rows.sort(
            key=lambda r: (
                r["boundary_semantic"] != "formal_control_reference",
                r["boundary_recommendation"] != "promote_to_sentiment_layer",
                -r["sentiment_top_rate"],
                -r["control_top_rate"],
                r["symbol"],
            )
        )
        recommended_sentiment_rows.sort(key=lambda r: (-r["sentiment_top_rate"], r["symbol"]))
        boundary_risk_rows.sort(key=lambda r: (-r["control_top_rate"], -r["sentiment_top_rate"], r["symbol"]))

        symbol_of_interest = next((row for row in boundary_rows if row["symbol"] == "000547"), None)
        summary = {
            "acceptance_posture": "freeze_v125d_commercial_aerospace_sentiment_control_boundary_audit_v1",
            "row_count": len(scored_rows),
            "symbol_count": len(boundary_rows),
            "recommended_sentiment_count": len(recommended_sentiment_rows),
            "boundary_risk_count": len(boundary_risk_rows),
            "000547_boundary_semantic": None if symbol_of_interest is None else symbol_of_interest["boundary_semantic"],
            "000547_boundary_recommendation": None
            if symbol_of_interest is None
            else symbol_of_interest["boundary_recommendation"],
            "authoritative_rule": "sentiment_strength_may_confirm_heat_or_upgrade_names_into_sentiment_layer_but_may_not_silently_take_control_authority",
            "recommended_next_posture": "refresh_role_grammar_if_boundary_audit_produces_clean_sentiment_promotions_and_no_nonformal_control_override",
        }
        interpretation = [
            "V1.25D audits the boundary between lawful industrial control authority and A-share sentiment leadership.",
            "The point is not to force name stocks into control, but to stop sentiment-dominant names from hiding inside a generic mirror bucket.",
            "A non-formal name should only be promoted if its rolling sentiment presence is durable while its control presence stays meaningfully lower.",
        ]
        return V125DCommercialAerospaceSentimentControlBoundaryAuditReport(
            summary=summary,
            boundary_rows=boundary_rows,
            recommended_sentiment_rows=recommended_sentiment_rows,
            boundary_risk_rows=boundary_risk_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125DCommercialAerospaceSentimentControlBoundaryAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125d_commercial_aerospace_sentiment_control_boundary_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
