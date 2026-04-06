from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareFeatureFoundationV1:
    summary: dict[str, Any]
    feature_registry_rows: list[dict[str, Any]]
    feature_surface_rows: list[dict[str, Any]]
    representation_backlog_rows: list[dict[str, Any]]


class MaterializeAShareFeatureFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.identity_path = repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        self.taxonomy_concept_path = repo_root / "data" / "reference" / "info_center" / "taxonomy" / "a_share_concept_membership_v1.csv"
        self.taxonomy_sector_path = repo_root / "data" / "reference" / "info_center" / "taxonomy" / "a_share_sector_membership_v1.csv"
        self.attention_path = repo_root / "data" / "reference" / "info_center" / "attention_registry" / "a_share_attention_registry_v1.csv"
        self.event_quality_path = repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_event_quality_registry_v1.csv"
        self.source_quality_path = repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_source_quality_registry_v1.csv"
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "feature_registry"
        self.feature_registry_path = self.output_dir / "a_share_feature_registry_v1.csv"
        self.feature_surface_path = self.output_dir / "a_share_feature_surface_v1.csv"
        self.representation_backlog_path = self.output_dir / "a_share_representation_feature_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_feature_foundation_manifest_v1.json"

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def materialize(self) -> MaterializedAShareFeatureFoundationV1:
        identity_rows = self._read_csv(self.identity_path)
        concept_rows = self._read_csv(self.taxonomy_concept_path)
        sector_rows = self._read_csv(self.taxonomy_sector_path)
        attention_rows = self._read_csv(self.attention_path)
        event_quality_rows = self._read_csv(self.event_quality_path)
        source_quality_rows = self._read_csv(self.source_quality_path)

        feature_registry_rows = [
            {"feature_id": "F_symbol_concept_membership_count", "feature_group": "symbolic", "target_type": "symbol", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_symbol_sector_membership_count", "feature_group": "symbolic", "target_type": "symbol", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_symbol_has_attention_case", "feature_group": "symbolic", "target_type": "symbol", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_symbol_attention_hard_role_flag", "feature_group": "symbolic", "target_type": "symbol", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_symbol_attention_soft_role_flag", "feature_group": "symbolic", "target_type": "symbol", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_event_source_authority_score", "feature_group": "statistical", "target_type": "event", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_event_bootstrap_evidence_gate", "feature_group": "statistical", "target_type": "event", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_event_timestamp_quality_band", "feature_group": "symbolic", "target_type": "event", "point_in_time_legal": "true", "registry_status": "defined"},
            {"feature_id": "F_repr_event_semantic_embedding", "feature_group": "representation", "target_type": "event", "point_in_time_legal": "deferred", "registry_status": "backlog_only"},
        ]

        concept_count = Counter(row["symbol"] for row in concept_rows)
        sector_count = Counter(row["symbol"] for row in sector_rows)
        attention_by_symbol = {row["symbol"]: row for row in attention_rows}

        feature_surface_rows: list[dict[str, Any]] = []
        for row in identity_rows:
            attention_row = attention_by_symbol.get(row["symbol"])
            feature_surface_rows.append(
                {
                    "target_type": "symbol",
                    "target_id": row["symbol"],
                    "feature_id": "F_symbol_concept_membership_count",
                    "feature_value": concept_count.get(row["symbol"], 0),
                }
            )
            feature_surface_rows.append(
                {
                    "target_type": "symbol",
                    "target_id": row["symbol"],
                    "feature_id": "F_symbol_sector_membership_count",
                    "feature_value": sector_count.get(row["symbol"], 0),
                }
            )
            feature_surface_rows.append(
                {
                    "target_type": "symbol",
                    "target_id": row["symbol"],
                    "feature_id": "F_symbol_has_attention_case",
                    "feature_value": int(attention_row is not None),
                }
            )
            feature_surface_rows.append(
                {
                    "target_type": "symbol",
                    "target_id": row["symbol"],
                    "feature_id": "F_symbol_attention_hard_role_flag",
                    "feature_value": int(attention_row is not None and attention_row["candidate_status"] == "hard_retained"),
                }
            )
            feature_surface_rows.append(
                {
                    "target_type": "symbol",
                    "target_id": row["symbol"],
                    "feature_id": "F_symbol_attention_soft_role_flag",
                    "feature_value": int(attention_row is not None and attention_row["candidate_status"] != "hard_retained"),
                }
            )

        source_quality_map = {row["source_id"]: row for row in source_quality_rows}
        for row in event_quality_rows:
            source_row = source_quality_map.get(row["source_id"], {})
            feature_surface_rows.append(
                {
                    "target_type": "event",
                    "target_id": row["event_id"],
                    "feature_id": "F_event_source_authority_score",
                    "feature_value": source_row.get("authority_score", ""),
                }
            )
            feature_surface_rows.append(
                {
                    "target_type": "event",
                    "target_id": row["event_id"],
                    "feature_id": "F_event_bootstrap_evidence_gate",
                    "feature_value": int(row["bootstrap_evidence_gate"] == "True" or row["bootstrap_evidence_gate"] is True),
                }
            )
            feature_surface_rows.append(
                {
                    "target_type": "event",
                    "target_id": row["event_id"],
                    "feature_id": "F_event_timestamp_quality_band",
                    "feature_value": row["timestamp_quality_band"],
                }
            )

        representation_backlog_rows = [
            {
                "feature_id": "F_repr_event_semantic_embedding",
                "backlog_reason": "representation_features_should_wait_until_symbolic_and_statistical_layers_stabilize",
            }
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)
        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.feature_registry_path, feature_registry_rows)
        _write(self.feature_surface_path, feature_surface_rows)
        _write(self.representation_backlog_path, representation_backlog_rows)

        summary = {
            "feature_registry_count": len(feature_registry_rows),
            "feature_surface_row_count": len(feature_surface_rows),
            "representation_backlog_count": len(representation_backlog_rows),
            "feature_registry_path": str(self.feature_registry_path.relative_to(self.repo_root)),
            "feature_surface_path": str(self.feature_surface_path.relative_to(self.repo_root)),
            "representation_backlog_path": str(self.representation_backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareFeatureFoundationV1(
            summary=summary,
            feature_registry_rows=feature_registry_rows,
            feature_surface_rows=feature_surface_rows,
            representation_backlog_rows=representation_backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareFeatureFoundationV1(repo_root).materialize()
    print(result.summary["feature_registry_path"])


if __name__ == "__main__":
    main()
