from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112TrainingProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112TrainingProtocolAnalyzer:
    """Freeze the minimal protocol for the first single-cycle experiment."""

    def analyze(
        self,
        *,
        pilot_cycle_selection_payload: dict[str, Any],
    ) -> V112TrainingProtocolReport:
        selection_summary = dict(pilot_cycle_selection_payload.get("summary", {}))
        if not bool(selection_summary.get("ready_for_training_protocol_next")):
            raise ValueError("V1.12 pilot cycle must be selected before freezing the training protocol.")

        protocol = {
            "training_objective": "maximize_cycle_return_under_drawdown_constraint",
            "sample_unit": "symbol_day_within_one_price_cycle_window",
            "feature_blocks": {
                "catalyst_state": [
                    "product_price_change_proxy",
                    "demand_acceleration_proxy",
                    "supply_tightness_proxy",
                    "official_or_industry_catalyst_presence",
                ],
                "earnings_transmission_bridge": [
                    "revenue_sensitivity_class",
                    "gross_margin_sensitivity_class",
                    "order_or_capacity_sensitivity_proxy",
                ],
                "expectation_gap": [
                    "earnings_revision_pressure_proxy",
                    "rerating_gap_proxy",
                ],
                "price_confirmation": [
                    "relative_strength_persistence",
                    "volume_expansion_confirmation",
                    "breakout_or_hold_structure",
                ],
            },
            "label_set": [
                "forward_return_bucket",
                "max_drawdown_bucket",
                "carry_outcome_class",
            ],
            "validation_rules": [
                "time_split_only_no_random_shuffle",
                "single_cycle_first_then_multi_object_expansion",
                "no_intraday_execution_features_in_first_pilot",
                "report_only_model_readout_in_first_pilot",
            ],
            "expansion_rules": [
                "only add new objects after first cycle protocol is frozen and reviewable",
                "do not mix carry families inside the first experiment",
                "later multi-object expansion must preserve the same label and split discipline",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v112_training_protocol_v1",
            "feature_block_count": len(protocol["feature_blocks"]),
            "label_count": len(protocol["label_set"]),
            "validation_rule_count": len(protocol["validation_rules"]),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The first price-cycle training experiment should be framed as a bounded report-only model problem, not a live-trading system.",
            "The protocol explicitly separates catalyst, earnings transmission, expectation gap, and price confirmation.",
            "This lets later scaling add objects while preserving the same unit, labels, and validation discipline.",
        ]
        return V112TrainingProtocolReport(summary=summary, protocol=protocol, interpretation=interpretation)


def write_v112_training_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112TrainingProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
