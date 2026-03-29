from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.data.loaders import load_stock_snapshots_from_csv


@dataclass(slots=True)
class FeaturePackCBalancedTurnoverWeaknessReport:
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


class FeaturePackCBalancedTurnoverWeaknessAnalyzer:
    """Explain whether balanced turnover weakness is structural or sector-masked."""

    def analyze(
        self,
        *,
        turnover_context_payload: dict[str, Any],
        stock_snapshots_csv: Path,
        case_names: list[str],
    ) -> FeaturePackCBalancedTurnoverWeaknessReport:
        stock_snapshots = load_stock_snapshots_from_csv(stock_snapshots_csv)
        snapshot_lookup = {
            (snapshot.trade_date.isoformat(), snapshot.symbol): snapshot
            for snapshot in stock_snapshots
        }

        case_rows: list[dict[str, Any]] = []
        weakness_counts = {
            "singleton_sector_masking": 0,
            "true_balanced_share_weakness": 0,
        }

        for row in turnover_context_payload.get("case_rows", []):
            case_name = str(row.get("case_name"))
            if case_name not in case_names or str(row.get("local_turnover_context")) != "balanced_share_weakness":
                continue

            trigger_date = str(row.get("trigger_date"))
            symbol = str(row.get("symbol"))
            snapshot = snapshot_lookup.get((trigger_date, symbol))
            if snapshot is None:
                continue

            weakness_class = self._classify(snapshot.liquidity_sector_symbol_count)
            weakness_counts[weakness_class] = weakness_counts.get(weakness_class, 0) + 1
            case_rows.append(
                {
                    "case_name": case_name,
                    "trigger_date": trigger_date,
                    "symbol": symbol,
                    "mechanism_type": row.get("mechanism_type"),
                    "sector_symbol_count": snapshot.liquidity_sector_symbol_count,
                    "market_turnover_share": round(snapshot.liquidity_turnover_share, 6),
                    "sector_turnover_share": round(snapshot.liquidity_sector_turnover_share, 6),
                    "turnover_rank": round(snapshot.liquidity_turnover_rank, 6),
                    "balanced_weakness_class": weakness_class,
                }
            )

        case_rows.sort(key=lambda item: (str(item["case_name"]), str(item["trigger_date"])))
        summary = {
            "case_count": len(case_names),
            "row_count": len(case_rows),
            "balanced_weakness_counts": weakness_counts,
            "recommended_fifth_feature_group": self._recommended_group(weakness_counts),
        }
        interpretation = [
            "Balanced turnover weakness should first be tested against sector breadth before it is treated as a real attention feature.",
            "A singleton sector means sector-relative share metrics are structurally uninformative and should not drive a new repair branch.",
            "Only multi-symbol balanced weakness should be considered a candidate for a genuine turnover-balance feature.",
        ]
        return FeaturePackCBalancedTurnoverWeaknessReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _classify(self, sector_symbol_count: int) -> str:
        if sector_symbol_count <= 1:
            return "singleton_sector_masking"
        return "true_balanced_share_weakness"

    def _recommended_group(self, weakness_counts: dict[str, int]) -> str:
        if weakness_counts.get("singleton_sector_masking", 0) > 0 and weakness_counts.get(
            "true_balanced_share_weakness", 0
        ) == 0:
            return "stop_turnover_lane_as_sector_masked"
        return "late_quality_true_balanced_turnover_context"


def write_feature_pack_c_balanced_turnover_weakness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCBalancedTurnoverWeaknessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
