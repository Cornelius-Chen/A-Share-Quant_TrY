from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V114UIntradayEventTimestampDisciplineProtocolReport:
    summary: dict[str, Any]
    mandatory_timestamp_rows: list[dict[str, Any]]
    field_schema_rows: list[dict[str, Any]]
    usage_boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mandatory_timestamp_rows": self.mandatory_timestamp_rows,
            "field_schema_rows": self.field_schema_rows,
            "usage_boundary_rows": self.usage_boundary_rows,
            "interpretation": self.interpretation,
        }


class V114UIntradayEventTimestampDisciplineProtocolAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V114UIntradayEventTimestampDisciplineProtocolReport:
        mandatory_timestamp_rows = [
            {
                "event_family": "news_flash",
                "granularity_required": "second",
                "why_required": "News flashes can change intraday add/reduce legality within minutes; minute-level bucketing is too coarse for replay integrity.",
            },
            {
                "event_family": "exchange_announcement",
                "granularity_required": "second",
                "why_required": "Announcements and trading notices often determine whether a symbol is tradable or whether a move is catalyst-backed.",
            },
            {
                "event_family": "company_announcement",
                "granularity_required": "second",
                "why_required": "Board diffusion strength can be genuine or false depending on when filings become public.",
            },
            {
                "event_family": "policy_or_regulation_release",
                "granularity_required": "second",
                "why_required": "Macro/policy events can reprice the whole board intraday and must not be backfilled as earlier-known context.",
            },
            {
                "event_family": "research_note_or_market_memo_public_release",
                "granularity_required": "second",
                "why_required": "Even if weaker than formal news, once used in intraday learning they need a legally visible timestamp.",
            },
        ]

        field_schema_rows = [
            {
                "field_name": "event_occurred_time",
                "required": True,
                "definition": "Best-known timestamp for when the underlying event happened in the world.",
            },
            {
                "field_name": "public_release_time",
                "required": True,
                "definition": "Timestamp for when the event first became publicly available.",
            },
            {
                "field_name": "system_visible_time",
                "required": True,
                "definition": "Timestamp for when the project pipeline could legally observe and use the event.",
            },
            {
                "field_name": "source_latency_ms",
                "required": True,
                "definition": "Observed or assumed latency from public release to system visibility.",
            },
            {
                "field_name": "source_id",
                "required": True,
                "definition": "Unique source/feed identifier for auditability.",
            },
            {
                "field_name": "timezone",
                "required": True,
                "definition": "Explicit timezone for all intraday event stamps; no implicit local-time assumptions.",
            },
            {
                "field_name": "event_confidence_tier",
                "required": False,
                "definition": "Optional trust rating for noisy informal sources that may later be filtered.",
            },
        ]

        usage_boundary_rows = [
            {
                "data_family": "intraday_action_inputs",
                "timestamp_rule": "must_have_precise_timestamp",
                "allowed_granularity": "second",
                "examples": [
                    "news",
                    "announcements",
                    "policy releases",
                    "exchange notices",
                    "alert events",
                ],
            },
            {
                "data_family": "intraday_market_bars",
                "timestamp_rule": "bar_time_required",
                "allowed_granularity": "minute_or_bar_level",
                "examples": [
                    "intraday OHLCV",
                    "intraday turnover",
                    "ETF/index intraday bars",
                ],
            },
            {
                "data_family": "slow_background_context",
                "timestamp_rule": "day_level_is_acceptable",
                "allowed_granularity": "daily",
                "examples": [
                    "board regime",
                    "world model priors",
                    "daily owner labels",
                ],
            },
            {
                "data_family": "replay_legality",
                "timestamp_rule": "system_visible_time_is_authoritative",
                "allowed_granularity": "second",
                "examples": [
                    "do not use event_occurred_time if public/system visibility is later",
                    "do not backfill post-close information into earlier intraday decisions",
                ],
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v114u_intraday_event_timestamp_discipline_protocol_v1",
            "objective": "make_intraday_learning_and_execution_point_in_time_legal",
            "mandatory_event_family_count": len(mandatory_timestamp_rows),
            "mandatory_schema_field_count": len(field_schema_rows),
            "core_rule": "any_external_information_that_can_change_intraday_actions_must_be_recorded_with_second_level_timestamp_and_system_visible_time",
            "recommended_next_posture": "apply_second_level_timestamp_discipline_to_all_future_intraday_news_and_event_collection",
        }

        interpretation = [
            "V1.14U makes timestamp discipline explicit: intraday decisions must be based on what the system could see at that moment, not on what later became knowable.",
            "The key operational timestamp is `system_visible_time`, not merely when the event happened in the world.",
            "This protocol prevents intraday news or event data from becoming a new forward-leak channel once minute-level replay is introduced.",
        ]

        return V114UIntradayEventTimestampDisciplineProtocolReport(
            summary=summary,
            mandatory_timestamp_rows=mandatory_timestamp_rows,
            field_schema_rows=field_schema_rows,
            usage_boundary_rows=usage_boundary_rows,
            interpretation=interpretation,
        )


def write_v114u_intraday_event_timestamp_discipline_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114UIntradayEventTimestampDisciplineProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114UIntradayEventTimestampDisciplineProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_v114u_intraday_event_timestamp_discipline_protocol_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114u_intraday_event_timestamp_discipline_protocol_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
