from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_overlap_resolver import (
    resolve_theme_governance,
)
from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_beneficiary_role_normalizer import (
    normalize_beneficiary_role,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


def _join_top(rows: list[dict[str, Any]], key: str, limit: int = 5) -> str:
    values = [str(row.get(key, "")).strip() for row in rows[:limit]]
    return ",".join([value for value in values if value])


def _rank_theme_rows(theme_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    confidence_order = {"high": 3, "medium": 2, "low": 1}
    return sorted(
        theme_rows,
        key=lambda row: (
            confidence_order.get(row.get("mapping_confidence", "medium"), 0),
            1 if row.get("beneficiary_role", "").startswith("direct_") else 0,
            row.get("symbol", ""),
        ),
        reverse=True,
    )


@dataclass(slots=True)
class MaterializedAShareThemeSymbolRoutingDrillV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareThemeSymbolRoutingDrillV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.alias_hit_drill_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_alias_hit_drill_v1.csv"
        )
        self.beneficiary_registry_path = (
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
            / "a_share_theme_symbol_routing_drill_v1.csv"
        )

    def materialize(self) -> MaterializedAShareThemeSymbolRoutingDrillV1:
        alias_rows = _read_csv(self.alias_hit_drill_path)
        registry_rows = _read_csv(self.beneficiary_registry_path)

        theme_registry: dict[str, list[dict[str, str]]] = {}
        for row in registry_rows:
            theme_registry.setdefault(row["theme_slug"], []).append(row)

        output_rows: list[dict[str, Any]] = []
        routed_count = 0
        direct_route_count = 0
        unresolved_primary_count = 0

        for row in alias_rows:
            detected = row["detected_theme_slug"]
            primary_theme_slug, secondary_theme_slug, governance_state = resolve_theme_governance(
                self.repo_root,
                detected,
            )
            ranked_theme_rows = _rank_theme_rows(theme_registry.get(primary_theme_slug, []))

            if ranked_theme_rows:
                top_row = ranked_theme_rows[0]
                _, linkage_class = normalize_beneficiary_role(
                    beneficiary_role=top_row["beneficiary_role"],
                    mapping_confidence=top_row["mapping_confidence"],
                )
                routing_state = "symbol_routing_ready"
                routed_count += 1
                if linkage_class == "direct_beneficiary":
                    direct_route_count += 1
            else:
                top_row = {}
                linkage_class = "none"
                routing_state = "theme_hit_without_curated_symbol_route"
                unresolved_primary_count += 1

            output_rows.append(
                {
                    "case_id": row["case_id"],
                    "case_type": row["case_type"],
                    "expected_theme_slug": row["expected_theme_slug"],
                    "detected_theme_slug": detected,
                    "match_state": row["match_state"],
                    "primary_theme_slug": primary_theme_slug,
                    "secondary_theme_slug": secondary_theme_slug,
                    "theme_governance_state": governance_state,
                    "top_symbol": top_row.get("symbol", ""),
                    "top_display_name": top_row.get("display_name", ""),
                    "top_mapping_confidence": top_row.get("mapping_confidence", "none"),
                    "top_linkage_class": linkage_class,
                    "top_beneficiary_role": top_row.get("beneficiary_role", ""),
                    "top_symbols_top3": _join_top(ranked_theme_rows, "symbol", limit=3),
                    "routing_state": routing_state,
                }
            )

        _write_csv(self.output_path, output_rows)
        summary = {
            "case_count": len(output_rows),
            "routed_count": routed_count,
            "direct_route_count": direct_route_count,
            "unresolved_primary_count": unresolved_primary_count,
            "authoritative_output": "a_share_theme_symbol_routing_drill_materialized",
        }
        return MaterializedAShareThemeSymbolRoutingDrillV1(summary=summary, rows=output_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareThemeSymbolRoutingDrillV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
