from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125f_commercial_aerospace_role_grammar_refresh_v3 import (
    V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer,
)
from a_share_quant.strategy.v125m_commercial_aerospace_decisive_event_protocol_v1 import (
    V125MCommercialAerospaceDecisiveEventProtocolAnalyzer,
)


EVENT_LOOKBACK_DAYS = 30
EVENT_DECAY_DAYS = 12.0
REGIME_K = 4
KMEANS_ITERS = 20


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


def _parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y%m%d").date()


def _parse_timestamp_date(value: str) -> datetime.date:
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


@dataclass(slots=True)
class V125NCommercialAerospaceStructuralRegimeDiscoveryReport:
    summary: dict[str, Any]
    regime_rows: list[dict[str, Any]]
    date_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "regime_rows": self.regime_rows,
            "date_rows": self.date_rows,
            "interpretation": self.interpretation,
        }


class V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer:
    FEATURE_KEYS = [
        "control_avg_return",
        "control_positive_breadth",
        "control_limit_heat",
        "control_turnover_mean",
        "control_amount_mean",
        "confirmation_positive_breadth",
        "sentiment_positive_breadth",
        "continuation_support",
        "turning_point_risk",
        "termination_risk",
    ]

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.daily_basic_path = (
            repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        )
        self.stk_limit_path = repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"

    def _group_by_symbol(self, rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row["symbol"], []).append(row)
        for values in grouped.values():
            values.sort(key=lambda r: r["trade_date"])
        return grouped

    def _role_sets(self) -> tuple[set[str], set[str], set[str]]:
        grammar = V125FCommercialAerospaceRoleGrammarRefreshV3Analyzer(self.repo_root).analyze()
        control_core = {row["symbol"] for row in grammar.role_rows if row["role_layer"] == "control_core"}
        confirmation = {row["symbol"] for row in grammar.role_rows if row["role_layer"] == "confirmation"}
        sentiment_watch = {row["symbol"] for row in grammar.role_rows if row["role_layer"] == "sentiment_watch"}
        return control_core, confirmation, sentiment_watch

    def _event_maps(self) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
        decisive = V125MCommercialAerospaceDecisiveEventProtocolAnalyzer(self.repo_root).analyze()
        rows = [row for row in decisive.decisive_rows if row["decisive_retained"] and row["public_release_time"]]
        event_rows = [
            {
                "date": _parse_timestamp_date(row["public_release_time"]),
                "semantic": row["decisive_semantic"],
            }
            for row in rows
            if row["record_type"] == "historical_source"
        ]

        daily_rows = _load_csv(self.daily_path)
        trade_dates = sorted({row["trade_date"] for row in daily_rows})
        continuation_map: dict[str, float] = {}
        turning_map: dict[str, float] = {}
        termination_map: dict[str, float] = {}
        for trade_date in trade_dates:
            current_date = _parse_trade_date(trade_date)
            continuation = 0.0
            turning = 0.0
            termination = 0.0
            for event in event_rows:
                days = (current_date - event["date"]).days
                if days < 0 or days > EVENT_LOOKBACK_DAYS:
                    continue
                weight = math.exp(-days / EVENT_DECAY_DAYS)
                if event["semantic"] == "continuation_enabler":
                    continuation += weight
                elif event["semantic"] == "turning_point_watch":
                    turning += weight
                elif event["semantic"] == "termination_or_regulation_risk":
                    termination += weight
            continuation_map[trade_date] = continuation
            turning_map[trade_date] = turning
            termination_map[trade_date] = termination
        return continuation_map, turning_map, termination_map

    def _date_feature_rows(self) -> list[dict[str, Any]]:
        control_core, confirmation, sentiment_watch = self._role_sets()
        continuation_map, turning_map, termination_map = self._event_maps()

        daily = _group_by_symbol = self._group_by_symbol(_load_csv(self.daily_path))
        daily_basic = self._group_by_symbol(_load_csv(self.daily_basic_path))
        stk_limit = self._group_by_symbol(_load_csv(self.stk_limit_path))

        all_dates = sorted({row["trade_date"] for rows in daily.values() for row in rows})
        date_rows: list[dict[str, Any]] = []
        for trade_date in all_dates:
            control_rows: list[dict[str, str]] = []
            control_basic_rows: list[dict[str, str]] = []
            control_limit_rows: list[dict[str, str]] = []
            conf_rows: list[dict[str, str]] = []
            sent_rows: list[dict[str, str]] = []

            for symbol in control_core:
                d_row = next((row for row in daily.get(symbol, []) if row["trade_date"] == trade_date), None)
                b_row = next((row for row in daily_basic.get(symbol, []) if row["trade_date"] == trade_date), None)
                l_row = next((row for row in stk_limit.get(symbol, []) if row["trade_date"] == trade_date), None)
                if d_row and b_row and l_row:
                    control_rows.append(d_row)
                    control_basic_rows.append(b_row)
                    control_limit_rows.append(l_row)
            for symbol in confirmation:
                d_row = next((row for row in daily.get(symbol, []) if row["trade_date"] == trade_date), None)
                if d_row:
                    conf_rows.append(d_row)
            for symbol in sentiment_watch:
                d_row = next((row for row in daily.get(symbol, []) if row["trade_date"] == trade_date), None)
                if d_row:
                    sent_rows.append(d_row)

            if len(control_rows) < 3:
                continue

            control_returns = [
                0.0 if _to_float(row["pre_close"]) == 0 else _to_float(row["close"]) / _to_float(row["pre_close"]) - 1.0
                for row in control_rows
            ]
            conf_returns = [
                0.0 if _to_float(row["pre_close"]) == 0 else _to_float(row["close"]) / _to_float(row["pre_close"]) - 1.0
                for row in conf_rows
            ]
            sent_returns = [
                0.0 if _to_float(row["pre_close"]) == 0 else _to_float(row["close"]) / _to_float(row["pre_close"]) - 1.0
                for row in sent_rows
            ]
            limit_heat = 0.0
            if control_limit_rows:
                limit_heat = sum(
                    1
                    for d_row, l_row in zip(control_rows, control_limit_rows, strict=False)
                    if _to_float(l_row["up_limit"]) > 0 and _to_float(d_row["close"]) / _to_float(l_row["up_limit"]) >= 0.97
                ) / len(control_limit_rows)
            date_rows.append(
                {
                    "trade_date": trade_date,
                    "control_avg_return": sum(control_returns) / len(control_returns),
                    "control_positive_breadth": sum(1 for value in control_returns if value > 0) / len(control_returns),
                    "control_limit_heat": limit_heat,
                    "control_turnover_mean": sum(_to_float(row["turnover_rate_f"]) for row in control_basic_rows) / len(control_basic_rows),
                    "control_amount_mean": sum(_to_float(row["amount"]) for row in control_rows) / len(control_rows),
                    "confirmation_positive_breadth": (
                        sum(1 for value in conf_returns if value > 0) / len(conf_returns) if conf_returns else 0.0
                    ),
                    "sentiment_positive_breadth": (
                        sum(1 for value in sent_returns if value > 0) / len(sent_returns) if sent_returns else 0.0
                    ),
                    "continuation_support": continuation_map.get(trade_date, 0.0),
                    "turning_point_risk": turning_map.get(trade_date, 0.0),
                    "termination_risk": termination_map.get(trade_date, 0.0),
                }
            )
        return date_rows

    def _standardize(self, date_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        stats: dict[str, tuple[float, float]] = {}
        for key in self.FEATURE_KEYS:
            values = [float(row[key]) for row in date_rows]
            mean = sum(values) / len(values)
            var = sum((value - mean) ** 2 for value in values) / len(values)
            std = math.sqrt(var) or 1.0
            stats[key] = (mean, std)

        standardized: list[dict[str, Any]] = []
        for row in date_rows:
            enriched = dict(row)
            for key in self.FEATURE_KEYS:
                mean, std = stats[key]
                enriched[f"{key}_z"] = (float(row[key]) - mean) / std
            standardized.append(enriched)
        return standardized

    def _kmeans(self, rows: list[dict[str, Any]]) -> list[int]:
        vectors = [[float(row[f"{key}_z"]) for key in self.FEATURE_KEYS] for row in rows]
        random.seed(42)
        seeds = [0, len(vectors) // 3, (2 * len(vectors)) // 3, len(vectors) - 1]
        centroids = [vectors[idx][:] for idx in seeds]
        assignments = [0] * len(vectors)

        for _ in range(KMEANS_ITERS):
            changed = False
            for idx, vector in enumerate(vectors):
                distances = [
                    sum((value - centroid[pos]) ** 2 for pos, value in enumerate(vector))
                    for centroid in centroids
                ]
                best = min(range(REGIME_K), key=lambda cluster_id: distances[cluster_id])
                if assignments[idx] != best:
                    assignments[idx] = best
                    changed = True
            new_centroids: list[list[float]] = []
            for cluster_id in range(REGIME_K):
                members = [vectors[idx] for idx, assignment in enumerate(assignments) if assignment == cluster_id]
                if not members:
                    new_centroids.append(centroids[cluster_id][:])
                    continue
                new_centroids.append(
                    [
                        sum(member[pos] for member in members) / len(members)
                        for pos in range(len(self.FEATURE_KEYS))
                    ]
                )
            centroids = new_centroids
            if not changed:
                break
        return assignments

    def _semantic_map(self, rows: list[dict[str, Any]], assignments: list[int]) -> dict[int, str]:
        cluster_profiles: dict[int, dict[str, float]] = {}
        for cluster_id in range(REGIME_K):
            members = [rows[idx] for idx, assignment in enumerate(assignments) if assignment == cluster_id]
            if not members:
                cluster_profiles[cluster_id] = {"strength": -999.0, "heat": -999.0, "risk": -999.0}
                continue
            strength = sum(
                float(row["control_avg_return_z"])
                + float(row["control_positive_breadth_z"])
                + float(row["confirmation_positive_breadth_z"])
                + float(row["continuation_support_z"])
                for row in members
            ) / len(members)
            heat = sum(
                float(row["control_limit_heat_z"]) + float(row["sentiment_positive_breadth_z"])
                for row in members
            ) / len(members)
            risk = sum(
                float(row["turning_point_risk_z"]) + float(row["termination_risk_z"])
                for row in members
            ) / len(members)
            cluster_profiles[cluster_id] = {"strength": strength, "heat": heat, "risk": risk}

        strongest = max(cluster_profiles, key=lambda cid: cluster_profiles[cid]["strength"])
        weakest = min(cluster_profiles, key=lambda cid: cluster_profiles[cid]["strength"] - cluster_profiles[cid]["risk"])
        remaining = [cid for cid in range(REGIME_K) if cid not in {strongest, weakest}]
        hottest_remaining = max(remaining, key=lambda cid: cluster_profiles[cid]["heat"]) if remaining else strongest

        semantic_map: dict[int, str] = {}
        for cluster_id in range(REGIME_K):
            if cluster_id == strongest:
                semantic_map[cluster_id] = "impulse_expansion"
            elif cluster_id == weakest:
                semantic_map[cluster_id] = "risk_off_deterioration"
            elif cluster_id == hottest_remaining:
                semantic_map[cluster_id] = "sentiment_overdrive_transition"
            else:
                if cluster_profiles[cluster_id]["strength"] > 0:
                    semantic_map[cluster_id] = "supported_continuation"
                else:
                    semantic_map[cluster_id] = "weak_drift_chop"
        return semantic_map

    def analyze(self) -> V125NCommercialAerospaceStructuralRegimeDiscoveryReport:
        date_rows = self._date_feature_rows()
        standardized = self._standardize(date_rows)
        assignments = self._kmeans(standardized)
        semantic_map = self._semantic_map(standardized, assignments)

        enriched_date_rows: list[dict[str, Any]] = []
        for idx, row in enumerate(standardized):
            cluster_id = assignments[idx]
            enriched_date_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "cluster_id": cluster_id,
                    "regime_semantic": semantic_map[cluster_id],
                    **{key: round(float(row[key]), 8) for key in self.FEATURE_KEYS},
                }
            )

        regime_rows: list[dict[str, Any]] = []
        for cluster_id in range(REGIME_K):
            members = [row for row in standardized if semantic_map[assignments[standardized.index(row)]] == semantic_map[cluster_id]]
            # avoid index lookups on dict equality complexity by using enriched list instead
        for cluster_id, semantic in semantic_map.items():
            members = [row for idx, row in enumerate(standardized) if assignments[idx] == cluster_id]
            regime_rows.append(
                {
                    "cluster_id": cluster_id,
                    "regime_semantic": semantic,
                    "date_count": len(members),
                    "control_avg_return_mean": round(sum(float(row["control_avg_return"]) for row in members) / len(members), 8),
                    "control_positive_breadth_mean": round(sum(float(row["control_positive_breadth"]) for row in members) / len(members), 8),
                    "control_limit_heat_mean": round(sum(float(row["control_limit_heat"]) for row in members) / len(members), 8),
                    "continuation_support_mean": round(sum(float(row["continuation_support"]) for row in members) / len(members), 8),
                    "turning_point_risk_mean": round(sum(float(row["turning_point_risk"]) for row in members) / len(members), 8),
                    "termination_risk_mean": round(sum(float(row["termination_risk"]) for row in members) / len(members), 8),
                }
            )
        regime_rows.sort(key=lambda row: row["cluster_id"])

        summary = {
            "acceptance_posture": "freeze_v125n_commercial_aerospace_structural_regime_discovery_v1",
            "date_count": len(enriched_date_rows),
            "regime_count": len(regime_rows),
            "regime_semantics": [row["regime_semantic"] for row in regime_rows],
            "authoritative_rule": "commercial_aerospace_chronology_should_now_be_audited_on_structure_regimes_not_calendar_years",
            "recommended_next_posture": "audit_event_conditioned_control_surface_by_structure_regime",
        }
        interpretation = [
            "V1.25N stops pretending that yearly buckets are the same thing as structural行情.",
            "The board is now segmented by its own daily control breadth, heat, confirmation, sentiment, and decisive-event support.",
            "This is the lawful bridge from calendar chronology into machine-discovered structural regimes.",
        ]
        return V125NCommercialAerospaceStructuralRegimeDiscoveryReport(
            summary=summary,
            regime_rows=regime_rows,
            date_rows=enriched_date_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125NCommercialAerospaceStructuralRegimeDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125n_commercial_aerospace_structural_regime_discovery_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
