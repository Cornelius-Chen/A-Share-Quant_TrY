from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.data.loaders import load_stock_snapshots_from_csv


@dataclass(slots=True)
class FeaturePackCTurnoverShareContextReport:
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


class FeaturePackCTurnoverShareContextAnalyzer:
    """Explain whether turnover-share-led rows are market-share or sector-share misses."""

    def analyze(
        self,
        *,
        context_payload: dict[str, Any],
        stock_snapshots_csv: Path,
        case_names: list[str],
    ) -> FeaturePackCTurnoverShareContextReport:
        stock_snapshots = load_stock_snapshots_from_csv(stock_snapshots_csv)
        snapshot_lookup = {
            (snapshot.trade_date.isoformat(), snapshot.symbol): snapshot
            for snapshot in stock_snapshots
        }

        case_rows: list[dict[str, Any]] = []
        context_counts = {
            "sector_peer_dominance": 0,
            "broad_attention_deficit": 0,
            "balanced_share_weakness": 0,
        }

        for row in context_payload.get("case_rows", []):
            case_name = str(row.get("case_name"))
            if case_name not in case_names or str(row.get("local_context_class")) != "turnover_share_led":
                continue

            trigger_date = str(row.get("trigger_date"))
            symbol = str(row.get("symbol"))
            snapshot = snapshot_lookup.get((trigger_date, symbol))
            if snapshot is None:
                continue

            market_share = float(snapshot.liquidity_turnover_share)
            sector_share = float(snapshot.liquidity_sector_turnover_share)
            top_sector_share = float(snapshot.liquidity_sector_top_turnover_share)
            mean_sector_share = float(snapshot.liquidity_sector_mean_turnover_share)
            sector_gap = float(snapshot.liquidity_sector_turnover_share_gap)
            rank = float(snapshot.liquidity_turnover_rank)

            local_context = self._classify_context(
                market_share=market_share,
                sector_share=sector_share,
                top_sector_share=top_sector_share,
                mean_sector_share=mean_sector_share,
                sector_gap=sector_gap,
                rank=rank,
            )
            context_counts[local_context] = context_counts.get(local_context, 0) + 1

            case_rows.append(
                {
                    "case_name": case_name,
                    "trigger_date": trigger_date,
                    "symbol": symbol,
                    "mechanism_type": row.get("mechanism_type"),
                    "market_turnover_share": round(market_share, 6),
                    "sector_turnover_share": round(sector_share, 6),
                    "sector_top_turnover_share": round(top_sector_share, 6),
                    "sector_mean_turnover_share": round(mean_sector_share, 6),
                    "sector_turnover_share_gap": round(sector_gap, 6),
                    "turnover_rank": round(rank, 6),
                    "local_turnover_context": local_context,
                }
            )

        case_rows.sort(key=lambda item: (str(item["case_name"]), str(item["trigger_date"])))
        summary = {
            "case_count": len(case_names),
            "row_count": len(case_rows),
            "local_turnover_context_counts": context_counts,
            "recommended_fourth_feature_group": self._recommended_group(context_counts),
        }
        interpretation = [
            "Turnover-share-led rows should be split by whether they are suppressed by a dominant sector peer or by low broad attention.",
            "Sector-peer dominance suggests a relative attention feature inside the sector; broad-attention deficit suggests a market-level participation feature.",
            "If both appear together, the next feature pack step should stay descriptive and avoid another threshold lane.",
        ]
        return FeaturePackCTurnoverShareContextReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _classify_context(
        self,
        *,
        market_share: float,
        sector_share: float,
        top_sector_share: float,
        mean_sector_share: float,
        sector_gap: float,
        rank: float,
    ) -> str:
        if sector_gap >= 0.20 or sector_share < mean_sector_share * 0.75:
            return "sector_peer_dominance"
        if market_share < 0.03 and rank < 0.45:
            return "broad_attention_deficit"
        return "balanced_share_weakness"

    def _recommended_group(self, context_counts: dict[str, int]) -> str:
        if context_counts.get("sector_peer_dominance", 0) >= max(
            context_counts.get("broad_attention_deficit", 0),
            context_counts.get("balanced_share_weakness", 0),
        ):
            return "late_quality_sector_peer_attention_context"
        if context_counts.get("broad_attention_deficit", 0) >= max(
            context_counts.get("sector_peer_dominance", 0),
            context_counts.get("balanced_share_weakness", 0),
        ):
            return "late_quality_broad_attention_context"
        return "late_quality_balanced_turnover_context"


def write_feature_pack_c_turnover_share_context_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCTurnoverShareContextReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
