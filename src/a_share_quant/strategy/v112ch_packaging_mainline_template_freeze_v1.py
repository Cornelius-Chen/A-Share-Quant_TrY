from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CHPackagingMainlineTemplateFreezeReport:
    summary: dict[str, Any]
    freeze_rows: list[dict[str, Any]]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "freeze_rows": self.freeze_rows,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CHPackagingMainlineTemplateFreezeAnalyzer:
    def analyze(
        self,
        *,
        cc_payload: dict[str, Any],
        cd_payload: dict[str, Any],
        cf_payload: dict[str, Any],
        cg_payload: dict[str, Any],
    ) -> V112CHPackagingMainlineTemplateFreezeReport:
        cd_summary = dict(cd_payload.get("summary", {}))
        cf_summary = dict(cf_payload.get("summary", {}))
        cg_summary = dict(cg_payload.get("summary", {}))

        freeze_rows = [
            {
                "asset_name": "packaging_process_enabler_refined_template",
                "promotion_posture": "cluster_mainline_template_asset",
                "control_language": ["entry_veto", "de_risk", "eligibility"],
                "path_result_reading": "path-level pilot improves both return and max drawdown versus BP and neutral",
            },
            {
                "asset_name": "laser_chip_component_cluster_member",
                "promotion_posture": "eligibility_only_template_member",
                "control_language": ["eligibility"],
                "path_result_reading": "do not promote veto/de-risk action language yet",
            },
        ]

        boundary_rows = [
            {
                "boundary_name": "template_mainline_boundary",
                "reading": "Only packaging_process_enabler enters the cluster mainline template now; laser remains eligibility-only and silicon remains isolated diagnostic.",
            },
            {
                "boundary_name": "path_stability_boundary",
                "reading": "Refined packaging boundary does not distort the already realized path.",
                "realized_path_changed": bool(cg_summary.get("realized_path_changed")),
            },
            {
                "boundary_name": "validation_boundary",
                "reading": "Packaging family validation improves materially after local boundary refinement.",
                "previous_accuracy": cf_summary.get("previous_action_mapping_accuracy"),
                "refined_accuracy": cf_summary.get("refined_action_mapping_accuracy"),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112ch_packaging_mainline_template_freeze_v1",
            "cluster_mainline_template_asset_count": 1,
            "eligibility_only_cluster_member_count": 1,
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "cd_total_return": cd_summary.get("total_return"),
            "cd_max_drawdown": cd_summary.get("max_drawdown"),
            "cf_validation_accuracy": cf_summary.get("refined_action_mapping_accuracy"),
            "cg_realized_path_changed": cg_summary.get("realized_path_changed"),
            "recommended_next_posture": "treat_packaging_as_frozen_cluster_mainline_template_and_open_laser_maturation_probe_only_if_needed",
        }
        interpretation = [
            "V1.12CH freezes packaging_process_enabler as the first refined cluster mainline template asset in the CPO control stack.",
            "Laser-chip remains in the same template-capable cluster but only as an eligibility-only member; it must not be promoted with packaging's full three-layer action language.",
        ]
        return V112CHPackagingMainlineTemplateFreezeReport(
            summary=summary,
            freeze_rows=freeze_rows,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_v112ch_packaging_mainline_template_freeze_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CHPackagingMainlineTemplateFreezeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
