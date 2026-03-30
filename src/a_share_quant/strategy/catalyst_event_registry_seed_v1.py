from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.common.config import load_yaml_config


@dataclass(slots=True)
class CatalystEventRegistrySeedReport:
    summary: dict[str, Any]
    seed_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "seed_rows": self.seed_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CatalystEventRegistrySeedAnalyzer:
    """Build the first bounded catalyst registry seed from already-closed lanes and carry rows."""

    def analyze(
        self,
        *,
        opening_reports: list[tuple[str, dict[str, Any]]],
        persistence_reports: list[tuple[str, dict[str, Any]]],
        carry_schema_payload: dict[str, Any],
    ) -> CatalystEventRegistrySeedReport:
        seed_rows: list[dict[str, Any]] = []

        for report_path, payload in opening_reports:
            summary = dict(payload.get("summary", {}))
            opening_edge = dict(payload.get("opening_edge") or {})
            symbol = Path(report_path).stem.split("_")[-2] if "_" in Path(report_path).stem else ""
            seed_rows.append(
                {
                    "lane_id": f"{summary.get('strategy_name')}::{summary.get('opening_trade_date')}::{symbol}",
                    "dataset_name": "seed_from_closed_opening_lane",
                    "slice_name": str(summary.get("window_start", ""))[:7],
                    "strategy_name": str(summary.get("strategy_name", "")),
                    "symbol": symbol,
                    "event_date": str(summary.get("opening_trade_date", "")),
                    "window_start": str(summary.get("window_start", "")),
                    "window_end": str(summary.get("window_end", "")),
                    "event_scope": "theme_or_sector",
                    "event_type": "seed_pending",
                    "source_authority_tier": "unknown",
                    "policy_scope": "unknown",
                    "execution_strength": "unknown",
                    "rumor_risk_level": "unknown",
                    "source_tier": "seed_pending",
                    "primary_source_ref": "",
                    "persistence_class": "single_pulse",
                    "reinforcement_count": 0,
                    "confirmation_delay_days": 0,
                    "followthrough_window_days": 0,
                    "board_pulse_breadth_class": "unknown",
                    "turnover_concentration_class": "unknown",
                    "first_impulse_return_pct": None,
                    "consolidation_days_after_pulse": None,
                    "retrace_depth_vs_ma5": None,
                    "retrace_depth_vs_ma10": None,
                    "reacceleration_present": False,
                    "reacceleration_delay_days": None,
                    "lane_outcome_label": "opening_led",
                    "context_posture": "seed_pending_manual_or_semimanual_fill",
                    "notes": str(opening_edge.get("specialist_assignment_reason", "")),
                }
            )

        for report_path, payload in persistence_reports:
            summary = dict(payload.get("summary", {}))
            persistence_edge = dict(payload.get("persistence_edge") or {})
            symbol = Path(report_path).stem.split("_")[-2] if "_" in Path(report_path).stem else ""
            seed_rows.append(
                {
                    "lane_id": f"{summary.get('strategy_name')}::{summary.get('persistence_trade_date')}::{symbol}",
                    "dataset_name": "seed_from_closed_persistence_lane",
                    "slice_name": str(summary.get("window_start", ""))[:7],
                    "strategy_name": str(summary.get("strategy_name", "")),
                    "symbol": symbol,
                    "event_date": str(summary.get("persistence_trade_date", "")),
                    "window_start": str(summary.get("window_start", "")),
                    "window_end": str(summary.get("window_end", "")),
                    "event_scope": "theme_or_sector",
                    "event_type": "seed_pending",
                    "source_authority_tier": "unknown",
                    "policy_scope": "unknown",
                    "execution_strength": "unknown",
                    "rumor_risk_level": "unknown",
                    "source_tier": "seed_pending",
                    "primary_source_ref": "",
                    "persistence_class": "multi_day_reinforcement",
                    "reinforcement_count": None,
                    "confirmation_delay_days": None,
                    "followthrough_window_days": None,
                    "board_pulse_breadth_class": "unknown",
                    "turnover_concentration_class": "unknown",
                    "first_impulse_return_pct": None,
                    "consolidation_days_after_pulse": None,
                    "retrace_depth_vs_ma5": None,
                    "retrace_depth_vs_ma10": None,
                    "reacceleration_present": None,
                    "reacceleration_delay_days": None,
                    "lane_outcome_label": "persistence_led",
                    "context_posture": "seed_pending_manual_or_semimanual_fill",
                    "notes": str(persistence_edge.get("specialist_exit_reason", "")),
                }
            )

        for row in list(carry_schema_payload.get("schema_rows", [])):
            seed_rows.append(
                {
                    "lane_id": f"{row.get('strategy_name')}::{row.get('trigger_date')}::300750",
                    "dataset_name": "seed_from_carry_observable_schema",
                    "slice_name": str(row.get("trigger_date", ""))[:7],
                    "strategy_name": str(row.get("strategy_name", "")),
                    "symbol": "300750",
                    "event_date": str(row.get("trigger_date", "")),
                    "window_start": str(row.get("challenger_entry_date", "")),
                    "window_end": str(row.get("challenger_exit_date", "")),
                    "event_scope": "theme_or_sector",
                    "event_type": "seed_pending",
                    "source_authority_tier": "unknown",
                    "policy_scope": "unknown",
                    "execution_strength": "unknown",
                    "rumor_risk_level": "unknown",
                    "source_tier": "seed_pending",
                    "primary_source_ref": "",
                    "persistence_class": "policy_followthrough",
                    "reinforcement_count": None,
                    "confirmation_delay_days": None,
                    "followthrough_window_days": int(row.get("challenger_carry_days", 0)),
                    "board_pulse_breadth_class": "unknown",
                    "turnover_concentration_class": "unknown",
                    "first_impulse_return_pct": None,
                    "consolidation_days_after_pulse": None,
                    "retrace_depth_vs_ma5": None,
                    "retrace_depth_vs_ma10": None,
                    "reacceleration_present": None,
                    "reacceleration_delay_days": None,
                    "lane_outcome_label": "carry_row_present",
                    "context_posture": "seed_pending_manual_or_semimanual_fill",
                    "notes": f"basis_advantage_bps={row.get('basis_advantage_bps')}",
                }
            )

        label_counts: dict[str, int] = {}
        for row in seed_rows:
            label = str(row["lane_outcome_label"])
            label_counts[label] = label_counts.get(label, 0) + 1

        summary = {
            "seed_posture": "open_catalyst_event_registry_seed_v1_as_bounded_lane_sample",
            "seed_row_count": len(seed_rows),
            "label_counts": label_counts,
            "opening_seed_count": label_counts.get("opening_led", 0),
            "persistence_seed_count": label_counts.get("persistence_led", 0),
            "carry_seed_count": label_counts.get("carry_row_present", 0),
            "ready_for_first_manual_or_semimanual_event_fill": len(seed_rows) > 0,
        }
        interpretation = [
            "The catalyst branch should begin with a small auditable lane sample instead of a wide news scrape.",
            "This seed intentionally mixes opening, persistence, and carry rows so later catalyst fields can be compared against already-frozen lane outcomes.",
            "The next step after this seed is not modeling; it is filling event-level fields for this bounded sample.",
        ]
        return CatalystEventRegistrySeedReport(
            summary=summary,
            seed_rows=seed_rows,
            interpretation=interpretation,
        )


def write_catalyst_event_registry_seed_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CatalystEventRegistrySeedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def load_catalyst_event_registry_seed_config(
    path: Path,
) -> tuple[list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]], dict[str, Any], Path, str]:
    payload = load_yaml_config(path)
    opening_reports = [
        (str(report_path), load_json_report(Path(str(report_path))))
        for report_path in payload["opening_reports"]
    ]
    persistence_reports = [
        (str(report_path), load_json_report(Path(str(report_path))))
        for report_path in payload["persistence_reports"]
    ]
    carry_schema_payload = load_json_report(Path(payload["paths"]["carry_schema_report"]))
    reports_dir = Path(payload["paths"]["reports_dir"])
    report_name = str(payload["report"]["name"])
    return opening_reports, persistence_reports, carry_schema_payload, reports_dir, report_name
