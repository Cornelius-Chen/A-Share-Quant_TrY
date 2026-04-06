from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v125i_commercial_aerospace_event_conditioned_control_surface_refresh_v1 import (
    V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer,
)
from a_share_quant.strategy.v125n_commercial_aerospace_structural_regime_discovery_v1 import (
    V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer,
)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


@dataclass(slots=True)
class V125PCommercialAerospaceSupervisedActionTrainingTableReport:
    summary: dict[str, Any]
    training_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "training_rows": self.training_rows,
            "interpretation": self.interpretation,
        }


class V125PCommercialAerospaceSupervisedActionTrainingTableAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.daily_path = repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"

    def _future_path_extremes(self) -> dict[tuple[str, str], dict[str, float]]:
        rows = _load_csv(self.daily_path)
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row["symbol"], []).append(row)
        for values in grouped.values():
            values.sort(key=lambda r: r["trade_date"])

        output: dict[tuple[str, str], dict[str, float]] = {}
        for symbol, values in grouped.items():
            for idx, row in enumerate(values[:-10]):
                close_now = float(row["close"])
                future_window = values[idx + 1 : idx + 11]
                future_closes = [float(item["close"]) for item in future_window]
                max_favorable = max((value / close_now) - 1.0 for value in future_closes) if close_now else 0.0
                max_adverse = min((value / close_now) - 1.0 for value in future_closes) if close_now else 0.0
                output[(symbol, row["trade_date"])] = {
                    "max_favorable_return_10": max_favorable,
                    "max_adverse_return_10": max_adverse,
                }
        return output

    def _event_state(self, *, trade_date: str, event_maps: tuple[dict[str, float], dict[str, float], dict[str, float]]) -> str:
        continuation_map, turning_map, termination_map = event_maps
        continuation = float(continuation_map.get(trade_date, 0.0))
        turning = float(turning_map.get(trade_date, 0.0))
        termination = float(termination_map.get(trade_date, 0.0))
        if termination > 0:
            return "termination_active"
        if turning > continuation and turning > 0:
            return "turning_point_active"
        if continuation > 0:
            return "continuation_active"
        return "event_neutral"

    def analyze(self) -> V125PCommercialAerospaceSupervisedActionTrainingTableReport:
        control_upstream = V125ICommercialAerospaceEventConditionedControlSurfaceRefreshAnalyzer(self.repo_root)
        row_pool, _layer_counts = control_upstream._build_rows()
        regime_upstream = V125NCommercialAerospaceStructuralRegimeDiscoveryAnalyzer(self.repo_root)
        regime_result = regime_upstream.analyze()
        regime_map = {row["trade_date"]: row["regime_semantic"] for row in regime_result.date_rows}
        event_maps = regime_upstream._event_maps()
        future_extremes = self._future_path_extremes()

        base_rows: list[dict[str, Any]] = []
        for row in row_pool:
            if row["layer"] != "control_core":
                continue
            key = (row["symbol"], row["trade_date"])
            if key not in future_extremes:
                continue
            enriched = {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "role_layer": row["layer"],
                "regime_semantic": regime_map[row["trade_date"]],
                "event_state": self._event_state(trade_date=row["trade_date"], event_maps=event_maps),
                "trend_return_20": round(float(row["trend_return_20"]), 8),
                "up_day_rate": round(float(row["up_day_rate"]), 8),
                "liquidity_amount_mean": round(float(row["liquidity_amount_mean"]), 8),
                "turnover_rate_f_mean": round(float(row["turnover_rate_f_mean"]), 8),
                "volume_ratio_mean": round(float(row["volume_ratio_mean"]), 8),
                "elg_buy_sell_ratio_mean": round(float(row["elg_buy_sell_ratio_mean"]), 8),
                "limit_heat_rate": round(float(row["limit_heat_rate"]), 8),
                "local_quality_support": round(float(row["local_quality_support"]), 8),
                "local_heat_support": round(float(row["local_heat_support"]), 8),
                "board_total_support": round(float(row["board_total_support"]), 8),
                "board_non_theme_support": round(float(row["board_non_theme_support"]), 8),
                "board_heat_score": round(float(row["board_heat_score"]), 8),
                "board_event_drought": round(float(row["board_event_drought"]), 8),
                "forward_return_10": round(float(row["forward_return_10"]), 8),
                "max_favorable_return_10": round(float(future_extremes[key]["max_favorable_return_10"]), 8),
                "max_adverse_return_10": round(float(future_extremes[key]["max_adverse_return_10"]), 8),
            }
            base_rows.append(enriched)

        forward_values = [float(row["forward_return_10"]) for row in base_rows]
        adverse_values = [float(row["max_adverse_return_10"]) for row in base_rows]
        q20 = _quantile(forward_values, 0.20)
        q60 = _quantile(forward_values, 0.60)
        q80 = _quantile(forward_values, 0.80)
        adverse_q20 = _quantile(adverse_values, 0.20)
        adverse_q50 = _quantile(adverse_values, 0.50)

        label_counts: dict[str, int] = {}
        for row in base_rows:
            forward_return = float(row["forward_return_10"])
            adverse_return = float(row["max_adverse_return_10"])
            if forward_return <= q20 or adverse_return <= adverse_q20:
                action_label = "de_risk_target"
            elif forward_return >= q80 and adverse_return > adverse_q50:
                action_label = "full_eligibility_target"
            elif forward_return >= q60 and adverse_return > adverse_q20:
                action_label = "probe_eligibility_target"
            else:
                action_label = "neutral_hold"
            row["supervised_action_label"] = action_label
            label_counts[action_label] = label_counts.get(action_label, 0) + 1

        summary = {
            "acceptance_posture": "freeze_v125p_commercial_aerospace_supervised_action_training_table_v1",
            "row_count": len(base_rows),
            "symbol_count": len({row["symbol"] for row in base_rows}),
            "feature_count": 18,
            "best_control_variant_reference": "quality_event_gate",
            "forward_return_q20": round(q20, 8),
            "forward_return_q60": round(q60, 8),
            "forward_return_q80": round(q80, 8),
            "max_adverse_q20": round(adverse_q20, 8),
            "max_adverse_q50": round(adverse_q50, 8),
            "label_counts": label_counts,
            "authoritative_rule": "commercial_aerospace_supervised_learning_should_use_structure_regime_plus_decisive_event_features_and_future_only_for_labels",
        }
        interpretation = [
            "V1.25P turns commercial-aerospace board research into a supervised action table rather than a hand-wavy narrative.",
            "Features are strictly contemporaneous: structure regime, event state, board support, and symbol state.",
            "Labels are future-only and are used offline to supervise probe, full-eligibility, de-risk, and neutral-hold semantics.",
        ]
        return V125PCommercialAerospaceSupervisedActionTrainingTableReport(
            summary=summary,
            training_rows=base_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V125PCommercialAerospaceSupervisedActionTrainingTableReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def write_csv_file(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V125PCommercialAerospaceSupervisedActionTrainingTableAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125p_commercial_aerospace_supervised_action_training_table_v1",
        result=result,
    )
    csv_path = write_csv_file(
        output_path=repo_root / "data" / "training" / "commercial_aerospace_supervised_action_training_table_v1.csv",
        rows=result.training_rows,
    )
    print(output_path)
    print(csv_path)


if __name__ == "__main__":
    main()
