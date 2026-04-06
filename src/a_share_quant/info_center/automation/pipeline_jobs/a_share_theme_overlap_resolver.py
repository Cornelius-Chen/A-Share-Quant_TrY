from __future__ import annotations

import csv
from functools import lru_cache
from itertools import combinations
from pathlib import Path


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=8)
def _load_rule_index(repo_root_str: str) -> dict[tuple[str, str], dict[str, str]]:
    repo_root = Path(repo_root_str)
    registry_path = (
        repo_root
        / "data"
        / "reference"
        / "info_center"
        / "taxonomy"
        / "a_share_theme_overlap_governance_registry_v1.csv"
    )
    rules = _read_csv(registry_path)
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rules:
        key = tuple(sorted((row["primary_theme_slug"], row["secondary_theme_slug"])))
        index[key] = row
    return index


def resolve_theme_governance(repo_root: Path, detected_theme_slug: str) -> tuple[str, str, str]:
    themes = [theme for theme in detected_theme_slug.split("|") if theme]
    themes = list(dict.fromkeys(themes))
    if not themes:
        return "broad_market", "", "no_theme_detected"
    if len(themes) == 1:
        theme = themes[0]
        if theme == "broad_market":
            return theme, "", "broad_market_passthrough"
        return theme, "", "single_theme_passthrough"

    rule_index = _load_rule_index(str(repo_root))
    scores = {theme: 0 for theme in themes}
    resolved_pair_count = 0

    for left, right in combinations(themes, 2):
        key = tuple(sorted((left, right)))
        rule = rule_index.get(key)
        if not rule:
            continue
        precedence_score = int(rule.get("precedence_score", "0"))
        primary = rule["primary_theme_slug"]
        secondary = rule["secondary_theme_slug"]
        scores[primary] += precedence_score
        scores[secondary] -= 1
        resolved_pair_count += 1

    if resolved_pair_count == 0:
        primary_theme = themes[0]
        secondary_themes = themes[1:]
        return primary_theme, "|".join(secondary_themes), "multi_theme_unresolved"

    primary_theme = max(themes, key=lambda theme: (scores[theme], -themes.index(theme)))
    secondary_themes = [theme for theme in themes if theme != primary_theme]
    return primary_theme, "|".join(secondary_themes), "multi_theme_resolved_by_rule"
