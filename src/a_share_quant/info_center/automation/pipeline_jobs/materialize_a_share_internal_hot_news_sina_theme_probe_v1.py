from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_beneficiary_role_normalizer import (
    normalize_beneficiary_role,
)
from a_share_quant.info_center.automation.pipeline_jobs.a_share_theme_overlap_resolver import (
    resolve_theme_governance,
)
from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_signal_enrichment_v1 import (
    THEME_ALIAS_MAP,
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


def _detect_themes(text: str) -> list[str]:
    hits: list[str] = []
    for theme_slug, aliases in THEME_ALIAS_MAP.items():
        if any(alias in text for alias in aliases):
            hits.append(theme_slug)
    return hits


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


def _join_top(rows: list[dict[str, Any]], key: str, limit: int = 5) -> str:
    values = [str(row.get(key, "")).strip() for row in rows[:limit]]
    return ",".join([value for value in values if value])


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsSinaThemeProbeV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsSinaThemeProbeV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.staging_path = (
            repo_root
            / "data"
            / "temp"
            / "info_center"
            / "ingest_staging"
            / "a_share_internal_hot_news_sina_7x24_staging_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_beneficiary_registry_v1.csv"
        )
        self.surface_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_sina_theme_probe_surface_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_sina_theme_probe_summary_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsSinaThemeProbeV1:
        staging_rows = _read_csv(self.staging_path)
        registry_rows = _read_csv(self.registry_path)

        theme_registry: dict[str, list[dict[str, str]]] = {}
        for row in registry_rows:
            theme_registry.setdefault(row["theme_slug"], []).append(row)

        output_rows: list[dict[str, Any]] = []
        for row in staging_rows:
            text = " ".join(
                [row.get("title", "").strip(), row.get("brief", "").strip(), row.get("content", "").strip()]
            )
            detected = _detect_themes(text)
            detected_slug = "|".join(detected) if detected else "broad_market"
            primary_theme_slug, secondary_theme_slug, governance_state = resolve_theme_governance(
                self.repo_root,
                detected_slug,
            )
            ranked_theme_rows = _rank_theme_rows(theme_registry.get(primary_theme_slug, []))

            if primary_theme_slug == "broad_market":
                probe_state = "broad_market_only"
                top_symbol = ""
                top_linkage_class = "none"
                top_mapping_confidence = "none"
            elif ranked_theme_rows:
                top_row = ranked_theme_rows[0]
                _, top_linkage_class = normalize_beneficiary_role(
                    beneficiary_role=top_row["beneficiary_role"],
                    mapping_confidence=top_row["mapping_confidence"],
                )
                top_symbol = top_row["symbol"]
                top_mapping_confidence = top_row["mapping_confidence"]
                probe_state = "theme_hit_with_symbol_route"
            else:
                top_symbol = ""
                top_linkage_class = "unmapped"
                top_mapping_confidence = "none"
                probe_state = "theme_hit_without_symbol_route"

            output_rows.append(
                {
                    "telegraph_id": row["telegraph_id"],
                    "public_ts": row["public_ts"],
                    "source_name": row["source_name"],
                    "title": row["title"],
                    "detected_theme_slug": detected_slug,
                    "primary_theme_slug": primary_theme_slug,
                    "secondary_theme_slug": secondary_theme_slug,
                    "theme_governance_state": governance_state,
                    "probe_state": probe_state,
                    "top_symbol": top_symbol,
                    "top_linkage_class": top_linkage_class,
                    "top_mapping_confidence": top_mapping_confidence,
                    "probe_delivery_state": "sina_theme_probe_ready",
                }
            )

        theme_hit_rows = [row for row in output_rows if row["probe_state"] != "broad_market_only"]
        symbol_route_rows = [row for row in output_rows if row["probe_state"] == "theme_hit_with_symbol_route"]
        summary_row = {
            "probe_id": "internal_hot_news_sina_theme_probe_latest",
            "sample_row_count": str(len(output_rows)),
            "broad_market_only_count": str(sum(row["probe_state"] == "broad_market_only" for row in output_rows)),
            "theme_hit_count": str(len(theme_hit_rows)),
            "theme_hit_with_symbol_route_count": str(len(symbol_route_rows)),
            "theme_hit_without_symbol_route_count": str(
                sum(row["probe_state"] == "theme_hit_without_symbol_route" for row in output_rows)
            ),
            "unique_primary_theme_count": str(len({row["primary_theme_slug"] for row in theme_hit_rows})),
            "top_primary_themes_top5": _join_top(theme_hit_rows, "primary_theme_slug"),
            "top_symbols_top5": _join_top(symbol_route_rows, "top_symbol"),
            "probe_summary_state": "sina_theme_probe_summarized",
        }

        _write_csv(self.surface_path, output_rows)
        _write_csv(self.summary_path, [summary_row])

        summary = {
            "sample_row_count": len(output_rows),
            "broad_market_only_count": int(summary_row["broad_market_only_count"]),
            "theme_hit_count": int(summary_row["theme_hit_count"]),
            "theme_hit_with_symbol_route_count": int(summary_row["theme_hit_with_symbol_route_count"]),
            "theme_hit_without_symbol_route_count": int(summary_row["theme_hit_without_symbol_route_count"]),
            "unique_primary_theme_count": int(summary_row["unique_primary_theme_count"]),
            "authoritative_output": "a_share_internal_hot_news_sina_theme_probe_materialized",
        }
        return MaterializedAShareInternalHotNewsSinaThemeProbeV1(summary=summary, rows=output_rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsSinaThemeProbeV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
