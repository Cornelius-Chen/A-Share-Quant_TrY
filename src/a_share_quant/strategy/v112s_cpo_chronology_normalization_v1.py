from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112SCPOChronologyNormalizationReport:
    summary: dict[str, Any]
    chronology_segment_rows: list[dict[str, Any]]
    timing_gap_rows: list[dict[str, Any]]
    catalyst_calendar_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "chronology_segment_rows": self.chronology_segment_rows,
            "timing_gap_rows": self.timing_gap_rows,
            "catalyst_calendar_rows": self.catalyst_calendar_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112SCPOChronologyNormalizationAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        draft_batch_payload: dict[str, Any],
    ) -> V112SCPOChronologyNormalizationReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112s_now")):
            raise ValueError("V1.12S must be open before chronology normalization.")

        chronology_sources = list(draft_batch_payload.get("chronology_source_rows", []))
        future_calendar = list(draft_batch_payload.get("future_catalyst_calendar_rows", []))
        if len(chronology_sources) < 5 or len(future_calendar) < 8:
            raise ValueError("V1.12S expects the first chronology and calendar draft batch to be present.")

        chronology_segment_rows = [
            {
                "segment_name": "pre_event_watch_window",
                "reading": "The bounded watch window before a known conference, earnings print, or route event.",
                "default_relative_span": "T-20_to_T-1",
            },
            {
                "segment_name": "event_window",
                "reading": "The anchor window where the conference, earnings release, or public route event actually happens.",
                "default_relative_span": "T0_to_T+2",
            },
            {
                "segment_name": "post_event_followthrough_window",
                "reading": "The first reaction and digestion window after the public event, when narrative reset often matters most.",
                "default_relative_span": "T+3_to_T+15",
            },
            {
                "segment_name": "between_event_quiet_window",
                "reading": "The dead zone between large public events where procurement, design, and qualification can still move.",
                "default_relative_span": "between_major_public_anchors",
            },
            {
                "segment_name": "pre_earnings_channel_check_window",
                "reading": "The pre-print window where channel checks and expectation drift often move before formal results.",
                "default_relative_span": "earnings_T-15_to_T-1",
            },
            {
                "segment_name": "post_earnings_reset_window",
                "reading": "The 1-3 week period after earnings when backlog, guidance, and tone reset the chronology.",
                "default_relative_span": "earnings_T+1_to_T+15",
            },
            {
                "segment_name": "capex_to_order_conversion_window",
                "reading": "The lagged window between hyperscaler capex talk and optical order conversion.",
                "default_relative_span": "quarter_plus_lag",
            },
            {
                "segment_name": "launch_to_ramp_window",
                "reading": "The lag between a product or route announcement and visible shipment or revenue inflection.",
                "default_relative_span": "announcement_to_ramp",
            },
            {
                "segment_name": "design_win_to_volume_window",
                "reading": "The latency between design-win or qualification news and true volume production.",
                "default_relative_span": "win_to_volume_lag",
            },
        ]

        timing_gap_rows = [
            {
                "timing_gap_name": "post_earnings_gap_after_major_vendor_reports",
                "why_it_matters": "Narrative reset often happens in the 1-3 weeks after earnings, not only on conference dates.",
                "best_target_layer_or_stage": "post_earnings_reset_window",
                "suggested_review_priority": "high",
            },
            {
                "timing_gap_name": "between_conference_dead_zones",
                "why_it_matters": "Multi-month quiet periods can still contain procurement and qualification drift.",
                "best_target_layer_or_stage": "between_event_quiet_window",
                "suggested_review_priority": "high",
            },
            {
                "timing_gap_name": "fiscal_quarter_boundary_sequencing",
                "why_it_matters": "Demand and capex narratives can shift at quarter boundaries even without a large optical event.",
                "best_target_layer_or_stage": "pre_earnings_channel_check_window",
                "suggested_review_priority": "high",
            },
            {
                "timing_gap_name": "pre_earnings_channel_check_window",
                "why_it_matters": "Expectation drift before prints can invert cause-and-effect if not marked separately.",
                "best_target_layer_or_stage": "pre_earnings_channel_check_window",
                "suggested_review_priority": "high",
            },
            {
                "timing_gap_name": "capex_announcement_to_order_conversion_lag",
                "why_it_matters": "Hyperscaler capex references often lead actual optical orders by a quarter or more.",
                "best_target_layer_or_stage": "capex_to_order_conversion_window",
                "suggested_review_priority": "high",
            },
            {
                "timing_gap_name": "product_launch_to_revenue_inflection_lag",
                "why_it_matters": "Product announcements can materially precede shipment ramps.",
                "best_target_layer_or_stage": "launch_to_ramp_window",
                "suggested_review_priority": "medium",
            },
            {
                "timing_gap_name": "standards_milestone_sequencing",
                "why_it_matters": "Spec or interoperability milestones are not the same as commercial demand timing.",
                "best_target_layer_or_stage": "event_window",
                "suggested_review_priority": "medium",
            },
            {
                "timing_gap_name": "customer_design_win_latency",
                "why_it_matters": "Design wins often arrive long before volume revenue.",
                "best_target_layer_or_stage": "design_win_to_volume_window",
                "suggested_review_priority": "high",
            },
            {
                "timing_gap_name": "budget_cycle_overlap_with_calendar_events",
                "why_it_matters": "Planning-cycle and conference timing can align or conflict, distorting attribution.",
                "best_target_layer_or_stage": "between_event_quiet_window",
                "suggested_review_priority": "medium",
            },
            {
                "timing_gap_name": "supply_chain_lead_time_transition",
                "why_it_matters": "Lead-time compression or stretch changes the effective chronology of demand realization.",
                "best_target_layer_or_stage": "launch_to_ramp_window",
                "suggested_review_priority": "medium",
            },
        ]

        catalyst_calendar_rows = []
        for row in future_calendar:
            source_name = str(row.get("source_name", ""))
            if source_name in {
                "ofc_official_event_page",
                "nvidia_gtc_official",
                "optica_executive_forum_at_ofc",
                "oif_ofc_2026_demo_listing",
                "broadcom_ofc_announcements",
                "lumentum_ofc_announcements",
            }:
                normalized_bucket = "conference_or_route_event"
            else:
                normalized_bucket = "csp_capex_or_results_anchor"
            catalyst_calendar_rows.append(
                {
                    "source_name": source_name,
                    "normalized_bucket": normalized_bucket,
                    "target_layer": row.get("target_layer"),
                    "likely_refresh_frequency": row.get("likely_refresh_frequency"),
                    "why_it_helps": row.get("why_it_helps"),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112s_cpo_chronology_normalization_v1",
            "chronology_segment_count": len(chronology_segment_rows),
            "timing_gap_count": len(timing_gap_rows),
            "normalized_calendar_anchor_count": len(catalyst_calendar_rows),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12S turns flat event anchors into a bounded chronology grammar with explicit lag windows.",
            "The goal is not more dates; the goal is more usable timing structure for later review.",
            "This still does not authorize training or execution logic.",
        ]
        return V112SCPOChronologyNormalizationReport(
            summary=summary,
            chronology_segment_rows=chronology_segment_rows,
            timing_gap_rows=timing_gap_rows,
            catalyst_calendar_rows=catalyst_calendar_rows,
            interpretation=interpretation,
        )


def write_v112s_cpo_chronology_normalization_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112SCPOChronologyNormalizationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
