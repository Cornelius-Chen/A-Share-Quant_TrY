from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V133OCommercialAerospacePointInTimeVisibilitySpecReport:
    summary: dict[str, Any]
    feed_column_rows: list[dict[str, Any]]
    semantics_rows: list[dict[str, Any]]
    acceptance_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feed_column_rows": self.feed_column_rows,
            "semantics_rows": self.semantics_rows,
            "acceptance_rows": self.acceptance_rows,
            "interpretation": self.interpretation,
        }


class V133OCommercialAerospacePointInTimeVisibilitySpecAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.protocol_path = (
            repo_root / "reports" / "analysis" / "v133m_commercial_aerospace_intraday_execution_build_protocol_v1.json"
        )
        self.registry_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )
        self.action_ladder_path = (
            repo_root / "reports" / "analysis" / "v132s_commercial_aerospace_intraday_override_action_ladder_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_point_in_time_visibility_spec_v1.csv"
        )

    def analyze(self) -> V133OCommercialAerospacePointInTimeVisibilitySpecReport:
        protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        action_ladder = json.loads(self.action_ladder_path.read_text(encoding="utf-8"))

        feed_column_rows = [
            {
                "column": "minute_ts",
                "domain": "identity",
                "visibility_rule": "exact minute close timestamp of the current 1min bar",
                "allowed_at_t": "yes",
                "notes": "all other columns must be attributable to this timestamp or earlier",
            },
            {
                "column": "symbol",
                "domain": "identity",
                "visibility_rule": "static session identity",
                "allowed_at_t": "yes",
                "notes": "used for joining minute bars to seed-session governance context",
            },
            {
                "column": "open_px/high_px/low_px/close_px",
                "domain": "bar_price",
                "visibility_rule": "current bar OHLC is only available after the 1min bar closes",
                "allowed_at_t": "close_of_bar_only",
                "notes": "same-minute aggregates must not be visible before bar close",
            },
            {
                "column": "bar_volume/bar_turnover",
                "domain": "bar_volume",
                "visibility_rule": "current bar aggregates are only available after the 1min bar closes",
                "allowed_at_t": "close_of_bar_only",
                "notes": "no mid-bar completion assumptions",
            },
            {
                "column": "ret_1m_lag1/ret_3m_lag1/ret_5m_lag1",
                "domain": "lagged_path",
                "visibility_rule": "computed only from fully closed bars strictly earlier than minute t",
                "allowed_at_t": "yes",
                "notes": "prevents same-bar leakage inside path features",
            },
            {
                "column": "draw_from_open_lag1/draw_15m_lag1/draw_30m_lag1",
                "domain": "lagged_path",
                "visibility_rule": "computed from the session path up to the last fully closed bar",
                "allowed_at_t": "yes",
                "notes": "used to reconstruct severe/reversal/mild escalation without same-bar peeking",
            },
            {
                "column": "close_location_lag1",
                "domain": "lagged_path",
                "visibility_rule": "close-location over the last visible rolling window, ending at the prior closed bar",
                "allowed_at_t": "yes",
                "notes": "must not use the current minute range before bar close",
            },
            {
                "column": "phase_state_visible",
                "domain": "governance_context",
                "visibility_rule": "session-level state inherited from frozen EOD/minute governance and visible from the open",
                "allowed_at_t": "yes",
                "notes": "examples: preheat_window, impulse_window, weak_drift proxy context",
            },
            {
                "column": "event_state_visible",
                "domain": "event_context",
                "visibility_rule": "must carry first_visible_ts and only activate at or after that timestamp",
                "allowed_at_t": "first_visible_ts_or_later",
                "notes": "day-level events must be converted into minute-visible state updates, never backfilled earlier",
            },
            {
                "column": "pre_open_event_status",
                "domain": "event_context",
                "visibility_rule": "session-level status frozen before the open",
                "allowed_at_t": "yes",
                "notes": "can be joined from the open because it is already decided before trading starts",
            },
            {
                "column": "severity_tier_shadow",
                "domain": "shadow_label",
                "visibility_rule": "derived minute governance tier for supervision/shadow only",
                "allowed_at_t": "shadow_only",
                "notes": "cannot be bound into the authoritative EOD lane",
            },
            {
                "column": "first_visible_ts/source_cutoff_ts",
                "domain": "lineage_guardrail",
                "visibility_rule": "mandatory lineage columns for every event/state field",
                "allowed_at_t": "yes",
                "notes": "core PIT audit fields; missing values fail the protocol",
            },
        ]

        ladder_rows = action_ladder["action_rows"]
        semantics_rows = [
            {
                "semantic_rule": "close_bar_activation",
                "detail": "same-minute OHLCV and any same-minute derived aggregate only become visible after the bar is complete",
            },
            {
                "semantic_rule": "first_visible_ts_required",
                "detail": "every event-derived or state-derived field must store the first timestamp at which it became lawful to see",
            },
            {
                "semantic_rule": "one_way_read_only_boundary",
                "detail": "the point-in-time feed may read frozen EOD context, but nothing in this feed may write back into the frozen EOD primary",
            },
            {
                "semantic_rule": "tier_to_action_mapping",
                "detail": "; ".join(
                    f"{row['minute_tier_label']} -> {row['governance_action']}" for row in ladder_rows
                ),
            },
        ]

        acceptance_rows = [
            {
                "acceptance_item": "seed_session_reconstructibility",
                "status": "required",
                "detail": f"all {registry['summary']['registry_row_count']} canonical seed sessions must be replayable minute by minute using only visible columns",
            },
            {
                "acceptance_item": "lineage_completeness",
                "status": "required",
                "detail": "all event/state fields must include first_visible_ts and source_cutoff_ts; null lineage fails acceptance",
            },
            {
                "acceptance_item": "same_bar_no_peek",
                "status": "required",
                "detail": "no path or bar aggregate may depend on the unfinished current bar before its close",
            },
            {
                "acceptance_item": "shadow_only_binding",
                "status": "required",
                "detail": "the resulting visibility feed remains governance/shadow-only until a later simulator and separate replay lane exist",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(feed_column_rows[0].keys()))
            writer.writeheader()
            writer.writerows(feed_column_rows)

        summary = {
            "acceptance_posture": "freeze_v133o_commercial_aerospace_point_in_time_visibility_spec_v1",
            "protocol_workstream": protocol["workstream_rows"][0]["workstream"],
            "feed_column_count": len(feed_column_rows),
            "semantic_rule_count": len(semantics_rows),
            "acceptance_item_count": len(acceptance_rows),
            "seed_session_count": registry["summary"]["registry_row_count"],
            "spec_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_point_in_time_visibility_spec_ready_for_phase_1_implementation",
        }
        interpretation = [
            "V1.33O converts phase_1_visibility from a blocker label into a concrete minute-state specification.",
            "The spec is intentionally narrow: it defines what minute columns may exist, when they become visible, and what lineage fields are mandatory before any simulator work starts.",
        ]
        return V133OCommercialAerospacePointInTimeVisibilitySpecReport(
            summary=summary,
            feed_column_rows=feed_column_rows,
            semantics_rows=semantics_rows,
            acceptance_rows=acceptance_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V133OCommercialAerospacePointInTimeVisibilitySpecReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V133OCommercialAerospacePointInTimeVisibilitySpecAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v133o_commercial_aerospace_point_in_time_visibility_spec_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
