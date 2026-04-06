from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _source_priority(name: str) -> int:
    if "v6_" in name:
        return 60
    if "v5_" in name:
        return 50
    if "v4_" in name:
        return 40
    if "v3_" in name:
        return 30
    if "v2_refresh" in name:
        return 26
    if "v2_seed" in name:
        return 25
    if "theme_research_v1" in name:
        return 22
    if "market_research_v1" in name:
        return 21
    if "market_research_v0" in name:
        return 20
    if "theme_bootstrap" in name:
        return 19
    if "baseline" in name:
        return 10
    if "lite_bootstrap" in name:
        return 5
    return 1


def _normalize_alias(value: str) -> str:
    return "".join(value.strip().split())


@dataclass(slots=True)
class MaterializedAShareIdentityFoundationV1:
    summary: dict[str, Any]
    security_master_rows: list[dict[str, Any]]
    alias_rows: list[dict[str, Any]]


class MaterializeAShareIdentityFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_dir = repo_root / "data" / "reference" / "security_master"
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "identity"
        self.security_master_path = self.output_dir / "a_share_security_master_v1.csv"
        self.alias_map_path = self.output_dir / "a_share_entity_alias_map_v1.csv"
        self.manifest_path = self.output_dir / "a_share_identity_foundation_manifest_v1.json"

    def _load_rows(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for path in sorted(self.input_dir.glob("*.csv")):
            priority = _source_priority(path.name)
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    rows.append(
                        {
                            **row,
                            "source_file": path.name,
                            "source_priority": str(priority),
                        }
                    )
        return rows

    @staticmethod
    def _nonnull_score(row: dict[str, str]) -> int:
        return sum(1 for key in ("name", "board", "exchange", "list_date", "delist_date") if row.get(key))

    def materialize(self) -> MaterializedAShareIdentityFoundationV1:
        input_rows = self._load_rows()
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in input_rows:
            grouped.setdefault(row["symbol"], []).append(row)

        security_master_rows: list[dict[str, Any]] = []
        alias_rows: list[dict[str, Any]] = []

        for symbol in sorted(grouped):
            source_rows = grouped[symbol]
            best_row = sorted(
                source_rows,
                key=lambda row: (int(row["source_priority"]), self._nonnull_score(row), row["source_file"]),
                reverse=True,
            )[0]
            distinct_names = sorted({row["name"] for row in source_rows if row.get("name")})
            distinct_sources = sorted({row["source_file"] for row in source_rows})
            security_master_rows.append(
                {
                    "symbol": symbol,
                    "name": best_row.get("name", ""),
                    "board": best_row.get("board", ""),
                    "exchange": best_row.get("exchange", ""),
                    "list_date": best_row.get("list_date", ""),
                    "delist_date": best_row.get("delist_date", ""),
                    "primary_source_file": best_row["source_file"],
                    "primary_source_priority": int(best_row["source_priority"]),
                    "source_file_count": len(distinct_sources),
                    "distinct_name_count": len(distinct_names),
                }
            )

            seen_aliases: set[tuple[str, str]] = set()
            for name in distinct_names:
                raw_alias = name.strip()
                normalized_alias = _normalize_alias(name)
                for alias_type, alias_value in (
                    ("raw_name", raw_alias),
                    ("normalized_name", normalized_alias),
                ):
                    if not alias_value:
                        continue
                    key = (alias_type, alias_value)
                    if key in seen_aliases:
                        continue
                    seen_aliases.add(key)
                    alias_rows.append(
                        {
                            "symbol": symbol,
                            "alias_type": alias_type,
                            "alias_value": alias_value,
                            "is_primary_name": raw_alias == best_row.get("name", "").strip(),
                            "source_file_count": len(distinct_sources),
                        }
                    )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.security_master_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(security_master_rows[0].keys()))
            writer.writeheader()
            writer.writerows(security_master_rows)
        with self.alias_map_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(alias_rows[0].keys()))
            writer.writeheader()
            writer.writerows(alias_rows)

        summary = {
            "input_source_file_count": len(sorted(self.input_dir.glob("*.csv"))),
            "input_row_count": len(input_rows),
            "materialized_symbol_count": len(security_master_rows),
            "materialized_alias_count": len(alias_rows),
            "multi_source_symbol_count": sum(1 for row in security_master_rows if row["source_file_count"] > 1),
            "max_source_file_count_per_symbol": max(row["source_file_count"] for row in security_master_rows),
            "security_master_path": str(self.security_master_path.relative_to(self.repo_root)),
            "alias_map_path": str(self.alias_map_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareIdentityFoundationV1(
            summary=summary,
            security_master_rows=security_master_rows,
            alias_rows=alias_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeAShareIdentityFoundationV1(repo_root).materialize()
    print(result.summary["security_master_path"])
    print(result.summary["alias_map_path"])


if __name__ == "__main__":
    main()
