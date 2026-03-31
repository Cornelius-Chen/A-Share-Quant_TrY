from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112RAdjacentCohortValidationReport:
    summary: dict[str, Any]
    validation_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "validation_rows": self.validation_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112RAdjacentCohortValidationAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        registry_payload: dict[str, Any],
        draft_batch_payload: dict[str, Any],
    ) -> V112RAdjacentCohortValidationReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112r_now")):
            raise ValueError("V1.12R must be open before adjacent cohort validation.")

        anchor_by_symbol = {
            str(row.get("symbol", "")): row
            for row in draft_batch_payload.get("adjacent_official_anchor_rows", [])
        }
        if len(anchor_by_symbol) < 10:
            raise ValueError("V1.12R expects the first official-anchor batch to be present.")

        registry_rows = {
            str(row.get("symbol", "")): row
            for row in registry_payload.get("cohort_rows", [])
        }

        plan = [
            ("002281", "validate_as_domestic_optics_platform_bridge_review_asset", "domestic_optics_platform_bridge", "Direct optics platform bridge worth preserving as a bounded adjacent review asset."),
            ("603083", "keep_pending_high_beta_extension_role_split", "high_beta_module_extension_cluster", "High-beta module-extension cluster is too broad to validate cleanly without a challenger split."),
            ("688205", "keep_pending_high_beta_extension_role_split", "high_beta_module_extension_cluster", "High-end module extension remains inside the same over-broad high-beta challenger cluster."),
            ("301205", "keep_pending_high_beta_extension_role_split", "high_beta_module_extension_cluster", "Smaller-cap high-beta module row should remain pending until the challenger hierarchy is cleaner."),
            ("300620", "keep_pending_cpo_enabler_split", "cpo_enabler_cluster", "Upstream photonics row appears useful, but still belongs to an unsplit CPO-enabler cluster."),
            ("300548", "keep_pending_cpo_enabler_split", "cpo_enabler_cluster", "Module or silicon-photonics adjacency remains too mixed for clean validation today."),
            ("300757", "keep_pending_cpo_enabler_split", "cpo_enabler_cluster", "Packaging or process adjacency should not be hidden inside a generic extension bucket."),
            ("000988", "keep_pending_vertical_platform_role_validation", "vertical_platform_pending", "Vertical optoelectronic platform role is still too wide to validate cleanly."),
            ("300570", "validate_as_connector_mpo_branch_review_asset", "connector_mpo_branch", "Connector or MPO branch row is structurally distinct enough to preserve as a review asset."),
            ("688498", "keep_pending_advanced_component_subsplit", "advanced_component_cluster", "Laser-chip adjacency should stay pending until separated from other advanced photonics rows."),
            ("688313", "keep_pending_advanced_component_subsplit", "advanced_component_cluster", "Silicon-photonics adjacency should stay pending until its sub-branch is cleaner."),
            ("601869", "validate_as_fiber_cable_extension_review_asset", "fiber_cable_extension", "Fiber and cable extension is a stable branch worth preserving for review."),
            ("600487", "validate_as_fiber_cable_extension_review_asset", "fiber_cable_extension", "Fiber and cable extension is a stable branch worth preserving for review."),
            ("600522", "validate_as_fiber_cable_extension_review_asset", "fiber_cable_extension", "Fiber and cable extension is a stable branch worth preserving for review."),
        ]

        validation_rows: list[dict[str, Any]] = []
        validated_count = 0
        pending_count = 0
        for symbol, disposition, refined_role, reading in plan:
            registry_row = registry_rows.get(symbol, {})
            anchor_row = anchor_by_symbol.get(symbol, {})
            if not registry_row:
                raise ValueError(f"Missing registry row for {symbol}.")
            validation_rows.append(
                {
                    "symbol": symbol,
                    "existing_chain_role": registry_row.get("chain_role"),
                    "anchor_type": anchor_row.get("anchor_type"),
                    "source_url": anchor_row.get("source_url"),
                    "review_disposition": disposition,
                    "refined_review_role": refined_role,
                    "reading": reading,
                }
            )
            if disposition.startswith("validate_as_"):
                validated_count += 1
            else:
                pending_count += 1

        summary = {
            "acceptance_posture": "freeze_v112r_adjacent_cohort_validation_v1",
            "reviewed_adjacent_row_count": len(validation_rows),
            "validated_review_asset_count": validated_count,
            "pending_split_or_role_validation_count": pending_count,
            "formal_training_candidate_count": 0,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12R improves the adjacent pool by separating already-usable review assets from unresolved structural clusters.",
            "Several rows are intentionally left pending because the real problem is role-coarseness, not lack of raw information.",
            "This still does not authorize training; it only improves the cleanliness of downstream review work.",
        ]
        return V112RAdjacentCohortValidationReport(
            summary=summary,
            validation_rows=validation_rows,
            interpretation=interpretation,
        )


def write_v112r_adjacent_cohort_validation_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112RAdjacentCohortValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
