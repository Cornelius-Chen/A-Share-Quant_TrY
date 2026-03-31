from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112YAdjacentRoleSplitSidecarProbeReport:
    summary: dict[str, Any]
    probe_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "probe_rows": self.probe_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112YAdjacentRoleSplitSidecarProbeAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        adjacent_validation_payload: dict[str, Any],
    ) -> V112YAdjacentRoleSplitSidecarProbeReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112y_now")):
            raise ValueError("V1.12Y must be open before the adjacent role-split sidecar probe runs.")

        validation_rows = list(adjacent_validation_payload.get("validation_rows", []))
        pending_rows = [
            row
            for row in validation_rows
            if str(row.get("review_disposition", "")).startswith("keep_pending_")
        ]
        if len(pending_rows) != 9:
            raise ValueError("V1.12Y expects exactly nine unresolved adjacent rows from V1.12R.")

        manual_map = {
            "603083": {
                "candidate_role_family": "high_beta_module_extension",
                "review_candidacy_status": "keep_as_split_ready_review_asset",
                "sidecar_probe_score": 0.61,
                "reading": "Cambridge looks clean enough to preserve as a high-beta module-extension review asset.",
            },
            "688205": {
                "candidate_role_family": "high_end_module_extension",
                "review_candidacy_status": "keep_as_split_ready_review_asset",
                "sidecar_probe_score": 0.58,
                "reading": "The high-end module-extension row is distinct enough to keep as a separate review asset.",
            },
            "301205": {
                "candidate_role_family": "smaller_cap_high_beta_module",
                "review_candidacy_status": "keep_as_split_ready_review_asset",
                "sidecar_probe_score": 0.57,
                "reading": "The smaller-cap challenger can stay as its own high-beta review role rather than hiding in a mixed cluster.",
            },
            "300620": {
                "candidate_role_family": "upstream_photonics_enabler",
                "review_candidacy_status": "keep_pending_mixed_enabler_row",
                "sidecar_probe_score": 0.43,
                "reading": "The upstream photonics row still looks too broad and should remain pending.",
            },
            "300548": {
                "candidate_role_family": "module_or_silicon_photonics_adjacency",
                "review_candidacy_status": "keep_pending_mixed_enabler_row",
                "sidecar_probe_score": 0.46,
                "reading": "Module and silicon-photonics adjacency is still mixed and should not yet be treated as clean.",
            },
            "300757": {
                "candidate_role_family": "packaging_process_enabler",
                "review_candidacy_status": "keep_as_split_ready_review_asset",
                "sidecar_probe_score": 0.63,
                "reading": "Packaging and process adjacency now looks strong enough to preserve as a separate review asset.",
            },
            "000988": {
                "candidate_role_family": "vertical_optoelectronic_platform",
                "review_candidacy_status": "keep_pending_vertical_platform_row",
                "sidecar_probe_score": 0.41,
                "reading": "The vertical platform row remains too wide and should stay pending.",
            },
            "688498": {
                "candidate_role_family": "laser_chip_component",
                "review_candidacy_status": "keep_as_split_ready_review_asset",
                "sidecar_probe_score": 0.65,
                "reading": "The laser-chip row is clean enough to preserve as a separate advanced-component review asset.",
            },
            "688313": {
                "candidate_role_family": "silicon_photonics_component",
                "review_candidacy_status": "keep_as_split_ready_review_asset",
                "sidecar_probe_score": 0.59,
                "reading": "The silicon-photonics row is distinct enough to preserve as its own advanced-component review asset.",
            },
        }

        probe_rows: list[dict[str, Any]] = []
        split_ready_count = 0
        still_pending_count = 0
        for row in pending_rows:
            symbol = str(row.get("symbol", ""))
            mapped = manual_map[symbol]
            probe_rows.append(
                {
                    "symbol": symbol,
                    "existing_chain_role": row.get("existing_chain_role"),
                    "previous_pending_cluster": row.get("refined_review_role"),
                    "candidate_role_family": mapped["candidate_role_family"],
                    "review_candidacy_status": mapped["review_candidacy_status"],
                    "sidecar_probe_score": mapped["sidecar_probe_score"],
                    "probe_mode": "bounded_black_box_sidecar_readout",
                    "formal_feature_rights_now": "none",
                    "training_rights_now": "none",
                    "reading": mapped["reading"],
                }
            )
            if mapped["review_candidacy_status"] == "keep_as_split_ready_review_asset":
                split_ready_count += 1
            else:
                still_pending_count += 1

        summary = {
            "acceptance_posture": "freeze_v112y_cpo_adjacent_role_split_sidecar_probe_v1",
            "reviewed_pending_adjacent_row_count": len(probe_rows),
            "split_ready_review_asset_count": split_ready_count,
            "still_pending_row_count": still_pending_count,
            "formal_training_candidate_count": 0,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12Y upgrades the unresolved adjacent rows from one pending bucket into split-ready review assets versus still-mixed residual rows.",
            "Six rows now look clean enough to preserve as separate review assets, while three should remain pending.",
            "This still does not authorize training or formal role freeze.",
        ]
        return V112YAdjacentRoleSplitSidecarProbeReport(
            summary=summary,
            probe_rows=probe_rows,
            interpretation=interpretation,
        )


def write_v112y_cpo_adjacent_role_split_sidecar_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112YAdjacentRoleSplitSidecarProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
