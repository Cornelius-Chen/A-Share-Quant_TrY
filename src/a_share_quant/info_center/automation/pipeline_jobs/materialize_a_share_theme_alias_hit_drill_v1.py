from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_signal_enrichment_v1 import (
    THEME_ALIAS_MAP,
)


def _detect_themes(text: str) -> list[str]:
    hits: list[str] = []
    for theme_slug, aliases in THEME_ALIAS_MAP.items():
        if any(alias in text for alias in aliases):
            hits.append(theme_slug)
    return hits


@dataclass(slots=True)
class MaterializedAShareThemeAliasHitDrillV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareThemeAliasHitDrillV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_alias_hit_drill_v1.csv"
        )

    @staticmethod
    def _build_cases() -> list[dict[str, str]]:
        cases: list[dict[str, str]] = []
        for theme_slug, aliases in THEME_ALIAS_MAP.items():
            primary_alias = aliases[0]
            secondary_alias = aliases[1] if len(aliases) > 1 else aliases[0]
            headline = f"{primary_alias}政策催化升温，{secondary_alias}方向再获市场关注"
            cases.append(
                {
                    "case_id": f"{theme_slug}_single_hit",
                    "expected_theme_slug": theme_slug,
                    "headline": headline,
                    "case_type": "single_theme_alias_hit",
                }
            )

        cases.extend(
            [
                {
                    "case_id": "pv_storage_dual_hit",
                    "expected_theme_slug": "pv_solar|energy_storage",
                    "headline": "光伏与储能景气共振，逆变器和储能系统同步升温",
                    "case_type": "dual_theme_alias_hit",
                },
                {
                    "case_id": "drug_device_dual_hit",
                    "expected_theme_slug": "innovative_drug|medicine_devices",
                    "headline": "创新药和医疗器械双线走强，CXO与设备采购同步改善",
                    "case_type": "dual_theme_alias_hit",
                },
                {
                    "case_id": "consumer_liquor_dual_hit",
                    "expected_theme_slug": "consumer_staples|liquor",
                    "headline": "内需消费修复，白酒与必选消费景气度回升",
                    "case_type": "dual_theme_alias_hit",
                },
            ]
        )
        return cases

    def materialize(self) -> MaterializedAShareThemeAliasHitDrillV1:
        rows: list[dict[str, Any]] = []
        for case in self._build_cases():
            expected = set(case["expected_theme_slug"].split("|"))
            detected = _detect_themes(case["headline"])
            detected_set = set(detected)
            if detected_set == expected:
                match_state = "exact_expected_hit"
            elif expected.issubset(detected_set):
                match_state = "expected_covered_with_overlap"
            else:
                match_state = "partial_or_miss"
            rows.append(
                {
                    "case_id": case["case_id"],
                    "case_type": case["case_type"],
                    "expected_theme_slug": case["expected_theme_slug"],
                    "headline": case["headline"],
                    "detected_theme_slug": "|".join(detected),
                    "detected_theme_count": str(len(detected)),
                    "match_state": match_state,
                }
            )

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "case_count": len(rows),
            "single_case_count": sum(row["case_type"] == "single_theme_alias_hit" for row in rows),
            "dual_case_count": sum(row["case_type"] == "dual_theme_alias_hit" for row in rows),
            "exact_expected_hit_count": sum(row["match_state"] == "exact_expected_hit" for row in rows),
            "expected_covered_count": sum(
                row["match_state"] in {"exact_expected_hit", "expected_covered_with_overlap"} for row in rows
            ),
            "overlap_hit_count": sum(row["match_state"] == "expected_covered_with_overlap" for row in rows),
            "partial_or_miss_count": sum(row["match_state"] == "partial_or_miss" for row in rows),
            "authoritative_output": "a_share_theme_alias_hit_drill_materialized",
        }
        return MaterializedAShareThemeAliasHitDrillV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareThemeAliasHitDrillV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
