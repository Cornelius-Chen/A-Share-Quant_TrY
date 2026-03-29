from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.data.loaders import load_stock_snapshots_from_csv


@dataclass(slots=True)
class FeaturePackCLateQualityResidualsReport:
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


class FeaturePackCLateQualityResidualsAnalyzer:
    """Inspect late-quality residual structure on fallback-dominated rows."""

    MAX_CONTRIBUTIONS = {
        "sector_strength": 0.30,
        "stability": 0.25,
        "liquidity": 0.20,
        "lag_balance": 0.15,
        "trend_support": 0.10,
    }

    def analyze(
        self,
        *,
        recheck_payload: dict[str, Any],
        stock_snapshots_csv: Path,
        case_names: list[str],
    ) -> FeaturePackCLateQualityResidualsReport:
        stock_snapshots = load_stock_snapshots_from_csv(stock_snapshots_csv)
        snapshot_lookup = {
            (snapshot.trade_date.isoformat(), snapshot.symbol): snapshot
            for snapshot in stock_snapshots
        }

        case_rows: list[dict[str, Any]] = []
        dominant_counts: dict[str, int] = {}
        concept_boost_active_count = 0
        raw_below_threshold_count = 0

        for row in recheck_payload.get("case_rows", []):
            case_name = str(row.get("case_name"))
            if case_name not in case_names:
                continue
            trigger_date = str(row.get("trigger_date"))
            symbol = str(row.get("symbol"))
            snapshot = snapshot_lookup.get((trigger_date, symbol))
            if snapshot is None:
                continue

            late_threshold = round(
                float(snapshot.late_mover_quality) - float(row.get("challenger_late_quality_margin", 0.0)),
                6,
            )
            required_uplift = round(max(0.0, late_threshold - float(snapshot.late_mover_quality)), 6)
            raw_gap_to_threshold = round(max(0.0, late_threshold - float(snapshot.late_quality_raw_score)), 6)
            if raw_gap_to_threshold > 0:
                raw_below_threshold_count += 1
            if float(snapshot.late_quality_concept_boost) > 0:
                concept_boost_active_count += 1

            component_deficits = {
                "sector_strength": round(
                    self.MAX_CONTRIBUTIONS["sector_strength"] - float(snapshot.late_quality_sector_contribution),
                    6,
                ),
                "stability": round(
                    self.MAX_CONTRIBUTIONS["stability"] - float(snapshot.late_quality_stability_contribution),
                    6,
                ),
                "liquidity": round(
                    self.MAX_CONTRIBUTIONS["liquidity"] - float(snapshot.late_quality_liquidity_contribution),
                    6,
                ),
                "lag_balance": round(
                    self.MAX_CONTRIBUTIONS["lag_balance"] - float(snapshot.late_quality_lag_contribution),
                    6,
                ),
                "trend_support": round(
                    self.MAX_CONTRIBUTIONS["trend_support"] - float(snapshot.late_quality_trend_contribution),
                    6,
                ),
            }
            dominant_component = max(component_deficits, key=lambda key: component_deficits[key])
            dominant_counts[dominant_component] = dominant_counts.get(dominant_component, 0) + 1

            case_rows.append(
                {
                    "case_name": case_name,
                    "trigger_date": trigger_date,
                    "symbol": symbol,
                    "mechanism_type": row.get("mechanism_type"),
                    "challenger_assignment_reason": row.get("challenger_assignment_reason"),
                    "late_quality": round(float(snapshot.late_mover_quality), 6),
                    "late_quality_raw_score": round(float(snapshot.late_quality_raw_score), 6),
                    "late_quality_concept_boost": round(float(snapshot.late_quality_concept_boost), 6),
                    "late_threshold": late_threshold,
                    "required_uplift": required_uplift,
                    "raw_gap_to_threshold": raw_gap_to_threshold,
                    "concept_support": round(float(snapshot.concept_support), 6),
                    "late_quality_sector_strength": round(float(snapshot.late_quality_sector_strength), 6),
                    "late_quality_lag_balance": round(float(snapshot.late_quality_lag_balance), 6),
                    "late_quality_trend_support": round(float(snapshot.late_quality_trend_support), 6),
                    "component_deficits": component_deficits,
                    "dominant_residual_component": dominant_component,
                }
            )

        case_rows.sort(key=lambda item: (str(item["case_name"]), str(item["trigger_date"])))
        summary = {
            "case_count": len(case_names),
            "row_count": len(case_rows),
            "dominant_residual_component_counts": dominant_counts,
            "concept_boost_active_count": concept_boost_active_count,
            "raw_below_threshold_count": raw_below_threshold_count,
            "recommended_second_feature_group": self._recommended_second_group(dominant_counts),
        }
        interpretation = [
            "Late-quality residuals should be read as weighted contribution deficits, not as another scalar threshold search.",
            "If one component dominates repeatedly, the next pack-c feature should expose its local causal context rather than widen concept support or approval thresholds.",
            "Concept boost matters only when the raw late-quality score stays near the threshold edge; otherwise the blocker is inside the raw late-quality stack.",
        ]
        return FeaturePackCLateQualityResidualsReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _recommended_second_group(self, dominant_counts: dict[str, int]) -> str:
        sector_count = dominant_counts.get("sector_strength", 0)
        stability_count = dominant_counts.get("stability", 0)
        liquidity_count = dominant_counts.get("liquidity", 0)
        lag_count = dominant_counts.get("lag_balance", 0)
        trend_count = dominant_counts.get("trend_support", 0)
        if stability_count > 0 and liquidity_count > 0 and max(stability_count, liquidity_count) >= max(
            sector_count,
            lag_count,
            trend_count,
        ):
            return "late_quality_stability_liquidity_context"
        if stability_count >= max(sector_count, liquidity_count, lag_count, trend_count):
            return "late_quality_stability_context"
        if liquidity_count >= max(sector_count, stability_count, lag_count, trend_count):
            return "late_quality_liquidity_context"
        if lag_count >= max(sector_count, trend_count):
            return "late_quality_lag_balance_context"
        if sector_count >= max(lag_count, trend_count):
            return "late_quality_sector_strength_context"
        return "late_quality_trend_support_context"


def write_feature_pack_c_late_quality_residuals_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCLateQualityResidualsReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
