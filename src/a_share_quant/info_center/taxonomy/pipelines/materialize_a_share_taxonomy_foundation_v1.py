from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.identity.pipelines.materialize_a_share_identity_foundation_v1 import (
    _source_priority,
)


@dataclass(slots=True)
class MaterializedAShareTaxonomyFoundationV1:
    summary: dict[str, Any]
    concept_rows: list[dict[str, Any]]
    sector_rows: list[dict[str, Any]]
    business_reference_backlog_rows: list[dict[str, Any]]
    concept_purity_backlog_rows: list[dict[str, Any]]


class MaterializeAShareTaxonomyFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.identity_path = repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        self.concept_input_dir = repo_root / "data" / "reference" / "concept_mapping_daily"
        self.sector_input_dir = repo_root / "data" / "reference" / "sector_mapping_daily"
        self.taxonomy_dir = repo_root / "data" / "reference" / "info_center" / "taxonomy"
        self.business_reference_dir = repo_root / "data" / "reference" / "info_center" / "business_reference"
        self.concept_purity_dir = repo_root / "data" / "reference" / "info_center" / "concept_purity"
        self.concept_output = self.taxonomy_dir / "a_share_concept_membership_v1.csv"
        self.sector_output = self.taxonomy_dir / "a_share_sector_membership_v1.csv"
        self.business_reference_backlog_output = self.business_reference_dir / "a_share_business_reference_backlog_v1.csv"
        self.concept_purity_backlog_output = self.concept_purity_dir / "a_share_concept_purity_backlog_v1.csv"
        self.manifest_output = self.taxonomy_dir / "a_share_taxonomy_foundation_manifest_v1.json"

    def _load_identity_symbols(self) -> list[dict[str, str]]:
        with self.identity_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _materialize_mapping(
        self,
        *,
        input_dir: Path,
        key_fields: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        identity_rows = self._load_identity_symbols()
        identity_symbols = {row["symbol"] for row in identity_rows}
        best_by_key: dict[tuple[str, ...], dict[str, Any]] = {}

        for path in sorted(input_dir.glob("*.csv")):
            priority = _source_priority(path.name)
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    symbol = row.get("symbol", "")
                    if symbol not in identity_symbols:
                        continue
                    materialized = {
                        **row,
                        "source_file": path.name,
                        "source_priority": priority,
                    }
                    key = tuple(materialized[field] for field in key_fields)
                    current = best_by_key.get(key)
                    if current is None or (
                        materialized["source_priority"],
                        materialized["mapping_version"],
                        materialized["source_file"],
                    ) > (
                        current["source_priority"],
                        current["mapping_version"],
                        current["source_file"],
                    ):
                        best_by_key[key] = materialized
        return [best_by_key[key] for key in sorted(best_by_key)]

    def materialize(self) -> MaterializedAShareTaxonomyFoundationV1:
        identity_rows = self._load_identity_symbols()
        concept_rows = self._materialize_mapping(
            input_dir=self.concept_input_dir,
            key_fields=("trade_date", "symbol", "concept_id", "concept_name"),
        )
        sector_rows = self._materialize_mapping(
            input_dir=self.sector_input_dir,
            key_fields=("trade_date", "symbol", "sector_id", "sector_name"),
        )

        concept_symbol_counts: dict[str, int] = {}
        sector_symbol_counts: dict[str, int] = {}
        for row in concept_rows:
            concept_symbol_counts[row["symbol"]] = concept_symbol_counts.get(row["symbol"], 0) + 1
        for row in sector_rows:
            sector_symbol_counts[row["symbol"]] = sector_symbol_counts.get(row["symbol"], 0) + 1

        business_reference_backlog_rows = [
            {
                "symbol": row["symbol"],
                "name": row["name"],
                "backlog_status": "pending_business_reference_fill",
                "concept_row_count": concept_symbol_counts.get(row["symbol"], 0),
                "sector_row_count": sector_symbol_counts.get(row["symbol"], 0),
            }
            for row in identity_rows
        ]
        concept_purity_backlog_rows = [
            {
                "symbol": row["symbol"],
                "name": row["name"],
                "backlog_status": "pending_concept_purity_assessment",
                "concept_row_count": concept_symbol_counts.get(row["symbol"], 0),
                "sector_row_count": sector_symbol_counts.get(row["symbol"], 0),
            }
            for row in identity_rows
        ]

        self.taxonomy_dir.mkdir(parents=True, exist_ok=True)
        self.business_reference_dir.mkdir(parents=True, exist_ok=True)
        self.concept_purity_dir.mkdir(parents=True, exist_ok=True)

        with self.concept_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(concept_rows[0].keys()))
            writer.writeheader()
            writer.writerows(concept_rows)
        with self.sector_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(sector_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sector_rows)
        with self.business_reference_backlog_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(business_reference_backlog_rows[0].keys()))
            writer.writeheader()
            writer.writerows(business_reference_backlog_rows)
        with self.concept_purity_backlog_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(concept_purity_backlog_rows[0].keys()))
            writer.writeheader()
            writer.writerows(concept_purity_backlog_rows)

        summary = {
            "identity_symbol_count": len(identity_rows),
            "concept_membership_row_count": len(concept_rows),
            "sector_membership_row_count": len(sector_rows),
            "concept_covered_symbol_count": len(concept_symbol_counts),
            "sector_covered_symbol_count": len(sector_symbol_counts),
            "business_reference_backlog_count": len(business_reference_backlog_rows),
            "concept_purity_backlog_count": len(concept_purity_backlog_rows),
            "concept_output_path": str(self.concept_output.relative_to(self.repo_root)),
            "sector_output_path": str(self.sector_output.relative_to(self.repo_root)),
            "business_reference_backlog_path": str(self.business_reference_backlog_output.relative_to(self.repo_root)),
            "concept_purity_backlog_path": str(self.concept_purity_backlog_output.relative_to(self.repo_root)),
        }
        self.manifest_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareTaxonomyFoundationV1(
            summary=summary,
            concept_rows=concept_rows,
            sector_rows=sector_rows,
            business_reference_backlog_rows=business_reference_backlog_rows,
            concept_purity_backlog_rows=concept_purity_backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeAShareTaxonomyFoundationV1(repo_root).materialize()
    print(result.summary["concept_output_path"])
    print(result.summary["sector_output_path"])


if __name__ == "__main__":
    main()
