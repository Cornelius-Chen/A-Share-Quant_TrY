from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113QCPOTrainingMaterialReadinessAuditReport:
    summary: dict[str, Any]
    checks: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "checks": self.checks,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _is_sorted_by(rows: list[dict[str, Any]], *keys: str) -> bool:
    ordered = [
        tuple(str(row[key]) for key in keys)
        for row in rows
    ]
    return ordered == sorted(ordered)


class V113QCPOTrainingMaterialReadinessAuditAnalyzer:
    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113p_payload: dict[str, Any],
    ) -> V113QCPOTrainingMaterialReadinessAuditReport:
        n_summary = dict(v113n_payload.get("summary", {}))
        p_summary = dict(v113p_payload.get("summary", {}))
        if str(n_summary.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.13Q expects V1.13N real episode population.")
        if str(p_summary.get("acceptance_posture")) != "freeze_v113p_cpo_full_board_coverage_and_t1_audit_v1":
            raise ValueError("V1.13Q expects V1.13P coverage audit.")

        board_episode_rows = list(v113n_payload.get("board_episode_rows", []))
        internal_point_rows = list(v113n_payload.get("internal_point_rows", []))
        world_model_prior_rows = list(v113n_payload.get("world_model_prior_rows", []))

        checks = [
            {
                "check_name": "board_episode_rows_time_sorted",
                "passed": _is_sorted_by(board_episode_rows, "trade_date", "board_phase_label_owner", "episode_id"),
            },
            {
                "check_name": "internal_point_rows_time_sorted",
                "passed": _is_sorted_by(internal_point_rows, "trade_date", "object_id", "control_label_assistant"),
            },
            {
                "check_name": "world_model_prior_rows_time_sorted",
                "passed": _is_sorted_by(world_model_prior_rows, "trade_date", "object_id", "world_model_prior_id"),
            },
            {
                "check_name": "full_board_symbol_market_feed_complete",
                "passed": bool(p_summary.get("full_board_content_complete_now", False)),
            },
            {
                "check_name": "full_board_action_replay_ready",
                "passed": bool(p_summary.get("full_board_action_replay_ready_now", False)),
            },
            {
                "check_name": "t_plus_one_enabled",
                "passed": bool(p_summary.get("t_plus_one_enabled_in_execution_layer", False)),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v113q_cpo_training_material_readiness_audit_v1",
            "board_name": "CPO",
            "time_order_ready": all(check["passed"] for check in checks[:3]),
            "full_board_information_complete": bool(p_summary.get("full_board_content_complete_now", False)),
            "full_board_training_ready_now": bool(p_summary.get("full_board_action_replay_ready_now", False)),
            "subset_training_ready_now": all(check["passed"] for check in checks[:3]),
            "t_plus_one_enabled": bool(p_summary.get("t_plus_one_enabled_in_execution_layer", False)),
            "recommended_next_posture": "do_not_claim_full_board_training_readiness_until_missing_cpo_symbol_market_feeds_and_internal_labels_are_completed",
        }
        interpretation = [
            "V1.13Q separates time-order readiness from full-board completeness so the project does not confuse a lawful subset seed with a complete board-level training corpus.",
            "Current CPO seed tables can support ordered subset training and replay, but they still do not satisfy full-board completeness.",
            "T+1 is now enabled, but that only hardens execution legality; it does not by itself complete the missing board-wide market feeds and labels.",
        ]
        return V113QCPOTrainingMaterialReadinessAuditReport(
            summary=summary,
            checks=checks,
            interpretation=interpretation,
        )


def write_v113q_cpo_training_material_readiness_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113QCPOTrainingMaterialReadinessAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
