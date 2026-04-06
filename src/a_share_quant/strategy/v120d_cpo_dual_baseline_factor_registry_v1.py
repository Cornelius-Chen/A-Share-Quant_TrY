from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report


@dataclass(slots=True)
class CpoDualBaselineFactorRegistryReport:
    summary: dict[str, Any]
    baseline_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "baseline_rows": self.baseline_rows,
            "interpretation": self.interpretation,
        }


class CpoDualBaselineFactorRegistryAnalyzer:
    """Freeze authoritative vs research-test baseline factor membership for CPO."""

    def analyze(
        self,
        *,
        repaired_replay_payload: dict[str, Any],
        cooling_triage_payload: dict[str, Any],
        sustained_triage_payload: dict[str, Any],
        elg_triage_payload: dict[str, Any],
        cooled_retention_payload: dict[str, Any],
        breakout_soft_payload: dict[str, Any],
    ) -> CpoDualBaselineFactorRegistryReport:
        baseline_rows = [
            {
                "baseline_name": "authoritative_baseline",
                "component_name": "repaired_cpo_execution_baseline",
                "component_class": "hard_mainline",
                "status": "active",
                "usage_mode": "full_board_replay_and_primary_performance_reference",
                "replay_facing_allowed": True,
                "shadow_replay_allowed": True,
                "mainline_allowed": True,
                "source_report": "v114t_cpo_replay_integrity_repair_v1.json",
                "key_reading": "唯一 authoritative CPO 全板块真实口径回测主线。",
            },
            {
                "baseline_name": "research_test_baseline",
                "component_name": "cooling_reacceleration_branch",
                "component_class": "candidate_only",
                "status": cooling_triage_payload["summary"]["cooling_reacceleration_branch_status"],
                "usage_mode": "soft_candidate_gate_or_shadow_add_research_only",
                "replay_facing_allowed": False,
                "shadow_replay_allowed": False,
                "mainline_allowed": False,
                "source_report": "v117z_cpo_wxy_three_run_adversarial_triage_v1.json",
                "key_reading": "保留候选，不准直接进主线或 replay-facing 扩张。",
            },
            {
                "baseline_name": "research_test_baseline",
                "component_name": "sustained_participation_non_chase_score_candidate",
                "component_class": "candidate_only",
                "status": sustained_triage_payload["summary"]["branch_status"],
                "usage_mode": "soft_candidate_gate_or_shadow_add_research_only",
                "replay_facing_allowed": False,
                "shadow_replay_allowed": False,
                "mainline_allowed": False,
                "source_report": "v118w_cpo_tuv_three_run_adversarial_triage_v1.json",
                "key_reading": "仍有信号，但时间切分不稳，只能研究保留。",
            },
            {
                "baseline_name": "research_test_baseline",
                "component_name": "participation_turnover_elg_support_score_candidate",
                "component_class": "candidate_only",
                "status": elg_triage_payload["summary"]["branch_status"],
                "usage_mode": "soft_candidate_gate_or_shadow_add_research_only",
                "replay_facing_allowed": False,
                "shadow_replay_allowed": False,
                "mainline_allowed": False,
                "source_report": "v119s_cpo_pqr_three_run_adversarial_triage_v1.json",
                "key_reading": "接近 hard candidate，但卡在 symbol/role entanglement 和 close leakage。",
            },
            {
                "baseline_name": "research_test_baseline",
                "component_name": str(cooled_retention_payload["summary"]["retained_variant_name"]),
                "component_class": "narrow_candidate_reference",
                "status": cooled_retention_payload["summary"]["candidate_posture"],
                "usage_mode": "quality_side_reference_only",
                "replay_facing_allowed": False,
                "shadow_replay_allowed": False,
                "mainline_allowed": False,
                "source_report": "v117a_cpo_quality_side_cooled_retention_v1.json",
                "key_reading": "窄参考线，当前主要是 PC1 驱动。",
            },
            {
                "baseline_name": "research_test_baseline",
                "component_name": "breakout_damage_soft_component",
                "component_class": "soft_expectancy_component",
                "status": breakout_soft_payload["summary"]["breakout_damage_soft_component_status"],
                "usage_mode": "soft_penalty_or_correction_reference_only",
                "replay_facing_allowed": False,
                "shadow_replay_allowed": False,
                "mainline_allowed": False,
                "source_report": "v118n_cpo_klm_soft_component_triage_v1.json",
                "key_reading": "允许保留为高期望软组件，不再争硬规则地位。",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v120d_cpo_dual_baseline_factor_registry_v1",
            "board_name": repaired_replay_payload["summary"]["board_name"],
            "authoritative_baseline_count": len([row for row in baseline_rows if row["baseline_name"] == "authoritative_baseline"]),
            "research_test_baseline_component_count": len([row for row in baseline_rows if row["baseline_name"] == "research_test_baseline"]),
            "candidate_only_count": len([row for row in baseline_rows if row["component_class"] == "candidate_only"]),
            "soft_expectancy_component_count": len([row for row in baseline_rows if row["component_class"] == "soft_expectancy_component"]),
            "authoritative_replay_stays_single": True,
            "research_test_baseline_replay_facing_disabled": True,
            "recommended_next_posture": "retain_non_dead_branches_inside_research_test_baseline_without_pretending_they_are_mainline_rules",
        }
        interpretation = [
            "Not-hard-enough branches should not be thrown away automatically; they should be retained in a research test baseline when expectancy value still exists.",
            "The authoritative baseline remains singular so performance reporting stays honest and comparable.",
            "The research test baseline is a retention layer, not a license to smuggle candidate-only branches into replay-facing production logic.",
        ]
        return CpoDualBaselineFactorRegistryReport(
            summary=summary,
            baseline_rows=baseline_rows,
            interpretation=interpretation,
        )


def write_cpo_dual_baseline_factor_registry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CpoDualBaselineFactorRegistryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_cpo_dual_baseline_factor_registry_csv(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "baseline_name",
        "component_name",
        "component_class",
        "status",
        "usage_mode",
        "replay_facing_allowed",
        "shadow_replay_allowed",
        "mainline_allowed",
        "source_report",
        "key_reading",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def load_required_payloads(repo_root: Path) -> dict[str, Any]:
    return {
        "repaired_replay_payload": load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        "cooling_triage_payload": load_json_report(repo_root / "reports/analysis/v117z_cpo_wxy_three_run_adversarial_triage_v1.json"),
        "sustained_triage_payload": load_json_report(repo_root / "reports/analysis/v118w_cpo_tuv_three_run_adversarial_triage_v1.json"),
        "elg_triage_payload": load_json_report(repo_root / "reports/analysis/v119s_cpo_pqr_three_run_adversarial_triage_v1.json"),
        "cooled_retention_payload": load_json_report(repo_root / "reports/analysis/v117a_cpo_quality_side_cooled_retention_v1.json"),
        "breakout_soft_payload": load_json_report(repo_root / "reports/analysis/v118n_cpo_klm_soft_component_triage_v1.json"),
    }
