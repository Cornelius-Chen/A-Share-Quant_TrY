from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class ThemeDataQualityReport:
    summary: dict[str, Any]
    missing_concept_symbols: list[str]
    primary_concept_distribution: list[dict[str, Any]]
    symbol_concept_profiles: list[dict[str, Any]]
    warnings: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "missing_concept_symbols": self.missing_concept_symbols,
            "primary_concept_distribution": self.primary_concept_distribution,
            "symbol_concept_profiles": self.symbol_concept_profiles,
            "warnings": self.warnings,
        }


class ThemeDataQualityAnalyzer:
    """Summarize theme-pack concept-mapping quality and likely risks."""

    def analyze(
        self,
        *,
        security_master_rows: list[dict[str, str]],
        concept_mapping_rows: list[dict[str, str]],
        sector_mapping_rows: list[dict[str, str]] | None = None,
    ) -> ThemeDataQualityReport:
        security_symbols = sorted({row["symbol"] for row in security_master_rows})
        concept_symbols = sorted({row["symbol"] for row in concept_mapping_rows})
        missing_symbols = sorted(set(security_symbols) - set(concept_symbols))

        primary_rows = [
            row
            for row in concept_mapping_rows
            if str(row.get("is_primary_concept", "")).lower() == "true"
        ]
        primary_counter = Counter(row["concept_name"] for row in primary_rows)
        primary_distribution = [
            {
                "concept_name": concept_name,
                "primary_row_count": count,
            }
            for concept_name, count in primary_counter.most_common()
        ]

        concepts_by_symbol: dict[str, set[str]] = defaultdict(set)
        primary_concepts_by_symbol: dict[str, set[str]] = defaultdict(set)
        primary_date_count_by_symbol: Counter[str] = Counter()
        total_date_count_by_symbol: Counter[str] = Counter()
        primary_weight_sum_by_symbol: defaultdict[str, float] = defaultdict(float)
        for row in concept_mapping_rows:
            symbol = row["symbol"]
            concept_name = row["concept_name"]
            concepts_by_symbol[symbol].add(concept_name)
            total_date_count_by_symbol[symbol] += 1
            if str(row.get("is_primary_concept", "")).lower() == "true":
                primary_concepts_by_symbol[symbol].add(concept_name)
                primary_date_count_by_symbol[symbol] += 1
                try:
                    primary_weight_sum_by_symbol[symbol] += float(row.get("weight", "0") or 0.0)
                except ValueError:
                    pass

        symbol_profiles: list[dict[str, Any]] = []
        static_primary_symbols = 0
        multi_concept_symbols = 0
        for symbol in concept_symbols:
            all_concepts = sorted(concepts_by_symbol[symbol])
            primary_concepts = sorted(primary_concepts_by_symbol[symbol])
            if len(primary_concepts) <= 1:
                static_primary_symbols += 1
            if len(all_concepts) > 1:
                multi_concept_symbols += 1
            symbol_profiles.append(
                {
                    "symbol": symbol,
                    "all_concept_count": len(all_concepts),
                    "all_concepts": all_concepts,
                    "primary_concept_count": len(primary_concepts),
                    "primary_concepts": primary_concepts,
                    "primary_date_count": int(primary_date_count_by_symbol[symbol]),
                    "total_mapping_rows": int(total_date_count_by_symbol[symbol]),
                    "primary_weight_sum": round(primary_weight_sum_by_symbol[symbol], 6),
                }
            )

        covered_symbol_count = len(concept_symbols)
        security_symbol_count = len(security_symbols)
        coverage_ratio = (
            round(covered_symbol_count / security_symbol_count, 6)
            if security_symbol_count
            else 0.0
        )
        static_primary_ratio = (
            round(static_primary_symbols / covered_symbol_count, 6)
            if covered_symbol_count
            else 0.0
        )
        multi_concept_ratio = (
            round(multi_concept_symbols / covered_symbol_count, 6)
            if covered_symbol_count
            else 0.0
        )
        mean_concepts_per_symbol = (
            round(
                sum(profile["all_concept_count"] for profile in symbol_profiles) / covered_symbol_count,
                6,
            )
            if covered_symbol_count
            else 0.0
        )
        top_primary_concept_share = (
            round(primary_distribution[0]["primary_row_count"] / len(primary_rows), 6)
            if primary_rows and primary_distribution
            else 0.0
        )

        sector_override_ratio = None
        if sector_mapping_rows is not None:
            concept_sector_names = {row["concept_name"] for row in concept_mapping_rows}
            sector_override_ratio = round(
                sum(1 for row in sector_mapping_rows if row["sector_name"] in concept_sector_names)
                / len(sector_mapping_rows),
                6,
            ) if sector_mapping_rows else 0.0

        warnings: list[dict[str, Any]] = []
        if coverage_ratio < 0.95:
            warnings.append(
                {
                    "type": "coverage_gap",
                    "detail": "Not every security in the theme pack has concept coverage.",
                    "value": coverage_ratio,
                }
            )
        if static_primary_ratio >= 0.9:
            warnings.append(
                {
                    "type": "static_primary_concepts",
                    "detail": "Primary concept assignments are nearly static across all dates, which suggests time-invariant mapping and potential lookahead contamination.",
                    "value": static_primary_ratio,
                }
            )
        if top_primary_concept_share >= 0.65:
            warnings.append(
                {
                    "type": "concept_concentration",
                    "detail": "One primary concept dominates the mapping too heavily, reducing theme diversity.",
                    "value": top_primary_concept_share,
                }
            )
        if multi_concept_ratio <= 0.2:
            warnings.append(
                {
                    "type": "low_multi_concept_coverage",
                    "detail": "Very few symbols carry multiple concepts, which may understate real A-share theme overlap.",
                    "value": multi_concept_ratio,
                }
            )

        summary = {
            "security_symbol_count": security_symbol_count,
            "concept_covered_symbol_count": covered_symbol_count,
            "concept_symbol_coverage_ratio": coverage_ratio,
            "unique_concept_count": len({row["concept_name"] for row in concept_mapping_rows}),
            "mean_concepts_per_covered_symbol": mean_concepts_per_symbol,
            "static_primary_symbol_ratio": static_primary_ratio,
            "multi_concept_symbol_ratio": multi_concept_ratio,
            "top_primary_concept_share": top_primary_concept_share,
            "warning_count": len(warnings),
        }
        if sector_override_ratio is not None:
            summary["sector_override_ratio"] = sector_override_ratio

        return ThemeDataQualityReport(
            summary=summary,
            missing_concept_symbols=missing_symbols,
            primary_concept_distribution=primary_distribution,
            symbol_concept_profiles=symbol_profiles,
            warnings=warnings,
        )


def write_theme_data_quality_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ThemeDataQualityReport,
    extras: dict[str, Any] | None = None,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    payload = result.as_dict()
    if extras:
        payload["extras"] = extras
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return output_path


def load_theme_quality_inputs(
    *,
    security_master_csv: Path,
    concept_mapping_csv: Path,
    sector_mapping_csv: Path | None = None,
) -> dict[str, list[dict[str, str]]]:
    payload = {
        "security_master_rows": _load_csv_rows(security_master_csv),
        "concept_mapping_rows": _load_csv_rows(concept_mapping_csv),
    }
    if sector_mapping_csv is not None and sector_mapping_csv.exists():
        payload["sector_mapping_rows"] = _load_csv_rows(sector_mapping_csv)
    return payload
