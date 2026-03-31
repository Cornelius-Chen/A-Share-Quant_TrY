from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CCTemplateCapableClusterActionMappingReviewReport:
    summary: dict[str, Any]
    shared_structure_rows: list[dict[str, Any]]
    role_action_rows: list[dict[str, Any]]
    coverage_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "shared_structure_rows": self.shared_structure_rows,
            "role_action_rows": self.role_action_rows,
            "coverage_rows": self.coverage_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CCTemplateCapableClusterActionMappingReviewAnalyzer:
    def analyze(
        self,
        *,
        by_payload: dict[str, Any],
        ca_payload: dict[str, Any],
        cb_payload: dict[str, Any],
    ) -> V112CCTemplateCapableClusterActionMappingReviewReport:
        cluster_rows = list(cb_payload.get("meta_cluster_rows", []))
        template_cluster = next(
            (row for row in cluster_rows if str(row.get("archetype")) == "template_capable_cluster"),
            None,
        )
        if template_cluster is None:
            raise ValueError("V1.12CC requires a template-capable cluster from V1.12CB.")

        template_roles = set(str(role) for role in list(template_cluster.get("member_roles", [])))
        promotion_rows = {
            str(row["role_family"]): row
            for row in list(ca_payload.get("promotion_rows", []))
            if str(row["role_family"]) in template_roles
        }
        sample_rows = [
            row
            for row in list(by_payload.get("sample_rows", []))
            if str(row.get("role_family")) in template_roles
        ]
        if not promotion_rows or not sample_rows:
            raise ValueError("V1.12CC requires promotion rows and transfer samples for template-capable roles.")

        coverage_rows: list[dict[str, Any]] = []
        role_action_rows: list[dict[str, Any]] = []
        eligibility_ready_count = 0
        full_three_layer_candidate_count = 0

        for role_family in sorted(template_roles):
            role_samples = [row for row in sample_rows if str(row.get("role_family")) == role_family]
            counts = self._count_bands(role_samples)
            promotion = promotion_rows[role_family]

            coverage_rows.append(
                {
                    "role_family": role_family,
                    "sample_count": len(role_samples),
                    "veto_band_count": counts["veto_band"],
                    "de_risk_band_count": counts["de_risk_band"],
                    "eligibility_band_count": counts["eligibility_band"],
                }
            )

            if counts["veto_band"] > 0 and counts["de_risk_band"] > 0 and counts["eligibility_band"] > 0:
                action_posture = "full_three_layer_action_mapping_candidate"
                mapped_actions = ["entry_veto", "de_risk", "eligibility"]
                full_three_layer_candidate_count += 1
            elif counts["eligibility_band"] > 0 and counts["veto_band"] == 0 and counts["de_risk_band"] == 0:
                action_posture = "eligibility_only_candidate_path"
                mapped_actions = ["eligibility"]
                eligibility_ready_count += 1
            elif counts["eligibility_band"] > 0 and counts["de_risk_band"] > 0 and counts["veto_band"] == 0:
                action_posture = "eligibility_plus_de_risk_candidate_path"
                mapped_actions = ["de_risk", "eligibility"]
            else:
                action_posture = "review_only_action_mapping"
                mapped_actions = []

            role_action_rows.append(
                {
                    "role_family": role_family,
                    "promotion_posture": str(promotion.get("promotion_posture")),
                    "edge_layer_status": str(promotion.get("edge_layer_status")),
                    "band_layer_status": str(promotion.get("band_layer_status")),
                    "action_mapping_posture": action_posture,
                    "mapped_actions": mapped_actions,
                }
            )

        shared_structure_rows = [
            {
                "shared_structure_name": "shared_direction_set",
                "shared_posture": "preserve_shared_direction_backbone",
                "reading": "The template-capable cluster shares the transferred direction set even when edge calibration differs by role.",
            },
            {
                "shared_structure_name": "shared_three_band_grammar",
                "shared_posture": "preserve_veto_de_risk_eligibility_framework",
                "reading": "All template promotion must keep the three-band grammar, even if empirical coverage differs across member roles.",
            },
            {
                "shared_structure_name": "shared_action_mapping_constraint",
                "shared_posture": "allow_role_specific_edge_calibration_but_not_role_specific_action_language",
                "reading": "Action language should remain cluster-level while edge placement can remain role-specific.",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112cc_template_capable_cluster_action_mapping_review_v1",
            "template_role_count": len(template_roles),
            "eligibility_only_candidate_count": eligibility_ready_count,
            "full_three_layer_candidate_count": full_three_layer_candidate_count,
            "recommended_next_posture": "run_role_specific_action_mapping_pilot_for_packaging_and_keep_laser_as_eligibility_only_template_member",
        }
        interpretation = [
            "V1.12CC upgrades action mapping from single-role review to template-capable-cluster review.",
            "The cluster shares a common direction backbone and three-band control grammar, but empirical action coverage is asymmetric: packaging-process-enabler supports full three-layer mapping, while laser-chip currently supports eligibility-only mapping.",
        ]
        return V112CCTemplateCapableClusterActionMappingReviewReport(
            summary=summary,
            shared_structure_rows=shared_structure_rows,
            role_action_rows=role_action_rows,
            coverage_rows=coverage_rows,
            interpretation=interpretation,
        )

    def _count_bands(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        counts = {"veto_band": 0, "de_risk_band": 0, "eligibility_band": 0}
        for row in rows:
            band = str(row.get("actual_band"))
            if band in counts:
                counts[band] += 1
        return counts


def write_v112cc_template_capable_cluster_action_mapping_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CCTemplateCapableClusterActionMappingReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
