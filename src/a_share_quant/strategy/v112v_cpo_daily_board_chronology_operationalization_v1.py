from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112VCPODailyBoardChronologyOperationalizationReport:
    summary: dict[str, Any]
    daily_series_rows: list[dict[str, Any]]
    table_column_rows: list[dict[str, Any]]
    source_precedence_rows: list[dict[str, Any]]
    unresolved_gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "daily_series_rows": self.daily_series_rows,
            "table_column_rows": self.table_column_rows,
            "source_precedence_rows": self.source_precedence_rows,
            "unresolved_gap_rows": self.unresolved_gap_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112VCPODailyBoardChronologyOperationalizationAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        schema_payload: dict[str, Any],
        chronology_payload: dict[str, Any],
        draft_batch_payload: dict[str, Any],
    ) -> V112VCPODailyBoardChronologyOperationalizationReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112v_now")):
            raise ValueError("V1.12V must be open before chronology operationalization.")

        chronology_summary = dict(chronology_payload.get("summary", {}))
        if int(chronology_summary.get("chronology_segment_count", 0)) < 9:
            raise ValueError("V1.12V expects the V1.12S chronology grammar to be present.")

        schema_rows = list(schema_payload.get("feature_slot_rows", []))
        board_rows = [
            row
            for row in schema_rows
            if row.get("layer_name") == "index_sentiment_and_liquidity"
        ]
        if len(board_rows) < 4:
            raise ValueError("V1.12V expects the index_sentiment_and_liquidity layer to be frozen in V1.12Q.")

        chronology_sources = list(draft_batch_payload.get("chronology_source_rows", []))
        if len(chronology_sources) < 5:
            raise ValueError("V1.12V expects chronology-source anchors from the V1.12Q draft batch.")

        daily_series_rows = [
            {
                "series_name": "concept_index_strength_daily",
                "intended_reading": "day-level strength of the CPO or optical-link board proxy",
                "derived_from": "board or concept index level and relative change",
                "posture": "review_first_operational_series",
            },
            {
                "series_name": "cohort_breadth_daily",
                "intended_reading": "how widely the cohort is participating on a given trading day",
                "derived_from": "advancers, strong-move count, or bounded breadth proxy",
                "posture": "review_first_operational_series",
            },
            {
                "series_name": "turnover_pressure_daily",
                "intended_reading": "whether the board is seeing capital concentration, churn, or exhaustion pressure",
                "derived_from": "turnover,成交额 proxy, or normalized liquidity state",
                "posture": "review_first_operational_series",
            },
            {
                "series_name": "cross_board_resonance_daily",
                "intended_reading": "whether CPO is moving in isolation or with larger AI-hardware or optical-chain resonance",
                "derived_from": "same-day resonance with adjacent boards",
                "posture": "review_first_operational_series",
            },
            {
                "series_name": "anchor_event_overlap_daily",
                "intended_reading": "whether a day falls inside pre-event, event, or follow-through windows tied to frozen anchors",
                "derived_from": "V1.12S chronology grammar plus normalized event anchors",
                "posture": "review_first_operational_series",
            },
        ]

        table_column_rows = [
            {"column_name": "trade_date", "column_role": "primary_time_key"},
            {"column_name": "board_family", "column_role": "board_identity"},
            {"column_name": "chronology_segment", "column_role": "time_window_attachment"},
            {"column_name": "concept_index_strength_daily", "column_role": "board_state"},
            {"column_name": "cohort_breadth_daily", "column_role": "board_state"},
            {"column_name": "turnover_pressure_daily", "column_role": "liquidity_state"},
            {"column_name": "cross_board_resonance_daily", "column_role": "sentiment_state"},
            {"column_name": "anchor_event_overlap_daily", "column_role": "event_alignment"},
            {"column_name": "source_quality_tier", "column_role": "source_confidence"},
            {"column_name": "observation_mode", "column_role": "measured_vs_review_proxy"},
            {"column_name": "missingness_reason", "column_role": "data_gap_trace"},
            {"column_name": "owner_review_flag", "column_role": "auditability"},
        ]

        source_precedence_rows = [
            {
                "precedence_tier": 1,
                "source_class": "structured_board_or_concept_index_series",
                "usage_rule": "Use first when a stable daily board or concept series exists.",
            },
            {
                "precedence_tier": 2,
                "source_class": "daily breadth_or_turnover proxy from bounded cohort reconstruction",
                "usage_rule": "Use when a clean board index is missing but cohort-level day reconstruction is possible.",
            },
            {
                "precedence_tier": 3,
                "source_class": "event-anchor overlap inferred from V1.12S chronology grammar",
                "usage_rule": "Use to attach timing structure even when numeric board series are incomplete.",
            },
            {
                "precedence_tier": 4,
                "source_class": "manual review placeholder with explicit missingness",
                "usage_rule": "Use only when the above tiers are unavailable; do not silently backfill.",
            },
        ]

        unresolved_gap_rows = [
            {
                "gap_name": "board_vendor_selection_not_yet_frozen",
                "why_it_still_matters": "The daily table spec exists, but the canonical board-series provider is not yet frozen.",
            },
            {
                "gap_name": "breadth_formula_not_yet_frozen",
                "why_it_still_matters": "Breadth is operationalized conceptually, but the exact bounded computation rule is not yet frozen.",
            },
            {
                "gap_name": "turnover_normalization_rule_not_yet_frozen",
                "why_it_still_matters": "Turnover pressure is a required daily field, but the exact normalization rule remains open.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112v_cpo_daily_board_chronology_operationalization_v1",
            "daily_series_count": len(daily_series_rows),
            "table_column_count": len(table_column_rows),
            "source_precedence_count": len(source_precedence_rows),
            "remaining_operational_gap_count": len(unresolved_gap_rows),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12V turns the board chronology gap into a bounded operational table spec.",
            "The line still does not have a full day-by-day backfill, but it now has an auditable operational target.",
            "This is still information-foundation work, not model or signal work.",
        ]
        return V112VCPODailyBoardChronologyOperationalizationReport(
            summary=summary,
            daily_series_rows=daily_series_rows,
            table_column_rows=table_column_rows,
            source_precedence_rows=source_precedence_rows,
            unresolved_gap_rows=unresolved_gap_rows,
            interpretation=interpretation,
        )


def write_v112v_cpo_daily_board_chronology_operationalization_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112VCPODailyBoardChronologyOperationalizationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
