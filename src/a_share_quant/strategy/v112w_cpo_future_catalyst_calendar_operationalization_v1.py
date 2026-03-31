from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112WFutureCatalystCalendarOperationalizationReport:
    summary: dict[str, Any]
    recurring_calendar_rows: list[dict[str, Any]]
    table_column_rows: list[dict[str, Any]]
    source_precedence_rows: list[dict[str, Any]]
    unresolved_gap_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "recurring_calendar_rows": self.recurring_calendar_rows,
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


class V112WFutureCatalystCalendarOperationalizationAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        chronology_payload: dict[str, Any],
        draft_batch_payload: dict[str, Any],
    ) -> V112WFutureCatalystCalendarOperationalizationReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112w_now")):
            raise ValueError("V1.12W must be open before future catalyst calendar operationalization.")

        chronology_summary = dict(chronology_payload.get("summary", {}))
        if int(chronology_summary.get("normalized_calendar_anchor_count", 0)) < 10:
            raise ValueError("V1.12W expects the V1.12S normalized catalyst calendar anchors to be present.")

        future_rows = list(draft_batch_payload.get("future_catalyst_calendar_rows", []))
        if len(future_rows) < 10:
            raise ValueError("V1.12W expects future catalyst calendar anchors from the V1.12Q draft batch.")

        recurring_calendar_rows = []
        for row in future_rows:
            source_name = str(row.get("source_name", ""))
            if source_name in {
                "ofc_official_event_page",
                "nvidia_gtc_official",
                "optica_executive_forum_at_ofc",
                "oif_ofc_2026_demo_listing",
            }:
                cadence_bucket = "annual_event_window"
            elif source_name in {
                "broadcom_ofc_announcements",
                "lumentum_ofc_announcements",
            }:
                cadence_bucket = "event_driven_company_route_release"
            else:
                cadence_bucket = "quarterly_csp_results_or_capex_anchor"

            recurring_calendar_rows.append(
                {
                    "source_name": source_name,
                    "cadence_bucket": cadence_bucket,
                    "target_layer": row.get("target_layer"),
                    "default_refresh_frequency": row.get("likely_refresh_frequency"),
                    "calendar_use_mode": "review_first_forward_anchor",
                    "why_it_helps": row.get("why_it_helps"),
                }
            )

        table_column_rows = [
            {"column_name": "calendar_anchor_id", "column_role": "primary_key"},
            {"column_name": "anchor_group", "column_role": "event_family"},
            {"column_name": "cadence_bucket", "column_role": "recurrence_type"},
            {"column_name": "expected_window_start", "column_role": "forward_timing"},
            {"column_name": "expected_window_end", "column_role": "forward_timing"},
            {"column_name": "target_layer", "column_role": "registry_attachment"},
            {"column_name": "confidence_tier", "column_role": "source_confidence"},
            {"column_name": "source_url", "column_role": "traceability"},
            {"column_name": "refresh_frequency", "column_role": "maintenance_rule"},
            {"column_name": "window_status", "column_role": "upcoming_or_passed_state"},
            {"column_name": "owner_review_flag", "column_role": "auditability"},
            {"column_name": "missingness_reason", "column_role": "data_gap_trace"},
        ]

        source_precedence_rows = [
            {
                "precedence_tier": 1,
                "source_class": "official_event_or_ir_calendar_page",
                "usage_rule": "Use first when an official event page or IR calendar exists.",
            },
            {
                "precedence_tier": 2,
                "source_class": "official_company_news_release",
                "usage_rule": "Use when event timing is disclosed through company PR rather than a stable calendar page.",
            },
            {
                "precedence_tier": 3,
                "source_class": "official_results_and_prepared_remarks_schedule",
                "usage_rule": "Use for quarterly capex or results anchors when event pages are absent.",
            },
            {
                "precedence_tier": 4,
                "source_class": "review_placeholder_with_explicit_missingness",
                "usage_rule": "Use only when no official timing source can be pinned down; do not silently infer dates.",
            },
        ]

        unresolved_gap_rows = [
            {
                "gap_name": "expected_window_fill_rule_not_yet_frozen",
                "why_it_still_matters": "The table shape exists, but the exact rule for window start/end filling across annual vs quarterly anchors remains open.",
            },
            {
                "gap_name": "confidence_tier_mapping_not_yet_frozen",
                "why_it_still_matters": "Confidence is required, but the exact tiering rubric across event pages, PRs, and results schedules remains open.",
            },
            {
                "gap_name": "calendar_rollforward_process_not_yet_frozen",
                "why_it_still_matters": "The recurring table exists conceptually, but the maintenance rule for expired anchors and next-cycle rollover remains open.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112w_cpo_future_catalyst_calendar_operationalization_v1",
            "recurring_anchor_count": len(recurring_calendar_rows),
            "table_column_count": len(table_column_rows),
            "source_precedence_count": len(source_precedence_rows),
            "remaining_operational_gap_count": len(unresolved_gap_rows),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12W turns forward-visible catalyst anchors into a bounded recurring calendar spec.",
            "The line still does not have a fully maintained forward calendar, but it now has an auditable operational target.",
            "This remains information-foundation work, not trigger logic or execution logic.",
        ]
        return V112WFutureCatalystCalendarOperationalizationReport(
            summary=summary,
            recurring_calendar_rows=recurring_calendar_rows,
            table_column_rows=table_column_rows,
            source_precedence_rows=source_precedence_rows,
            unresolved_gap_rows=unresolved_gap_rows,
            interpretation=interpretation,
        )


def write_v112w_cpo_future_catalyst_calendar_operationalization_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112WFutureCatalystCalendarOperationalizationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
