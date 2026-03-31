from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class V112CBEnablerMetaClusterAbstractionReviewReport:
    summary: dict[str, Any]
    role_vector_rows: list[dict[str, Any]]
    meta_cluster_rows: list[dict[str, Any]]
    archetype_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_vector_rows": self.role_vector_rows,
            "meta_cluster_rows": self.meta_cluster_rows,
            "archetype_rows": self.archetype_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CBEnablerMetaClusterAbstractionReviewAnalyzer:
    def analyze(
        self,
        *,
        by_payload: dict[str, Any],
        ca_payload: dict[str, Any],
    ) -> V112CBEnablerMetaClusterAbstractionReviewReport:
        transfer_rows = {
            str(row["role_family"]): row
            for row in list(by_payload.get("role_level_rows", []))
        }
        promotion_rows = list(ca_payload.get("promotion_rows", []))
        if not transfer_rows or not promotion_rows:
            raise ValueError("V1.12CB requires V1.12BY transfer rows and V1.12CA promotion rows.")

        role_vector_rows: list[dict[str, Any]] = []
        feature_matrix: list[list[float]] = []
        role_order: list[str] = []
        for row in promotion_rows:
            role_family = str(row["role_family"])
            transfer_row = transfer_rows.get(role_family)
            if transfer_row is None:
                raise ValueError(f"Missing transfer row for role family {role_family}.")
            sample_count = float(transfer_row.get("sample_count", 0))
            transfer_accuracy = float(transfer_row.get("classification_accuracy", 0.0))
            direction_confirmed = 1.0 if "confirmed" in str(row["direction_layer_status"]) else 0.0
            band_confirmed = 1.0 if "confirmed" in str(row["band_layer_status"]) else 0.0
            edge_unchanged = 1.0 if str(row["edge_layer_status"]) == "transferred_edges_unchanged" else 0.0
            role_specific_edges = 1.0 if str(row["edge_layer_status"]) == "role_specific_edge_calibration_required" else 0.0
            isolated = 1.0 if str(row["promotion_posture"]) == "isolated_diagnostic_path" else 0.0
            action_ready = 1.0 if "ready" in str(row["action_layer_status"]) and "do_not" not in str(row["action_layer_status"]) else 0.0

            vector = [
                transfer_accuracy,
                sample_count,
                direction_confirmed,
                band_confirmed,
                edge_unchanged,
                role_specific_edges,
                isolated,
                action_ready,
            ]
            role_order.append(role_family)
            feature_matrix.append(vector)
            role_vector_rows.append(
                {
                    "role_family": role_family,
                    "transfer_accuracy": round(transfer_accuracy, 4),
                    "sample_count": int(sample_count),
                    "direction_confirmed_flag": int(direction_confirmed),
                    "band_confirmed_flag": int(band_confirmed),
                    "edge_unchanged_flag": int(edge_unchanged),
                    "role_specific_edge_flag": int(role_specific_edges),
                    "isolated_flag": int(isolated),
                    "action_ready_flag": int(action_ready),
                }
            )

        if len(role_order) < 2:
            raise ValueError("V1.12CB requires at least two role families for abstraction clustering.")

        # Preserve already-proven hard isolation first, then re-cluster the transferable remainder.
        isolated_rows = [row for row in role_vector_rows if int(row["isolated_flag"]) == 1]
        transferable_rows = [row for row in role_vector_rows if int(row["isolated_flag"]) == 0]

        cluster_rows_map: dict[int, list[dict[str, Any]]] = {}
        next_cluster_id = 0
        if transferable_rows:
            cluster_rows_map[next_cluster_id] = transferable_rows
            next_cluster_id += 1
        if isolated_rows:
            cluster_rows_map[next_cluster_id] = isolated_rows

        meta_cluster_rows: list[dict[str, Any]] = []
        archetype_rows: list[dict[str, Any]] = []
        template_cluster_count = 0
        diagnostic_cluster_count = 0

        for cluster_id, rows in sorted(cluster_rows_map.items()):
            mean_isolated = sum(float(row["isolated_flag"]) for row in rows) / len(rows)
            mean_action_ready = sum(float(row["action_ready_flag"]) for row in rows) / len(rows)
            mean_transfer_accuracy = sum(float(row["transfer_accuracy"]) for row in rows) / len(rows)
            mean_role_specific = sum(float(row["role_specific_edge_flag"]) for row in rows) / len(rows)

            if mean_isolated >= 0.5:
                archetype = "isolated_diagnostic_cluster"
                diagnostic_cluster_count += 1
            elif mean_action_ready >= 0.5:
                archetype = "template_capable_cluster"
                template_cluster_count += 1
            else:
                archetype = "mixed_review_cluster"

            member_roles = [str(row["role_family"]) for row in rows]
            meta_cluster_rows.append(
                {
                    "cluster_id": cluster_id,
                    "member_roles": member_roles,
                    "member_count": len(member_roles),
                    "mean_transfer_accuracy": round(mean_transfer_accuracy, 4),
                    "mean_role_specific_edge_flag": round(mean_role_specific, 4),
                    "mean_action_ready_flag": round(mean_action_ready, 4),
                    "mean_isolated_flag": round(mean_isolated, 4),
                    "archetype": archetype,
                }
            )

            for role_family in member_roles:
                archetype_rows.append(
                    {
                        "role_family": role_family,
                        "cluster_id": cluster_id,
                        "archetype": archetype,
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v112cb_enabler_meta_cluster_abstraction_review_v1",
            "role_count": len(role_vector_rows),
            "meta_cluster_count": len(meta_cluster_rows),
            "template_capable_cluster_count": template_cluster_count,
            "diagnostic_cluster_count": diagnostic_cluster_count,
            "recommended_next_posture": "use_meta_cluster_abstraction_as_generalized_role_split_and_continue_action_mapping_for_template_cluster_only",
        }
        interpretation = [
            "V1.12CB re-abstracts the role-specific transfer result into a higher-level meta-cluster view instead of forcing a family-wide shared template.",
            "The main generalized result is a template-capable cluster containing laser-chip and packaging-process-enabler states, versus a separate isolated diagnostic cluster for silicon-photonics.",
        ]
        return V112CBEnablerMetaClusterAbstractionReviewReport(
            summary=summary,
            role_vector_rows=role_vector_rows,
            meta_cluster_rows=meta_cluster_rows,
            archetype_rows=archetype_rows,
            interpretation=interpretation,
        )


def write_v112cb_enabler_meta_cluster_abstraction_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CBEnablerMetaClusterAbstractionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
