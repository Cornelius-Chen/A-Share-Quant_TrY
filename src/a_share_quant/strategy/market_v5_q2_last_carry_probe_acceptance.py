from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MarketV5Q2LastCarryProbeAcceptanceReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class MarketV5Q2LastCarryProbeAcceptanceAnalyzer:
    """Close the last bounded v5 true-carry probe without over-promoting non-carry structure."""

    def analyze(
        self,
        *,
        target_symbol: str,
        reassessment_payload: dict[str, Any],
        divergence_payload: dict[str, Any],
        opening_payload: dict[str, Any],
        persistence_payload: dict[str, Any],
    ) -> MarketV5Q2LastCarryProbeAcceptanceReport:
        reassessment_summary = dict(reassessment_payload.get("summary", {}))
        divergence_rows = list(divergence_payload.get("strategy_symbol_summary", []))
        target_divergence = next(
            (row for row in divergence_rows if str(row.get("symbol")) == target_symbol),
            None,
        )
        if target_divergence is None:
            raise ValueError(f"Target symbol {target_symbol} is not present in the v5 divergence report.")

        target_delta = float(target_divergence.get("pnl_delta", 0.0))
        opening_summary = dict(opening_payload.get("summary", {}))
        persistence_summary = dict(persistence_payload.get("summary", {}))
        opening_present = bool(opening_summary.get("specialist_opened_window"))
        persistence_present = bool(persistence_summary.get("specialist_preserved_window"))

        if opening_present and not persistence_present:
            acceptance_posture = "close_market_v5_q2_last_true_carry_probe_as_opening_led_not_true_carry"
            lane_changes_training_reading = False
        elif persistence_present:
            acceptance_posture = "close_market_v5_q2_last_true_carry_probe_as_persistence_led_not_true_carry"
            lane_changes_training_reading = False
        elif abs(target_delta) > 1e-9:
            acceptance_posture = "close_market_v5_q2_last_true_carry_probe_as_divergent_but_not_true_carry"
            lane_changes_training_reading = False
        else:
            acceptance_posture = "close_market_v5_q2_last_true_carry_probe_as_no_active_structural_lane"
            lane_changes_training_reading = False

        summary = {
            "acceptance_posture": acceptance_posture,
            "target_symbol": target_symbol,
            "target_pnl_delta": target_delta,
            "opening_present": opening_present,
            "persistence_present": persistence_present,
            "lane_changes_training_reading": lane_changes_training_reading,
            "phase_allowed_last_true_carry_probe": bool(
                reassessment_summary.get("do_open_last_true_carry_probe_now")
            ),
            "do_continue_current_symbol_now": False,
            "do_continue_v5_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "v5_reassessment_gate",
                "actual": {
                    "acceptance_posture": reassessment_summary.get("acceptance_posture"),
                    "recommended_next_symbol": reassessment_summary.get("recommended_next_symbol"),
                    "phase_allowed_last_true_carry_probe": reassessment_summary.get("do_open_last_true_carry_probe_now"),
                },
                "reading": "The last carry probe is only legal because reassessment exhausted the clean-persistence track first.",
            },
            {
                "evidence_name": "divergence_signature",
                "actual": {
                    "target_symbol": target_symbol,
                    "target_pnl_delta": target_delta,
                    "incumbent_trade_count": target_divergence.get("incumbent_trade_count"),
                    "challenger_trade_count": target_divergence.get("challenger_trade_count"),
                },
                "reading": "A nominal carry target still needs a real specialist-owned structure before it can be treated as carry evidence.",
            },
            {
                "evidence_name": "window_checks",
                "actual": {
                    "opening_present": opening_present,
                    "opening_trade_date": opening_summary.get("opening_trade_date"),
                    "persistence_present": persistence_present,
                    "persistence_trade_date": persistence_summary.get("persistence_trade_date"),
                },
                "reading": "Opening or persistence can explain the lane, but neither should be relabelled into true carry evidence.",
            },
        ]
        interpretation = [
            "The last v5 probe exists to exhaust the current bounded manifest, not to force a carry conclusion.",
            "A nominal true-carry target that only yields opening, persistence, or generic divergence still does not repair the carry-row-diversity gap.",
            "So this probe should close cleanly unless it produces something materially stronger than the structures already observed.",
        ]
        return MarketV5Q2LastCarryProbeAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_market_v5_q2_last_carry_probe_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: MarketV5Q2LastCarryProbeAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
