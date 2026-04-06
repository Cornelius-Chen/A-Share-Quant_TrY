from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


OFFICIAL_POLICY_KEYWORDS = (
    "国务院",
    "国常会",
    "政府工作报告",
    "发改委",
    "工信部",
    "证监会",
    "国资委",
    "财政部",
    "央行",
    "人民银行",
    "白皮书",
    "行动计划",
    "实施方案",
    "专项规划",
    "指导意见",
)

POSITIVE_DIRECTIONAL_KEYWORDS = (
    "支持",
    "推进",
    "实施",
    "加快",
    "鼓励",
    "落地",
    "规划",
    "方案",
    "意见",
    "启动",
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


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _source_authority_score(source_family: str) -> float:
    if source_family == "cls":
        return 0.88
    if source_family == "sina":
        return 0.74
    return 0.70


def _official_policy_signal(title: str) -> float:
    return 1.0 if _contains_any(title, OFFICIAL_POLICY_KEYWORDS) else 0.0


def _directional_policy_signal(title: str) -> float:
    return 1.0 if _contains_any(title, POSITIVE_DIRECTIONAL_KEYWORDS) else 0.0


def _theme_registry_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["theme_slug"]: row for row in rows}


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsFocusScoringSurfaceV1:
    summary: dict[str, Any]
    detail_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsFocusScoringSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        derived_base = repo_root / "data" / "derived" / "info_center" / "time_slices"
        taxonomy_base = repo_root / "data" / "reference" / "info_center" / "taxonomy"
        serving_base = repo_root / "data" / "reference" / "info_center" / "serving_registry"
        self.candidate_surface_path = (
            derived_base / "a_share_internal_hot_news_controlled_merge_candidate_surface_v1.csv"
        )
        self.focus_cycle_registry_path = (
            taxonomy_base / "a_share_theme_focus_cycle_registry_v1.csv"
        )
        self.detail_output_path = (
            derived_base / "a_share_internal_hot_news_focus_scoring_surface_v1.csv"
        )
        self.summary_output_path = (
            derived_base / "a_share_internal_hot_news_focus_scoring_summary_v1.csv"
        )
        self.registry_path = (
            serving_base / "a_share_internal_hot_news_focus_scoring_surface_registry_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsFocusScoringSurfaceV1:
        candidate_rows = _read_csv(self.candidate_surface_path)
        cycle_registry = _theme_registry_map(_read_csv(self.focus_cycle_registry_path))

        grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in candidate_rows:
            theme_slug = row.get("primary_theme_slug", "")
            top_symbol = row.get("top_symbol", "")
            if not theme_slug or theme_slug == "broad_market" or not top_symbol:
                continue
            grouped[(theme_slug, top_symbol)].append(row)

        detail_rows: list[dict[str, Any]] = []
        for (theme_slug, top_symbol), rows in grouped.items():
            cycle = cycle_registry.get(
                theme_slug,
                {
                    "policy_persistence_score": "0.50",
                    "policy_sensitivity_score": "0.50",
                    "second_wave_retrigger_score": "0.50",
                    "crowding_exhaustion_score": "0.50",
                    "tradability_score": "0.50",
                    "cycle_state": "unclassified_cycle_state",
                    "focus_bias_class": "unclassified_focus_bias",
                },
            )
            policy_persistence = _to_float(cycle["policy_persistence_score"], 0.5)
            policy_sensitivity = _to_float(cycle["policy_sensitivity_score"], 0.5)
            second_wave = _to_float(cycle["second_wave_retrigger_score"], 0.5)
            crowding = _to_float(cycle["crowding_exhaustion_score"], 0.5)
            tradability = _to_float(cycle["tradability_score"], 0.5)

            row_scores: list[float] = []
            official_hits = 0
            directional_hits = 0
            source_families: list[str] = []
            source_row_ids: list[str] = []
            for row in rows:
                title = row.get("title", "")
                source_family = row.get("source_family", "")
                source_families.append(source_family)
                source_row_ids.append(row.get("source_row_id", ""))
                official_signal = _official_policy_signal(title)
                directional_signal = _directional_policy_signal(title)
                official_hits += int(official_signal)
                directional_hits += int(directional_signal)
                authority = _source_authority_score(source_family)
                message_multiplier = (
                    authority
                    * (1.0 + 0.35 * official_signal * policy_sensitivity)
                    * (1.0 + 0.15 * directional_signal * policy_persistence)
                )
                cycle_multiplier = (
                    (0.70 + 0.30 * policy_persistence)
                    * (0.65 + 0.35 * second_wave)
                    * (0.65 + 0.35 * tradability)
                    * (1.10 - 0.35 * crowding)
                )
                row_scores.append(round(message_multiplier * cycle_multiplier, 6))

            focus_total_score = round(sum(row_scores), 4)
            focus_score_density = round(focus_total_score / max(len(row_scores), 1), 4)
            detail_rows.append(
                {
                    "theme_slug": theme_slug,
                    "watch_symbol": top_symbol,
                    "support_row_count": str(len(rows)),
                    "support_source_family_count": str(len(set(source_families))),
                    "official_policy_hit_count": str(official_hits),
                    "directional_policy_hit_count": str(directional_hits),
                    "policy_persistence_score": cycle["policy_persistence_score"],
                    "policy_sensitivity_score": cycle["policy_sensitivity_score"],
                    "second_wave_retrigger_score": cycle["second_wave_retrigger_score"],
                    "crowding_exhaustion_score": cycle["crowding_exhaustion_score"],
                    "tradability_score": cycle["tradability_score"],
                    "cycle_state": cycle["cycle_state"],
                    "focus_bias_class": cycle["focus_bias_class"],
                    "focus_total_score": f"{focus_total_score:.4f}",
                    "focus_score_density": f"{focus_score_density:.4f}",
                    "support_source_row_ids_top5": ",".join([rid for rid in source_row_ids[:5] if rid]),
                    "focus_scoring_state": "focus_scoring_ready",
                }
            )

        detail_rows.sort(
            key=lambda row: (
                -_to_float(row["focus_total_score"]),
                -_to_float(row["focus_score_density"]),
                -int(row["support_row_count"]),
                row["theme_slug"],
                row["watch_symbol"],
            )
        )

        summary_row = {
            "focus_scoring_id": "internal_hot_news_focus_scoring_latest",
            "scored_row_count": str(len(detail_rows)),
            "top_theme_slug": detail_rows[0]["theme_slug"] if detail_rows else "none",
            "top_watch_symbol": detail_rows[0]["watch_symbol"] if detail_rows else "",
            "top_focus_total_score": detail_rows[0]["focus_total_score"] if detail_rows else "0.0000",
            "top_cycle_state": detail_rows[0]["cycle_state"] if detail_rows else "none",
            "focus_scoring_summary_state": "focus_scoring_summarized",
        }

        _write_csv(self.detail_output_path, detail_rows)
        _write_csv(self.summary_output_path, [summary_row])
        _write_csv(
            self.registry_path,
            [
                {
                    "view_id": "internal_hot_news_focus_scoring_surface",
                    "artifact_path": str(self.detail_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
                {
                    "view_id": "internal_hot_news_focus_scoring_summary",
                    "artifact_path": str(self.summary_output_path.relative_to(self.repo_root)),
                    "view_state": "read_ready_internal_only",
                },
            ],
        )

        summary = {
            "scored_row_count": len(detail_rows),
            "top_theme_slug": summary_row["top_theme_slug"],
            "top_watch_symbol": summary_row["top_watch_symbol"],
            "top_focus_total_score": _to_float(summary_row["top_focus_total_score"]),
            "top_cycle_state": summary_row["top_cycle_state"],
            "authoritative_output": "a_share_internal_hot_news_focus_scoring_surface_materialized",
        }
        return MaterializedAShareInternalHotNewsFocusScoringSurfaceV1(
            summary=summary,
            detail_rows=detail_rows,
            summary_rows=[summary_row],
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsFocusScoringSurfaceV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
