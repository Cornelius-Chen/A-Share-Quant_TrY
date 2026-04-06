from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEATURE_KEYS = [
    "trend_return_20",
    "turnover_rate_f_mean",
    "volume_ratio_mean",
    "elg_buy_sell_ratio_mean",
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
class V124TCommercialAerospaceLocalFeedUniverseTriageReport:
    summary: dict[str, Any]
    control_eligible_rows: list[dict[str, Any]]
    confirmation_rows: list[dict[str, Any]]
    mirror_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "control_eligible_rows": self.control_eligible_rows,
            "confirmation_rows": self.confirmation_rows,
            "mirror_rows": self.mirror_rows,
            "interpretation": self.interpretation,
        }


class V124TCommercialAerospaceLocalFeedUniverseTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.universe_path = repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        self.daily_basic_path = repo_root / "data" / "reference" / "tushare_daily_basic" / "tushare_commercial_aerospace_daily_basic_v1.csv"
        self.moneyflow_path = repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
        self.stk_limit_path = repo_root / "data" / "reference" / "stk_limit" / "tushare_commercial_aerospace_stk_limit_v1.csv"

    def _build_feature_rows(self) -> list[dict[str, Any]]:
        universe_rows = _load_csv(self.universe_path)
        daily_rows = _load_csv(self.daily_path)
        daily_basic_rows = _load_csv(self.daily_basic_path)
        moneyflow_rows = _load_csv(self.moneyflow_path)
        stk_limit_rows = _load_csv(self.stk_limit_path)

        daily_by_symbol: dict[str, list[dict[str, str]]] = {}
        for row in daily_rows:
            daily_by_symbol.setdefault(row["symbol"], []).append(row)
        for rows in daily_by_symbol.values():
            rows.sort(key=lambda r: r["trade_date"])

        daily_basic_by_symbol: dict[str, list[dict[str, str]]] = {}
        for row in daily_basic_rows:
            daily_basic_by_symbol.setdefault(row["symbol"], []).append(row)
        moneyflow_by_symbol: dict[str, list[dict[str, str]]] = {}
        for row in moneyflow_rows:
            moneyflow_by_symbol.setdefault(row["symbol"], []).append(row)
        stk_limit_by_symbol: dict[str, list[dict[str, str]]] = {}
        for row in stk_limit_rows:
            stk_limit_by_symbol.setdefault(row["symbol"], []).append(row)

        feature_rows: list[dict[str, Any]] = []
        for row in universe_rows:
            symbol = row["symbol"]
            daily = daily_by_symbol.get(symbol, [])
            daily_basic = daily_basic_by_symbol.get(symbol, [])
            moneyflow = moneyflow_by_symbol.get(symbol, [])
            stk_limit = stk_limit_by_symbol.get(symbol, [])
            if not daily or not daily_basic or not moneyflow or not stk_limit:
                continue
            last_daily = daily[-60:]
            last_basic = daily_basic[-60:]
            last_moneyflow = moneyflow[-60:]
            last_limit = stk_limit[-60:]
            close_now = _to_float(last_daily[-1]["close"])
            close_prev20 = _to_float(last_daily[-20]["close"]) if len(last_daily) >= 20 else _to_float(last_daily[0]["close"])
            trend_return_20 = 0.0 if close_prev20 == 0 else close_now / close_prev20 - 1.0
            up_day_rate = sum(1 for item in last_daily if _to_float(item["close"]) > _to_float(item["pre_close"])) / len(last_daily)
            liquidity_amount_mean = sum(_to_float(item["amount"]) for item in last_daily) / len(last_daily)
            turnover_rate_f_mean = sum(_to_float(item["turnover_rate_f"]) for item in last_basic) / len(last_basic)
            volume_ratio_mean = sum(_to_float(item["volume_ratio"]) for item in last_basic) / len(last_basic)
            elg_buy_sell_ratio_mean = sum(
                (_to_float(item.get("buy_elg_amount", "")) + 1.0) / (_to_float(item.get("sell_elg_amount", "")) + 1.0)
                for item in last_moneyflow
            ) / len(last_moneyflow)
            limit_heat_rate = sum(
                1
                for item_daily, item_limit in zip(last_daily[-len(last_limit):], last_limit)
                if _to_float(item_limit["up_limit"]) > 0 and _to_float(item_daily["close"]) / _to_float(item_limit["up_limit"]) >= 0.97
            ) / len(last_limit)
            feature_rows.append(
                {
                    "symbol": symbol,
                    "name": row["name"],
                    "group": row["group"],
                    "subgroup": row["subgroup"],
                    "confidence": row["confidence"],
                    "source_layer": row["source_layer"],
                    "reason": row["reason"],
                    "trend_return_20": trend_return_20,
                    "turnover_rate_f_mean": turnover_rate_f_mean,
                    "volume_ratio_mean": volume_ratio_mean,
                    "elg_buy_sell_ratio_mean": elg_buy_sell_ratio_mean,
                    "limit_heat_rate": limit_heat_rate,
                    "up_day_rate": up_day_rate,
                    "liquidity_amount_mean": liquidity_amount_mean,
                }
            )
        return feature_rows

    def _zscore_matrix(self, rows: list[dict[str, Any]]) -> list[list[float]]:
        means = {k: sum(row[k] for row in rows) / len(rows) for k in FEATURE_KEYS}
        stds = {}
        for key in FEATURE_KEYS:
            var = sum((row[key] - means[key]) ** 2 for row in rows) / max(len(rows), 1)
            stds[key] = math.sqrt(var) or 1.0
        return [[(row[key] - means[key]) / stds[key] for key in FEATURE_KEYS] for row in rows]

    def _kmeans4(self, rows: list[dict[str, Any]]) -> tuple[list[int], dict[int, str]]:
        matrix = self._zscore_matrix(rows)
        seeds = [
            max(range(len(rows)), key=lambda i: rows[i]["liquidity_amount_mean"]),
            max(range(len(rows)), key=lambda i: rows[i]["trend_return_20"]),
            max(range(len(rows)), key=lambda i: rows[i]["limit_heat_rate"]),
            min(range(len(rows)), key=lambda i: rows[i]["trend_return_20"]),
        ]
        centroids = [matrix[i][:] for i in seeds]
        assignments = [0] * len(rows)
        for _ in range(10):
            changed = False
            for i, vec in enumerate(matrix):
                dists = [sum((vec[j] - centroid[j]) ** 2 for j in range(len(FEATURE_KEYS))) for centroid in centroids]
                best = min(range(len(dists)), key=lambda cid: dists[cid])
                if assignments[i] != best:
                    assignments[i] = best
                    changed = True
            for cid in range(4):
                members = [matrix[i] for i, aid in enumerate(assignments) if aid == cid]
                if members:
                    centroids[cid] = [sum(member[j] for member in members) / len(members) for j in range(len(FEATURE_KEYS))]
            if not changed:
                break

        cluster_rows: dict[int, list[dict[str, Any]]] = {0: [], 1: [], 2: [], 3: []}
        for row, aid in zip(rows, assignments):
            cluster_rows[aid].append(row)

        ranked = sorted(
            cluster_rows,
            key=lambda cid: (
                sum(r["liquidity_amount_mean"] for r in cluster_rows[cid]) / len(cluster_rows[cid]) if cluster_rows[cid] else -999,
                sum(r["trend_return_20"] for r in cluster_rows[cid]) / len(cluster_rows[cid]) if cluster_rows[cid] else -999,
            ),
            reverse=True,
        )
        semantics = {
            ranked[0]: "control_eligible_primary",
            ranked[1]: "control_eligible_support",
            ranked[2]: "confirmation_only_adjacent",
            ranked[3]: "mirror_or_pending",
        }
        return assignments, semantics

    def analyze(self) -> V124TCommercialAerospaceLocalFeedUniverseTriageReport:
        rows = self._build_feature_rows()
        assignments, semantics = self._kmeans4(rows)

        control_eligible_rows: list[dict[str, Any]] = []
        confirmation_rows: list[dict[str, Any]] = []
        mirror_rows: list[dict[str, Any]] = []
        for row, cluster_id in zip(rows, assignments):
            semantic = semantics[cluster_id]
            enriched = {
                **row,
                "machine_cluster_id": cluster_id,
                "machine_semantic": semantic,
            }
            if semantic.startswith("control_eligible"):
                control_eligible_rows.append(enriched)
            elif semantic == "confirmation_only_adjacent":
                confirmation_rows.append(enriched)
            else:
                mirror_rows.append(enriched)

        control_eligible_rows.sort(key=lambda r: (r["machine_semantic"], -r["liquidity_amount_mean"], r["symbol"]))
        confirmation_rows.sort(key=lambda r: (-r["liquidity_amount_mean"], r["symbol"]))
        mirror_rows.sort(key=lambda r: (-r["limit_heat_rate"], r["symbol"]))

        summary = {
            "acceptance_posture": "freeze_v124t_commercial_aerospace_local_feed_universe_triage_v1",
            "fully_supported_count": len(rows),
            "control_eligible_count": len(control_eligible_rows),
            "confirmation_count": len(confirmation_rows),
            "mirror_count": len(mirror_rows),
            "authoritative_rule": "machine_triage_is_now_based_on_local_daily_bars_daily_basic_moneyflow_and_stk_limit_not_web_membership_only",
            "recommended_next_posture": "use_control_eligible_core_for_control_extraction_and_keep_confirmation_or_mirror_names_outside_action_authority",
        }
        interpretation = [
            "V1.24T refreshes commercial aerospace machine triage on a wider locally supported set rather than the earlier 3-symbol snapshot bottleneck.",
            "The goal is not to declare final leaders forever, but to stop relying on web-only concept breadth for lawful control authority.",
            "This should be the last step before control extraction, assuming subagent review does not block it.",
        ]
        return V124TCommercialAerospaceLocalFeedUniverseTriageReport(
            summary=summary,
            control_eligible_rows=control_eligible_rows,
            confirmation_rows=confirmation_rows,
            mirror_rows=mirror_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124TCommercialAerospaceLocalFeedUniverseTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V124TCommercialAerospaceLocalFeedUniverseTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124t_commercial_aerospace_local_feed_universe_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
