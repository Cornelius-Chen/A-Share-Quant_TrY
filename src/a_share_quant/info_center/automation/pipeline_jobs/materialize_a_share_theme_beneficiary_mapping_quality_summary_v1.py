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


def _quality_state(*, direct_count: int, proxy_count: int, weak_count: int, total_count: int) -> str:
    if total_count == 0:
        return "empty"
    if direct_count == total_count:
        return "direct_clean"
    if direct_count >= proxy_count and weak_count == 0:
        return "direct_led_with_proxy_tail"
    if proxy_count >= direct_count and weak_count == 0:
        return "proxy_heavy"
    if weak_count > 0 and direct_count > 0:
        return "mixed_with_weak_tail"
    if weak_count > 0 and direct_count == 0:
        return "weak_exposed"
    return "mixed"


@dataclass(slots=True)
class MaterializedAShareThemeBeneficiaryMappingQualitySummaryV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareThemeBeneficiaryMappingQualitySummaryV1:
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
            / "a_share_theme_beneficiary_mapping_quality_summary_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    def materialize(self) -> MaterializedAShareThemeBeneficiaryMappingQualitySummaryV1:
        registry_rows = _read_csv(self.registry_path)
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in registry_rows:
            grouped.setdefault(row["theme_slug"], []).append(row)

        rows: list[dict[str, Any]] = []
        total_direct = 0
        total_proxy = 0
        total_weak = 0

        for theme_slug in sorted(grouped):
            theme_rows = grouped[theme_slug]
            linkage_rows: list[str] = []
            for row in theme_rows:
                _, linkage_class = normalize_beneficiary_role(
                    beneficiary_role=row["beneficiary_role"],
                    mapping_confidence=row["mapping_confidence"],
                )
                linkage_rows.append(linkage_class)

            direct_count = sum(linkage == "direct_beneficiary" for linkage in linkage_rows)
            proxy_count = sum(linkage == "proxy_beneficiary" for linkage in linkage_rows)
            weak_count = sum(linkage == "weak_association" for linkage in linkage_rows)
            total_count = len(theme_rows)

            total_direct += direct_count
            total_proxy += proxy_count
            total_weak += weak_count

            dominant_linkage_class = max(
                (
                    ("direct_beneficiary", direct_count),
                    ("proxy_beneficiary", proxy_count),
                    ("weak_association", weak_count),
                ),
                key=lambda item: (item[1], item[0] == "direct_beneficiary", item[0] == "proxy_beneficiary"),
            )[0]

            rows.append(
                {
                    "theme_slug": theme_slug,
                    "target_board": theme_rows[0]["target_board"],
                    "symbol_count": str(len({row["symbol"] for row in theme_rows})),
                    "registry_row_count": str(total_count),
                    "direct_count": str(direct_count),
                    "proxy_count": str(proxy_count),
                    "weak_count": str(weak_count),
                    "high_confidence_count": str(sum(row["mapping_confidence"] == "high" for row in theme_rows)),
                    "medium_confidence_count": str(sum(row["mapping_confidence"] == "medium" for row in theme_rows)),
                    "low_confidence_count": str(sum(row["mapping_confidence"] == "low" for row in theme_rows)),
                    "dominant_linkage_class": dominant_linkage_class,
                    "quality_state": _quality_state(
                        direct_count=direct_count,
                        proxy_count=proxy_count,
                        weak_count=weak_count,
                        total_count=total_count,
                    ),
                    "summary_state": "mapping_quality_summarized",
                }
            )

        self._write_csv(self.output_path, rows)

        summary = {
            "theme_count": len(rows),
            "direct_row_count": total_direct,
            "proxy_row_count": total_proxy,
            "weak_row_count": total_weak,
            "direct_clean_theme_count": sum(row["quality_state"] == "direct_clean" for row in rows),
            "proxy_heavy_theme_count": sum(row["quality_state"] == "proxy_heavy" for row in rows),
            "weak_exposed_theme_count": sum(row["weak_count"] != "0" for row in rows),
            "authoritative_output": "a_share_theme_beneficiary_mapping_quality_summary_materialized",
        }
        return MaterializedAShareThemeBeneficiaryMappingQualitySummaryV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareThemeBeneficiaryMappingQualitySummaryV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
