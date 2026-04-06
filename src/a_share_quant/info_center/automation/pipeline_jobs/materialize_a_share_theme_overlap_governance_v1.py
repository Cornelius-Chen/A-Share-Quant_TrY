from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


OVERLAP_RULES = [
    {
        "primary_theme_slug": "consumer_electronics",
        "secondary_theme_slug": "consumer_staples",
        "overlap_class": "broad_vs_specific",
        "precedence_score": "90",
        "governance_action": "prefer_primary_theme",
        "rationale": "消费电子是更窄更交易化的子主题，消费是宽口径上位主题。",
    },
    {
        "primary_theme_slug": "innovative_drug",
        "secondary_theme_slug": "pharmaceutical",
        "overlap_class": "specific_vs_general",
        "precedence_score": "95",
        "governance_action": "prefer_primary_theme",
        "rationale": "创新药是医药中的高辨识子主题，适合优先作为交易主标签。",
    },
    {
        "primary_theme_slug": "medicine_devices",
        "secondary_theme_slug": "pharmaceutical",
        "overlap_class": "adjacent_specific_vs_general",
        "precedence_score": "92",
        "governance_action": "prefer_primary_theme",
        "rationale": "医疗器械比医药更具体，应在器械命中时优先保留。",
    },
    {
        "primary_theme_slug": "energy_storage",
        "secondary_theme_slug": "power_equipment",
        "overlap_class": "specific_vs_general",
        "precedence_score": "93",
        "governance_action": "prefer_primary_theme",
        "rationale": "储能是电力设备中的更窄主题，交易上通常优先。",
    },
    {
        "primary_theme_slug": "pv_solar",
        "secondary_theme_slug": "power_equipment",
        "overlap_class": "specific_vs_general",
        "precedence_score": "93",
        "governance_action": "prefer_primary_theme",
        "rationale": "光伏具备更强板块独立性，优先于电力设备大类。",
    },
    {
        "primary_theme_slug": "military_electronics",
        "secondary_theme_slug": "defense_industry",
        "overlap_class": "specific_vs_general",
        "precedence_score": "94",
        "governance_action": "prefer_primary_theme",
        "rationale": "军工电子是军工中的更窄子方向，应优先作为主主题。",
    },
    {
        "primary_theme_slug": "liquor",
        "secondary_theme_slug": "consumer_staples",
        "overlap_class": "specific_vs_general",
        "precedence_score": "91",
        "governance_action": "prefer_primary_theme",
        "rationale": "白酒是消费中的高辨识度子主题，交易上应优先于宽口径消费。",
    },
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class MaterializedAShareThemeOverlapGovernanceV1:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    resolved_rows: list[dict[str, Any]]


class MaterializeAShareThemeOverlapGovernanceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.drill_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_alias_hit_drill_v1.csv"
        )
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_overlap_governance_registry_v1.csv"
        )
        self.resolved_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "taxonomy"
            / "a_share_theme_overlap_resolution_drill_v1.csv"
        )

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        materialized_rows = rows or [{"row_state": "empty"}]
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
            writer.writeheader()
            writer.writerows(materialized_rows)

    @staticmethod
    def _build_rule_index() -> dict[tuple[str, str], dict[str, str]]:
        index: dict[tuple[str, str], dict[str, str]] = {}
        for row in OVERLAP_RULES:
            key = tuple(sorted((row["primary_theme_slug"], row["secondary_theme_slug"])))
            index[key] = row
        return index

    def materialize(self) -> MaterializedAShareThemeOverlapGovernanceV1:
        drill_rows = _read_csv(self.drill_path)
        rule_index = self._build_rule_index()

        registry_rows = [
            {
                **row,
                "mapping_source": "curated_theme_overlap_governance_v1",
            }
            for row in OVERLAP_RULES
        ]

        resolved_rows: list[dict[str, Any]] = []
        for row in drill_rows:
            detected = [item for item in row["detected_theme_slug"].split("|") if item]
            primary_theme = detected[0] if detected else ""
            secondary_themes = detected[1:] if len(detected) > 1 else []
            governance_state = "no_overlap"
            applied_rule = ""

            if len(detected) > 1:
                governance_state = "overlap_unresolved"
                for candidate_secondary in detected:
                    if candidate_secondary == primary_theme:
                        continue
                    key = tuple(sorted((primary_theme, candidate_secondary)))
                    if key in rule_index:
                        rule = rule_index[key]
                        primary_theme = rule["primary_theme_slug"]
                        secondary_themes = [theme for theme in detected if theme != primary_theme]
                        applied_rule = f"{rule['primary_theme_slug']}>{rule['secondary_theme_slug']}"
                        governance_state = "overlap_resolved_by_rule"
                        break

            resolved_rows.append(
                {
                    "case_id": row["case_id"],
                    "expected_theme_slug": row["expected_theme_slug"],
                    "detected_theme_slug": row["detected_theme_slug"],
                    "primary_theme_slug": primary_theme,
                    "secondary_theme_slug": "|".join(secondary_themes),
                    "governance_state": governance_state,
                    "applied_rule": applied_rule,
                }
            )

        self._write_csv(self.registry_path, registry_rows)
        self._write_csv(self.resolved_path, resolved_rows)

        summary = {
            "governance_rule_count": len(registry_rows),
            "resolution_case_count": len(resolved_rows),
            "resolved_overlap_count": sum(
                row["governance_state"] == "overlap_resolved_by_rule" for row in resolved_rows
            ),
            "unresolved_overlap_count": sum(
                row["governance_state"] == "overlap_unresolved" for row in resolved_rows
            ),
            "authoritative_output": "a_share_theme_overlap_governance_materialized",
        }
        return MaterializedAShareThemeOverlapGovernanceV1(
            summary=summary,
            registry_rows=registry_rows,
            resolved_rows=resolved_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareThemeOverlapGovernanceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
