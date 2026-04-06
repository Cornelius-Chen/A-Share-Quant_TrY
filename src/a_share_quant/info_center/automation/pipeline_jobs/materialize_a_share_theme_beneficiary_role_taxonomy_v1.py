from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_beneficiary_role_normalizer import (
    normalize_beneficiary_role,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class MaterializedAShareThemeBeneficiaryRoleTaxonomyV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareThemeBeneficiaryRoleTaxonomyV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_beneficiary_registry_v1.csv"
        )
        self.output_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_beneficiary_role_taxonomy_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareThemeBeneficiaryRoleTaxonomyV1:
        registry_rows = _read_csv(self.registry_path)
        distinct_roles = sorted({row["beneficiary_role"] for row in registry_rows})

        rows: list[dict[str, Any]] = []
        for role in distinct_roles:
            role_rows = [row for row in registry_rows if row["beneficiary_role"] == role]
            dominant_confidence = max(
                {row.get("mapping_confidence", "medium") for row in role_rows},
                key=lambda value: {"high": 3, "medium": 2, "low": 1}.get(value, 0),
            )
            normalized_role_family, linkage_class = normalize_beneficiary_role(
                beneficiary_role=role,
                mapping_confidence=dominant_confidence,
            )
            rows.append(
                {
                    "beneficiary_role": role,
                    "normalized_role_family": normalized_role_family,
                    "dominant_mapping_confidence": dominant_confidence,
                    "linkage_class": linkage_class,
                    "example_theme_slug": role_rows[0]["theme_slug"],
                    "role_count": str(len(role_rows)),
                    "taxonomy_state": "normalized",
                }
            )

        self._write_csv(self.output_path, rows)

        summary = {
            "role_variant_count": len(rows),
            "normalized_role_family_count": len({row["normalized_role_family"] for row in rows}),
            "linkage_class_count": len({row["linkage_class"] for row in rows}),
            "authoritative_output": "a_share_theme_beneficiary_role_taxonomy_materialized",
        }
        return MaterializedAShareThemeBeneficiaryRoleTaxonomyV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareThemeBeneficiaryRoleTaxonomyV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
