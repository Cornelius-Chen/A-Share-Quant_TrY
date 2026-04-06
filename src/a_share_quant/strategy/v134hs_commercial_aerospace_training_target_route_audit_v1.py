from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HSCommercialAerospaceTrainingTargetRouteAuditV1Report:
    summary: dict[str, Any]
    phase_rows: list[dict[str, Any]]
    label_rows: list[dict[str, Any]]
    blocker_rows: list[dict[str, Any]]
    agent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "phase_rows": self.phase_rows,
            "label_rows": self.label_rows,
            "blocker_rows": self.blocker_rows,
            "agent_rows": self.agent_rows,
            "interpretation": self.interpretation,
        }


class V134HSCommercialAerospaceTrainingTargetRouteAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_training_target_route_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        path = self.repo_root / relative_path
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_decisive_event_summary(self) -> tuple[int, int]:
        path = (
            self.repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        total_count = 0
        retained_count = 0
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                total_count += 1
                if str(row.get("decisive_retained", "")).strip().lower() == "true":
                    retained_count += 1
        return total_count, retained_count

    def analyze(self) -> V134HSCommercialAerospaceTrainingTargetRouteAuditV1Report:
        reduce_status = self._load_json(
            "reports/analysis/v134cv_commercial_aerospace_reduce_final_status_card_v1.json"
        )
        add_status = self._load_json(
            "reports/analysis/v134gn_commercial_aerospace_add_completion_status_audit_v1.json"
        )
        boundary_policy = self._load_json(
            "reports/analysis/v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1.json"
        )
        negative_module = self._load_json(
            "reports/analysis/v134hq_commercial_aerospace_board_weak_symbol_strong_concentration_audit_v1.json"
        )
        decisive_total_count, decisive_retained_count = self._load_decisive_event_summary()

        phase_rows = [
            {
                "phase_id": 1,
                "phase_name": "negative_environment_semantics",
                "objective": "lift local negative families into environment-level semantics rather than action rules",
                "core_outputs": "attention_distorted | capital_misaligned_with_board | board_fragile_divergence",
                "evidence_anchor": "v134hq_board_weak_symbol_strong_concentration",
                "current_status": "ready_to_train",
                "promotion_boundary": "supervision_only",
            },
            {
                "phase_id": 2,
                "phase_name": "event_attention_layer",
                "objective": "separate event trigger validity from heat capture and decoy behavior",
                "core_outputs": "event_trigger_validity | attention_anchor | attention_decoy",
                "evidence_anchor": "commercial_aerospace_decisive_event_registry_v1",
                "current_status": "ready_to_train",
                "promotion_boundary": "supervision_only",
            },
            {
                "phase_id": 3,
                "phase_name": "capital_selection_layer",
                "objective": "separate true capital selection from mere heat concentration",
                "core_outputs": "capital_true_selection | followthrough_leader",
                "evidence_anchor": "named_counterexample_and_crowding_modules",
                "current_status": "deferred_until_phase_2_labels_exist",
                "promotion_boundary": "supervision_only",
            },
            {
                "phase_id": 4,
                "phase_name": "state_machine_integration",
                "objective": "bind environment and role labels into lockout/unlock/reentry/add governance",
                "core_outputs": "lockout_veto | probe_reentry_allowed | unlock_confirmed | false_reentry_risk",
                "evidence_anchor": "shadow_replay_lane_protocol_and_bridge_specs",
                "current_status": "deferred_until_phase_1_to_3_labels_exist",
                "promotion_boundary": "read_only_shadow_only",
            },
            {
                "phase_id": 5,
                "phase_name": "future_shadow_modules",
                "objective": "only after the label chain stabilizes, trial shadow-only modules for divergence and reentry",
                "core_outputs": "event_attention_divergence_shadow | reentry_unlock_shadow_module",
                "evidence_anchor": "future_only",
                "current_status": "blocked_until_explicit_future_shift",
                "promotion_boundary": "execution_blocked",
            },
        ]

        label_rows = [
            {
                "label_name": "board_weak_symbol_strong_concentration",
                "learning_priority": "already_retained_negative_module",
                "layer": "environment_seed",
                "training_status": "frozen_complete",
                "why": "strong local names inside a weak board must remain negative context rather than restart evidence",
            },
            {
                "label_name": "attention_distorted",
                "learning_priority": "learn_first",
                "layer": "environment_semantics",
                "training_status": "next_core_target",
                "why": "captures the user's core observation that heat and tradable selection can diverge",
            },
            {
                "label_name": "capital_misaligned_with_board",
                "learning_priority": "learn_first",
                "layer": "environment_semantics",
                "training_status": "next_core_target",
                "why": "formalizes weak-board / strong-symbol concentration as a money-allocation mismatch",
            },
            {
                "label_name": "board_fragile_divergence",
                "learning_priority": "learn_first",
                "layer": "environment_semantics",
                "training_status": "next_core_target",
                "why": "becomes the higher-level veto candidate above add/reentry",
            },
            {
                "label_name": "event_trigger_validity",
                "learning_priority": "learn_first",
                "layer": "event_layer",
                "training_status": "next_core_target",
                "why": "prevents news presence from being mistaken for a valid board impulse",
            },
            {
                "label_name": "attention_anchor",
                "learning_priority": "learn_first",
                "layer": "event_attention_layer",
                "training_status": "next_core_target",
                "why": "identifies who captures board attention without assuming they are the main attack target",
            },
            {
                "label_name": "attention_decoy",
                "learning_priority": "learn_first",
                "layer": "event_attention_layer",
                "training_status": "next_core_target",
                "why": "directly matches the user's hypothesis about hot names that absorb focus but do not become the real leader",
            },
            {
                "label_name": "capital_true_selection",
                "learning_priority": "learn_second",
                "layer": "capital_selection_layer",
                "training_status": "deferred_until_attention_labels_exist",
                "why": "should only be learned after attention and decoy states are separated",
            },
            {
                "label_name": "followthrough_leader",
                "learning_priority": "learn_last",
                "layer": "capital_selection_layer",
                "training_status": "deferred_until_true_selection_labels_exist",
                "why": "requires not just stock strength but evidence of durable board followthrough",
            },
            {
                "label_name": "probe_reentry_allowed",
                "learning_priority": "future_shadow_only",
                "layer": "state_machine_layer",
                "training_status": "deferred_until_environment_and_selection_labels_exist",
                "why": "should not be promoted before the environment and attention-capital chain is stable",
            },
            {
                "label_name": "unlock_confirmed",
                "learning_priority": "future_shadow_only",
                "layer": "state_machine_layer",
                "training_status": "deferred_until_explicit_boundary_extension_and_shadow_shift",
                "why": "current boundary policy and raw-only post-lockout coverage still block lawful unlock evaluation",
            },
            {
                "label_name": "manifold_learning_representation",
                "learning_priority": "optional_late_exploration",
                "layer": "representation_layer",
                "training_status": "deferred_until_label_stack_is_richer",
                "why": "representation learning is too unconstrained before the core supervision chain is labeled",
            },
        ]

        blocker_rows = [
            {
                "blocker_name": "shadow_boundary_frozen",
                "status": "active_blocker",
                "evidence": boundary_policy["summary"]["current_policy"],
                "reading": "post-lockout board-state derivation remains frozen, so unlock and reentry handoff cannot be lawfully extended",
            },
            {
                "blocker_name": "execution_authority_absent",
                "status": "active_blocker",
                "evidence": reduce_status["summary"]["execution_blocker_count"],
                "reading": "reduce execution still has four blockers and add execution authority remains blocked",
            },
            {
                "blocker_name": "add_positive_portability_failure",
                "status": "active_blocker",
                "evidence": add_status["summary"]["non_seed_positive_hit_rate"],
                "reading": "current positive add rules remain too dense outside the seed surface and cannot be used as a portable selection authority",
            },
            {
                "blocker_name": "single_slot_template_unobserved",
                "status": "active_blocker",
                "evidence": add_status["summary"]["observed_single_slot_day_count"],
                "reading": "add still lacks a naturally observed single-slot template, so later action layers must stay conservative",
            },
            {
                "blocker_name": "event_attention_capital_labels_not_yet_built",
                "status": "active_blocker",
                "evidence": decisive_retained_count,
                "reading": "event sources exist locally, but the divergence label chain has not yet been formalized into supervision registries",
            },
        ]

        agent_rows = [
            {
                "agent_name": "Schrodinger",
                "primary_recommendation": "build environment semantics before action semantics",
                "high_signal_point": "upgrade local concentration into attention_distorted -> capital_misaligned_with_board -> board_fragile_divergence",
            },
            {
                "agent_name": "Nash",
                "primary_recommendation": "reconstruct a supervision-first state machine",
                "high_signal_point": "connect event/attention/capital layers to lockout/unlock/reentry while keeping execution blocked",
            },
            {
                "agent_name": "Tesla",
                "primary_recommendation": "separate heat from true selection before learning leaders",
                "high_signal_point": "learn attention_anchor vs attention_decoy first, then capital_true_selection, and only then followthrough_leader",
            },
        ]

        flat_rows: list[dict[str, Any]] = []
        for row in phase_rows:
            flat_rows.append(
                {
                    "row_type": "phase",
                    "name": row["phase_name"],
                    "priority_or_status": row["current_status"],
                    "payload": row["core_outputs"],
                }
            )
        for row in label_rows:
            flat_rows.append(
                {
                    "row_type": "label",
                    "name": row["label_name"],
                    "priority_or_status": row["learning_priority"],
                    "payload": row["training_status"],
                }
            )
        for row in blocker_rows:
            flat_rows.append(
                {
                    "row_type": "blocker",
                    "name": row["blocker_name"],
                    "priority_or_status": row["status"],
                    "payload": row["evidence"],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat_rows[0].keys()))
            writer.writeheader()
            writer.writerows(flat_rows)

        summary = {
            "acceptance_posture": "freeze_v134hs_commercial_aerospace_training_target_route_audit_v1",
            "reduce_status": "frozen_mainline",
            "add_supervision_status": "complete_enough_but_execution_blocked",
            "negative_module_member_count": negative_module["summary"]["module_member_count"],
            "decisive_event_source_count": decisive_total_count,
            "decisive_event_retained_count": decisive_retained_count,
            "roadmap_phase_count": len(phase_rows),
            "agent_consensus_count": len(agent_rows),
            "roadmap_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the next complete training route should move from frozen local negative labels into staged event-attention-capital divergence supervision, then only later into state-machine integration and future shadow modules while execution remains blocked",
        }
        interpretation = [
            "V1.34HS is a route-setting audit rather than another local alpha search.",
            "The route is intentionally layered: first learn environment distortion and event-attention divergence, then learn true capital selection, then integrate those labels into lockout/unlock/reentry governance, and only later consider shadow modules.",
        ]
        return V134HSCommercialAerospaceTrainingTargetRouteAuditV1Report(
            summary=summary,
            phase_rows=phase_rows,
            label_rows=label_rows,
            blocker_rows=blocker_rows,
            agent_rows=agent_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HSCommercialAerospaceTrainingTargetRouteAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HSCommercialAerospaceTrainingTargetRouteAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hs_commercial_aerospace_training_target_route_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
