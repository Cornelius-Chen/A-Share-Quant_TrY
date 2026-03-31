from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113EPilotProtocolReport:
    summary: dict[str, Any]
    pilot_basis: dict[str, Any]
    labeling_protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "pilot_basis": self.pilot_basis,
            "labeling_protocol": self.labeling_protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113EPilotProtocolAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        archetype_usage_payload: dict[str, Any],
    ) -> V113EPilotProtocolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_pilot_protocol_next")):
            raise ValueError("V1.13E requires an open bounded labeling pilot charter.")

        archetype_rows = list(archetype_usage_payload.get("archetype_review_rows", []))
        clean_rows = [row for row in archetype_rows if row.get("review_disposition") == "preserve_as_clean_template_review_asset"]
        if len(clean_rows) != 1:
            raise ValueError("V1.13E expects exactly one clean template review asset from V1.13D.")

        selected = clean_rows[0]
        pilot_basis = {
            "selected_archetype": selected.get("archetype_name"),
            "pilot_scope": "single_archetype_only",
            "pilot_posture": "report_only_labeling_and_training_readiness",
            "why_selected": selected.get("reading"),
        }
        labeling_protocol = {
            "sample_unit": "symbol_day_within_one_theme_diffusion_window",
            "label_blocks": {
                "state_label": ["ignition", "diffusion", "relay", "decay"],
                "role_label": ["leader", "mid_core", "laggard_catchup", "mapping_activation"],
                "strength_labels": [
                    "mainline_persistence_level",
                    "mainline_height_level",
                    "mainline_absorption_quality",
                    "a_kill_risk_level",
                ],
                "driver_presence_review_flags": [
                    "policy_backing_tier",
                    "industrial_advantage_alignment",
                    "market_regime_tailwind",
                    "event_resonance_intensity",
                ],
            },
            "validation_rules": [
                "report_only_pilot",
                "no_execution_features",
                "no_signal_generation",
                "single_archetype_first",
                "owner_review_before_dataset_widening",
            ],
            "training_posture": {
                "allowed": True,
                "scope": "minimal_baseline_only_after_dataset_assembly",
                "disallowed": [
                    "execution_modeling",
                    "strategy_signal_training",
                    "multi_archetype_joint_training",
                    "automatic_promotion",
                ],
            },
        }
        summary = {
            "acceptance_posture": "freeze_v113e_theme_diffusion_pilot_protocol_v1",
            "selected_archetype": pilot_basis["selected_archetype"],
            "label_block_count": len(labeling_protocol["label_blocks"]),
            "validation_rule_count": len(labeling_protocol["validation_rules"]),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.13E does not yet assemble or train the pilot; it freezes the minimum lawful pilot basis first.",
            "The selected seed is intentionally the cleanest archetype to reduce early grammar distortion.",
            "If this pilot later opens, it must stay report-only and single-archetype until owner review says otherwise.",
        ]
        return V113EPilotProtocolReport(
            summary=summary,
            pilot_basis=pilot_basis,
            labeling_protocol=labeling_protocol,
            interpretation=interpretation,
        )


def write_v113e_pilot_protocol_report(
    *, reports_dir: Path, report_name: str, result: V113EPilotProtocolReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
