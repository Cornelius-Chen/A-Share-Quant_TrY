from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CWPackagingMainlineExtensionStatusFreezeReport:
    summary: dict[str, Any]
    stack_rows: list[dict[str, Any]]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stack_rows": self.stack_rows,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CWPackagingMainlineExtensionStatusFreezeAnalyzer:
    def analyze(
        self,
        *,
        ch_payload: dict[str, Any],
        cs_payload: dict[str, Any],
        cv_payload: dict[str, Any],
    ) -> V112CWPackagingMainlineExtensionStatusFreezeReport:
        ch_summary = dict(ch_payload.get("summary", {}))
        cs_rows = list(cs_payload.get("stack_rows", []))
        cv_summary = dict(cv_payload.get("summary", {}))

        inherited_rows = []
        for row in cs_rows:
            if str(row.get("stack_item")) in {
                "300308_core_module_leader",
                "300502_high_beta_core_module",
                "laser_chip_component",
            }:
                inherited_rows.append(row)

        summary = {
            "acceptance_posture": "freeze_v112cw_packaging_mainline_extension_status_freeze_v1",
            "mainline_template_asset_count": 1,
            "mainline_extension_count": 1,
            "core_residual_candidate_count": 1,
            "core_residual_sidecar_count": 1,
            "eligibility_only_member_count": 1,
            "joint_promotion_ready": False,
            "recommended_next_posture": "treat_packaging_template_plus_packaging_admission_as_frozen_mainline_surface_and_keep_core_residual_stack_separate",
        }
        stack_rows = [
            {
                "stack_item": "packaging_process_enabler",
                "status": "cluster_mainline_template_asset",
                "control_language": ["entry_veto", "de_risk", "eligibility"],
                "evidence": {
                    "path_total_return": ch_summary.get("cd_total_return"),
                    "path_max_drawdown": ch_summary.get("cd_max_drawdown"),
                    "validation_accuracy": ch_summary.get("cf_validation_accuracy"),
                },
            },
            {
                "stack_item": "packaging_admission_extension",
                "status": "controlled_mainline_extension",
                "control_language": ["full_20d_admission"],
                "evidence": {
                    "replayed_total_return": cv_summary.get("replayed_total_return"),
                    "replayed_max_drawdown": cv_summary.get("replayed_max_drawdown"),
                    "return_delta_vs_neutral": cv_summary.get("return_delta_vs_neutral"),
                    "drawdown_delta_vs_neutral": cv_summary.get("drawdown_delta_vs_neutral"),
                    "displaced_neutral_trade_count": cv_summary.get("displaced_neutral_trade_count"),
                },
            },
            *inherited_rows,
        ]
        boundary_rows = [
            {
                "boundary_name": "mainline_surface_boundary",
                "reading": "Packaging now owns both the frozen refined template asset and a controlled admission extension; these form the packaging mainline surface.",
            },
            {
                "boundary_name": "template_learning_boundary",
                "reading": "The admission extension does not reopen packaging template learning and must remain a governed replay object.",
            },
            {
                "boundary_name": "core_residual_stack_boundary",
                "reading": "300308 and 300502 remain outside packaging's mainline surface. Joint core residual promotion stays deferred.",
                "joint_promotion_ready": False,
            },
        ]
        interpretation = [
            "V1.12CW freezes packaging's mainline status into a two-part governed surface: the refined template asset plus the controlled admission extension.",
            "This freeze keeps packaging strong while preserving separation from the unresolved 300308/300502 core residual stack.",
        ]
        return V112CWPackagingMainlineExtensionStatusFreezeReport(
            summary=summary,
            stack_rows=stack_rows,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_v112cw_packaging_mainline_extension_status_freeze_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CWPackagingMainlineExtensionStatusFreezeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
