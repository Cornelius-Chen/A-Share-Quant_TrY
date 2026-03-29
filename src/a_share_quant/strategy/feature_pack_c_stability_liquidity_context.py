from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.data.loaders import load_stock_snapshots_from_csv


@dataclass(slots=True)
class FeaturePackCStabilityLiquidityContextReport:
    summary: dict[str, Any]
    case_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "case_rows": self.case_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackCStabilityLiquidityContextAnalyzer:
    """Read whether late-quality misses are mainly volatility or liquidity context misses."""

    def analyze(
        self,
        *,
        residual_payload: dict[str, Any],
        stock_snapshots_csv: Path,
        case_names: list[str],
    ) -> FeaturePackCStabilityLiquidityContextReport:
        stock_snapshots = load_stock_snapshots_from_csv(stock_snapshots_csv)
        snapshot_lookup = {
            (snapshot.trade_date.isoformat(), snapshot.symbol): snapshot
            for snapshot in stock_snapshots
        }

        case_rows: list[dict[str, Any]] = []
        context_counts = {
            "volatility_led": 0,
            "turnover_share_led": 0,
            "turnover_rank_led": 0,
            "mixed_stability_liquidity": 0,
        }

        for row in residual_payload.get("case_rows", []):
            case_name = str(row.get("case_name"))
            if case_name not in case_names:
                continue

            dominant_component = str(row.get("dominant_residual_component", ""))
            if dominant_component not in {"stability", "liquidity"}:
                continue

            trigger_date = str(row.get("trigger_date"))
            symbol = str(row.get("symbol"))
            snapshot = snapshot_lookup.get((trigger_date, symbol))
            if snapshot is None:
                continue

            stability_gap = round(0.25 - float(snapshot.late_quality_stability_contribution), 6)
            liquidity_gap = round(0.20 - float(snapshot.late_quality_liquidity_contribution), 6)
            volatility_pressure = round(float(snapshot.stability_volatility) / 0.06, 6)
            turnover_share_deficit = round(1.0 - float(snapshot.liquidity_turnover_share), 6)
            turnover_rank_deficit = round(1.0 - float(snapshot.liquidity_turnover_rank), 6)

            local_context = self._classify_context(
                dominant_component=dominant_component,
                volatility_pressure=volatility_pressure,
                turnover_share_deficit=turnover_share_deficit,
                turnover_rank_deficit=turnover_rank_deficit,
            )
            context_counts[local_context] = context_counts.get(local_context, 0) + 1

            case_rows.append(
                {
                    "case_name": case_name,
                    "trigger_date": trigger_date,
                    "symbol": symbol,
                    "mechanism_type": row.get("mechanism_type"),
                    "dominant_residual_component": dominant_component,
                    "local_context_class": local_context,
                    "stability_gap": stability_gap,
                    "liquidity_gap": liquidity_gap,
                    "volatility_pressure": volatility_pressure,
                    "stability_volatility": round(float(snapshot.stability_volatility), 6),
                    "turnover_share_deficit": turnover_share_deficit,
                    "turnover_rank_deficit": turnover_rank_deficit,
                    "liquidity_turnover_share": round(float(snapshot.liquidity_turnover_share), 6),
                    "liquidity_turnover_rank": round(float(snapshot.liquidity_turnover_rank), 6),
                }
            )

        case_rows.sort(key=lambda item: (str(item["case_name"]), str(item["trigger_date"])))
        summary = {
            "case_count": len(case_names),
            "row_count": len(case_rows),
            "local_context_counts": context_counts,
            "recommended_third_feature_group": self._recommended_group(context_counts),
        }
        interpretation = [
            "Stability-led rows should be split by whether the gap comes from realized volatility or from a more mixed quality stack.",
            "Liquidity-led rows should be split by turnover-share weakness versus weak cross-sectional rank.",
            "If a mixed class dominates, the next pack-c move should stay descriptive rather than immediately introducing a new scalar signal.",
        ]
        return FeaturePackCStabilityLiquidityContextReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _classify_context(
        self,
        *,
        dominant_component: str,
        volatility_pressure: float,
        turnover_share_deficit: float,
        turnover_rank_deficit: float,
    ) -> str:
        if dominant_component == "stability":
            if volatility_pressure >= 0.75:
                return "volatility_led"
            return "mixed_stability_liquidity"
        if turnover_share_deficit >= turnover_rank_deficit:
            return "turnover_share_led"
        return "turnover_rank_led"

    def _recommended_group(self, context_counts: dict[str, int]) -> str:
        if context_counts.get("volatility_led", 0) >= max(
            context_counts.get("turnover_share_led", 0),
            context_counts.get("turnover_rank_led", 0),
            context_counts.get("mixed_stability_liquidity", 0),
        ):
            return "late_quality_volatility_context"
        if context_counts.get("turnover_share_led", 0) >= max(
            context_counts.get("volatility_led", 0),
            context_counts.get("turnover_rank_led", 0),
            context_counts.get("mixed_stability_liquidity", 0),
        ):
            return "late_quality_turnover_share_context"
        if context_counts.get("turnover_rank_led", 0) >= max(
            context_counts.get("volatility_led", 0),
            context_counts.get("turnover_share_led", 0),
            context_counts.get("mixed_stability_liquidity", 0),
        ):
            return "late_quality_turnover_rank_context"
        return "late_quality_mixed_stability_liquidity_context"


def write_feature_pack_c_stability_liquidity_context_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCStabilityLiquidityContextReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
