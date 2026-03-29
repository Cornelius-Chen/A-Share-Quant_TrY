from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config, merge_config
from a_share_quant.data.loaders import (
    load_sector_snapshots_from_csv,
    load_stock_snapshots_from_csv,
)
from a_share_quant.regime.mainline_sector_scorer import MainlineSectorScorer


@dataclass(slots=True)
class FeaturePackARecheckReport:
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


class FeaturePackARecheckAnalyzer:
    """Recheck feature-gap suspects using richer snapshot fields and candidate thresholds."""

    def analyze(self, *, case_specs: list[dict[str, Any]]) -> FeaturePackARecheckReport:
        case_rows: list[dict[str, Any]] = []

        for case_spec in case_specs:
            case_rows.extend(self._analyze_case(case_spec))

        feature_edge_count = sum(
            1
            for row in case_rows
            if row["late_quality_straddle"]
            or row["non_junk_straddle"]
            or row["top_score_straddle"]
        )
        summary = {
            "case_count": len(case_specs),
            "row_count": len(case_rows),
            "feature_edge_row_count": feature_edge_count,
            "cases_with_feature_edge": sorted(
                {
                    row["case_name"]
                    for row in case_rows
                    if row["late_quality_straddle"]
                    or row["non_junk_straddle"]
                    or row["top_score_straddle"]
                }
            ),
        }
        interpretation = [
            "A candidate row is most interesting when incumbent and challenger sit on opposite sides of a threshold edge.",
            "Late-quality and non-junk-composite straddles point to hierarchy feature gaps.",
            "Top-score straddles point to approval-edge feature gaps rather than hierarchy gaps.",
        ]
        return FeaturePackARecheckReport(
            summary=summary,
            case_rows=case_rows,
            interpretation=interpretation,
        )

    def _analyze_case(self, case_spec: dict[str, Any]) -> list[dict[str, Any]]:
        timeline_payload = load_json_report(Path(str(case_spec["timeline_report_path"])))
        cycle_payload = load_json_report(Path(str(case_spec["cycle_report_path"])))
        timeline_config = load_yaml_config(Path(str(case_spec["timeline_config_path"])))
        dataset_config = load_yaml_config(Path(str(timeline_config["dataset"]["config_path"])))

        incumbent_name = str(timeline_config["comparison"]["incumbent_candidate"])
        challenger_name = str(timeline_config["comparison"]["challenger_candidate"])
        candidate_configs = self._candidate_config_map(
            dataset_config=dataset_config,
            timeline_config=timeline_config,
        )
        incumbent_config = candidate_configs[incumbent_name]
        challenger_config = candidate_configs[challenger_name]

        stock_snapshots = load_stock_snapshots_from_csv(Path(str(case_spec["stock_snapshots_csv"])))
        sector_snapshots = load_sector_snapshots_from_csv(Path(str(case_spec["sector_snapshots_csv"])))
        stock_lookup = {
            (snapshot.trade_date.isoformat(), snapshot.symbol): snapshot for snapshot in stock_snapshots
        }
        sector_score_lookup = self._sector_score_lookup(sector_snapshots)

        candidate_records = {
            (str(record["strategy_name"]), str(record["candidate_name"])): record
            for record in timeline_payload.get("candidate_records", [])
        }
        strategy_name = str(cycle_payload["summary"]["strategy_name"])
        symbol = str(timeline_payload["summary"]["symbol"])
        incumbent_record = candidate_records[(strategy_name, incumbent_name)]
        challenger_record = candidate_records[(strategy_name, challenger_name)]
        incumbent_daily = {str(item["trade_date"]): item for item in incumbent_record.get("daily_records", [])}
        challenger_daily = {str(item["trade_date"]): item for item in challenger_record.get("daily_records", [])}

        rows: list[dict[str, Any]] = []
        for mechanism_row in cycle_payload.get("mechanism_rows", []):
            trigger_date = str(
                mechanism_row.get("trigger_date")
                or mechanism_row["incumbent_cycle"]["entry_date"]
            )
            stock_snapshot = stock_lookup.get((trigger_date, symbol))
            incumbent_daily_record = incumbent_daily.get(trigger_date, {})
            challenger_daily_record = challenger_daily.get(trigger_date, {})
            approved_sector_id = str(
                incumbent_daily_record.get("approved_sector_id")
                or challenger_daily_record.get("approved_sector_id")
                or ""
            )
            sector_context = sector_score_lookup.get(trigger_date, {})
            approved_score = float(sector_context.get("sector_scores", {}).get(approved_sector_id, 0.0))
            top_score = float(sector_context.get("top_score", 0.0))
            second_score = float(sector_context.get("second_score", 0.0))
            top_score_gap = round(top_score - second_score, 6)

            late_quality = float(getattr(stock_snapshot, "late_mover_quality", 0.0) if stock_snapshot else 0.0)
            resonance = float(getattr(stock_snapshot, "resonance", 0.0) if stock_snapshot else 0.0)
            non_junk_composite = float(
                getattr(stock_snapshot, "non_junk_composite_score", 0.0) if stock_snapshot else 0.0
            )

            incumbent_late_threshold = float(
                incumbent_config["trend"]["hierarchy"]["min_quality_for_late_mover"]
            )
            challenger_late_threshold = float(
                challenger_config["trend"]["hierarchy"]["min_quality_for_late_mover"]
            )
            incumbent_non_junk_threshold = float(
                incumbent_config["trend"]["hierarchy"]["min_composite_for_non_junk"]
            )
            challenger_non_junk_threshold = float(
                challenger_config["trend"]["hierarchy"]["min_composite_for_non_junk"]
            )
            incumbent_top_score_threshold = float(incumbent_config["regime"]["min_top_score"])
            challenger_top_score_threshold = float(challenger_config["regime"]["min_top_score"])
            incumbent_margin_threshold = float(incumbent_config["regime"].get("min_score_margin", 0.0))
            challenger_margin_threshold = float(challenger_config["regime"].get("min_score_margin", 0.0))
            incumbent_switch_buffer = float(incumbent_config["regime"].get("switch_margin_buffer", 0.0))
            challenger_switch_buffer = float(challenger_config["regime"].get("switch_margin_buffer", 0.0))

            incumbent_late_margin = round(late_quality - incumbent_late_threshold, 6)
            challenger_late_margin = round(late_quality - challenger_late_threshold, 6)
            incumbent_non_junk_margin = round(non_junk_composite - incumbent_non_junk_threshold, 6)
            challenger_non_junk_margin = round(non_junk_composite - challenger_non_junk_threshold, 6)
            incumbent_top_score_gap = round(approved_score - incumbent_top_score_threshold, 6)
            challenger_top_score_gap = round(approved_score - challenger_top_score_threshold, 6)
            incumbent_margin_gap = round(top_score_gap - incumbent_margin_threshold, 6)
            challenger_margin_gap = round(top_score_gap - challenger_margin_threshold, 6)
            incumbent_resonance_margin = round(
                resonance - float(incumbent_config["trend"]["hierarchy"]["min_resonance_for_core"]),
                6,
            )
            challenger_resonance_margin = round(
                resonance - float(challenger_config["trend"]["hierarchy"]["min_resonance_for_core"]),
                6,
            )
            fallback_reason_score = self._fallback_reason_score(
                assignment_reason=str(challenger_daily_record.get("assignment_reason") or ""),
                late_margin=challenger_late_margin,
                non_junk_margin=challenger_non_junk_margin,
                resonance_margin=challenger_resonance_margin,
            )
            incumbent_switch_buffer_gap, challenger_switch_buffer_gap = self._switch_buffer_gaps(
                incumbent_daily_record=incumbent_daily_record,
                challenger_daily_record=challenger_daily_record,
                sector_context=sector_context,
                incumbent_switch_buffer=incumbent_switch_buffer,
                challenger_switch_buffer=challenger_switch_buffer,
            )

            rows.append(
                {
                    "case_name": str(case_spec["case_name"]),
                    "dataset_name": str(case_spec["dataset_name"]),
                    "strategy_name": strategy_name,
                    "symbol": symbol,
                    "mechanism_type": str(mechanism_row["mechanism_type"]),
                    "trigger_date": trigger_date,
                    "trigger_reason": mechanism_row.get("trigger_reason"),
                    "approved_sector_id": approved_sector_id or None,
                    "top_sector_id": sector_context.get("top_sector_id"),
                    "top_score": round(top_score, 6),
                    "second_score": round(second_score, 6),
                    "top_score_gap": top_score_gap,
                    "incumbent_top_score_gap": incumbent_top_score_gap,
                    "challenger_top_score_gap": challenger_top_score_gap,
                    "incumbent_margin_gap": incumbent_margin_gap,
                    "challenger_margin_gap": challenger_margin_gap,
                    "incumbent_switch_buffer_gap": incumbent_switch_buffer_gap,
                    "challenger_switch_buffer_gap": challenger_switch_buffer_gap,
                    "incumbent_assignment_layer": incumbent_daily_record.get("assignment_layer"),
                    "challenger_assignment_layer": challenger_daily_record.get("assignment_layer"),
                    "incumbent_assignment_reason": incumbent_daily_record.get("assignment_reason"),
                    "challenger_assignment_reason": challenger_daily_record.get("assignment_reason"),
                    "fallback_reason_score": fallback_reason_score,
                    "incumbent_permission_allowed": incumbent_daily_record.get("permission_allowed"),
                    "challenger_permission_allowed": challenger_daily_record.get("permission_allowed"),
                    "incumbent_hysteresis_hold": bool(
                        incumbent_daily_record.get("approved_sector_id")
                        and sector_context.get("top_sector_id")
                        and incumbent_daily_record.get("approved_sector_id") != sector_context.get("top_sector_id")
                    ),
                    "challenger_hysteresis_hold": bool(
                        challenger_daily_record.get("approved_sector_id")
                        and sector_context.get("top_sector_id")
                        and challenger_daily_record.get("approved_sector_id") != sector_context.get("top_sector_id")
                    ),
                    "late_mover_quality": round(late_quality, 6),
                    "resonance": round(resonance, 6),
                    "non_junk_composite_score": round(non_junk_composite, 6),
                    "concept_support": round(
                        float(getattr(stock_snapshot, "concept_support", 0.0) if stock_snapshot else 0.0),
                        6,
                    ),
                    "primary_concept_weight": round(
                        float(
                            getattr(stock_snapshot, "primary_concept_weight", 0.0)
                            if stock_snapshot
                            else 0.0
                        ),
                        6,
                    ),
                    "concept_count": int(getattr(stock_snapshot, "concept_count", 0) if stock_snapshot else 0),
                    "concept_concentration_ratio": round(
                        float(
                            getattr(stock_snapshot, "concept_concentration_ratio", 0.0)
                            if stock_snapshot
                            else 0.0
                        ),
                        6,
                    ),
                    "leader_component_score": round(
                        float(
                            getattr(stock_snapshot, "leader_component_score", 0.0)
                            if stock_snapshot
                            else 0.0
                        ),
                        6,
                    ),
                    "core_component_score": round(
                        float(
                            getattr(stock_snapshot, "core_component_score", 0.0)
                            if stock_snapshot
                            else 0.0
                        ),
                        6,
                    ),
                    "late_component_score": round(
                        float(
                            getattr(stock_snapshot, "late_component_score", 0.0)
                            if stock_snapshot
                            else 0.0
                        ),
                        6,
                    ),
                    "incumbent_late_quality_margin": incumbent_late_margin,
                    "challenger_late_quality_margin": challenger_late_margin,
                    "incumbent_non_junk_margin": incumbent_non_junk_margin,
                    "challenger_non_junk_margin": challenger_non_junk_margin,
                    "incumbent_resonance_margin": incumbent_resonance_margin,
                    "challenger_resonance_margin": challenger_resonance_margin,
                    "late_quality_straddle": incumbent_late_margin >= 0 > challenger_late_margin,
                    "non_junk_straddle": incumbent_non_junk_margin >= 0 > challenger_non_junk_margin,
                    "top_score_straddle": incumbent_top_score_gap >= 0 > challenger_top_score_gap,
                    "margin_straddle": incumbent_margin_gap >= 0 > challenger_margin_gap,
                }
            )

        return rows

    def _candidate_config_map(
        self,
        *,
        dataset_config: dict[str, Any],
        timeline_config: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        candidate_map: dict[str, dict[str, Any]] = {}
        for candidate in timeline_config.get("candidates", []):
            merged = merge_config(dataset_config, candidate.get("override", {}))
            candidate_map[str(candidate["candidate_name"])] = merged
        return candidate_map

    def _sector_score_lookup(self, sector_snapshots: list[Any]) -> dict[str, dict[str, Any]]:
        scores = MainlineSectorScorer().score(sector_snapshots)
        by_date: dict[str, list[Any]] = {}
        for score in scores:
            by_date.setdefault(score.trade_date.isoformat(), []).append(score)
        lookup: dict[str, dict[str, Any]] = {}
        for trade_date, date_scores in by_date.items():
            ordered = sorted(date_scores, key=lambda item: item.rank)
            top = ordered[0] if ordered else None
            second = ordered[1] if len(ordered) > 1 else None
            lookup[trade_date] = {
                "top_sector_id": top.sector_id if top else None,
                "top_score": top.composite_score if top else 0.0,
                "second_score": second.composite_score if second else 0.0,
                "sector_scores": {score.sector_id: score.composite_score for score in ordered},
            }
        return lookup

    def _fallback_reason_score(
        self,
        *,
        assignment_reason: str,
        late_margin: float,
        non_junk_margin: float,
        resonance_margin: float,
    ) -> float:
        if assignment_reason == "low_composite_or_low_resonance":
            return round(max(0.0, -min(non_junk_margin, resonance_margin)), 6)
        if assignment_reason == "fallback_to_junk":
            return round(max(0.0, -min(late_margin, non_junk_margin)), 6)
        return 0.0

    def _switch_buffer_gaps(
        self,
        *,
        incumbent_daily_record: dict[str, Any],
        challenger_daily_record: dict[str, Any],
        sector_context: dict[str, Any],
        incumbent_switch_buffer: float,
        challenger_switch_buffer: float,
    ) -> tuple[float | None, float | None]:
        top_sector_id = sector_context.get("top_sector_id")
        sector_scores = sector_context.get("sector_scores", {})

        def compute_gap(record: dict[str, Any], threshold: float) -> float | None:
            approved_sector_id = record.get("approved_sector_id")
            if not approved_sector_id or not top_sector_id or approved_sector_id == top_sector_id:
                return None
            approved_score = sector_scores.get(str(approved_sector_id))
            top_score = sector_scores.get(str(top_sector_id))
            if approved_score is None or top_score is None:
                return None
            return round((float(top_score) - float(approved_score)) - threshold, 6)

        return (
            compute_gap(incumbent_daily_record, incumbent_switch_buffer),
            compute_gap(challenger_daily_record, challenger_switch_buffer),
        )


def write_feature_pack_a_recheck_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackARecheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
