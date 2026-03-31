from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V13ConceptSeedReport:
    summary: dict[str, Any]
    seed_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "seed_rows": self.seed_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V13ConceptSeedAnalyzer:
    """Select the first bounded concept-focused seed from the catalyst context rows."""

    def analyze(
        self,
        *,
        concept_inventory_payload: dict[str, Any],
        catalyst_fill_payload: dict[str, Any],
    ) -> V13ConceptSeedReport:
        inventory_summary = dict(concept_inventory_payload.get("summary", {}))
        fill_rows = list(catalyst_fill_payload.get("fill_rows", []))

        theme_rows = [
            row
            for row in fill_rows
            if str(row.get("event_scope", "")) == "theme"
        ]
        seed_rows = [
            {
                "lane_id": str(row.get("lane_id", "")),
                "symbol": str(row.get("symbol", "")),
                "strategy_name": str(row.get("strategy_name", "")),
                "slice_name": str(row.get("slice_name", "")),
                "lane_outcome_label": str(row.get("lane_outcome_label", "")),
                "mapped_context_name": str(row.get("mapped_context_name", "")),
                "mapping_source": str(row.get("mapping_source", "")),
                "persistence_class": str(row.get("persistence_class", "")),
            }
            for row in theme_rows
        ]
        unique_symbols = {row["symbol"] for row in seed_rows}
        cross_strategy_symbols = {
            symbol for symbol in unique_symbols if sum(1 for row in seed_rows if row["symbol"] == symbol) > 1
        }
        ready_next = bool(inventory_summary.get("ready_for_bounded_concept_seed_next")) and len(seed_rows) > 0

        summary = {
            "acceptance_posture": (
                "open_v13_concept_seed_v1_as_bounded_theme_scope_sample"
                if ready_next
                else "hold_v13_concept_seed_v1_until_inventory_is_ready"
            ),
            "seed_row_count": len(seed_rows),
            "unique_symbol_count": len(unique_symbols),
            "cross_strategy_symbol_count": len(cross_strategy_symbols),
            "label_counts": {
                label: sum(1 for row in seed_rows if row["lane_outcome_label"] == label)
                for label in sorted({row["lane_outcome_label"] for row in seed_rows})
            },
            "ready_for_concept_source_fill_next": ready_next,
        }
        interpretation = [
            "The first concept-focused seed should stay inside already-mapped theme-scope rows, not expand into fresh scraping.",
            "That keeps V1.3 tied to closed lanes while still covering opening, persistence, and carry-labeled contexts inside theme mappings.",
            "The next legal action after this seed is bounded concept-source fill rather than new replay or direct model work.",
        ]
        return V13ConceptSeedReport(
            summary=summary,
            seed_rows=seed_rows,
            interpretation=interpretation,
        )


def write_v13_concept_seed_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V13ConceptSeedReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
