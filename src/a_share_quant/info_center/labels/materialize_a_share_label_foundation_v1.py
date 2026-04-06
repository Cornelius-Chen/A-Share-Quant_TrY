from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareLabelFoundationV1:
    summary: dict[str, Any]
    label_definition_rows: list[dict[str, Any]]
    label_assignment_rows: list[dict[str, Any]]
    state_backlog_rows: list[dict[str, Any]]
    governance_backlog_rows: list[dict[str, Any]]


class MaterializeAShareLabelFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.event_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "event_registry" / "a_share_event_registry_v1.csv"
        )
        self.attention_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "attention_registry" / "a_share_attention_registry_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "label_registry"
        self.label_registry_path = self.output_dir / "a_share_label_registry_v1.csv"
        self.label_assignment_path = self.output_dir / "a_share_label_assignment_v1.csv"
        self.state_backlog_path = self.output_dir / "a_share_state_label_backlog_v1.csv"
        self.governance_backlog_path = self.output_dir / "a_share_governance_label_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_label_foundation_manifest_v1.json"

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def materialize(self) -> MaterializedAShareLabelFoundationV1:
        event_rows = self._read_csv(self.event_registry_path)
        attention_rows = self._read_csv(self.attention_registry_path)

        label_definition_rows = [
            {"label_id": "L1_policy_release", "label_layer": "L1_fact", "label_name": "policy_release", "label_scope": "event", "registry_status": "defined"},
            {"label_id": "L1_capital_mapping", "label_layer": "L1_fact", "label_name": "capital_mapping", "label_scope": "event", "registry_status": "defined"},
            {"label_id": "L1_supply_chain_validation", "label_layer": "L1_fact", "label_name": "supply_chain_validation", "label_scope": "event", "registry_status": "defined"},
            {"label_id": "L1_turning_point_watch", "label_layer": "L1_fact", "label_name": "turning_point_watch", "label_scope": "event", "registry_status": "defined"},
            {"label_id": "L2_attention_anchor", "label_layer": "L2_semantic", "label_name": "attention_anchor", "label_scope": "symbol_attention", "registry_status": "defined"},
            {"label_id": "L2_attention_decoy", "label_layer": "L2_semantic", "label_name": "attention_decoy", "label_scope": "symbol_attention", "registry_status": "defined"},
            {"label_id": "L2_attention_carrier_candidate", "label_layer": "L2_semantic", "label_name": "attention_carrier_candidate", "label_scope": "symbol_attention", "registry_status": "defined"},
            {"label_id": "L2_non_anchor_concentration", "label_layer": "L2_semantic", "label_name": "non_anchor_concentration", "label_scope": "symbol_attention", "registry_status": "defined"},
            {"label_id": "L2_high_beta_follow_candidate", "label_layer": "L2_semantic", "label_name": "high_beta_follow_candidate", "label_scope": "symbol_attention", "registry_status": "defined"},
            {"label_id": "L3_lockout_worthy", "label_layer": "L3_state", "label_name": "lockout_worthy", "label_scope": "board_state", "registry_status": "defined_backlog_only"},
            {"label_id": "L3_false_bounce_only", "label_layer": "L3_state", "label_name": "false_bounce_only", "label_scope": "board_state", "registry_status": "defined_backlog_only"},
            {"label_id": "L3_unlock_watch", "label_layer": "L3_state", "label_name": "unlock_watch", "label_scope": "board_state", "registry_status": "defined_backlog_only"},
            {"label_id": "L3_reentry_blocked", "label_layer": "L3_state", "label_name": "reentry_blocked", "label_scope": "symbol_state", "registry_status": "defined_backlog_only"},
            {"label_id": "L4_reduce_only", "label_layer": "L4_governance", "label_name": "reduce_only", "label_scope": "governance", "registry_status": "defined_backlog_only"},
            {"label_id": "L4_shadow_consult_only", "label_layer": "L4_governance", "label_name": "shadow_consult_only", "label_scope": "governance", "registry_status": "defined_backlog_only"},
        ]

        event_scope_to_label = {
            "capital_mapping": "L1_capital_mapping",
            "supply_chain_validation": "L1_supply_chain_validation",
            "turning_point_watch": "L1_turning_point_watch",
        }
        label_assignment_rows: list[dict[str, Any]] = []
        for row in event_rows:
            label_id = event_scope_to_label.get(row["event_scope"], "L1_policy_release")
            label_assignment_rows.append(
                {
                    "assignment_id": f"{row['event_id']}::{label_id}",
                    "target_type": "event",
                    "target_id": row["event_id"],
                    "label_id": label_id,
                    "assignment_state": "bootstrap_assigned",
                }
            )

        role_map = {
            "attention_anchor_and_attention_decoy": ("L2_attention_anchor", "L2_attention_decoy"),
            "crowded_attention_carrier_candidate": ("L2_attention_carrier_candidate",),
            "crowding_only_role_candidate": ("L2_non_anchor_concentration",),
            "outlier_breakout_concentration_candidate": ("L2_non_anchor_concentration",),
            "high_beta_attention_follow_candidate": ("L2_high_beta_follow_candidate",),
        }
        for row in attention_rows:
            label_ids = role_map.get(row["attention_role"], ())
            for label_id in label_ids:
                label_assignment_rows.append(
                    {
                        "assignment_id": f"{row['symbol']}::{label_id}",
                        "target_type": "symbol_attention",
                        "target_id": row["symbol"],
                        "label_id": label_id,
                        "assignment_state": row["candidate_status"],
                    }
                )

        state_backlog_rows = [
            {
                "label_id": "L3_lockout_worthy",
                "backlog_reason": "state_assignment_should_wait_for_pti_and_board_state_surfaces",
            },
            {
                "label_id": "L3_false_bounce_only",
                "backlog_reason": "state_assignment_should_wait_for_pti_and_board_state_surfaces",
            },
            {
                "label_id": "L3_unlock_watch",
                "backlog_reason": "state_assignment_should_wait_for_pti_and_board_state_surfaces",
            },
            {
                "label_id": "L3_reentry_blocked",
                "backlog_reason": "state_assignment_should_wait_for_pti_and_symbol_state_surfaces",
            },
        ]
        governance_backlog_rows = [
            {
                "label_id": "L4_reduce_only",
                "backlog_reason": "governance_assignment_should_wait_for_pti_and replay_consumers",
            },
            {
                "label_id": "L4_shadow_consult_only",
                "backlog_reason": "governance_assignment_should_wait_for shadow_and_serving_layers",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)
        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.label_registry_path, label_definition_rows)
        _write(self.label_assignment_path, label_assignment_rows)
        _write(self.state_backlog_path, state_backlog_rows)
        _write(self.governance_backlog_path, governance_backlog_rows)

        summary = {
            "label_definition_count": len(label_definition_rows),
            "label_assignment_count": len(label_assignment_rows),
            "state_backlog_count": len(state_backlog_rows),
            "governance_backlog_count": len(governance_backlog_rows),
            "label_registry_path": str(self.label_registry_path.relative_to(self.repo_root)),
            "label_assignment_path": str(self.label_assignment_path.relative_to(self.repo_root)),
            "state_backlog_path": str(self.state_backlog_path.relative_to(self.repo_root)),
            "governance_backlog_path": str(self.governance_backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareLabelFoundationV1(
            summary=summary,
            label_definition_rows=label_definition_rows,
            label_assignment_rows=label_assignment_rows,
            state_backlog_rows=state_backlog_rows,
            governance_backlog_rows=governance_backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareLabelFoundationV1(repo_root).materialize()
    print(result.summary["label_registry_path"])


if __name__ == "__main__":
    main()
