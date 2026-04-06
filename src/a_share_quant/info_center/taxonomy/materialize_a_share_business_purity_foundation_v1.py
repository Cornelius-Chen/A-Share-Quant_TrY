from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _latest_group(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    by_symbol: dict[str, list[dict[str, str]]] = {}
    latest_date: dict[str, str] = {}
    for row in rows:
        symbol = row["symbol"]
        trade_date = row["trade_date"]
        if symbol not in latest_date or trade_date > latest_date[symbol]:
            latest_date[symbol] = trade_date
    for row in rows:
        symbol = row["symbol"]
        if row["trade_date"] == latest_date[symbol]:
            by_symbol.setdefault(symbol, []).append(row)
    return by_symbol


def _sector_priority(row: dict[str, str]) -> tuple[int, int, str]:
    sector_name = row["sector_name"]
    sector_id = row["sector_id"]
    mapping_source = row["mapping_source"]
    if "cninfo" in mapping_source and not sector_id.startswith("BK"):
        return (0, -len(sector_name), sector_name)
    if not sector_id.startswith("BK"):
        return (1, -len(sector_name), sector_name)
    return (2, -len(sector_name), sector_name)


@dataclass(slots=True)
class MaterializedAShareBusinessPurityFoundationV1:
    summary: dict[str, Any]
    business_rows: list[dict[str, Any]]
    purity_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareBusinessPurityFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.identity_path = repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        self.sector_path = repo_root / "data" / "reference" / "info_center" / "taxonomy" / "a_share_sector_membership_v1.csv"
        self.concept_path = repo_root / "data" / "reference" / "info_center" / "taxonomy" / "a_share_concept_membership_v1.csv"
        self.business_dir = repo_root / "data" / "reference" / "info_center" / "business_reference"
        self.purity_dir = repo_root / "data" / "reference" / "info_center" / "concept_purity"
        self.business_path = self.business_dir / "a_share_business_reference_v1.csv"
        self.purity_path = self.purity_dir / "a_share_concept_purity_v1.csv"
        self.residual_path = self.purity_dir / "a_share_business_purity_residual_backlog_v1.csv"
        self.manifest_path = self.purity_dir / "a_share_business_purity_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareBusinessPurityFoundationV1:
        identity_rows = _read_csv(self.identity_path)
        sector_rows = _read_csv(self.sector_path)
        concept_rows = _read_csv(self.concept_path)

        latest_sectors = _latest_group(sector_rows, "sector_name")
        latest_concepts = _latest_group(concept_rows, "concept_name")

        business_rows: list[dict[str, Any]] = []
        purity_rows: list[dict[str, Any]] = []
        residual_rows: list[dict[str, Any]] = []

        for identity_row in identity_rows:
            symbol = identity_row["symbol"]
            name = identity_row["name"]
            symbol_sectors = sorted(latest_sectors.get(symbol, []), key=_sector_priority)
            symbol_concepts = sorted(
                latest_concepts.get(symbol, []),
                key=lambda row: (-float(row.get("weight") or 0.0), row["concept_name"]),
            )

            anchor_sector = symbol_sectors[0]["sector_name"] if symbol_sectors else ""
            anchor_sector_source = symbol_sectors[0]["mapping_source"] if symbol_sectors else ""
            top_concepts = symbol_concepts[:3]
            top_concept_names = [row["concept_name"] for row in top_concepts]

            if symbol_sectors and symbol_concepts:
                reference_quality = "sector_backed_with_concepts"
            elif symbol_sectors:
                reference_quality = "sector_only_reference"
            elif symbol_concepts:
                reference_quality = "concept_only_reference"
            else:
                reference_quality = "sparse_reference"

            business_summary = anchor_sector or "/".join(top_concept_names) or "unclassified"
            business_rows.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "anchor_sector_name": anchor_sector,
                    "anchor_sector_source": anchor_sector_source,
                    "business_summary": business_summary,
                    "top_concept_1": top_concept_names[0] if len(top_concept_names) > 0 else "",
                    "top_concept_2": top_concept_names[1] if len(top_concept_names) > 1 else "",
                    "top_concept_3": top_concept_names[2] if len(top_concept_names) > 2 else "",
                    "latest_sector_count": len(symbol_sectors),
                    "latest_concept_count": len(symbol_concepts),
                    "reference_quality": reference_quality,
                }
            )

            latest_trade_date = ""
            if symbol_concepts:
                latest_trade_date = symbol_concepts[0]["trade_date"]
                top_weight = float(symbol_concepts[0]["weight"] or 0.0)
                second_weight = float(symbol_concepts[1]["weight"] or 0.0) if len(symbol_concepts) > 1 else 0.0
                if len(symbol_concepts) == 1 or top_weight >= 0.8:
                    purity_band = "high_purity_single_theme"
                elif top_weight >= 0.55 and second_weight <= 0.30:
                    purity_band = "moderate_focus"
                else:
                    purity_band = "mixed_multi_theme"
                if len(symbol_concepts) >= 3 and top_weight < 0.5:
                    cross_theme_risk = "high"
                elif len(symbol_concepts) >= 2 and top_weight < 0.65:
                    cross_theme_risk = "medium"
                else:
                    cross_theme_risk = "low"
                purity_rows.append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "latest_trade_date": latest_trade_date,
                        "primary_concept_name": symbol_concepts[0]["concept_name"],
                        "primary_concept_weight": symbol_concepts[0]["weight"],
                        "secondary_concept_name": symbol_concepts[1]["concept_name"] if len(symbol_concepts) > 1 else "",
                        "secondary_concept_weight": symbol_concepts[1]["weight"] if len(symbol_concepts) > 1 else "",
                        "concept_count_latest": len(symbol_concepts),
                        "purity_band": purity_band,
                        "cross_theme_risk": cross_theme_risk,
                    }
                )
            else:
                purity_rows.append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "latest_trade_date": "",
                        "primary_concept_name": "",
                        "primary_concept_weight": "",
                        "secondary_concept_name": "",
                        "secondary_concept_weight": "",
                        "concept_count_latest": 0,
                        "purity_band": "no_concept_surface",
                        "cross_theme_risk": "unknown",
                    }
                )

            if reference_quality != "sector_backed_with_concepts":
                residual_rows.append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "residual_reason": reference_quality,
                    }
                )

        self.business_dir.mkdir(parents=True, exist_ok=True)
        self.purity_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.business_path, business_rows)
        _write(self.purity_path, purity_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "business_reference_count": len(business_rows),
            "concept_purity_count": len(purity_rows),
            "sector_backed_with_concepts_count": sum(
                row["reference_quality"] == "sector_backed_with_concepts" for row in business_rows
            ),
            "high_purity_count": sum(row["purity_band"] == "high_purity_single_theme" for row in purity_rows),
            "mixed_multi_theme_count": sum(row["purity_band"] == "mixed_multi_theme" for row in purity_rows),
            "residual_count": len(residual_rows),
            "business_path": str(self.business_path.relative_to(self.repo_root)),
            "purity_path": str(self.purity_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareBusinessPurityFoundationV1(
            summary=summary,
            business_rows=business_rows,
            purity_rows=purity_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareBusinessPurityFoundationV1(repo_root).materialize()
    print(result.summary["business_path"])


if __name__ == "__main__":
    main()
