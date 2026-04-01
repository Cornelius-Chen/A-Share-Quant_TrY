from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113JBoardResearchWorldModelProtocolReport:
    summary: dict[str, Any]
    world_model_layers: list[dict[str, Any]]
    teaching_boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "world_model_layers": self.world_model_layers,
            "teaching_boundary_rows": self.teaching_boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113JBoardResearchWorldModelProtocolAnalyzer:
    def analyze(
        self,
        *,
        v113i_payload: dict[str, Any],
        world_model_teaching_approved: bool,
    ) -> V113JBoardResearchWorldModelProtocolReport:
        i_summary = dict(v113i_payload.get("summary", {}))
        if str(i_summary.get("acceptance_posture")) != "freeze_v113i_board_level_owner_labeling_protocol_v1":
            raise ValueError("V1.13J expects the board-level owner labeling protocol to be frozen first.")

        world_model_layers = [
            {
                "layer_name": "objects",
                "purpose": "Define the reusable board-level entities that appear across themes.",
                "examples": [
                    "theme board",
                    "phase family",
                    "role family",
                    "driver family",
                    "noise family",
                    "risk surface",
                ],
            },
            {
                "layer_name": "relations",
                "purpose": "Encode who leads, who follows, who merely maps, and which links are dangerous or weak.",
                "examples": [
                    "leader_to_core relation",
                    "core_to_sidecar relation",
                    "board_to_spillover relation",
                    "driver_to_resonance relation",
                    "false_extension relation",
                ],
            },
            {
                "layer_name": "transitions",
                "purpose": "Teach how board states and internal roles evolve over time instead of teaching static labels as answers.",
                "examples": [
                    "ignition_to_markup",
                    "markup_to_diffusion",
                    "diffusion_to_decay",
                    "eligibility_to_de_risk",
                    "continue_to_holding_veto",
                    "admission_miss_to_wakeup_window",
                ],
            },
            {
                "layer_name": "constraints",
                "purpose": "Freeze impossible or dangerous co-existence patterns so the model learns boundaries, not just opportunities.",
                "examples": [
                    "high_saturation_plus_weak_resonance_is_dangerous",
                    "false_mainline_cannot_be_taught_as_true_board_eligibility",
                    "diagnostic_cluster_outputs_cannot_directly_trigger_execution",
                    "review_only_labels_cannot_override_owner_board_truth",
                ],
            },
        ]

        teaching_boundary_rows = [
            {
                "boundary_name": "no_answer_injection",
                "reading": "Board research is taught as state, relation, transition, and constraint priors rather than direct buy/sell answers.",
            },
            {
                "boundary_name": "owner_truth_boundary",
                "reading": "Owner board-level labels remain the top-level truth; world-model teaching may organize them but may not silently replace them.",
            },
            {
                "boundary_name": "execution_boundary",
                "reading": "World-model knowledge enters execution only through priors, eligibility context, and trigger semantics, not through forced hindsight conclusions.",
            },
            {
                "boundary_name": "generalization_boundary",
                "reading": "The protocol exists to promote generalization by teaching mechanisms and transitions instead of single-cycle answers.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113j_board_research_world_model_protocol_v1",
            "world_model_teaching_approved": world_model_teaching_approved,
            "layer_count": len(world_model_layers),
            "teaching_mode": "teach_mechanism_not_answer",
            "recommended_next_posture": "map_existing_board_research_assets_into_objects_relations_transitions_constraints_tables",
        }
        interpretation = [
            "V1.13J formalizes how early broad board research can enter the system without hard-coding hindsight answers.",
            "The protocol teaches a world model made of objects, relations, transitions, and constraints so later models can generalize rather than memorize.",
            "This turns broad board research into an upstream prior layer for training and execution instead of a direct signal layer.",
        ]
        return V113JBoardResearchWorldModelProtocolReport(
            summary=summary,
            world_model_layers=world_model_layers,
            teaching_boundary_rows=teaching_boundary_rows,
            interpretation=interpretation,
        )


def write_v113j_board_research_world_model_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113JBoardResearchWorldModelProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
